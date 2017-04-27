import base64
import json

from django.conf import settings
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http

scopes = [
    'https://www.googleapis.com/auth/admin.directory.user',
    'https://www.googleapis.com/auth/admin.directory.group'
]


class GSuiteLib:
    def __init__(self):
        credentials = self.get_credentials()
        self.client = build('admin', 'directory_v1', http=credentials.authorize(Http()),
                            cache_discovery=False)

    def get_credentials(self):
        if settings.GSUITE_CREDENTIALS is None:
            raise Exception('Missing google credentials')
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(settings.GSUITE_CREDENTIALS, scopes)
        return credentials.create_delegated(settings.GSUITE_DELEGATED_ACCOUNT)

    def get_user(self, user_key):
        return self.client.users().get(userKey=user_key).execute()

    def user_exists(self, user_key):
        try:
            self.get_user(user_key)
            return True
        except HttpError as e:
            if e.resp.status == 404:
                return False
            raise

    def create_user(self, user_object):
        return self.client.users().insert(body=user_object).execute()

    def update_user(self, user_key, user_object):
        return self.client.users().update(userKey=user_key, body=user_object).execute()

    def delete_user(self, user_key):
        return self.client.users().delete(userKey=user_key).execute()

    def get_group(self, group_key):
        return self.client.groups().get(groupKey=group_key).execute()

    def group_exists(self, group_key):
        try:
            self.get_group(group_key)
            return True
        except HttpError as e:
            if e.resp.status == 404:
                return False
            raise

    def create_group(self, group_object):
        return self.client.groups().insert(body=group_object).execute()

    def update_group(self, group_key, group_object):
        return self.client.groups().insert(groupKey=group_key, body=group_object).execute()

    def delete_group(self, group_key):
        return self.client.groups().delete(groupKey=group_key).execute()

    def get_members(self, group_key):
        members = self.client.members().list(groupKey=group_key).execute()
        if 'members' in members:
            return members['members']
        return []

    def set_memberships(self, group_key, member_keys):
        gsuite_member_keys = [member['email'] for member in self.get_members(group_key)]
        for member_key in member_keys:
            if member_key not in gsuite_member_keys:
                self.add_membership(
                    group_key=group_key,
                    user_key=member_key
                )

        for user_key in set(gsuite_member_keys) - set(member_keys):
            self.delete_membership(group_key, user_key)

    def add_membership(self, group_key, user_key, role="MEMBER"):
        return self.client.members().insert(groupKey=group_key, body=dict(
            role=role,
            email=user_key
        )).execute()

    def update_membership(self, group_key, user_key, role="MEMBER"):
        return self.client.members().update(groupKey=group_key, memberKey=user_key, body=dict(
            role=role
        )).execute()

    def delete_membership(self, group_key, user_key):
        return self.client.members().delete(groupKey=group_key, memberKey=user_key).execute()

