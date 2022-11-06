FULL_TIME = "full_time"
PART_TIME = "part_time"
SUMMER_JOB = "summer_job"
MASTER_THESIS = "master_thesis"
OTHER = "other"

JOB_TYPE_CHOICES = (
    (FULL_TIME, FULL_TIME),
    (PART_TIME, PART_TIME),
    (SUMMER_JOB, SUMMER_JOB),
    (MASTER_THESIS, MASTER_THESIS),
    (OTHER, OTHER),
)

JOB_TYPE_TRANSLATIONS = {
    SUMMER_JOB: "Sommerjobb",
    PART_TIME: "Deltid",
    FULL_TIME: "Fulltid",
    MASTER_THESIS: "Masteroppgave",
    OTHER: "Annet",
}

YEAR_CHOICES = ((1, 1), (2, 2), (3, 3), (4, 4), (5, 5))
