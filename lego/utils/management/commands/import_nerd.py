import logging
import os

import yaml
from django.core.management import call_command

from lego.apps.users.fixtures.initial_abakus_groups import initial_tree
from lego.apps.users.models import AbakusGroup
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

    def run(self, *args, **options):
        if not os.path.exists(IMPORT_DIRECTORY):
            log.error(f'Missing import directory: {IMPORT_DIRECTORY}')
            exit(1)

        self.load_initial_fixtures()
        file_names = os.listdir(IMPORT_DIRECTORY)
        file_names.sort()

        print('Found the following files/fixtures to import:')
        for file_name in file_names:
            print(f'\t{file_name}')

        # We need to update the group MPTT mapping
        group_tree = initial_tree
        nerd_groups = self.load_yaml(f'{IMPORT_DIRECTORY}/1_nerd_export_groups.yaml')
        for group_model in nerd_groups:
            group_fields = group_model['fields']
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
                choice = input('Do you wish to import this group? (y/n)').lower()
                if choice == 'n' or choice == 'no' or choice == 'nei':
                    print(f'[IGNORE] Ignoring {group_name}\n----------------')
                    continue
            results[0][0][1][group_name] = [group_fields, {}]
            print(f'[SUCCESS] Added {group_name} to the import tree\n------------------')

        insert_abakus_groups(group_tree)
        AbakusGroup.objects.rebuild()
        file_names.remove('1_nerd_export_groups.yaml')
        # End MPTT mapping

        print('Starting import of fixtures')
        for file_name in file_names:
            self.import_nerd_fixture(file_name)



