from lego.apps.users.models import AbakusGroup
from lego.utils.functions import insert_abakus_groups

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
                    '/sudo/admin/companies/',
                    '/sudo/admin/joblistings/',
                ]},
                {
                    'Arrkom': [{'is_committee': True, 'logo_id': 'abakus_arrkom.png'}, {}],
                    'backup': [{'is_committee': True, 'logo_id': 'abakus_backup.png'}, {}],
                    'Bedkom': [{'is_committee': True, 'logo_id': 'abakus_bedkom.png'}, {}],
                    'Fagkom': [{'is_committee': True, 'logo_id': 'abakus_fagkom.png'}, {}],
                    'Koskom': [{'is_committee': True, 'logo_id': 'abakus_koskom.png'}, {}],
                    'LaBamba': [{'is_committee': True, 'logo_id': 'abakus_labamba.png'}, {}],
                    'PR': [{'is_committee': True, 'logo_id': 'abakus_pr.png'}, {}],
                    'readme': [{'is_committee': True, 'logo_id': 'abakus_readme.png'}, {}],
                    'Webkom': [{
                        'is_committee': True,
                        'logo_id': 'abakus_webkom.png',
                        'permissions': ['/sudo/'],
                    }, {}],
                    'Hovedstyret': [{
                        'logo_id': 'abakus_hs.png',
                        'permissions': ['/sudo/admin/'],
                    }, {}]
                }
            ],
            'Interessegrupper': [{}, {}]
        }
    ],
    'Students': [{}, {
        'Datateknologi': [{}, {
            '1. klasse Datateknologi': [{'is_grade': True}, {}],
            '2. klasse Datateknologi': [{'is_grade': True}, {}],
            '3. klasse Datateknologi': [{'is_grade': True}, {}],
            '4. klasse Datateknologi': [{'is_grade': True}, {}],
            '5. klasse Datateknologi': [{'is_grade': True}, {}],
        }],
        'Kommunikasjonsteknologi': [{}, {
            '1. klasse Kommunikasjonsteknologi': [{'is_grade': True}, {}],
            '2. klasse Kommunikasjonsteknologi': [{'is_grade': True}, {}],
            '3. klasse Kommunikasjonsteknologi': [{'is_grade': True}, {}],
            '4. klasse Kommunikasjonsteknologi': [{'is_grade': True}, {}],
            '5. klasse Kommunikasjonsteknologi': [{'is_grade': True}, {}],
        }]
    }]
}


def load_abakus_groups():
    insert_abakus_groups(initial_tree)
    AbakusGroup.objects.rebuild()
