import pygame
import resources
import settings

from asset import Asset
from character import Character
from tile import Tile


class Office:
    """ Le bureau. """

    def __init__(self) -> None:
        """
        Initialise une instance de bureau (objet Office).
        """
        self.__floor_and_walls = None
        self.__surface = None
        self.__tile_size = None

        self.__ambience_sound = resources.sounds_collection.get(
            'OFFICE-AMBIENCE')
        self.__ambience_enabled = False

        self.__assets = {}
        self.__characters = {}

    def build(self, floor_and_walls: list) -> None:
        """
        Construit le bureau (agencement de tuiles) à partir de la grille fournie (floor_and_walls).
        :param floor_and_walls: grille contenant les identifiants de tuiles à utiliser
        :return: aucun
        """
        # Créer l'ensemble des tuiles représentant la structure du bureau ainsi que la surface (l'image)
        # statique du bureau (plancher et murs)
        width = len(floor_and_walls)
        height = len(floor_and_walls[0])

        self.__floor_and_walls = [
            [Tile(Tile.VOID, (0, 0)) for _ in range(height)] for _ in range(width)]

        tile = resources.tiles_collection.get(0)
        self.__tile_size = tile.get_width()

        surface = pygame.Surface(
            (width * self.__tile_size, height * self.__tile_size))

        __DELTAS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0),
                    (-1, -1), (0, -1), (1, -1), (0, 0)]
        __BORDER_WIDTH = 5

        for y in range(height):
            for x in range(width):
                tile_id = floor_and_walls[x][y]

                if tile_id < Tile.FLOOR:
                    continue

                pos_x = x * self.__tile_size
                pos_y = y * self.__tile_size

                self.__floor_and_walls[x][y] = Tile(
                    tile_id, (pos_x, pos_y))

                # On veut afficher une tuile speciale comme une tuile classique de sol.
                if tile_id == Tile.SPECIAL:
                    tile_id = Tile.FLOOR

                if tile_id == Tile.FLOOR:
                    self.__floor_and_walls[x][y].walkable = True

                if not (tile := resources.tiles_collection.get(tile_id).copy()):
                    continue

                # Cropping
                # Recuperation de la matrice autour de la case (9*9)
                outline = [[-1 for _ in range(3)]for _ in range(3)]
                for delta in __DELTAS:
                    # On met -1 si on sort des bords de la liste
                    try:
                        outline[delta[0] + 1][delta[1] + 1] = floor_and_walls[x + delta[0]][y + delta[1]
                                                                                            ] if x + delta[0] > -1 and y + delta[1] > -1 else -1
                    except IndexError:
                        outline[delta[0] + 1][delta[1] + 1] = -1

                # Bords adjacents à un vide (et angles exterieurs par extension)
                # Gauche
                if outline[0][1] == -1:
                    for k in range(__BORDER_WIDTH):
                        for l in range(self.__tile_size):
                            tile.set_at((k, l), 0)
                # Haut
                if outline[1][0] == -1:
                    for k in range(self.__tile_size):
                        for l in range(__BORDER_WIDTH):
                            tile.set_at((k, l), 0)
                # Droite
                if outline[2][1] == -1:
                    # On ajoute 1 pour atteindre le max
                    for k in range(__BORDER_WIDTH + 1):
                        for l in range(self.__tile_size):
                            tile.set_at((self.__tile_size - k, l), 0)
                # Bas
                if outline[1][2] == -1:
                    for k in range(self.__tile_size):
                        for l in range(__BORDER_WIDTH + 1):
                            tile.set_at((k, self.__tile_size - l), 0)

                # Angles interieurs
                # Haut Gauche
                if outline[0][0] == -1:
                    for k in range(__BORDER_WIDTH):
                        for l in range(__BORDER_WIDTH):
                            tile.set_at((k, l), 0)
                # Haut Droite
                if outline[0][2] == -1:
                    for k in range(__BORDER_WIDTH):
                        for l in range(__BORDER_WIDTH + 1):
                            tile.set_at((k, self.__tile_size - l), 0)
                # Bas Gauche
                if outline[2][0] == -1:
                    for k in range(__BORDER_WIDTH + 1):
                        for l in range(__BORDER_WIDTH):
                            tile.set_at((self.__tile_size - k, l), 0)
                # Bas Droite
                if outline[2][2] == -1:
                    for k in range(__BORDER_WIDTH + 1):
                        for l in range(__BORDER_WIDTH + 1):
                            tile.set_at(
                                (self.__tile_size - k, self.__tile_size - l), 0)

                # On place la tuile
                surface.blit(tile, (pos_x, pos_y),
                             (0, 0, self.__tile_size, self.__tile_size))

        self.__surface = surface

    def add_asset(self, asset: Asset) -> None:
        """
        Ajoute un actif au bureau.
        :param asset: l'actif à ajouter
        :return: aucun
        """
        self.__assets[asset.name] = asset

        # Configuration de la tuile sous-jacente pour qu'elle devienne un obstacle
        x, y = asset.tile_position
        tile = self.__floor_and_walls[x][y]
        tile.walkable = False

    def add_character(self, character: Character) -> None:
        """
        Ajoute un personnage au bureau.
        :param character: le personnage à ajouter
        :return: aucun
        """
        self.__characters[character.name] = character

    def disable_ambience(self) -> None:
        """ Désactive les éléments d'ambience du bureau. """
        if self.__ambience_enabled:
            self.__ambience_sound.fadeout(1)
            self.__ambience_enabled = False

    def enable_ambience(self) -> None:
        """ Active les éléments d'ambience du bureau. """
        if not self.__ambience_enabled:
            self.__ambience_sound.play(-1)
            self.__ambience_enabled = True

    def get_image(self, display_name) -> pygame.Surface:
        """
        Retourne l'image du bureau incluant les actifs et les personnages.
        :return: surface représentant une image du bureau
        """

        combined = self.__surface.copy()

        for asset in self.__assets.values():
            asset.draw(combined, display_name)

        for character in self.__characters.values():
            character.draw(combined, display_name)

        return combined

    def in_navmesh(self, point: tuple) -> bool:
        """
        Vérifie si un point donné (point) se trouve sur une tuile sur laquelle il est possible de marcher.
        :param point: coordonnée (x, y) en pixels à vérifier
        :return:
        """
        tile_x = int(point[0] // self.__tile_size)
        tile_y = int(point[1] // self.__tile_size)

        return self.__floor_and_walls[tile_x][tile_y].walkable

    def get_tile(self, point: tuple) -> Tile:
        """
        Vérifie si un point donné (point) se trouve sur une tuile sur laquelle il est possible de marcher.
        :param point: coordonnée (x, y) en pixels à vérifier
        :return:
        """
        tile_x = int(point[0] // self.__tile_size)
        tile_y = int(point[1] // self.__tile_size)

        return self.__floor_and_walls[tile_x][tile_y]
