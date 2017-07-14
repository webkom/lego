from lego.apps.users.models import AbakusGroup
from lego.utils.functions import insert_abakus_groups

test_tree = {
    'UserAdminTest': [{
        'permissions': [
            '/sudo/admin/users/list/',
            '/sudo/admin/users/retrieve/',
            '/sudo/admin/users/create/',
            '/sudo/admin/users/update/',
            '/sudo/admin/users/destroy/'
        ]}, {}
    ],
    'AbakusGroupAdminTest': [{
        'permissions': [
            '/sudo/admin/groups/list/',
            '/sudo/admin/groups/retrieve/',
            '/sudo/admin/groups/create/',
            '/sudo/admin/groups/update/',
            '/sudo/admin/groups/destroy/'
        ]}, {}
    ],
    'TestGroup': [{}, {}],
    'EventAdminTest': [{
        'permissions': [
            '/sudo/admin/events/list/',
            '/sudo/admin/events/retrieve/',
            '/sudo/admin/events/create/',
            '/sudo/admin/events/update/',
            '/sudo/admin/events/destroy/'
        ]}, {}
    ],
    'CommentTest': [{
        'permissions': [
            '/sudo/admin/comments/list/',
            '/sudo/admin/comments/retrieve/',
            '/sudo/admin/comments/create/',
            '/sudo/admin/comments/update/',
            '/sudo/admin/comments/destroy/',
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
            '/sudo/admin/quotes/retrieve/',
            '/sudo/admin/quotes/create/',
            '/sudo/admin/quotes/update/',
            '/sudo/admin/quotes/destroy/'
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
            '/sudo/admin/interestgroups/retrieve/',
            '/sudo/admin/interestgroups/create/',
            '/sudo/admin/interestgroups/update/',
            '/sudo/admin/interestgroups/destroy/'
        ]}, {}
    ],
    'Interessegrupper': [{}, {
        'TestInterestGroup': [{}, {}]
    }],
    'GalleryAdminTest': [{
        'permissions': ['/sudo/admin/gallerys/']
    }, {}],
    'GalleryTest': [{
        'permissions': ['/sudo/admin/gallerys/list/', '/sudo/admin/gallerys/retrieve/']
    }, {}],
}


def load_test_abakus_groups():
    insert_abakus_groups(test_tree)
    AbakusGroup.objects.rebuild()
