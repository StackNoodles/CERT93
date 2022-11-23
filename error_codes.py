from enum import IntEnum


class Error_codes(IntEnum):
    """ Codes d'erreur pour les initialisations """
    SUCCES = 0
    IMG_CHAR = 101
    IMG_TILES = 201
    SQUARES_TILES = 202
    IMG_ASSETS = 301
    SQUARES_ASSETS = 302
    IMG_INCIDENTS = 401
    SQUARES_INCIDENTS = 402
    SOUND_PHONE = 501
    SOUND_HANGUP = 502
    SOUND_SOLVE = 503
    SOUND_FAIL = 504
    SOUND_AMBIENCE = 505
    SOUND_MUSIC = 506