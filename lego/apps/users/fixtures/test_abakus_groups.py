from lego.apps.users.constants import GROUP_COMMITTEE, GROUP_INTEREST
from lego.apps.users.models import AbakusGroup
from lego.utils.functions import insert_abakus_groups

test_tree = {
    "UserAdminTest": [
        {
            "permissions": [
                "/sudo/admin/users/list/",
                "/sudo/admin/users/view/",
                "/sudo/admin/users/create/",
                "/sudo/admin/users/edit/",
                "/sudo/admin/users/delete/",
            ]
        },
        {},
    ],
    "AbakusGroupAdminTest": [
        {
            "permissions": [
                "/sudo/admin/groups/list/",
                "/sudo/admin/groups/view/",
                "/sudo/admin/groups/create/",
                "/sudo/admin/groups/edit/",
                "/sudo/admin/groups/delete/",
            ]
        },
        {},
    ],
    "TestGroup": [{}, {}],
    "EventAdminTest": [
        {
            "permissions": [
                "/sudo/admin/events/list/",
                "/sudo/admin/events/view/",
                "/sudo/admin/events/create/",
                "/sudo/admin/events/edit/",
                "/sudo/admin/events/delete/",
            ]
        },
        {},
    ],
    "CommentTest": [
        {
            "permissions": [
                "/sudo/admin/comments/list/",
                "/sudo/admin/comments/view/",
                "/sudo/admin/comments/create/",
                "/sudo/admin/comments/edit/",
                "/sudo/admin/comments/delete/",
            ]
        },
        {},
    ],
    "APIApplicationTest": [
        {
            "permissions": [
                "/sudo/admin/apiapplications/list/",
                "/sudo/admin/apiapplications/create/",
            ]
        },
        {},
    ],
    "QuoteAdminTest": [
        {
            "permissions": [
                "/sudo/admin/quotes/like/",
                "/sudo/admin/quotes/change-approval/",
                "/sudo/admin/quotes/list-unapproved/",
                "/sudo/admin/quotes/list/",
                "/sudo/admin/quotes/view/",
                "/sudo/admin/quotes/create/",
                "/sudo/admin/quotes/edit/",
                "/sudo/admin/quotes/delete/",
            ]
        },
        {},
    ],
    "PodcastAdminTest": [{"permissions": ["/sudo/admin/podcasts/"]}, {}],
    "PollAdminTest": [{"permissions": ["/sudo/admin/polls/"]}, {}],
    "ReactionTest": [{"permissions": ["/sudo/admin/reactions/create/"]}, {}],
    "ReactionAdminTest": [{"permissions": ["/sudo/admin/reactions/"]}, {}],
    "InterestGroupAdminTest": [
        {
            "permissions": [
                "/sudo/admin/interestgroups/list/",
                "/sudo/admin/interestgroups/view/",
                "/sudo/admin/interestgroups/create/",
                "/sudo/admin/interestgroups/edit/",
                "/sudo/admin/interestgroups/delete/",
            ]
        },
        {},
    ],
    "Interessegrupper": [{}, {"TestInterestGroup": [{}, {}]}],
    "GalleryAdminTest": [{"permissions": ["/sudo/admin/gallerys/"]}, {}],
    "GalleryTest": [
        {"permissions": ["/sudo/admin/gallerys/list/", "/sudo/admin/gallerys/view/"]},
        {},
    ],
    "EmailAdminTest": [
        {
            "permissions": [
                "/sudo/admin/emailusers/",
                "/sudo/admin/emailgroups/",
                "/sudo/admin/emaillists/",
            ]
        },
        {},
    ],
    "Users": [{"description": "Brukere på Abakus.no"}, {}],
    "Abakus": [
        {
            "description": "Medlemmer av Abakus",
            "permissions": [
                "/sudo/admin/meetings/create",
                "/sudo/admin/meetinginvitations/create",
                "/sudo/admin/registrations/create/",
                "/sudo/admin/events/payment/",
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
                    "Bedkom": [
                        {
                            "type": GROUP_COMMITTEE,
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
                            "permissions": [
                                "/sudo/admin/companyinterest/",
                                "/sudo/admin/surveys/",
                                "/sudo/admin/submissions/",
                            ],
                        },
                        {},
                    ],
                    "Webkom": [
                        {"type": GROUP_COMMITTEE, "permissions": ["/sudo/"]},
                        {},
                    ],
                },
            ],
            "Interessegrupper": [
                {},
                {
                    "AbaBrygg": [
                        {
                            "permissions": [],
                            "description": "Interessegruppe for AbaBrygg",
                            "text": "Hender det seg at du tar en pils? Er lommeboken ofte tom, "
                            "kanskje på grunn av pils?\nVisste du at ved å brygge øl selv "
                            "kan man enkelt produsere øl til 3-4 kroner flaska?\nIkke bare "
                            "er det koselig, besparende, og luktfritt (!) å brygge eget øl, "
                            "men imotsetningtil vinbrygging trenger man ikke være supermann "
                            "for at sluttresultatet smaker godt.\n\nabaBrygg er en liten "
                            "gruppe som passer deg som har en lidenskap for øl, harlyst til "
                            "å prøve noe nytt, eller bare trenger litt starthjelp med "
                            "brygginga.\n",
                            "type": GROUP_INTEREST,
                        },
                        {},
                    ],
                    "abaGolf": [
                        {
                            "permissions": [],
                            "description": "Interessegruppe for abaGolf",
                            "text": "Hei, er du en person som liker å klaske baller på grønne "
                            "baner?Da er Abakus golf gruppa for deg.\nVi tenker at dette vil "
                            "være en portal for oss som ønsker åkomme oss ut på banene med "
                            "noen hyggelige folk fra Abakus.\nDet vil også bli blestet om "
                            "eventuelleturnerninger som måtte dukke opp.\nSamt vil det være "
                            "treningsmuligheter gjennom hele vintereni samarbeid med NTNUI "
                            "Golf.\n",
                            "type": GROUP_INTEREST,
                        },
                        {},
                    ],
                    "Turgruppa": [
                        {
                            "permissions": [],
                            "description": "Interessegruppe for Turgruppa",
                            "text": "Abakus sin turgruppe er for alle som elsker, liker eller har "
                            "sett norsk natur. Denne turgruppenvil arrangere ulike turer i "
                            "fjell skog og mark. Om vinteren vil det være mulighet for "
                            "toppturereller å gå mellom hytter på vidda. Høst og vår, vil "
                            "turene gå i fjell og langs elv og vann.Det vil alltid være "
                            "flott stemning og minneverdige turopplevelser som er målet.\n\n "
                            "Om du harforslag til tur eller lurer på om dette er noe du kan "
                            "være med på, ikke nøl med å ta kontakt.",
                            "type": GROUP_INTEREST,
                        },
                        {},
                    ],
                },
            ],
        },
    ],
    "Students": [{}, {}],
}


def load_test_abakus_groups():
    insert_abakus_groups(test_tree)
    AbakusGroup.objects.rebuild()
