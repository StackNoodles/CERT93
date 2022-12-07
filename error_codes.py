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
    SOUND_SQUEAK = 507
    SOUND_25_LEFT = 508
    SOUND_10_LEFT = 509
    IMG_ARROW = 601
    IMG_ICONES_CHAR = 701
    SQUARES_ICONES_CHAR = 702
    IMG_PROGRESS_BAR = 801
    SQUARES_PROGRESS_BAR = 802


ERROR_CODES_TEXT = {
    Error_codes.SUCCES: "Tout s'est passé comme prévu",
    Error_codes.IMG_CHAR: "Erreur lors de du chargement des images de personnages",
    Error_codes.IMG_TILES: "Erreur lors de du chargement des images de tuiles",
    Error_codes.SQUARES_TILES: "Erreur lors de la creation des tuiles, elle ne sont pas carrées",
    Error_codes.IMG_ASSETS: "Erreur lors de du chargement des images des actifs",
    Error_codes.SQUARES_ASSETS: "Erreur lors de la creation des actifs, ils ne sont pas carrées",
    Error_codes.IMG_INCIDENTS: "Erreur lors de du chargement des images des incidents",
    Error_codes.SQUARES_INCIDENTS: "Erreur lors de la creation des incidents, ils ne sont pas carrées",
    Error_codes.SOUND_PHONE: "Erreur lors du chargement du son de telephone",
    Error_codes.SOUND_HANGUP: "Erreur lors du chargement du son de raccrochage du telepghone",
    Error_codes.SOUND_SOLVE: "Erreur lors du chargement du son de resolution",
    Error_codes.SOUND_FAIL: "Erreur lors du chargement du son d'echec",
    Error_codes.SOUND_AMBIENCE: "Erreur lors du chargement du son d'ambience de burreau",
    Error_codes.SOUND_MUSIC: "Erreur lors du chargement de la musique de fond",
    Error_codes.SOUND_SQUEAK: "Erreur lors du chargement du bruit mystère",
    Error_codes.IMG_ARROW: "Erreur lors du chargement de l'image de flèche",
    Error_codes.SOUND_25_LEFT: "Erreur lors du chargement de l'alerte 25 restant",
    Error_codes.SOUND_10_LEFT: "Erreur lors du chargement du l'alerte 10 restant",
    Error_codes.IMG_ICONES_CHAR: "Erreur lors de du chargement des images d'icones de personnages",
    Error_codes.SQUARES_ICONES_CHAR: "Erreur lors de la creation des icones de personnages, ils ne sont pas carrés",
    Error_codes.IMG_PROGRESS_BAR: "Erreur lors de du chargement des images pour la barre de progression de tâches",
    Error_codes.SQUARES_PROGRESS_BAR: "Erreur lors de la creation des images de barre de progression, elles ne sont pas carrées",
}
