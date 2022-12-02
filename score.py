import pygame


DEFAULT_FONT_SIZE = 20


class Score:
    """ Score du ou des joueur(s) pour la partie en cours. """

    def __init__(self) -> None:
        """ Initialise une instance de score (objet Score). """
        self.__points = 0

        default_font_name = pygame.font.get_default_font()
        self.__font = pygame.font.Font(default_font_name, DEFAULT_FONT_SIZE)

        # surface qui contient le score en format graphique
        self.__surface = self.__build_score_surface()

    def add_points(self, points: int) -> None:
        """
        Ajoute des points au score.
        :param points: points à ajouter
        :return: aucun
        """
        self.__points += points
        self.__surface = self.__build_score_surface()

    def draw(self, destination: pygame.Surface, center_position: tuple) -> None:
        """
        Dessine le score sur la surface spécifiée (destination) à la position donnée (center_position).
        :param destination: surface sur laquelle dessiner le score
        :param center_position: position (x, y) où centrer l'affichage du score
        :return: aucun
        """
        center_x, center_y = center_position
        score_width, score_height = self.__surface.get_size()
        x = center_x - (score_width / 2)
        y = center_y - (score_height / 2)
        destination.blit(self.__surface, (x, y))

    def __build_score_surface(self) -> pygame.Surface:
        """
        Construit la surface graphique du score à partir de la valeur numérique stockée.
        :return: surface contenant le score à afficher
        """
        score_str = f'SCORE: {self.__points}'
        return self.__font.render(score_str, True, (255, 255, 255))
