SPRING = 'spring'
AUTUMN = 'autumn'

SEMESTER = (
    (SPRING, SPRING),
    (AUTUMN, AUTUMN),
)

COMPANY_PRESENTATION = 'company_presentation'
COURSE = 'course'
LUNCH_PRESENTATION = 'lunch_presentation'
BEDEX = 'bedex'
OTHER = 'other'

COMPANY_EVENTS = (
    (COMPANY_PRESENTATION, COMPANY_PRESENTATION),
    (COURSE, COURSE),
    (LUNCH_PRESENTATION, LUNCH_PRESENTATION),
    (BEDEX, BEDEX),
    (OTHER, OTHER),
)

TRANSLATED_EVENTS = {
    COMPANY_PRESENTATION: 'Bedriftspresentasjon',
    COURSE: 'Kurs',
    LUNCH_PRESENTATION: 'Lunsjpresentasjon',
    BEDEX: 'Bedex',
    OTHER: 'Alternativt arrangement',
}

COLLABORATION = 'collaboration'
README = 'readme'
ITDAGENE = 'itdagene'
LABAMBA_SPONSOR = 'labamba_sponsor'

OTHER_OFFERS = (
    (COLLABORATION, COLLABORATION),
    (README, README),
    (ITDAGENE, ITDAGENE),
    (LABAMBA_SPONSOR, LABAMBA_SPONSOR),
)

TRANSLATED_OTHER_OFFERS = {
    COLLABORATION: 'Samarbeid med andre linjeforeninger',
    README: 'Annonsering i readme',
    ITDAGENE: 'Stand på itDAGENE',
    LABAMBA_SPONSOR: 'Sponsing av LaBamba',
}

CONTACT_IN_OSLO = 'contact_in_oslo'
INTERESTED = 'interested'
NOT_INTERESTED = 'not_interested'
CONTACTED = 'contacted'
NOT_CONTACTED = 'not_contacted'

SEMESTER_STATUSES = (
    (COMPANY_PRESENTATION, COMPANY_PRESENTATION),
    (COURSE, COURSE),
    (LUNCH_PRESENTATION, LUNCH_PRESENTATION),
    (BEDEX, BEDEX),
    (CONTACT_IN_OSLO, CONTACT_IN_OSLO),
    (INTERESTED, INTERESTED),
    (NOT_INTERESTED, NOT_INTERESTED),
    (CONTACTED, CONTACTED),
    (NOT_CONTACTED, NOT_CONTACTED),
)
