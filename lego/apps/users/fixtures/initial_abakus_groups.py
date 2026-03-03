from lego.apps.users.constants import (
    GROUP_BOARD,
    GROUP_COMMITTEE,
    GROUP_GRADE,
    GROUP_ORDAINED,
    GROUP_OTHER,
    GROUP_REVUE,
    GROUP_SUB,
)
from lego.apps.users.models import AbakusGroup
from lego.utils.functions import insert_abakus_groups

#  isort:skip
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
    "Users": [{"description": "Brukere på Abakus.no"}, {}],
    "Abakus": [
        {
            "description": "Medlemmer av Abakus",
            "permissions": [
                "/sudo/admin/meetings/create/",
                "/sudo/admin/meetinginvitations/create/",
                "/sudo/admin/registrations/create/",
                "/sudo/admin/events/payment/",
                "/sudo/admin/comments/create/",
                "/sudo/admin/meetings/list/",
            ],
        },
        {
            "Abakom": [
                {
                    "description": "Medlemmer av Abakom",
                    "permissions": [
                        "/sudo/admin/events/",
                        "/sudo/admin/pools/",
                        "/sudo/admin/registrations/",
                        "/sudo/admin/companies/",
                        "/sudo/admin/joblistings/",
                    ],
                },
                {
                    "Arrkom": [
                        {"type": GROUP_COMMITTEE, "logo_id": "abakus_arrkom.png"},
                        {},
                    ],
                    "backup": [
                        {"type": GROUP_COMMITTEE, "logo_id": "abakus_backup.png"},
                        {},
                    ],
                    "Bankkom": [
                        {"type": GROUP_COMMITTEE, "logo_id": "abakus_bankkom.png"},
                        {},
                    ],
                    "Bedkom": [
                        {
                            "type": GROUP_COMMITTEE,
                            "logo_id": "abakus_bedkom.png",
                            "permissions": [
                                "/sudo/admin/companyinterest/",
                                "/sudo/admin/surveys/",
                                "/sudo/admin/submissions/",
                            ],
                        },
                        {},
                    ],
                    "Fagkom": [
                        {
                            "type": GROUP_COMMITTEE,
                            "logo_id": "abakus_fagkom.png",
                            "permissions": [
                                "/sudo/admin/companyinterest/",
                                "/sudo/admin/surveys/",
                                "/sudo/admin/submissions/",
                            ],
                        },
                        {},
                    ],
                    "Hovedstyret": [
                        {
                            "type": GROUP_BOARD,
                            "logo_id": "abakus_hs.png",
                            "permissions": ["/sudo/admin/"],
                            "contact_email": "hs@abakus.no",
                        },
                        {
                            "Abakus-leder": [{}, {}],
                            "Abakus-nestleder": [{}, {}],
                        },
                    ],
                    "Komiteledere": [
                        {
                            "type": GROUP_OTHER,
                            "permissions": ["/sudo/admin/"],
                        },
                        {},
                    ],
                    "Koskom": [
                        {"type": GROUP_COMMITTEE, "logo_id": "abakus_koskom.png"},
                        {},
                    ],
                    "LaBamba": [
                        {"type": GROUP_COMMITTEE, "logo_id": "abakus_labamba.png"},
                        {},
                    ],
                    "PR": [{"type": GROUP_COMMITTEE, "logo_id": "abakus_pr.png"}, {}],
                    "readme": [
                        {"type": GROUP_COMMITTEE, "logo_id": "abakus_readme.png"},
                        {},
                    ],
                    "Webkom": [
                        {
                            "type": GROUP_COMMITTEE,
                            "logo_id": "abakus_webkom.png",
                            "permissions": ["/sudo/admin/"],
                            "text": "hei",
                        },
                        {},
                    ],
                },
            ],
            "Baksida": [
                {},
                {
                    "Baksida-Komite": [{}, {}],
                    "Baksida-Revy": [{}, {}],
                },
            ],
            "Formaterte": [
                {},
                {},
            ],
            "Interessegrupper": [
                {"description": "Super-gruppe for alle interessegrupper i Abakus"},
                {},
            ],
            "Kasserere": [
                {"description": "Gruppe for alle økonomiansvarlige i Abakus"},
                {},
            ],
            "Klassetillitsvalgt": [
                {"description": "Gruppe for alle klassetillitsvalgte i Abakus"},
                {},
            ],
            "Nestledere": [
                {"description": "Gruppe for alle nestledere i komiteer og revy"},
                {},
            ],
            "Revy": [
                {},
                {
                    "Band": [
                        {"type": GROUP_REVUE},
                        {},
                    ],
                    "Dans": [
                        {"type": GROUP_REVUE},
                        {},
                    ],
                    "Kor": [
                        {"type": GROUP_REVUE},
                        {},
                    ],
                    "Kostyme": [
                        {"type": GROUP_REVUE},
                        {},
                    ],
                    "PR-revy": [
                        {"type": GROUP_REVUE},
                        {},
                    ],
                    "Regi": [
                        {"type": GROUP_REVUE},
                        {},
                    ],
                    "Revystyret": [
                        {"type": GROUP_BOARD},
                        {},
                    ],
                    "Scene": [
                        {"type": GROUP_REVUE},
                        {},
                    ],
                    "Skuespill": [
                        {"type": GROUP_REVUE},
                        {},
                    ],
                    "Sosial": [
                        {"type": GROUP_REVUE},
                        {},
                    ],
                    "Teknikk": [
                        {"type": GROUP_REVUE},
                        {},
                    ],
                },
            ],
            "Undergrupper": [
                {},
                {
                    "1. Klasse Taskforce": [
                        {"type": GROUP_SUB},
                        {},
                    ],
                    "Ababand": [
                        {"type": GROUP_SUB},
                        {},
                    ],
                    "Abax": [
                        {"type": GROUP_SUB},
                        {},
                    ],
                    "AbelLAN": [
                        {"type": GROUP_SUB},
                        {},
                    ],
                    "AVF": [
                        {"type": GROUP_SUB},
                        {},
                    ],
                    "DatakamerateneFKG": [
                        {"type": GROUP_SUB},
                        {},
                    ],
                    "DatakamerateneFKJ": [
                        {"type": GROUP_SUB},
                        {},
                    ],
                    "Koseprogg": [
                        {"type": GROUP_SUB},
                        {},
                    ],
                },
            ],
        },
    ],
    "Fondsstyret": [
        {"type": GROUP_BOARD},
        {},
    ],
    "Ordenen": [
        {},
        {
            "Abakusorden": [{}, {}],
            "Kantzelliet": [{"type": GROUP_ORDAINED}, {}],
            "Ordensmedlemmer": [{"type": GROUP_ORDAINED}, {}],
            "Ordenspromosjon": [{}, {}],
        },
    ],
    "Students": [
        {},
        {
            "Datateknologi": [
                {},
                {
                    "1. klasse Datateknologi": [{"type": GROUP_GRADE}, {}],
                    "2. klasse Datateknologi": [{"type": GROUP_GRADE}, {}],
                    "3. klasse Datateknologi": [{"type": GROUP_GRADE}, {}],
                    "4. klasse Datateknologi": [{"type": GROUP_GRADE}, {}],
                    "5. klasse Datateknologi": [{"type": GROUP_GRADE}, {}],
                },
            ],
            "Kommunikasjonsteknologi": [
                {},
                {
                    "1. klasse Kommunikasjonsteknologi": [{"type": GROUP_GRADE}, {}],
                    "2. klasse Kommunikasjonsteknologi": [{"type": GROUP_GRADE}, {}],
                    "3. klasse Kommunikasjonsteknologi": [{"type": GROUP_GRADE}, {}],
                    "4. klasse Kommunikasjonsteknologi": [{"type": GROUP_GRADE}, {}],
                    "5. klasse Kommunikasjonsteknologi": [{"type": GROUP_GRADE}, {}],
                },
            ],
        },
    ],
}


def load_abakus_groups():
    insert_abakus_groups(initial_tree)
    AbakusGroup.objects.rebuild()
