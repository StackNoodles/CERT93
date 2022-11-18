# Ensemble des paramètres de l'application

SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768

ACTIONABLE_DISTANCE = 32  # en pixels

BACKDROP_FILENAME = 'img/cert_backdrop.png'
CHARACTERS_FILENAME = 'img/cert_characters.png'
TILES_FILENAME = 'img/cert_tileset.png'
ASSETS_FILENAME = 'img/cert_equipements.png'
INCIDENTS_FILENAME = 'img/cert_incidents.png'
OFFICE_FILENAME = 'bin/office.pickle'

BACKGROUND_MUSIC = 'snd/650556__stephiequeen__communicate-song-loop.ogg'
OFFICE_AMBIENCE_SOUND = 'snd/407292__nightwatcher98__office-ambience-MODIFIED.mp3'
PHONE_RING_SOUND_FILENAME = 'snd/24929__acclivity__phoneringing.mp3'
PHONE_HANGUP_SOUND_FILENAME = 'snd/334982__paulocorona__hanging-phone-MODIFIED.wav'
FAILURE_SOUND_FILENAME = 'snd/572936__bloodpixelhero__error.wav'
SOLVE_SOUND_FILENAME = 'snd/511484__mlaudio__success-bell.wav'

HELPDESK_ASSET_ID = 0
HELPDESK_MIN_SOLVING_TIME = 5  # temps minimum pour prendre un appel
HELPDESK_MAX_SOLVING_TIME = 60  # temps maximum pour prendre un appel

NB_CHARACTERS = 8
NB_SKILLS = 7

TIME_PER_LEVEL = 300  # en secondes

NB_INCIDENT_TIMER_IMAGES = 17
TIMER_PERCENTAGE_SLICE_SIZE = 100 / (NB_INCIDENT_TIMER_IMAGES - 1)

INACTIVITY_THRESHOLD = 5  # en secondes
