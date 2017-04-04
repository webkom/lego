from lego.apps.users.models import AbakusGroup

"""
The structure of the tree is key and a list of two dicts.
The first dict is the parameters of the current group
and the second dict are the children of the current group.

E.g. Abakus: [
    {
        description: 'ABAKUSGRUPPE',
        permissions: ['/sudo/...']
        ...
    },
    {
        'Webkom': [{
            description: 'WEBKOMGRUPPE',
            permissions: ['/sudo/']
            ...
        }, {}]
    }
]
"""

initial_tree = {
    'Users': [{
        'description': 'Brukere på Abakus.no'
    }, {}],
    'Abakus': [{
        'description': 'Medlemmer av Abakus',
        'permissions': [
            '/sudo/admin/meetings/create',
            '/sudo/admin/meetinginvitations/create',
            '/sudo/admin/registrations/create/',
            '/sudo/admin/events/payment/'
        ]},
        {
            'Abakom': [{
                'description': 'Medlemmer av Abakom',
                'permissions': [
                    '/sudo/admin/events/',
                    '/sudo/admin/pools/',
                    '/sudo/admin/registrations/',
                    '/sudo/admin/companies/'
                ]},
                {
                    'Arrkom': [{}, {}],
                    'backup': [{}, {}],
                    'Bedkom': [{}, {}],
                    'Fagkom': [{}, {}],
                    'LaBamba': [{}, {}],
                    'PR': [{}, {}],
                    'readme': [{}, {}],
                    'Webkom': [{
                        'permissions': ['/sudo/']
                    }, {}],
                    'Hovedstyret': [{
                        'permissions': ['/sudo/admin/']
                    }, {}]
                }
            ],
            'Interessegrupper': [{}, {}]
        }
    ],
    'Students': [{}, {
        'Datateknologi': [{}, {
            '1. klasse Datateknologi': [{}, {}],
            '2. klasse Datateknologi': [{}, {}],
            '3. klasse Datateknologi': [{}, {}],
            '4. klasse Datateknologi': [{}, {}],
            '5. klasse Datateknologi': [{}, {}],
        }],
        'Kommunikasjonsteknologi': [{}, {
            '1. klasse Kommunikasjonsteknologi': [{}, {}],
            '2. klasse Kommunikasjonsteknologi': [{}, {}],
            '3. klasse Kommunikasjonsteknologi': [{}, {}],
            '4. klasse Kommunikasjonsteknologi': [{}, {}],
            '5. klasse Kommunikasjonsteknologi': [{}, {}],
        }]
    }]
}


def load_abakus_groups():
    insert_groups(initial_tree)
    AbakusGroup.objects.rebuild()


def insert_groups(tree, parent=None):
    for key, value in tree.items():
        kwargs = value[0]
        node = AbakusGroup.objects.update_or_create(
            name=key, defaults={**kwargs, 'parent': parent}
        )[0]
        insert_groups(value[1], node)
