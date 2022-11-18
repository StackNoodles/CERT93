import pygame

from office import Office


class View:
    """ Vue sur le bureau. """
    WIDTH_ONE_PLAYER = 1200
    WIDTH_TWO_PLAYERS = 590
    HEIGHT = 590

    def __init__(self, screen: pygame.Surface,
                 office: Office,
                 view_width: int,
                 view_height: int) -> None:
        """
        Initialise une vue (instance de View).
        :param screen: Surface écran de pygame
        :param office: Le bureau observé à travers la vue
        :param view_width: Largeur de la vue (en pixels)
        :param view_height: Hauteur de la vue (en pixels)
        """
        self.__screen = screen
        self.__view_width = view_width
        self.__view_height = view_height

        self.__office = office

        office_surface = office.get_image()
        self.__office_width = office_surface.get_width()
        self.__office_height = office_surface.get_height()

        padded_width = (2 * screen.get_width()) + self.__office_width
        padded_height = (2 * screen.get_height()) + self.__office_height
        self.__padded_office_surface = pygame.Surface((padded_width, padded_height), depth=32)

        # Positionnement par défaut au centre du bureau
        center_x, center_y = self.__office_width / 2, self.__office_height / 2
        self.__center_in_office = center_x, center_y

        self.__office_rect = self.__center_to_rect(center_x, center_y)

        # Positionnement par défaut au centre de l'écran
        self.__screen_rect = self.__center_to_rect(screen.get_width() / 2, screen.get_height() / 2)

    def __center_to_rect(self, x: float, y: float) -> pygame.Rect:
        """
        Retourne un rectangle correspondant aux dimensions de la vue centrée sur (x,y).
        :param x: centre horizontal
        :param y: centre vertical
        :return: rectangle
        """
        left = x - (self.__view_width / 2)
        top = y - (self.__view_height / 2)

        return pygame.Rect(left, top, self.__view_width, self.__view_height)

    def center_in_office(self, pixel_center: tuple) -> None:
        """
        Centre la vue dans le bureau (zone du bureau que la vue présente).
        :param pixel_center: centre de la zone à voir/présenter (coordonnée en pixels)
        :return: aucun
        """
        x, y = pixel_center
        self.__office_rect = self.__center_to_rect(x, y)

    def center_on_screen(self, x: float, y: float) -> None:
        """
        Centre la vue sur l'écran (endroit où positionner la vue sur l'écran).
        :param x: position horizontale où placer le centre de la vue
        :param y: position verticale où placer le centre de la vue
        :return: aucun
        """
        self.__screen_rect = self.__center_to_rect(x, y)

    def draw(self) -> None:
        """ Dessine la vue à l'écran. """
        # nettoyage de la surface d'extraction
        self.__padded_office_surface.fill((0, 0, 0))

        # "ajout" des marges noires autour du bureau
        self.__padded_office_surface.blit(self.__office.get_image(),
                                          (self.__screen.get_width(), self.__screen.get_height()))

        # calcul de la zone à extraire
        top = self.__office_rect.top + self.__screen.get_height()
        left = self.__office_rect.left + self.__screen.get_width()
        width = self.__view_width
        height = self.__view_height
        area = pygame.Rect(left, top, width, height)

        # extraction de la vue
        self.__screen.blit(self.__padded_office_surface, self.__screen_rect, area)

        # rectangle autour de la vue
        pygame.draw.rect(self.__screen, (255, 255, 255), self.__screen_rect, 2)

    def resize(self, width: int, height: int) -> None:
        """
        Modifie les dimensions de la vue. Repositionne également la vue en fonction de ces nouvelles dimensions.
        :param width: nouvelle largeur
        :param height: nouvelle hauteur
        :return: aucun
        """
        self.__view_width = width
        self.__view_height = height

        # repositionnement dans le bureau (enregistrement du rectangle décrivant la zone)
        cx = self.__office_rect.x + (self.__office_rect.width / 2)
        cy = self.__office_rect.y + (self.__office_rect.height / 2)
        self.center_in_office((cx, cy))

        # repositionnement à l'écran (enregistrement du rectangle décrivant la zone)
        cx = self.__screen_rect.x + (self.__screen_rect.width / 2)
        cy = self.__screen_rect.y + (self.__screen_rect.height / 2)
        self.center_on_screen(cx, cy)

    @property
    def screen_rect(self) -> pygame.Rect:
        return self.__screen_rect
