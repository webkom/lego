MALE = 'male'
FEMALE = 'female'
OTHER = 'other'

GENDERS = (
    (MALE, MALE),
    (FEMALE, FEMALE),
    (OTHER, OTHER)
)

MEMBER = 'member'
LEADER = 'leader'
CO_LEADER = 'co-leader'
TREASURER = 'treasurer'
RECRUITING = 'recruiting'
DEVELOPMENT = 'development'
EDITOR = 'editor'
RETIREE = 'retiree'
MEDIA_RELATIONS = 'media relations'
ACTIVE_RETIREE = 'active retiree'
ALUMNI = 'alumni'
WEBMASTER = 'webmaster'
INTEREST_GROUP_ADMIN = 'interest group admin'
ALUMNI_ADMIN = 'alumni admin'
VOTE_COUNTER = 'vote counter'
RETIREE_EMAIL = 'retiree email'
COMPANY_ADMIN = 'company admin'
DUGNAD_ADMIN = 'dugnad admin'
TRIP_ADMIN = 'trip admin'
SPONSOR_ADMIN = 'sponsor admin'
SOCIAL_ADMIN = 'social admin'

ROLES = (
    (MEMBER, MEMBER),
    (LEADER, LEADER),
    (CO_LEADER, CO_LEADER),
    (TREASURER, TREASURER),
    (RECRUITING, RECRUITING),
    (DEVELOPMENT, DEVELOPMENT),
    (EDITOR, EDITOR),
    (RETIREE, RETIREE),
    (MEDIA_RELATIONS, MEDIA_RELATIONS),
    (ACTIVE_RETIREE, ACTIVE_RETIREE),
    (ALUMNI, ALUMNI),
    (WEBMASTER, WEBMASTER),
    (INTEREST_GROUP_ADMIN, INTEREST_GROUP_ADMIN),
    (ALUMNI_ADMIN, ALUMNI_ADMIN),
    (VOTE_COUNTER, VOTE_COUNTER),
    (RETIREE_EMAIL, RETIREE_EMAIL),
    (COMPANY_ADMIN, COMPANY_ADMIN),
    (DUGNAD_ADMIN, DUGNAD_ADMIN),
    (TRIP_ADMIN, TRIP_ADMIN),
    (SPONSOR_ADMIN, SPONSOR_ADMIN),
    (SOCIAL_ADMIN, SOCIAL_ADMIN)
)

DATA = 'data'
KOMTEK = 'komtek'

COURSES = (
    (DATA, DATA),
    (KOMTEK, KOMTEK)
)


DATA_LONG = 'Datateknologi'
KOMTEK_LONG = 'Kommunikasjonsteknologi'

COURSES_LONG = (
    (DATA_LONG, DATA_LONG),
    (KOMTEK_LONG, KOMTEK_LONG)
)

FIRST_GRADE_DATA = '1. klasse Datateknologi'
FIRST_GRADE_KOMTEK = '1. klasse Kommunikasjonsteknologi'

FIRST_GRADES = (
    (FIRST_GRADE_DATA, FIRST_GRADE_DATA),
    (FIRST_GRADE_KOMTEK, FIRST_GRADE_KOMTEK)
)

USER_GROUP = 'Users'
MEMBER_GROUP = 'Abakus'

STUDENT_EMAIL_DOMAIN = 'stud.ntnu.no'
