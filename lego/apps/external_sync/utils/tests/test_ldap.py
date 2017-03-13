from django.test import TestCase
from passlib.hash import sha512_crypt

from lego.apps.external_sync.utils.ldap import LDAPLib, create_ldap_password_hash


class LDAPUtilsTestCase(TestCase):

    def test_create_ldap_password_hash(self):
        """Create a password hash and verify it"""
        password = 'random_password'
        hash = create_ldap_password_hash(password)
        to_verify = hash[7:]

        self.assertTrue(sha512_crypt.verify(password, to_verify))


class LDAPLibTestCase(TestCase):

    def setUp(self):
        self.ldap = LDAPLib()

    def test_kek(self):
        print('hello')
