import random
import time

import settings

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

        self.__expertise = expertise
        self.__time_to_solve = time_to_solve
        self.__remaining_time = time_to_solve

        self.__event = Event()  # événement servant à arrêter la tâche (va aussi la réveiller si nécessaire)

    def run(self) -> None:
        """ Méthode principale exécutée par la tâche d'incident. """
        previous_time = time.time()

        while not self.__event.is_set():
            now = time.time()
            if self.__remaining_time > 0:
                self.__remaining_time -= now - previous_time
                if self.__remaining_time < 0:
                    self.__remaining_time = 0
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
    __DEFAULT_MIN_TIME_BETWEEN_INDICENTS = 1  # en secondes
    __DEFAULT_MAX_TIME_BETWEEN_INDICENTS = 30  # en secondes

    __TIME_BEFORE_FIRST_INCIDENT = 2  # en secondes

    def __init__(self) -> None:
        """ Initialise le générateur d'incidents. """
        super().__init__()

        self.__queue = Queue()  # queue dans laquelle on place les incidents générés
        self.__event = Event()  # événement servant à arrêter la tâche (va aussi la réveiller si nécessaire)

        self.__min_time_between = self.__DEFAULT_MIN_TIME_BETWEEN_INDICENTS
        self.__max_time_between = self.__DEFAULT_MAX_TIME_BETWEEN_INDICENTS

        self.__creating_incidents = True  # va créer des incidents seulement si __creating_incidents est True

    def run(self) -> None:
        """ Méthode principale exécutée par la tâche du générateur d'incidents. """
        # attendre un certain temps avant de générer le premier incident
        self.__create_and_send_next_incident(self.__TIME_BEFORE_FIRST_INCIDENT, self.__TIME_BEFORE_FIRST_INCIDENT + 2)

        # tant que la tâche exécute, on génère des événements
        while not self.__event.is_set():
            self.__create_and_send_next_incident(self.__min_time_between, self.__max_time_between)

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
            time_to_solve = random.randint(settings.HELPDESK_MIN_SOLVING_TIME, settings.HELPDESK_MAX_SOLVING_TIME)
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
