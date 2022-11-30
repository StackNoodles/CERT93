import pygame
import resources


class Tile:
    """ Une tuile. """

    FLOOR = 0
    VOID = -1
    SPECIAL = 16

    def __init__(self, tile_id: int, position: tuple, walkable: bool = False) -> None:
        """
        Initialise une tuile (objet Tile).
        :param tile_id: identifiant servant à récupérer l'image de la tuile dans les ressources
        :param position: position (x, y) de la tuile dans le bureau
        :param walkable: True si les personnages peuvent marcher sur la tuile, False sinon
        """
        self.__action = self.__crack
        self.__tile_id = tile_id
        self.__position = position
        self.__walkable = walkable

    def draw(self, destination: pygame.Surface) -> None:
        """
        Dessine la tuile sur la surface spécifiée.
        :param destination: surface sur laquelle dessiner la tuile
        :return: aucun
        """
        destination.blit(resources.tiles_collection.get(self.__tile_id), self.__position)

    def __crack() -> None:
        """
        Action déclenchée lorsque le personnage marche sur une tuile spéciale.
        """
        print("crack?")

    @property
    def walkable(self) -> bool:
        return self.__walkable

    @walkable.setter
    def walkable(self, is_walkable: bool) -> None:
        self.__walkable = is_walkable