from django.db import models

SPRING = "spring"
AUTUMN = "autumn"

SEMESTER = ((SPRING, SPRING), (AUTUMN, AUTUMN))

COMPANY_PRESENTATION = "company_presentation"
COURSE = "course"
BREAKFAST_TALK = "breakfast_talk"
LUNCH_PRESENTATION = "lunch_presentation"
BEDEX = "bedex"
DIGITAL_PRESENTATION = "digital_presentation"
OTHER = "other"
SPONSOR = "sponsor"
START_UP = "start_up"
COMPANY_TO_COMPANY = "company_to_company"

COMPANY_EVENTS = (
    (COMPANY_PRESENTATION, COMPANY_PRESENTATION),
    (LUNCH_PRESENTATION, LUNCH_PRESENTATION),
    (COURSE, COURSE),
    (BREAKFAST_TALK, BREAKFAST_TALK),
    (DIGITAL_PRESENTATION, DIGITAL_PRESENTATION),
    (BEDEX, BEDEX),
    (OTHER, OTHER),
    (SPONSOR, SPONSOR),
    (START_UP, START_UP),
    (COMPANY_TO_COMPANY, COMPANY_TO_COMPANY),
)

TRANSLATED_EVENTS = {
    COMPANY_PRESENTATION: "Bedriftspresentasjon",
    LUNCH_PRESENTATION: "Lunsjpresentasjon",
    COURSE: "Kurs",
    BREAKFAST_TALK: "Frokostforedrag",
    DIGITAL_PRESENTATION: "Digital presentasjon",
    BEDEX: "BedEx (vinter 2021)",
    OTHER: "Alternativt arrangement",
    START_UP: "Start-up kveld",
    COMPANY_TO_COMPANY: "Bedrift-til-bedrift",
}

COLLABORATION = "collaboration"
README = "readme"
ITDAGENE = "itdagene"
LABAMBA_SPONSOR = "labamba_sponsor"
SOCIAL_MEDIA = "social_media"
THURSDAY_EVENT = "thursday_event"

OTHER_OFFERS = (
    (COLLABORATION, COLLABORATION),
    (README, README),
    (ITDAGENE, ITDAGENE),
    (LABAMBA_SPONSOR, LABAMBA_SPONSOR),
    (SOCIAL_MEDIA, SOCIAL_MEDIA),
    (THURSDAY_EVENT, THURSDAY_EVENT),
)

TRANSLATED_OTHER_OFFERS = {
    COLLABORATION: "Samarbeid med andre linjeforeninger",
    README: "Annonsering i readme",
    ITDAGENE: "Stand på itDAGENE",
    LABAMBA_SPONSOR: "Sponsing av LaBamba",
    SOCIAL_MEDIA: "Profilering på sosiale medier",
}

COLLABORATION_ONLINE = "collaboration_online"
COLLABORATION_OMEGA = "collaboration_omega"
COLLABORATION_TIHLDE = "collaboration_tihlde"
COLLABORATION_REVUE = "collaboration_revue"
COLLABORATION_ANNIVERSARY = "collaboration_anniversary"
COLLABORATION_REVUE_ANNIVERSARY = "collaboration_revue_anniversary"

COLLABORATIONS = (
    (COLLABORATION_ONLINE, COLLABORATION_ONLINE),
    (COLLABORATION_OMEGA, COLLABORATION_OMEGA),
    (COLLABORATION_TIHLDE, COLLABORATION_TIHLDE),
    (COLLABORATION_REVUE, COLLABORATION_REVUE),
    (COLLABORATION_ANNIVERSARY, COLLABORATION_ANNIVERSARY),
    (COLLABORATION_REVUE_ANNIVERSARY, COLLABORATION_REVUE_ANNIVERSARY),
)

TRANSLATED_COLLABORATIONS = {
    COLLABORATION_ONLINE: "Online linjeforening",
    COLLABORATION_OMEGA: "Omega linjeforening",
    COLLABORATION_TIHLDE: "TIHLDE linjeforening",
    COLLABORATION_REVUE: "Abakusrevyen",
    COLLABORATION_ANNIVERSARY: "Abakus jubileum",
    COLLABORATION_REVUE_ANNIVERSARY: "Abakusrevy jubileum",
}


class COMPANY_TYPES(models.TextChoices):
    SMALL_CONSULTANT = "company_types_small_consultant"
    MEDIUM_CONSULTANT = "company_types_medium_consultant"
    LARGE_CONSULTANT = "company_types_large_consultant"
    INHOUSE = "company_types_inhouse"
    TYPES_OTHERS = "company_types_others"
    START_UP = "company_types_start_up"
    GOVERNMENTAL = "company_types_governmental"


TRANSLATED_COMPANY_TYPES = {
    COMPANY_TYPES.SMALL_CONSULTANT: "Liten Konsulentbedrift",
    COMPANY_TYPES.MEDIUM_CONSULTANT: "Medium konsulentbedrift",
    COMPANY_TYPES.LARGE_CONSULTANT: "Stor konsulentbedrift",
    COMPANY_TYPES.INHOUSE: "Inhouse",
    COMPANY_TYPES.TYPES_OTHERS: "Annet",
    COMPANY_TYPES.START_UP: "Start-up",
    COMPANY_TYPES.GOVERNMENTAL: "Statlig",
}


class COMPANY_COURSE_THEMES(models.TextChoices):
    SECURITY = "company_survey_security"
    AI = "company_survey_ai"
    DATA = "company_survey_big_data"
    END = "company_survey_front_back_end"
    IOT = "company_survey_iot"
    GAMEDEV = "company_survey_gamedev"
    SOFTSKILLS = "company_survey_softskills"
    FINTECH = "company_survey_fintech"


TRANSLATED_COURSE_THEMES = {
    COMPANY_COURSE_THEMES.SECURITY: "Sikkerhet",
    COMPANY_COURSE_THEMES.AI: "Kunstlig intellligens",
    COMPANY_COURSE_THEMES.DATA: "Big data",
    COMPANY_COURSE_THEMES.END: "Front end/Back end",
    COMPANY_COURSE_THEMES.IOT: "Internet of things",
    COMPANY_COURSE_THEMES.GAMEDEV: "Spillutvikling",
    COMPANY_COURSE_THEMES.SOFTSKILLS: "Softskills",
    COMPANY_COURSE_THEMES.FINTECH: "Finansiell teknologi",
}

CONTACT_IN_OSLO = "contact_in_oslo"
INTERESTED = "interested"
NOT_INTERESTED = "not_interested"
CONTACTED = "contacted"
NOT_CONTACTED = "not_contacted"

SEMESTER_STATUSES = (
    (COMPANY_PRESENTATION, COMPANY_PRESENTATION),
    (COURSE, COURSE),
    (BREAKFAST_TALK, BREAKFAST_TALK),
    (LUNCH_PRESENTATION, LUNCH_PRESENTATION),
    (BEDEX, BEDEX),
    (CONTACT_IN_OSLO, CONTACT_IN_OSLO),
    (INTERESTED, INTERESTED),
    (NOT_INTERESTED, NOT_INTERESTED),
    (CONTACTED, CONTACTED),
    (NOT_CONTACTED, NOT_CONTACTED),
)
