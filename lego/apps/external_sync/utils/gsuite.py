from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials

scopes = [
    'https://www.googleapis.com/auth/admin.directory.user',
    'https://www.googleapis.com/auth/admin.directory.group'
]


class GSuiteLib:
    """
    Wrapper around the Google Directory API

    user_key: Unique user email (eirsyl@abakus.no)
    """
    def __init__(self):
        credentials = self.get_credentials()
        self.client = build(
            'admin', 'directory_v1', http=credentials.authorize(Http()), cache_discovery=False
        )

    def get_credentials(self):
        """
        Build GSuite credentials
        """
        if settings.GSUITE_CREDENTIALS is None:
            raise ImproperlyConfigured('Missing GSuite credentials')

        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            settings.GSUITE_CREDENTIALS, scopes
        )
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

    def add_user(self, user_id, user_key, first_name, last_name, email, password_hash):
        return self.client.users().insert(body={
            'name': {
                'givenName': first_name,
                'familyName': last_name
            },
            'password': password_hash,
            'hashFunction': 'crypt',
            'changePasswordAtNextLogin': False,
            'primaryEmail': user_key,
            'externalIds': [
                {'type': 'account', 'value': str(user_id)}
            ],
            'emails': [
                {'address': email, 'type': 'other'}
            ]
        }).execute()

    def update_user(self, user_id, user_key, first_name, last_name, email, password_hash):
        return self.client.users().update(userKey=user_key, body={
            'suspended': False,
            'name': {
                'givenName': first_name,
                'familyName': last_name
            },
            'password': password_hash,
            'hashFunction': 'crypt',
            'externalIds': [
                {'type': 'account', 'value': str(user_id)}
            ],
            'emails': [
                {'address': email, 'type': 'other'}
            ]
        }).execute()

    def delete_user(self, user_key):
        """
        The delete method is actually just to suspend the user.
        """
        if user_key not in settings.GSUITE_EXTERNAL_USERS:
            return self.client.users().update(userKey=user_key, body={'suspended': True}).execute()

    def get_all_users(self):
        """
        Retrieve all users on Google GSuite.
        """
        users = []
        api = self.client.users()
        request = api.list(domain='abakus.no', query='isSuspended=false')

        while request is not None:
            users_response = request.execute()

            remote_users = users_response.get('users', [])
            users = users + remote_users

            request = api.list_next(request, users_response)

        return users

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

    def add_group(self, name, group_key):
        return self.client.groups().insert(body={
            'name': name,
            'email': group_key
        }).execute()

    def update_group(self, group_key, name):
        return self.client.groups().update(groupKey=group_key, body={
            'name': name
        }).execute()

    def get_members(self, group_key):
        members = []
        try:
            api = self.client.members()
            request = api.list(groupKey=group_key)

            while request is not None:
                members_response = request.execute()

                remote_members = members_response.get('members', [])
                members = members + remote_members

                request = api.list_next(request, members_response)

            return members
        except HttpError as e:
            if e.resp.status == 404:
                return members
            raise

    def set_memberships(self, group_key, member_keys):
        remote_members = [member['email'] for member in self.get_members(group_key)]

        for member in member_keys:
            if member not in remote_members:
                self.add_membership(
                    group_key=group_key,
                    user_key=member
                )

        for excess_member in set(remote_members) - set(member_keys):
            self.delete_membership(group_key, excess_member)

    def add_membership(self, group_key, user_key, role='MEMBER'):
        """
        The API returns 404 when we try to add an unknown gmail account.
        """
        try:
            return self.client.members().insert(groupKey=group_key, body={
                'role': role,
                'email': user_key
            }).execute()
        except HttpError as e:
            if e.resp.status == 404:
                return
            elif e.resp.status == 409:
                # Member already exists.
                return
            raise

    def delete_membership(self, group_key, user_key):
        return self.client.members().delete(groupKey=group_key, memberKey=user_key).execute()
