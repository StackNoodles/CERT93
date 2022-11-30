import pygame
import settings

from expertise import Expertise
from error_codes import Error_codes

class __CharactersCollection:
    """ Collection de personnages utilisée par l'objet global characters_collection (voir plus bas). """

    def __init__(self) -> None:
        self.__surfaces = None

    def init(self) -> Error_codes:
        """
        Initialise l'instance unique de resources.characters_collection.
        La méthode init() permet d'éviter de ralentir l'importation du module avec des entrées/sorties. Elle permet
        aussi de diminuer l'impact d'importations multiples et de gérer les erreurs à un seul endroit, une fois les
        importations terminées.
        :return: 999 si l'initialisation s'est bien passée, le code d'erreur sinon
        """

        # charge l'image contenant tous les personnages
        try :
            characters_sheet = pygame.image.load(settings.CHARACTERS_FILENAME).convert_alpha()
        except :
            return Error_codes.IMG_CHAR
        
        if not characters_sheet:
            return Error_codes.IMG_CHAR
        
        # découpe la surface de personnages en surfaces individuelles (une pour chaque personnage)
        height = characters_sheet.get_height()
        width = characters_sheet.get_width() / settings.NB_CHARACTERS

        self.__surfaces = []
        for i in range(settings.NB_CHARACTERS):
            character_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            source_area = pygame.Rect(i * width, 0, width, height)
            character_surface.blit(characters_sheet, (0, 0), source_area)
            self.__surfaces.append(character_surface)
            
        return Error_codes.SUCCES

    def get(self, character_id: int) -> pygame.Surface or None:
        """
        Retourne la surface correspondant à l'identifiant de personnage (character_id).
        :param character_id: identifiant de personnage
        :return: la surface si disponible, None sinon
        """
        assert self.__surfaces
        if 0 <= character_id < settings.NB_CHARACTERS:
            return self.__surfaces[character_id]

        return None


class __TilesCollection:
    """ Collection de tuiles utilisée par l'objet global tiles_collection (voir plus bas). """

    def __init__(self) -> None:
        self.__surfaces = None

    def init(self) -> Error_codes:
        """
        Initialise l'instance unique de resources.tiles_collection.
        La méthode init() permet d'éviter de ralentir l'importation du module avec des entrées/sorties. Elle permet
        aussi de diminuer l'impact d'importations multiples et de gérer les erreurs à un seul endroit, une fois les
        importations terminées.
        :return: 999 si l'initialisation s'est bien passée, le code d'erreur sinon
        """

        # charge l'image contenant toutes les tuiles
        try : 
            tiles_sheet = pygame.image.load(settings.TILES_FILENAME).convert()
        except :
            return Error_codes.IMG_TILES
        
        if not tiles_sheet:
            return Error_codes.IMG_TILES

        # s'assure que les tuiles soient carrées
        if tiles_sheet.get_width() % tiles_sheet.get_height() != 0:
            return Error_codes.SQUARES_TILES

        # découpe la surface de tuiles en surfaces individuelles (une pour chaque tuile)
        height = width = tiles_sheet.get_height()
        self.__surfaces = []
        for i in range(tiles_sheet.get_width() // width):
            tile_surface = pygame.Surface((width, height))
            source_area = pygame.Rect(i * width, 0, width, height)
            tile_surface.blit(tiles_sheet, (0, 0), source_area)
            self.__surfaces.append(tile_surface)

        return Error_codes.SUCCES

    def get(self, tile_id: int) -> pygame.Surface or None:
        """
        Retourne la surface correspondant à l'identifiant de tuile (tile_id).
        :param tile_id: identifiant de tuile
        :return: la surface si disponible, None sinon
        """
        assert self.__surfaces
        if 0 <= tile_id < len(self.__surfaces):
            return self.__surfaces[tile_id]

        return None

    def tile_size(self) -> int:
        """
        Retourne les dimensions d'une image de tuile.
        :return: Dimensions d'une tuile (largeur, hauteur)
        """
        assert self.__surfaces and len(self.__surfaces) > 0

        return self.__surfaces[0].get_size()

    def pixel_pos_to_tile_pos(self, pixel_position: tuple) -> tuple:
        """
        Convertit une coordonnée de pixels en coordonnée de tuile
        :param pixel_position: Position (coordonnée) en pixels
        :return: Position (coordonnée) de la tuile
        """
        assert self.__surfaces and len(self.__surfaces) > 0

        pixel_x, pixel_y = pixel_position
        tile_x = pixel_x % self.__surfaces[0].get_width()
        tile_y = pixel_y % self.__surfaces[0].get_height()
        return tile_x, tile_y

    def tile_pos_to_pixel_pos(self, tile_position: tuple) -> tuple:
        """
        Convertit une coordonnée de tuile en coordonnée de pixels
        :param tile_position: Position (coordonnée) de la tuile
        :return: Position (coordonnée) en pixels
        """
        assert self.__surfaces and len(self.__surfaces) > 0

        tile_x, tile_y = tile_position
        pixel_x = tile_x * self.__surfaces[0].get_width()
        pixel_y = tile_y * self.__surfaces[0].get_height()
        return pixel_x, pixel_y

    def tile_pos_to_center_pixel_pos(self, tile_position: tuple) -> tuple:
        """
        Convertit une coordonnée de tuile en coordonnée de pixels pour le centre de la tuile
        :param tile_position: Position (coordonnée) de la tuile
        :return: Position (coordonnée) du centre de la tuile en pixels
        """
        assert self.__surfaces and len(self.__surfaces) > 0

        pixel_x, pixel_y = self.tile_pos_to_pixel_pos(tile_position)
        center_x = pixel_x + (self.__surfaces[0].get_width() / 2)
        center_y = pixel_y + (self.__surfaces[0].get_height() / 2)
        return center_x, center_y


class __AssetsCollection:
    """ Collection d'actifs (assets) utilisée par l'objet global assets_collection (voir plus bas). """

    def __init__(self) -> None:
        self.__surfaces = None

    def init(self) -> Error_codes:
        """
        Initialise l'instance unique de resources.assets_collection.
        La méthode init() permet d'éviter de ralentir l'importation du module avec des entrées/sorties. Elle permet
        aussi de diminuer l'impact d'importations multiples et de gérer les erreurs à un seul endroit, une fois les
        importations terminées.
        :return: 999 si l'initialisation s'est bien passée, le code d'erreur sinon
        """

        # charge l'image contenant tous les actifs
        try :
            assets_sheet = pygame.image.load(settings.ASSETS_FILENAME).convert_alpha()
        except :
            return Error_codes.IMG_ASSETS
            
        if not assets_sheet:
            return Error_codes.IMG_ASSETS

        # s'assure que les actifs soient carrés
        if assets_sheet.get_width() % assets_sheet.get_height() != 0:
            return Error_codes.SQUARES_ASSETS

        # découpe la surface d'actifs en surfaces individuelles (une pour chaque actif)
        height = width = assets_sheet.get_height()
        self.__surfaces = []
        for i in range(assets_sheet.get_width() // width):
            asset_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            source_area = pygame.Rect(i * width, 0, width, height)
            asset_surface.blit(assets_sheet, (0, 0), source_area)
            self.__surfaces.append(asset_surface)

        return Error_codes.SUCCES

    def get(self, asset_id: int) -> pygame.Surface or None:
        """
        Retourne la surface correspondant à l'identifiant de l'actif (asset_id).
        :param asset_id: identifiant d'actif
        :return: la surface si disponible, None sinon
        """
        assert self.__surfaces
        if 0 <= asset_id < len(self.__surfaces):
            return self.__surfaces[asset_id]

        return None


class __IncidentsCollection:
    """
    Collection de minuteries et d'icônes pour les incidents utilisée par l'objet global incidents_collection
    (voir plus bas).
    """

    def __init__(self) -> None:
        self.__incident_surfaces = None

    def init(self) -> Error_codes:
        """
        Initialise l'instance unique de resources.incidents_collection.
        La méthode init() permet d'éviter de ralentir l'importation du module avec des entrées/sorties. Elle permet
        aussi de diminuer l'impact d'importations multiples et de gérer les erreurs à un seul endroit, une fois les
        importations terminées.
        :return: 999 si l'initialisation s'est bien passée, le code d'erreur sinon
        """

        # Chargement de l'image contenant toutes images reliées aux incidents:
        #   17 images de minuterie (pleine à terminée) et 7 images pour les icônes
        try :
            incidents_sheet = pygame.image.load(settings.INCIDENTS_FILENAME).convert_alpha()
        except :
            return Error_codes.IMG_INCIDENTS
            
        if not incidents_sheet:
            return Error_codes.IMG_INCIDENTS

        # Vérifications que les images soient carrées
        if incidents_sheet.get_width() % incidents_sheet.get_height() != 0:
            return Error_codes.SQUARES_INCIDENTS

        # Découpage de la surface chargée en surfaces individuelles (une pour chaque image de minuterie)
        height = width = incidents_sheet.get_height()
        timer_surfaces = []
        for i in range(settings.NB_INCIDENT_TIMER_IMAGES):
            timer_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            source_area = pygame.Rect(i * width, 0, width, height)
            timer_surface.blit(incidents_sheet, (0, 0), source_area)
            timer_surfaces.append(timer_surface)

        # Découpage de la surface chargée en surfaces individuelles (une pour chaque icône d'incident)
        icons_surfaces = []
        for i in range(settings.NB_INCIDENT_TIMER_IMAGES, settings.NB_INCIDENT_TIMER_IMAGES + settings.NB_SKILLS):
            icon_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            source_area = pygame.Rect(i * width, 0, width, height)
            icon_surface.blit(incidents_sheet, (0, 0), source_area)
            icons_surfaces.append(icon_surface)

        # Construction des surfaces combinées (minuterie + icône)
        self.__incident_surfaces = []
        for skill_index in range(settings.NB_SKILLS):
            series = []
            for timer_index in range(len(timer_surfaces)):
                combined_surface = timer_surfaces[timer_index].copy()
                combined_surface.blit(icons_surfaces[skill_index], (0, 0))
                series.append(combined_surface)
            self.__incident_surfaces.append(series)

        return Error_codes.SUCCES

    def get(self, timer_id: int, expertise: Expertise) -> pygame.Surface or None:
        """
        Retourne la surface correspondant à la minuterie (timer_id) pour un incident d'une
        expertise donnée (expertise).
        :param timer_id: identifiant de l'image de minuterie
        :param expertise: expertise sollicitée par l'incident
        :return: la surface si disponible, None sinon
        """
        assert self.__incident_surfaces
        expertise_id = int(expertise)
        if 0 <= timer_id < len(self.__incident_surfaces[expertise_id]):
            return self.__incident_surfaces[expertise_id][timer_id]

        return None


class __SoundsCollection:
    """ Collection de sons utilisée par l'objet global sounds_collection (voir plus bas). """

    def __init__(self) -> None:
        self.__surfaces = None
        self.__sounds = None

    def init(self) -> Error_codes:
        """
        Initialise l'instance unique de resources.sounds_collection.
        La méthode init() permet d'éviter de ralentir l'importation du module avec des entrées/sorties. Elle permet
        aussi de diminuer l'impact d'importations multiples et de gérer les erreurs à un seul endroit, une fois les
        importations terminées.
        :return: 999 si l'initialisation s'est bien passée, le code d'erreur sinon
        """
        self.__sounds = {}
        try :
            sound = pygame.mixer.Sound(settings.PHONE_RING_SOUND_FILENAME)
        except :
            return Error_codes.SOUND_PHONE
            
        if not sound:
            return Error_codes.SOUND_PHONE
        self.__sounds['HELPDESK-PHONE-RING'] = sound

        try : 
            sound = pygame.mixer.Sound(settings.PHONE_HANGUP_SOUND_FILENAME)
        except :
            return Error_codes.SOUND_HANGUP
            
        if not sound:
            return Error_codes.SOUND_HANGUP
        self.__sounds['HELPDESK-PHONE-HANGUP'] = sound

        try :
            sound = pygame.mixer.Sound(settings.SOLVE_SOUND_FILENAME)
        except :
            return Error_codes.SOUND_SOLVE
        
        if not sound:
            return Error_codes.SOUND_SOLVE
        self.__sounds['INCIDENT-SOLVE'] = sound

        try :
            sound = pygame.mixer.Sound(settings.FAILURE_SOUND_FILENAME)
        except :
            return Error_codes.SOUND_FAIL
        
        if not sound:
            return Error_codes.SOUND_FAIL
        self.__sounds['INCIDENT-FAIL'] = sound

        try :
            sound = pygame.mixer.Sound(settings.OFFICE_AMBIENCE_SOUND)
        except :
            return Error_codes.SOUND_AMBIENCE
            
        if not sound:
            return Error_codes.SOUND_AMBIENCE
        sound.set_volume(0.25)
        self.__sounds['OFFICE-AMBIENCE'] = sound

        try :
            sound = pygame.mixer.Sound(settings.BACKGROUND_MUSIC)
        except :
            return Error_codes.SOUND_MUSIC
            
        if not sound:
            return Error_codes.SOUND_MUSIC
        sound.set_volume(0.25)
        self.__sounds['BACKGROUND-MUSIC'] = sound

        return Error_codes.SUCCES

    def get(self, name: str) -> pygame.mixer.Sound or None:
        """
        Retourne le son correspondant au nom spécifié (name).
        :param name: nom du son
        :return: le son si disponible, None sinon
        """
        assert self.__sounds
        return self.__sounds.get(name, None)


# collection de personnages (singleton du GoF implémenté avec un Global Object Pattern de python)
characters_collection = None

# collection de tuiles (singleton du GoF implémenté avec un Global Object Pattern de python)
tiles_collection = None

# collection d'actifs (assets) (singleton du GoF implémenté avec un Global Object Pattern de python)
assets_collection = None

# collection d'images de minuterie et d'icônes pour les incidents
# (singleton du GoF implémenté avec un Global Object Pattern de python)
incidents_collection = None

# collection de sons (singleton du GoF implémenté avec un Global Object Pattern de python)
sounds_collection = None


def init() -> Error_codes:
    """ Initialise l'ensemble des ressources. """

    global characters_collection
    if not characters_collection:
        characters_collection = __CharactersCollection()
        return_code = characters_collection.init()
        if return_code != Error_codes.SUCCES:
            return return_code

    global tiles_collection
    if not tiles_collection:
        tiles_collection = __TilesCollection()
        return_code = tiles_collection.init()
        if return_code != Error_codes.SUCCES:
            return return_code

    global assets_collection
    if not assets_collection:
        assets_collection = __AssetsCollection()
        return_code = assets_collection.init()
        if return_code != Error_codes.SUCCES:
            return return_code

    global incidents_collection
    if not incidents_collection:
        incidents_collection = __IncidentsCollection()
        return_code = incidents_collection.init()
        if return_code != Error_codes.SUCCES:
            return return_code

    global sounds_collection
    if not sounds_collection:
        sounds_collection = __SoundsCollection()
        return_code = sounds_collection.init()
        if return_code != Error_codes.SUCCES:
            return return_code

    return Error_codes.SUCCES
