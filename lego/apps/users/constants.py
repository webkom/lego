from enum import Enum

from django.db import models

MALE = "male"
FEMALE = "female"
OTHER = "other"

GENDERS = ((MALE, MALE), (FEMALE, FEMALE), (OTHER, OTHER))

MEMBER = "member"
LEADER = "leader"
CO_LEADER = "co-leader"
TREASURER = "treasurer"
RECRUITING = "recruiting"
DEVELOPMENT = "development"
EDITOR = "editor"
RETIREE = "retiree"
MEDIA_RELATIONS = "media_relations"
ACTIVE_RETIREE = "active_retiree"
ALUMNI = "alumni"
WEBMASTER = "webmaster"
INTEREST_GROUP_ADMIN = "interest_group_admin"
ALUMNI_ADMIN = "alumni_admin"
RETIREE_EMAIL = "retiree_email"
COMPANY_ADMIN = "company_admin"
DUGNAD_ADMIN = "dugnad_admin"
TRIP_ADMIN = "trip_admin"
SPONSOR_ADMIN = "sponsor_admin"
SOCIAL_ADMIN = "social_admin"
MERCH_ADMIN = "merch_admin"
HS_REPRESENTATIVE = "hs_representative"
CUDDLING_MANAGER = "cuddling_manager"
PHOTO_FILM_ADMIN = "photo_admin"
GRAPHIC_ADMIN = "graphic_admin"
SOCIAL_MEDIA_ADMIN = "social_media_admin"

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
    (RETIREE_EMAIL, RETIREE_EMAIL),
    (COMPANY_ADMIN, COMPANY_ADMIN),
    (DUGNAD_ADMIN, DUGNAD_ADMIN),
    (TRIP_ADMIN, TRIP_ADMIN),
    (SPONSOR_ADMIN, SPONSOR_ADMIN),
    (SOCIAL_ADMIN, SOCIAL_ADMIN),
    (MERCH_ADMIN, MERCH_ADMIN),
    (HS_REPRESENTATIVE, HS_REPRESENTATIVE),
    (CUDDLING_MANAGER, CUDDLING_MANAGER),
    (PHOTO_FILM_ADMIN, PHOTO_FILM_ADMIN),
    (GRAPHIC_ADMIN, GRAPHIC_ADMIN),
    (SOCIAL_MEDIA_ADMIN, SOCIAL_MEDIA_ADMIN),
)

DATA = "data"
KOMTEK = "komtek"

COURSES = ((DATA, DATA), (KOMTEK, KOMTEK))

DATA_LONG = "Datateknologi"
KOMTEK_LONG = "Kommunikasjonsteknologi"

COURSES_LONG = ((DATA_LONG, DATA_LONG), (KOMTEK_LONG, KOMTEK_LONG))

FIRST_GRADE_DATA = "1. klasse Datateknologi"
FIRST_GRADE_KOMTEK = "1. klasse Kommunikasjonsteknologi"

FOURTH_GRADE_DATA = "4. klasse Datateknologi"
FOURTH_GRADE_KOMTEK = "4. klasse Kommunikasjonsteknologi"

FIRST_GRADES = (
    (FIRST_GRADE_DATA, FIRST_GRADE_DATA),
    (FIRST_GRADE_KOMTEK, FIRST_GRADE_KOMTEK),
)

USER_GROUP = "Users"
MEMBER_GROUP = "Abakus"


class FSGroup(Enum):
    @classmethod
    def values(cls) -> list[str]:
        return [e.value for e in cls]

    MTDT = "fc:fs:fs:prg:ntnu.no:MTDT"
    MTKOM = "fc:fs:fs:prg:ntnu.no:MTKOM"
    MIDT = "fc:fs:fs:prg:ntnu.no:MIDT"
    MSTCNNS = "fc:fs:fs:prg:ntnu.no:MSTCNNS"
    MSSECCLO = "fc:fs:fs:prg:ntnu.no:MSSECCLO"


AbakusGradeFSMapping = {
    FSGroup.MTDT: FIRST_GRADE_DATA,
    FSGroup.MTKOM: FIRST_GRADE_KOMTEK,
    FSGroup.MIDT: FOURTH_GRADE_DATA,
    FSGroup.MSTCNNS: FOURTH_GRADE_KOMTEK,
    FSGroup.MSSECCLO: FOURTH_GRADE_KOMTEK,
}

GROUP_COMMITTEE = "komite"
GROUP_INTEREST = "interesse"
GROUP_BOARD = "styre"
GROUP_REVUE = "revy"
GROUP_SUB = "under"
GROUP_ORDAINED = "ordenen"
GROUP_GRADE = "klasse"
GROUP_OTHER = "annen"
GROUP_TYPES = (
    (GROUP_COMMITTEE, GROUP_COMMITTEE),
    (GROUP_INTEREST, GROUP_INTEREST),
    (GROUP_BOARD, GROUP_BOARD),
    (GROUP_REVUE, GROUP_REVUE),
    (GROUP_GRADE, GROUP_GRADE),
    (GROUP_OTHER, GROUP_OTHER),
    (GROUP_SUB, GROUP_SUB),
    (GROUP_ORDAINED, GROUP_ORDAINED),
)
OPEN_GROUPS = (GROUP_INTEREST,)

PUBLIC_GROUPS = (GROUP_INTEREST, GROUP_COMMITTEE, GROUP_SUB, GROUP_BOARD, GROUP_REVUE)


SPRING = "spring"
AUTUMN = "autumn"

SEMESTERS = (
    (SPRING, SPRING),
    (AUTUMN, AUTUMN),
)

WEBSITE_DOMAIN = "WEBSITE"
SOCIAL_MEDIA_DOMAIN = "SOCIAL_MEDIA"
PHOTO_CONSENT_DOMAINS = (
    (WEBSITE_DOMAIN, WEBSITE_DOMAIN),
    (SOCIAL_MEDIA_DOMAIN, SOCIAL_MEDIA_DOMAIN),
)

AUTO_THEME = "auto"
LIGHT_THEME = "light"
DARK_THEME = "dark"

THEMES = (
    (AUTO_THEME, AUTO_THEME),
    (LIGHT_THEME, LIGHT_THEME),
    (DARK_THEME, DARK_THEME),
)


LATE_PRESENCE_PENALTY_WEIGHT = 1


class PENALTY_WEIGHTS(models.TextChoices):
    LATE_PRESENCE = 1


class PENALTY_TYPES(models.TextChoices):
    PRESENCE = "presence"
    PAYMENT = "payment"
    OTHER = "other"
