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

        self.__ambience_sound = resources.sounds_collection.get('OFFICE-AMBIENCE')
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

        self.__floor_and_walls = [[Tile(Tile.VOID, (0, 0)) for _ in range(height)] for _ in range(width)]

        tile = resources.tiles_collection.get(0)
        self.__tile_size = tile.get_width()

        surface = pygame.Surface((width * self.__tile_size, height * self.__tile_size))

        __DELTAS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (0, 0)]

        for y in range(height):
            for x in range(width):
                tile_id = floor_and_walls[x][y]
                if tile_id >= Tile.FLOOR:
                    pos_x = x * self.__tile_size
                    pos_y = y * self.__tile_size
                    self.__floor_and_walls[x][y] = Tile(tile_id, (pos_x, pos_y))
                    if tile_id == Tile.FLOOR:
                        self.__floor_and_walls[x][y].walkable = True

                    isBorder = False
                    outline = [[-1 for _ in range(3)]for _ in range(3)]
                    mask = [
                        [0, 0, 0],
                        [0, 0, 0],
                        [0, 0, 0]
                    ]
                    for delta in __DELTAS:
                        try:
                            outline[delta[0] + 1][delta[1] + 1] = floor_and_walls[x + delta[0]][y + delta[1]] if x + delta[0] > -1 and y + delta[1] > -1 else -1
                        except IndexError:
                            outline[delta[0] + 1][delta[1] + 1] = -1
                    
                    # print(str(outline[0][0]) + ", " + str(outline[1][0]) + ", " + str(outline[2][0]) + "\n" + str(outline[0][1]) + ", " + str(outline[1][1]) + ", " + str(outline[2][1]) + "\n"+ str(outline[2][2]) + ", " + str(outline[0][2]) + ", " + str(outline[1][2])+ "\n")

                    nombreVides = 0
                    for i in range(len(outline)):
                        for j in range(len(outline[i])):
                            if outline[i][j] == -1 :
                                nombreVides += 1

                    # if nombreVides == 3:
                    #     tile = resources.tiles_collection.get(5)
                    #     surface.blit(tile, (pos_x, pos_y))
                    # elif nombreVides == 5:
                    #     tile = resources.tiles_collection.get(6)
                    #     surface.blit(tile, (pos_x, pos_y))
                    # else:
                    
                    if tile := resources.tiles_collection.get(tile_id):
                        surface.blit(tile, (pos_x, pos_y))

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

    def get_image(self) -> pygame.Surface:
        """
        Retourne l'image du bureau incluant les actifs et les personnages.
        :return: surface représentant une image du bureau
        """

        combined = self.__surface.copy()

        for asset in self.__assets.values():
            asset.draw(combined)

        for character in self.__characters.values():
            character.draw(combined)

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
