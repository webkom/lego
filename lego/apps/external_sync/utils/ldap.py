from django.conf import settings
from ldap3 import MODIFY_DELETE, MODIFY_REPLACE, Connection
from passlib.hash import sha512_crypt


def create_ldap_password_hash(password):
    """
    OpenLDAP only supports simple hashing schemes like MD5 or SHA1
    We use the OS's crypto handler instead, glibc when running on linux.
    glibc supports the MCF hash format. sha512_crypt creates a SHA512 hash on the MCF format.
    We use SHA512 with a secure random salt and 656000 rounds by default.
    This should be secure enough compared to the default SHA1 hash.
    REMEMBER: always run LDAP over TLS.
    """
    return '{CRYPT}' + sha512_crypt.hash(password)


class LDAPLib:

    def __init__(self):
        self.connection = Connection(
            server=settings.LDAP_SERVER,
            user=settings.LDAP_USER,
            password=settings.LDAP_PASSWORD,
            auto_bind=True
        )

        self.user_base = ','.join(('ou=users', settings.LDAP_BASE_DN))
        self.group_base = ','.join(('ou=groups', settings.LDAP_BASE_DN))

        self.user_attributes = ['uid', 'cn', 'sn']
        self.group_attributes = ['gidNumber', 'cn']

    def get_all_users(self):
        search_filter = '(cn=*)'
        result = self.connection.search(
            self.user_base, search_filter, attributes=self.user_attributes
        )
        if result:
            return self.connection.entries
        return []

    def get_all_groups(self):
        search_filter = '(cn=*)'
        result = self.connection.search(
            self.group_base, search_filter, attributes=self.group_attributes
        )
        if result:
            return self.connection.entries
        return []

    def search_user(self, query):
        search_filter = f'(uid={query})'
        result = self.connection.search(
            self.user_base, search_filter, attributes=self.user_attributes
        )
        if result:
            return self.connection.entries[0]

    def add_user(self, uid, first_name, last_name, email, password_hash):
        dn = ','.join((f'uid={uid}', self.user_base))
        return self.connection.add(dn, ['inetOrgPerson', 'top'], {
            'uid': uid,
            'cn': first_name,
            'sn': last_name,
            'mail': email,
            'userPassword': password_hash
        })

    def search_group(self, query):
        search_filter = f'(gidNumber={query})'
        result = self.connection.search(
            self.group_base, search_filter, attributes=self.group_attributes
        )
        if result:
            return self.connection.entries[0]

    def add_group(self, gid, name):
        dn = ','.join((f'cn={name}', self.group_base))
        return self.connection.add(dn, ['posixGroup', 'top'], {
            'gidNumber': gid,
            'cn': name,
        })

    def update_organization_unit(self, name):
        """
        Make sure the organization unit exists in LDAP.
        """
        search_filter = f'(ou={name})'
        result = self.connection.search(
            settings.LDAP_BASE_DN, search_filter, attributes=['ou']
        )
        if not result:
            dn = ','.join((f'ou={name}', settings.LDAP_BASE_DN))
            self.connection.add(
                dn, ['organizationalUnit', 'top'], {'ou': name}
            )

    def delete_user(self, uid):
        dn = ','.join((f'uid={uid}', self.user_base))
        return self.connection.delete(dn)

    def delete_group(self, cn):
        dn = ','.join((f'cn={cn}', self.group_base))
        return self.connection.delete(dn)

    def check_password(self, uid, password_hash):
        dn = ','.join((f'uid={uid}', self.user_base))
        return self.connection.compare(dn, 'userPassword', password_hash)

    def change_password(self, uid, password_hash):
        dn = ','.join((f'uid={uid}', self.user_base))

        changes = {
            'userPassword': [(MODIFY_REPLACE, [password_hash])]
        }
        self.connection.modify(dn, changes)

    def update_group_members(self, cn, members):
        dn = ','.join((f'cn={cn}', self.group_base))

        if members:
            changes = {
                'memberUid': [(MODIFY_REPLACE, members)]
            }
        else:
            changes = {
                'memberUid': [(MODIFY_DELETE, [])]
            }

        self.connection.modify(dn, changes)
