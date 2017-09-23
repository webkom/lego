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

ROLES = (
    (MEMBER, MEMBER),
    (LEADER, LEADER),
    (CO_LEADER, CO_LEADER),
    (TREASURER, TREASURER)
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

GROUP_COMMITTEE = 'komite'
GROUP_INTEREST = 'interesse'
GROUP_OTHER = 'annen'
GROUP_TYPES = (
    (GROUP_COMMITTEE, GROUP_COMMITTEE),
    (GROUP_INTEREST, GROUP_INTEREST),
    (GROUP_OTHER, GROUP_OTHER),
)
