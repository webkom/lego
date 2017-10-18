from lego.apps.users.constants import GROUP_COMMITTEE, GROUP_GRADE
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
            '/sudo/admin/events/payment/',
            '/sudo/admin/comments/create'
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
                    'Arrkom': [{'type': GROUP_COMMITTEE, 'logo_id': 'abakus_arrkom.png'}, {}],
                    'backup': [{'type': GROUP_COMMITTEE, 'logo_id': 'abakus_backup.png'}, {}],
                    'Bedkom': [{
                        'type': GROUP_COMMITTEE,
                        'logo_id': 'abakus_bedkom.png',
                        'permissions': ['/sudo/admin/companyinterest']
                    }, {}],
                    'Fagkom': [{
                        'type': GROUP_COMMITTEE,
                        'logo_id': 'abakus_fagkom.png',
                        'permissions': ['/sudo/admin/companyinterest']
                    }, {}],
                    'Koskom': [{'type': GROUP_COMMITTEE, 'logo_id': 'abakus_koskom.png'}, {}],
                    'LaBamba': [{'type': GROUP_COMMITTEE, 'logo_id': 'abakus_labamba.png'}, {}],
                    'PR': [{'type': GROUP_COMMITTEE, 'logo_id': 'abakus_pr.png'}, {}],
                    'readme': [{'type': GROUP_COMMITTEE, 'logo_id': 'abakus_readme.png'}, {}],
                    'Webkom': [{
                        'type': GROUP_COMMITTEE,
                        'logo_id': 'abakus_webkom.png',
                        'permissions': ['/sudo/'],
                        'text': 'hei'
                    }, {}],
                    'Hovedstyret': [{
                        'logo_id': 'abakus_hs.png',
                        'permissions': ['/sudo/admin/'],
                    }, {}]
                }
            ],
            'Interessegrupper': [{
                'description': 'Super-gruppe for alle interessegrupper i Abakus'
                },
                {}]
        }
    ],
    'Students': [{}, {
        'Datateknologi': [{}, {
            '1. klasse Datateknologi': [{'type': GROUP_GRADE}, {}],
            '2. klasse Datateknologi': [{'type': GROUP_GRADE}, {}],
            '3. klasse Datateknologi': [{'type': GROUP_GRADE}, {}],
            '4. klasse Datateknologi': [{'type': GROUP_GRADE}, {}],
            '5. klasse Datateknologi': [{'type': GROUP_GRADE}, {}],
        }],
        'Kommunikasjonsteknologi': [{}, {
            '1. klasse Kommunikasjonsteknologi': [{'type': GROUP_GRADE}, {}],
            '2. klasse Kommunikasjonsteknologi': [{'type': GROUP_GRADE}, {}],
            '3. klasse Kommunikasjonsteknologi': [{'type': GROUP_GRADE}, {}],
            '4. klasse Kommunikasjonsteknologi': [{'type': GROUP_GRADE}, {}],
            '5. klasse Kommunikasjonsteknologi': [{'type': GROUP_GRADE}, {}],
        }]
    }]
}


def load_abakus_groups():
    insert_abakus_groups(initial_tree)
    AbakusGroup.objects.rebuild()
