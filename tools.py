# Outils génériques utilisés par l'application
import math


def find_distance(point_one: tuple, point_two: tuple) -> float:
    """
    Retourne la distance (en pixels) entre deux points.
    :param point_one: premier point
    :param point_two: deuxième point
    :return: la distance entre les deux points
    """
    one_x, one_y = point_one
    two_x, two_y = point_two
    return math.sqrt(((one_x - two_x) ** 2) + ((one_y - two_y) ** 2))
