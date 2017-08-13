import crypt


def create_password_hash(password):
    """
    OpenLDAP only supports simple hashing schemes like MD5 or SHA1
    We use the OS's crypto handler instead, glibc when running on linux.
    This method returns the password as the MCF hash format with strongest available method.
    This should be secure enough compared to the default SHA1 hash.
    REMEMBER: always run LDAP over TLS.
    """
    crypt_method = crypt.methods[0]
    return crypt.crypt(password, crypt_method)
