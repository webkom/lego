from lego.apps.users.constants import GROUP_COMMITTEE, GROUP_GRADE, GROUP_INTEREST
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
                {
                    'AbaBrygg': [{
                        'permissions': [],
                        'description': 'Interessegruppe for AbaBrygg',
                        'text': 'Hender det seg at du tar en pils? Er lommeboken ofte tom, '
                                'kanskje på grunn av pils?\nVisste du at ved å brygge øl selv '
                                'kan man enkelt produsere øl til 3-4 kroner flaska?\nIkke bare '
                                'er det koselig, besparende, og luktfritt (!) å brygge eget øl, '
                                'men imotsetningtil vinbrygging trenger man ikke være supermann '
                                'for at sluttresultatet smaker godt.\n\nabaBrygg er en liten '
                                'gruppe som passer deg som har en lidenskap for øl, harlyst til '
                                'å prøve noe nytt, eller bare trenger litt starthjelp med '
                                'brygginga.\n',
                        'type': GROUP_INTEREST
                    }, {}],
                    'abaGolf': [{
                        'permissions': [],
                        'description': 'Interessegruppe for abaGolf',
                        'text': 'Hei, er du en person som liker å klaske baller på grønne '
                                'baner?Da er Abakus golf gruppa for deg.\nVi tenker at dette vil '
                                'være en portal for oss som ønsker åkomme oss ut på banene med '
                                'noen hyggelige folk fra Abakus.\nDet vil også bli blestet om '
                                'eventuelleturnerninger som måtte dukke opp.\nSamt vil det være '
                                'treningsmuligheter gjennom hele vintereni samarbeid med NTNUI '
                                'Golf.\n',
                        'type': GROUP_INTEREST
                    }, {}],
                    'Turgruppa': [{
                        'permissions': [],
                        'description': 'Interessegruppe for Turgruppa',
                        'text': 'Abakus sin turgruppe er for alle som elsker, liker eller har '
                                'sett norsk natur. Denne turgruppenvil arrangere ulike turer i '
                                'fjell skog og mark. Om vinteren vil det være mulighet for '
                                'toppturereller å gå mellom hytter på vidda. Høst og vår, vil '
                                'turene gå i fjell og langs elv og vann.Det vil alltid være '
                                'flott stemning og minneverdige turopplevelser som er målet.\n\n '
                                'Om du harforslag til tur eller lurer på om dette er noe du kan '
                                'være med på, ikke nøl med å ta kontakt.',
                        'type': GROUP_INTEREST
                    }, {}]
            }]
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
