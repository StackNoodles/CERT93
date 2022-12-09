import pygame
from incidents import Incident
from progress_bar import ProgressBar

import resources

from expertise import Expertise


class Character:
    """ Un personnage. """

    def __init__(self, name: str, character_id: int, expertise: Expertise, speed: float, tile_position: tuple) -> None:
        """
        Initialise une instance de personnage (Character).
        :param name: nom du personnage
        :param character_id: identifiant permettant de récupérer l'image du personnage
        :param expertise: expertise du personnage
        :param speed: vitesse de déplacement du personnage
        :param tile_position: position dans le bureau (coordonnée de tuile)
        """
        self.__name = name
        self.__character_id = character_id
        self.__speed = speed
        self.__expertise = expertise
        self.__locked = False
        self.__progress_bar = None
        self.__current_working_incident = None

        font = pygame.font.SysFont(None, 24)
        self.text_char = font.render(self.__name, True, (255, 255, 255))

        # Conversion de la position d'une coordonnée en tuile vers une coordonnée en pixels
        x, y = resources.tiles_collection.tile_pos_to_pixel_pos(tile_position)
        tile_width, tile_height = resources.tiles_collection.tile_size()
        # On positionne le personnage au centre de la tuile
        self.__feet_position = x + (tile_width / 2), y + (tile_height/2)

    def draw(self, destination: pygame.Surface, display_name) -> None:
        """
        Dessine le personnage.
        :param destination: surface sur laquelle dessiner le personnage
        :return: aucun
        """

        image = resources.characters_collection.get(self.__character_id)
        x = self.__feet_position[0] - (image.get_width() / 2)
        y = self.__feet_position[1] - image.get_height()

        destination.blit(image, (x, y))
        if display_name:
            destination.blit(
                self.text_char, (x - self.text_char.get_width() / 2, y + image.get_height()))

    def compute_next_feet_position(self, movement: tuple, delta_time: float) -> tuple:
        """
        Calcule une position des pieds projetée à partir du positionnement courant et d'un déplacement.
        :param movement: mouvement (horizontal, vertical)
        :param delta_time: temps depuis l'affichage de la trame précédente
        :return: position projetée
        """
        x = self.__feet_position[0] + (movement[0] * delta_time * self.__speed)
        y = self.__feet_position[1] + (movement[1] * delta_time * self.__speed)
        return x, y

    def add_progress_bar(self, incident: Incident) -> None:
        """
        Ajoute une barre de progression au personage.
        :param incident: l'incident que le personnage resoud
        :reutrn: aucun
        """
        # The Hulk est un expert en tout (id 5)
        expiration_time = incident.duration / \
            10 if self.expertise == incident.expertise or self.__character_id == 5 else incident.duration/5
        self.__current_working_incident = incident
        self.__locked = True
        self.__progress_bar = ProgressBar(expiration_time)
        self.__progress_bar.start()

    def remove_progress_bar(self) -> None:
        """
        Retire la barre de progression du personage.
        :reutrn: aucun
        """
        self.__current_working_incident = None
        self.__progress_bar.stop()
        self.__progress_bar = None
        self.__locked = False

    @property
    def is_locked(self) -> tuple:
        return self.__locked

    @property
    def current_working_incident(self) -> Incident:
        return self.__current_working_incident

    @property
    def progress_bar(self) -> ProgressBar:
        return self.__progress_bar

    @property
    def feet_position(self) -> tuple:
        return self.__feet_position

    @feet_position.setter
    def feet_position(self, position: tuple) -> None:
        self.__feet_position = position

    @property
    def name(self) -> str:
        return self.__name

    @property
    def speed(self) -> float:
        return self.__speed

    @property
    def icon(self) -> pygame.Surface:
        return resources.characters_icons_collection.get(self.__character_id)

    @property
    def expertise(self) -> pygame.Surface:
        return self.__expertise
