from lego.apps.users.models import AbakusGroup
from lego.utils.functions import insert_abakus_groups

test_tree = {
    'UserAdminTest': [{
        'permissions': [
            '/sudo/admin/users/list/',
            '/sudo/admin/users/view/',
            '/sudo/admin/users/create/',
            '/sudo/admin/users/edit/',
            '/sudo/admin/users/delete/'
        ]}, {}
    ],
    'AbakusGroupAdminTest': [{
        'permissions': [
            '/sudo/admin/groups/list/',
            '/sudo/admin/groups/view/',
            '/sudo/admin/groups/create/',
            '/sudo/admin/groups/edit/',
            '/sudo/admin/groups/delete/'
        ]}, {}
    ],
    'TestGroup': [{}, {}],
    'EventAdminTest': [{
        'permissions': [
            '/sudo/admin/events/list/',
            '/sudo/admin/events/view/',
            '/sudo/admin/events/create/',
            '/sudo/admin/events/edit/',
            '/sudo/admin/events/delete/'
        ]}, {}
    ],
    'CommentTest': [{
        'permissions': [
            '/sudo/admin/comments/list/',
            '/sudo/admin/comments/view/',
            '/sudo/admin/comments/create/',
            '/sudo/admin/comments/edit/',
            '/sudo/admin/comments/delete/',
        ]}, {}
    ],
    'APIApplicationTest': [{
        'permissions': [
            '/sudo/admin/apiapplications/list/',
            '/sudo/admin/apiapplications/create/'
        ]}, {}
    ],
    'QuoteAdminTest': [{
        'permissions': [
            '/sudo/admin/quotes/like/',
            '/sudo/admin/quotes/change-approval/',
            '/sudo/admin/quotes/list-unapproved/',
            '/sudo/admin/quotes/list/',
            '/sudo/admin/quotes/view/',
            '/sudo/admin/quotes/create/',
            '/sudo/admin/quotes/edit/',
            '/sudo/admin/quotes/delete/'
        ]}, {}
    ],
    'ReactionTest': [{
        'permissions': ['/sudo/admin/reactions/create/']
    }, {}],
    'ReactionAdminTest': [{
        'permissions': ['/sudo/admin/reactions/']
    }, {}],
    'InterestGroupAdminTest': [
        {'permissions': [
            '/sudo/admin/interestgroups/list/',
            '/sudo/admin/interestgroups/view/',
            '/sudo/admin/interestgroups/create/',
            '/sudo/admin/interestgroups/edit/',
            '/sudo/admin/interestgroups/delete/'
        ]}, {}
    ],
    'Interessegrupper': [{}, {
        'TestInterestGroup': [{}, {}]
    }],
    'GalleryAdminTest': [{
        'permissions': ['/sudo/admin/gallerys/']
    }, {}],
    'GalleryTest': [{
        'permissions': ['/sudo/admin/gallerys/list/', '/sudo/admin/gallerys/view/']
    }, {}],
    'EmailAdminTest': [{
        'permissions': [
            '/sudo/admin/emailusers/',
            '/sudo/admin/emailgroups/',
            '/sudo/admin/emaillists/'
        ]
    }, {}],
    'Webkom': [{
        'permissions': [
            '/sudo/'
        ]
    }, {}]
}


def load_test_abakus_groups():
    insert_abakus_groups(test_tree)
    AbakusGroup.objects.rebuild()
