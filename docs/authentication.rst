Authentication
==============

Lego uses CORS to deny requests from other domains than the once we control. OAuth2 authorization
is required if you want to create an app that consumes information from the Lego API.

JSON Web Tokens
---------------

To authenticate using JWT, post to ``/api/token-auth/`` with a username and password.
This will return a token, which can later be used with the following header:
``Authorization: JWT <insert token here>``.

To refresh a token, post to ``/api/token-auth/refresh`` with the token in the body.
Both these endpoints can be used with JSON and regular forms.

The webapp uses this authentication flow, third party apps should use OAuth2.

OAuth2
------

Lego has support for OAuth2 authentication using the ``authorization-code`` method. Everyone with
a valid user and the right permissions is able to create an OAuth2 application. This works in the
same way as ``Login with GitHub`` or any other OAuth2 system.

You should newer expose the ``client_secret`` to the public. Never implement the OAuth2
authorization flow in a browser.

The snippet bellow can be used together with ``python-social-auth`` to authenticate with Lego as
the user directory.

::

    from six.moves.urllib.parse import urljoin

    from social_core.backends.oauth import BaseOAuth2


    class LegoOAuth2(BaseOAuth2):

        name = 'lego'
        ACCESS_TOKEN_METHOD = 'POST'
        SCOPE_SEPARATOR = ','
        EXTRA_DATA = [
            ('id', 'id'),
            ('expires_in', 'expires_in'),
        ]

        def api_url(self):
            api_url = self.setting('API_URL')
            if not api_url:
                raise ValueError('Please set the LEGO_API_URL setting.')
            return api_url

        def authorization_url(self):
            return urljoin(self.api_url(), '/authorization/oauth2/authorize/')

        def access_token_url(self):
            return urljoin(self.api_url(), '/authorization/oauth2/token/')

        def get_user_details(self, response):
            """Return user details from Lego account"""
            fullname, first_name, last_name = self.get_user_names(
                response.get('fullName'),
                response.get('firstName'),
                response.get('lastName')
            )
            return {'username': response.get('username'),
                    'email': response.get('email') or '',
                    'fullname': fullname,
                    'first_name': first_name,
                    'last_name': last_name}

        def user_data(self, access_token, *args, **kwargs):
            return self._user_data(access_token)

        def _user_data(self, access_token):
            url = urljoin(self.api_url(), 'api/v1/users/me/')
            return self.get_json(url, headers={'AUTHORIZATION': 'Bearer %s' % access_token})

