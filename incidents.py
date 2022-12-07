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

        self.__is_paused = False

    def run(self) -> None:
        """ Méthode principale exécutée par la tâche d'incident. """

        previous_time = time.time()

        while not self.__event.is_set():
            now = time.time()
            if self.__remaining_time > 0 and not self.__is_paused:
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

    def pause(self) -> None:
        """ Pause la tâche. """
        self.__is_paused = True

    def unpause(self) -> None:
        """ Relance la tâche. """
        self.__is_paused = False

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
    
    @property
    def duration(self) -> Expertise:
        return self.__time_to_solve
    
    @property
    def is_paused(self) -> bool:
        return self.__is_paused


class __IncidentSpawner(Thread):
    """ Générateur d'incidents. """

    def __init__(self) -> None:
        """ Initialise le générateur d'incidents. """
        super().__init__()
        
        self.__remaining_time = settings.TIME_PER_LEVEL
        self.__ticks = 0
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
        self.__multiplier = 1
        self.__next_event_time = 2
        self.__min_time_between = __min_time_between_incidents
        self.__max_time_between = __max_time_between_indicents

        # va créer des incidents seulement si __creating_incidents est True
        self.__creating_incidents = True

    def get_first_event_time(self) -> int:
        __time_before_first_incident = 2
        """Si le temps avant le premier incident qui se trouve dans les settings est plus grand que 
        0 alors on attribue ce temps à la variable"""
        if settings.TIME_BEFORE_FIRST_INCIDENT > 0:
           __time_before_first_incident = settings.TIME_BEFORE_FIRST_INCIDENT
        return __time_before_first_incident

    def run(self) -> None:
        

        """ Méthode principale exécutée par la tâche du générateur d'incidents. """
        self.__next_event_time = self.get_first_event_time()

        # tant que la tâche exécute, on génère des événements
        while not self.__event.is_set():
                if self.__ticks >= self.__next_event_time:
                    self.__create_and_send_next_incident()
                    self.__next_event_time = self.__ticks + (self.__multiplier*random.randint(self.__min_time_between, self.__max_time_between))
                self.__event.wait(1)
                self.__ticks += 1
                self.__remaining_time -= 1
                self.__multiplier = 0.5+((self.__remaining_time/settings.TIME_PER_LEVEL)/2)

    def pause(self) -> None:
        """ Pause la génération d'incidents. """
        self.__creating_incidents = False

    def reset(self) -> None:
        self.__remaining_time = settings.TIME_PER_LEVEL
        self.__multiplier = 1
        self.__ticks = 0
        self.__next_event_time = self.get_first_event_time()

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
    
    def __create_and_send_next_incident(self) -> None:
        """
        Crée et envoie le prochain incident.
        """

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
