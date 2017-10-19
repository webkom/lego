import logging
import os
from datetime import datetime

import yaml
from django.conf import settings
from django.core.management import call_command
from django.utils.crypto import get_random_string
from slugify import slugify

from lego.apps.articles.models import Article
from lego.apps.events.models import Event
from lego.apps.files.exceptions import UnknownFileType
from lego.apps.files.models import File
from lego.apps.files.storage import storage
from lego.apps.flatpages.models import Page
from lego.apps.joblistings.models import Joblisting
from lego.apps.meetings.models import Meeting
from lego.apps.quotes.models import Quote
from lego.apps.users.fixtures.initial_abakus_groups import initial_tree
from lego.apps.users.models import AbakusGroup, User
from lego.utils.functions import insert_abakus_groups
from lego.utils.management_command import BaseCommand

log = logging.getLogger(__name__)
IMPORT_DIRECTORY = '.nerd_export'

lego_group_ids = {
    1: 'Users',
    2: 'Abakus',
    3: 'Abakom',
    4: 'Arrkom',
    5: 'backup',
    6: 'Bedkom',
    7: 'Fagkom',
    8: 'LaBamba',
    9: 'PR',
    10: 'readme',
    11: 'Webkom',
    12: 'Hovedstyret',
    13: 'Interessegrupper',
    14: 'Students',
    15: 'Datateknologi',
    16: '1. klasse Datateknologi',
    17: '2. klasse Datateknologi',
    18: '3. klasse Datateknologi',
    19: '4. klasse Datateknologi',
    20: '5. klasse Datateknologi',
    21: 'Kommunikasjonsteknologi',
    22: '1. klasse Kommunikasjonsteknologi',
    23: '2. klasse Kommunikasjonsteknologi',
    24: '3. klasse Kommunikasjonsteknologi',
    25: '4. klasse Kommunikasjonsteknologi',
    26: '5. klasse Kommunikasjonsteknologi'
}


def filepath_to_key(filepath):
    return None if not filepath else slugify(filepath.rsplit('.', 1)[0])


class Command(BaseCommand):
    help = 'Imports data from NERD, requires data (fixtures) to be placed inside a directory.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            default=False,
            help='Dry run the import (only test the import).',
        )
        parser.add_argument(
            '--yes',
            action='store_true',
            default=False,
            help='Answer yes during questions'
        )

    def call_command(self, *args, **options):
        call_command(*args, verbosity=self.verbosity, **options)

    def load_yaml(self, fixture):
        with open(fixture, 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                exit(0)

    def load_fixtures(self, fixtures):
        for fixture in fixtures:
            path = 'lego/apps/{}'.format(fixture)
            self.call_command('loaddata', path)

    def load_initial_fixtures(self):
        log.info('Loading initial fixtures:')

        self.load_fixtures([
            'files/fixtures/initial_files.yaml',
            'tags/fixtures/initial_tags.yaml',
        ])

        log.info('Done loading initial fixtures!')

    def import_nerd_fixture(self, file_name):
        log.info(f'Importing fixture: {file_name}')
        path = f'{IMPORT_DIRECTORY}/{file_name}'
        self.call_command('loaddata', path)
        log.info(f'Done importing fixture: {file_name}')

    def find_group_path(self, key, dictionary, path=None):
        if not path:
            path = []
        for k, v in dictionary.items():
            if k == key:
                yield v, path + [k]
            elif isinstance(v, dict):
                for result, path in self.find_group_path(key, v, path + [k]):
                    yield result, path
            elif isinstance(v, list):
                for d in v:
                    if isinstance(d, dict):
                        for result, path in self.find_group_path(key, d, path + [k]):
                            yield result, path

    def upload_files(self, uploads_bucket, directory):
        for file in os.listdir(directory):
            if file[0] == '.':
                # Ignore all files / directories that start with a period
                continue
            file_path = os.path.join(directory, file)
            if os.path.isdir(file_path):
                continue
            try:
                file_type = File.get_file_type(file)
            except UnknownFileType:
                log.warning(f'Unknown filetype for file: {file_path}')
                continue

            file_pk = file_path.replace(f'{IMPORT_DIRECTORY}/files/', '')

            log.info(f'Uploading {file_path} to bucket with key: "{file_pk}"')
            storage.upload_file(uploads_bucket, file, file_path)

            # Kind of hacky, but no other option on Linux
            file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
            # Only create the file if does not exist
            File.objects.get_or_create(pk=file_pk, defaults={
                'created_at': file_date,
                'state': 'ready',
                'file_type': file_type,
                'token': get_random_string(32),
                'user': None,
                'public': False
            })

    def handle_fixture_import(self, file_name, skip_questions=False):
        if os.path.isdir(f'{IMPORT_DIRECTORY}/{file_name}'):
            return
        log.info(f'Handling fixture: {file_name}')
        if not skip_questions:
            choice = input('Do you wish to import this fixture? [Y/n]').lower()
            if choice == 'n' or choice == 'no' or choice == 'nei':
                print(f'[IGNORE] Ignoring fixture {file_name}\n----------------')
                return
        self.import_nerd_fixture(file_name)

    def run(self, *args, **options):
        if not os.path.exists(IMPORT_DIRECTORY):
            log.error(f'Missing import directory: "{IMPORT_DIRECTORY}"')
            exit(1)

        self.load_initial_fixtures()

        # Upload files
        if os.path.exists(f'{IMPORT_DIRECTORY}/files'):
            # Prepare storage bucket for development.
            # We skip this in production, where the bucket needs to be created manually.
            uploads_bucket = getattr(settings, 'AWS_S3_BUCKET', None)
            log.info(f'Makes sure the {uploads_bucket} bucket exists')
            storage.create_bucket(uploads_bucket)
            if not options['yes']:
                choice = input('Do you wish to upload/import all files? [Y/n]').lower()
                if choice == 'n' or choice == 'no' or choice == 'nei':
                    print(f'[IGNORE] Ignoring upload of files\n----------------')
                else:
                    self.upload_files(uploads_bucket, f'{IMPORT_DIRECTORY}/files')
            else:
                self.upload_files(uploads_bucket, f'{IMPORT_DIRECTORY}/files')
        # End upload files

        file_names = os.listdir(IMPORT_DIRECTORY)
        file_names.sort()

        print('Found the following files/fixtures to import:')
        for file_name in file_names:
            if not os.path.isfile(f'{IMPORT_DIRECTORY}/{file_name}'):
                continue
            print(f'\t{file_name}')

        if os.path.isfile(f'{IMPORT_DIRECTORY}/1_nerd_export_group_files.yaml'):
            self.handle_fixture_import('1_nerd_export_group_files.yaml', options['yes'])
            file_names.remove('1_nerd_export_group_files.yaml')

        if os.path.isfile(f'{IMPORT_DIRECTORY}/1_nerd_export_group_objects.yaml'):
            # We need to update the group MPTT mapping
            group_tree = initial_tree
            nerd_groups = self.load_yaml(f'{IMPORT_DIRECTORY}/1_nerd_export_group_objects.yaml')
            for group_model in nerd_groups:
                group_fields = group_model['fields']
                if group_fields['logo']:
                    group_fields['logo'] = File.objects.get(key=group_fields['logo'])
                group_name = group_fields['name']
                lego_group_ids[group_model['pk']] = group_name
                group_fields.pop('name', None)
                if group_fields['parent'] is None:
                    group_fields.pop('parent', None)
                    group_tree[group_name] = [group_fields, {}]
                    continue
                parent = lego_group_ids[group_fields['parent']]
                group_fields.pop('parent', None)
                print(f'Attempting to find path for group: {group_name}')
                results = list(self.find_group_path(parent, group_tree))
                path = ' -> '.join(results[0][1] + [group_name])
                print(f'Found group path: {path}')
                if not options['yes']:
                    choice = input('Do you wish to import this group? [Y/n]').lower()
                    if choice == 'n' or choice == 'no' or choice == 'nei':
                        print(f'[IGNORE] Ignoring {group_name}\n----------------')
                        continue
                results[0][0][1][group_name] = [group_fields, {}]
                print(f'[SUCCESS] Added {group_name} to the import tree\n------------------')

            insert_abakus_groups(group_tree)
            AbakusGroup.objects.rebuild()
            file_names.remove('1_nerd_export_group_objects.yaml')
            # End MPTT mapping

        print('Starting import of fixtures')
        for file_name in file_names:
            self.handle_fixture_import(file_name, options['yes'])

        # Make sure user profile pictures are owned by the users
        print('Setting ownership of user profile pictures')
        for user in User.all_objects.exclude(picture__isnull=True):
            if user.picture.token == 'token':
                continue
            user.picture.user = user
            user.picture.save()

        # Loop through all the models and generate slug for them if they do not exist
        for article in Article.all_objects.all():
            article.save()

        for event in Event.all_objects.all():
            event.save()

        for page in Page.all_objects.all():
            page.save()

        for joblisting in Joblisting.all_objects.all():
            joblisting.save()

        for meeting in Meeting.all_objects.all():
            meeting.save()

        for quote in Quote.all_objects.all():
            quote.save()
