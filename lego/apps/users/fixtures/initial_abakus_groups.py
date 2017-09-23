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
                        'group_text': 'Hei hallo hva skjer? \n\n Vi progger LEGO xd'
                    }, {}],
                    'Hovedstyret': [{
                        'logo_id': 'abakus_hs.png',
                        'permissions': ['/sudo/admin/'],
                    }, {}]
                }
            ],
            'Interessegrupper': [
                {
                    'AbaBrygg': [{
                        'permissions': [],
                        'is_interest_group': True,
                        'description': 'Interessegruppe for AbaBrygg',
                        'description_long': """
Hender det seg at du tar en pils? Er lommeboken ofte tom, kanskje på grunn av pils?\n
Visste du at ved å brygge øl selv kan man enkelt produsere øl til 3-4 kroner flaska?\n
Ikke bare er det koselig, besparende, og luktfritt (!) å brygge eget øl, men imotsetning
til vinbrygging trenger man ikke være supermann for at sluttresultatet smaker godt.\n\n
abaBrygg er en liten gruppe som passer deg som har en lidenskap for øl, har
lyst til å prøve noe nytt, eller bare trenger litt starthjelp med brygginga.\n
"""
                    }, {}],
                    'abaGolf': [{
                        'permissions': [],
                        'is_interest_group': True,
                        'description': 'Interessegruppe for abaGolf',
                        'description_long': """
Hei, er du en person som liker å klaske baller på grønne baner?
Da er Abakus golf gruppa for deg.\nVi tenker at dette vil være en portal for oss som ønsker å
komme oss ut på banene med noen hyggelige folk fra Abakus.\nDet vil også bli blestet om eventuelle
turnerninger som måtte dukke opp.\nSamt vil det være treningsmuligheter gjennom hele vinteren
i samarbeid med NTNUI Golf.\n
"""
                    }, {}],
                    'Turgruppa': [{
                        'permissions': [],
                        'is_interest_group': True,
                        'description': 'Interessegruppe for Turgruppa',
                        'description_long': """
Abakus sin turgruppe er for alle som elsker, liker eller har sett norsk natur. Denne turgruppen
vil arrangere ulike turer i fjell skog og mark. Om vinteren vil det være mulighet for toppturer
eller å gå mellom hytter på vidda. Høst og vår, vil turene gå i fjell og langs elv og vann.
Det vil alltid være flott stemning og minneverdige turopplevelser som er målet.\n\n Om du har
forslag til tur eller lurer på om dette er noe du kan være med på, ikke nøl med å ta kontakt.
"""
                    }, {}]
                }
                , {}]
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
