from lego.apps.social_groups.models import InterestGroup
from lego.apps.users.models import AbakusGroup

interest_group_tree = {
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


def load_dev_interest_groups():
    parent = AbakusGroup.objects.get(name='Interessegrupper')
    insert_interest_groups(interest_group_tree, parent)
    AbakusGroup.objects.rebuild()


def insert_interest_groups(tree, parent=None):
    """This inserts interest groups, not regular AbakusGroups"""
    for key, value in tree.items():
        kwargs = value[0]
        node = InterestGroup.objects.update_or_create(
            name=key, defaults={**kwargs, 'parent': parent}
        )[0]
        insert_interest_groups(value[1], node)
