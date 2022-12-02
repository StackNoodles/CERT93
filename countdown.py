import pygame
import settings
import time
import datetime
from threading import Thread, Event

DEFAULT_FONT_SIZE = 20

TIME_PER_LEVEL = settings.TIME_PER_LEVEL


class Countdown(Thread):
    """ Trames par seconde (minuteur - Countdown). """

    def __init__(self) -> None:
        """
        Initialise une instance de Countdown. Un objet Countdowm permet permet d'avoir un minuteur en second.
        """
        super().__init__()

        self.__time = TIME_PER_LEVEL

        default_font_name = pygame.font.get_default_font()
        self.__font = pygame.font.Font(default_font_name, DEFAULT_FONT_SIZE)

        self.__surface = None

        # événement servant à arrêter la tâche (va aussi la réveiller si nécessaire)
        self.__event = Event()

    def timeout(self) -> bool:
        if self.__time <= 0:
            return True
        return False
    def reset_timer(self):
        self.__time = settings.TIME_PER_LEVEL
    def get(self) -> pygame.Surface:
        """
        Retourne une surface pour l'affichage du minuteur.
        :return: la surface qui contient le texte (Countdown)
        """
        countdown_str = f"Time remaining = {self.__time}"
        return self.__font.render(countdown_str, True, (255, 255, 255))

    def run(self) -> None:
        """ Tâche de compilation du Countdown. """

        while not self.__event.is_set():
            self.__event.wait(1)
            self.__time -= 1  # sauvegarde le FPS obtenu pour la dernière seconde écoulée

    def stop(self) -> None:
        """ Arrête la tâche Countdown. """
        self.__event.set()
