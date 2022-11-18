import pygame

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

        # Conversion de la position d'une coordonnée en tuile vers une coordonnée en pixels
        x, y = resources.tiles_collection.tile_pos_to_pixel_pos(tile_position)
        tile_width, tile_height = resources.tiles_collection.tile_size()
        self.__feet_position = x + (tile_width / 2), y + tile_height

    def draw(self, destination: pygame.Surface) -> None:
        """
        Dessine le personnage.
        :param destination: surface sur laquelle dessiner le personnage
        :return: aucun
        """
        image = resources.characters_collection.get(self.__character_id)
        x = self.__feet_position[0] - (image.get_width() / 2)
        y = self.__feet_position[1] - image.get_height()

        destination.blit(image, (x, y))

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
