import pygame

DEFAULT_FONT_SIZE = 20


class Score:
    """ Score du ou des joueur(s) pour la partie en cours. """

    def __init__(self) -> None:
        """ Initialise une instance de score (objet Score). """
        self.__points = 0

    def add_points(self, points: int) -> None:
        """
        Ajoute des points au score.
        :param points: points à ajouter
        :return: aucun
        """
        self.__points += points

    def get_score_display(self) -> str:
        """
        Construit la surface graphique du score à partir de la valeur numérique stockée.
        :return: surface contenant le score à afficher
        """
        return f'SCORE: {self.__points}'

    def get_score(self) -> int:
        return self.__points
