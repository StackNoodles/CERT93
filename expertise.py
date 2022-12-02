from enum import IntEnum


class Expertise(IntEnum):
    """ Expertise d'un personnage ou sollicitée par un incident. Attention: les valeurs sont importantes. """
    HELPDESK = 0
    SERVER = 1
    MANAGEMENT = 2
    NETWORKING = 3
    DATABASE = 4
    PROGRAMMING = 5
    DESKTOP = 6
    SUPERHERO = 7