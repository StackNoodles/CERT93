# Ensemble des paramètres de l'application
import configparser

config = configparser.ConfigParser(inline_comment_prefixes="#")
config.read("config/config.ini")


SCREEN_WIDTH = int(config.get("Settings", "SCREEN_WIDTH"))
SCREEN_HEIGHT = int(config.get("Settings", "SCREEN_HEIGHT"))

ACTIONABLE_DISTANCE = int(config.get(
    "Settings", "ACTIONABLE_DISTANCE"))  # en pixels

BACKDROP_FILENAME = config.get("Images", "BACKDROP_FILENAME")
CHARACTERS_FILENAME = config.get("Images", "CHARACTERS_FILENAME")
TILES_FILENAME = config.get("Images", "TILES_FILENAME")
ASSETS_FILENAME = config.get("Images", "ASSETS_FILENAME")
INCIDENTS_FILENAME = config.get("Images", "INCIDENTS_FILENAME")

OFFICE_FILENAME = config.get("Assets", "OFFICE_FILENAME")

BACKGROUND_MUSIC = config.get("Sounds", "BACKGROUND_MUSIC")
OFFICE_AMBIENCE_SOUND = config.get("Sounds", "OFFICE_AMBIENCE_SOUND")
PHONE_RING_SOUND_FILENAME = config.get("Sounds", "PHONE_RING_SOUND_FILENAME")
PHONE_HANGUP_SOUND_FILENAME = config.get(
    "Sounds", "PHONE_HANGUP_SOUND_FILENAME")
FAILURE_SOUND_FILENAME = config.get("Sounds", "FAILURE_SOUND_FILENAME")
SOLVE_SOUND_FILENAME = config.get("Sounds", "SOLVE_SOUND_FILENAME")

HELPDESK_ASSET_ID = int(config.get("Settings", "HELPDESK_ASSET_ID"))
HELPDESK_MIN_SOLVING_TIME = int(config.get(
    "Settings", "HELPDESK_MIN_SOLVING_TIME"))  # temps minimum pour prendre un appel
HELPDESK_MAX_SOLVING_TIME = int(config.get(
    "Settings", "HELPDESK_MAX_SOLVING_TIME"))  # temps maximum pour prendre un appel

NB_CHARACTERS = int(config.get("Settings", "NB_CHARACTERS"))
NB_SKILLS = int(config.get("Settings", "NB_SKILLS"))

TIME_PER_LEVEL = int(config.get("Settings", "TIME_PER_LEVEL"))  # en secondes

DEFAULT_TIME_TO_SOLVE_MIN = int(config.get("Settings", "DEFAULT_TIME_TO_SOLVE_MIN"))
DEFAULT_TIME_TO_SOLVE_MAX = int(config.get("Settings", "DEFAULT_TIME_TO_SOLVE_MAX"))

NB_INCIDENT_TIMER_IMAGES = int(config.get(
    "Settings", "NB_INCIDENT_TIMER_IMAGES"))
TIMER_PERCENTAGE_SLICE_SIZE = int(config.get(
    "Settings", "TIMER_PERCENTAGE_SLICE_SIZE")) / (NB_INCIDENT_TIMER_IMAGES - 1)

INACTIVITY_THRESHOLD = 5  # en secondes

DEFAULT_MIN_TIME_BETWEEN_INDICENTS = int(config.get(
    "Settings", "DEFAULT_MIN_TIME_BETWEEN_INDICENTS"))
DEFAULT_MAX_TIME_BETWEEN_INDICENTS = int(config.get(
    "Settings", "DEFAULT_MAX_TIME_BETWEEN_INDICENTS"))
TIME_BEFORE_FIRST_INCIDENT = int(config.get(
    "Settings", "TIME_BEFORE_FIRST_INCIDENT"))
