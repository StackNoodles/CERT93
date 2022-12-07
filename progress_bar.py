import math
import pygame
import settings
import time
import datetime
from threading import Thread, Event

PROGRESS_TICK = 0.25  # en secondes

class ProgressBar(Thread):
    """ Barre de progression de resolution d'un incident. """

    def __init__(self, time_to_solve: float) -> None:
        """
        Initialise la barre.
        :param time_to_solve: temps de résolution (en secondes)
        """
        super().__init__()
        self.__time_to_solve = time_to_solve
        self.__remaining_time = time_to_solve

        # événement servant à arrêter la tâche (va aussi la réveiller si nécessaire)
        self.__event = Event()

        self.__is_paused = False

    def pause(self):
        self.__is_pause = True

    def unpause(self):
        self.__is_pause = False

    def get(self) -> pygame.Surface:
        """
        Retourne une surface pour l'affichage de la barre.
        :return: la surface qui contient l'image'
        """
        return 

    def run(self) -> None:
        """ Méthode principale exécutée par la tâche de resolution. """

        previous_time = time.time()

        while not self.__event.is_set():
            now = time.time()
            if self.__remaining_time > 0 and not self.__is_paused:
                self.__remaining_time -= now - previous_time
                if self.__remaining_time < 0:
                    self.__remaining_time = 0
            previous_time = now

            self.__event.wait(PROGRESS_TICK)

    def get_remaining_time_percentage(self) -> float:
        """
        Récupère le temps qui reste (en pourcentage).
        :return: pourcentage du temps restant (de 0.0 à 100.0)
        """
        # le pourcentage de résolution est le temps restant sur le temps alloué (x 100 pour une valeur ##.##)
        return self.__remaining_time / self.__time_to_solve * 100
    
    def stop(self) -> None:
        """ Arrête la tâche Countdown. """
        self.__event.set()
        
@staticmethod
def compute_progress_bar_id(progress_bar: ProgressBar) -> int:
    """
    Calcule l'index de l'image de la barre qui correspond au pourcentage de temps restant.
    :param progress_bar: la barre pour laquelle on calcule l'index
    :return: l'index de barre (progress_bar_id)
    """
    percentage = progress_bar.get_remaining_time_percentage()
    time_slice = math.ceil(
        percentage / settings.TIMER_PERCENTAGE_SLICE_SIZE)
    progress_bar_id = (settings.NB_INCIDENT_TIMER_IMAGES - 1) - time_slice
    return progress_bar_id
