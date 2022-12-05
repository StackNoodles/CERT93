import random
import time
import settings
import resources
from queue import Queue
from threading import Thread, Event

from expertise import Expertise


INCIDENT_TICK = 0.25  # en secondes


class Incident(Thread):
    """ Un incident. """

    def __init__(self, expertise: Expertise, time_to_solve: float) -> None:
        """
        Initialise l'incident.
        :param expertise: type de l'incident (expertise sollicitée)
        :param time_to_solve: temps de résolution permis (en secondes)
        """
        super().__init__()
        self.__percent_25_notif = False
        self.__percent_10_notif = False
        self.__expertise = expertise
        self.__time_to_solve = time_to_solve
        self.__remaining_time = time_to_solve
        self.__25_percent_sound = resources.sounds_collection.get(
            'PERCENT_25_ALERT')
        self.__10_percent_sound = resources.sounds_collection.get(
            'PERCENT_10_ALERT')

        # événement servant à arrêter la tâche (va aussi la réveiller si nécessaire)
        self.__event = Event()

    def run(self) -> None:
        """ Méthode principale exécutée par la tâche d'incident. """
        previous_time = time.time()

        while not self.__event.is_set():
            now = time.time()
            if self.__remaining_time > 0:
                self.__remaining_time -= now - previous_time
                if self.__remaining_time < 0:
                    self.__remaining_time = 0
                elif self.__remaining_time <= (self.__time_to_solve/4) and self.expertise != Expertise.HELPDESK and self.__percent_25_notif is False:
                    self.__25_percent_sound.play()
                    self.__percent_25_notif = True
                elif self.__remaining_time <= (self.__time_to_solve/10) and self.expertise != Expertise.HELPDESK and self.__percent_10_notif is False:
                    self.__10_percent_sound.play()
                    self.__percent_10_notif = True
            previous_time = now

            self.__event.wait(INCIDENT_TICK)

    def stop(self) -> None:
        """ Arrête la tâche d'incident. """
        self.__event.set()

    def get_remaining_time_percentage(self) -> float:
        """
        Récupère le temps qui reste pour résoudre l'incident (en pourcentage).
        :return: pourcentage du temps restant (de 0.0 à 100.0)
        """
        # le pourcentage de résolution est le temps restant sur le temps alloué (x 100 pour une valeur ##.##)
        return self.__remaining_time / self.__time_to_solve * 100

    def has_expired(self) -> bool:
        """
        Vérifie si l'incident est expiré.
        :return: True si l'incident est expiré, False sinon
        """
        return self.__remaining_time == 0

    @property
    def expertise(self) -> Expertise:
        return self.__expertise


class __IncidentSpawner(Thread):
    """ Générateur d'incidents. """

    # __DEFAULT_MIN_TIME_BETWEEN_INDICENTS = 1  # en secondes
    # __DEFAULT_MAX_TIME_BETWEEN_INDICENTS = 30  # en secondes

    # __TIME_BEFORE_FIRST_INCIDENT = 2  # en secondes

    def __init__(self) -> None:
        """ Initialise le générateur d'incidents. """
        super().__init__()

        __max_time_between_indicents = 30
        __min_time_between_incidents = 1
        """Si le temps max par défaut est plus grand que 0 dans les settings et que le temps min par 
        défaut est plus grand que 0 dans les settings et que le temps max est plus grand que le
         temps min alors on attribue aux variables le temps qui se trouve dans les settings"""
        if settings.DEFAULT_MIN_TIME_BETWEEN_INDICENTS > 0 and settings.DEFAULT_MAX_TIME_BETWEEN_INDICENTS > settings.DEFAULT_MIN_TIME_BETWEEN_INDICENTS:
            __max_time_between_indicents = settings.DEFAULT_MAX_TIME_BETWEEN_INDICENTS
            __min_time_between_incidents = settings.DEFAULT_MIN_TIME_BETWEEN_INDICENTS

        self.__queue = Queue()  # queue dans laquelle on place les incidents générés
        # événement servant à arrêter la tâche (va aussi la réveiller si nécessaire)
        self.__event = Event()

        self.__min_time_between = __min_time_between_incidents
        self.__max_time_between = __max_time_between_indicents

        # va créer des incidents seulement si __creating_incidents est True
        self.__creating_incidents = True

    def run(self) -> None:
        __time_before_incident = 2
        """Si le temps avant le premier incident qui se trouve dans les settings est plus grand que 
        0 alors on attribue ce temps à la variable"""
        if settings.TIME_BEFORE_FIRST_INCIDENT > 0:
            __time_before_incident = settings.TIME_BEFORE_FIRST_INCIDENT
        """ Méthode principale exécutée par la tâche du générateur d'incidents. """
        # attendre un certain temps avant de générer le premier incident
        self.__create_and_send_next_incident(
            __time_before_incident, __time_before_incident + 2)

        # tant que la tâche exécute, on génère des événements
        while not self.__event.is_set():
            self.__create_and_send_next_incident(
                self.__min_time_between, self.__max_time_between)

    def pause(self) -> None:
        """ Pause la génération d'incidents. """
        self.__creating_incidents = False

    def unpause(self) -> None:
        """ Relance la génération d'incidents. """
        self.__creating_incidents = True

    def stop(self) -> None:
        """ Arrête le générateur d'incidents. """
        self.__event.set()

    def get(self) -> list:
        """
        Récupère tous les incidents se trouvant dans la queue d'incidents.
        :return: liste contenant les incidents récupérés
        """
        incidents = []

        if not self.__event.is_set():
            while not self.__queue.empty():
                incidents.append(self.__queue.get())

        return incidents

    def put(self, incident: Incident) -> None:
        """
        Place un incident dans la queue d'incidents.
        :param incident: incident à placer dans la queue
        :return: aucun
        """
        if not self.__event.is_set():
            self.__queue.put(incident)

    def __create_and_send_next_incident(self, min_delay: int, max_delay: int) -> None:
        """
        Crée et envoie le prochain incident.
        :param min_delay: délai minimum à respecter avant de créer l'incident
        :param max_delay: délai maximal pour créer l'incident
        :return: aucun
        """
        # Calcul du délai avant la production du prochain incident, puis attente
        time_to_indicent = random.randint(min_delay, max_delay)
        self.__event.wait(time_to_indicent)

        if self.__creating_incidents:
            # Création d'un incident pour le centre d'appels (tous les incidents entrent par le centre d'appels)
            time_to_solve = random.randint(
                settings.HELPDESK_MIN_SOLVING_TIME, settings.HELPDESK_MAX_SOLVING_TIME)
            incident = Incident(Expertise.HELPDESK, time_to_solve)

            # Envoi de l'incident sur la queue d'incidents
            self.__queue.put(incident)


# générateur d'incidents (singleton du GoF implémenté avec un Global Object Pattern de python)
spawner = None


def init() -> None:
    """ Initialise le spawner, mais ne le démarre pas. """

    global spawner
    if not spawner:
        spawner = __IncidentSpawner()
