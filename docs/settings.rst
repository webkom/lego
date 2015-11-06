Settings
========


Lego settings
-------------
Lego has a few settings. The defaults is placed in lego/settings/lego.py.

- API_VERSION: Current api version used by default.
- LOGIN_REDIRECT_URL: The redirect after a login. This is by default the api root.

Production settings
-------------------
Production settings is provided by our configuration tool - Puppet. Puppet creates a json-file
called .configuration.json in the project root. The file lego/settings/production.py uses this
file when configuring the production environment. To add more production settings:

1. Update the configuration in puppet - hieradata/common.yaml
2. Run puppet agent -t
3. Create the setting in lego/settings/production.py :code:`production_values.get('NEW_SETTING', 'default_value')`
4. Restart lego
