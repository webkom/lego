Authentication
==============

JSON Web Tokens
---------------

To authenticate using JWT, post to ``/api/token-auth/`` with a username and password.
This will return a token, which can later be used with the following header:
``Authorization: JWT <insert token here>``.

To refresh a token, post to ``/api/token-auth/refresh`` with the token in the body.
Both these endpoints can be used with JSON and regular forms.
