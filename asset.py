import math

import pygame
import queue
from queue import Queue
from typing import Callable

import resources
import settings
from incidents import Incident


class Asset:
    """ Actif (personne ou appareil). """

    def __init__(self, name: str, asset_id: int, tile_position: tuple) -> None:
        """
        Initialise une instance d'Asset.
        :param name: nom de l'actif
        :param asset_id: identifiant d'actif (sert à récupérer la bonne image)
        :param tile_position: position (x, y) de la tuile dans le bureau
        """
        self._name = name
        self._asset_id = asset_id
        self._tile_position = tile_position

        # Conversion de la position : d'une coordonnée en tuile vers une coordonnée en pixels
        self._position = resources.tiles_collection.tile_pos_to_pixel_pos(tile_position)

        # Coordonnée du centre de l'actif (en pixels) - pour le calcul des distances
        self._center_position = resources.tiles_collection.tile_pos_to_center_pixel_pos(tile_position)

        self._incidents = Queue()
        self._active_incident = None

        self._incoming_action = None  # action à faire lorsqu'un incident arrive pour cet actif en particulier
        self._expiring_action = None  # action à faire lorsqu'un incident expire pour cet actif en particulier
        self._solving_action = None  # action à faire lorsqu'un incident est résolu pour cet actif en particulier

        self._fail_sound = resources.sounds_collection.get('INCIDENT-FAIL')
        self._solve_sound = resources.sounds_collection.get('INCIDENT-SOLVE')

        self._incident_image = None
        self._timer_id = 0

    def add_incident(self, incident: Incident) -> None:
        """
        Ajoute un incident à la queue d'incidents pour cet actif.
        :param incident: l'incident à ajouter
        :return: aucun
        """
        self._incidents.put(incident)

    def solve_incident(self) -> None:
        """
        Solutionne l'incident (s'il y a lieu) affectant cet actif.
        :return: aucun
        """
        if self._active_incident:
            if self._solving_action:
                self._play_solve_sound()
                remaining_percentage = self._active_incident.get_remaining_time_percentage()
                self._solving_action(math.floor(remaining_percentage))
            self._active_incident.stop()
            self._active_incident = None

    def draw(self, destination: pygame.Surface) -> None:
        """
        Dessine l'actif (et l'incident qui l'affecte s'il y en a un).
        :param destination: surface sur laquelle dessiner l'actif
        :return: aucun
        """
        # Dessin de l'actif
        asset_surface = resources.assets_collection.get(self._asset_id)
        destination.blit(asset_surface, self._position)

        # Dessin de l'incident, s'il y a lieu
        if self._active_incident:
            incident_type = self._active_incident.expertise
            incident_surface = resources.incidents_collection.get(self._timer_id, incident_type)
            offset = (asset_surface.get_width() - incident_surface.get_width()) / 2
            x, y = self._position
            position = x + offset, y + offset
            destination.blit(incident_surface, position)

    def set_incoming_action(self, action: Callable) -> None:
        """
        Assigne l'action à accomplir lorsqu'un incident arrive.
        :param action: action à accomplir (nom de la fonction à appeler)
        :return: aucun
        """
        self._incoming_action = action

    def set_expiring_action(self, action: Callable) -> None:
        """
        Assigne l'action à accomplir lorsqu'un incident expire.
        :param action: action à accomplir (nom de la fonction à appeler)
        :return: aucun
        """
        self._expiring_action = action

    def set_solving_action(self, action: Callable) -> None:
        """
        Assigne l'action à accomplir lorsqu'un incident est résolu.
        :param action: action à accomplir (nom de la fonction à appeler)
        :return: aucun
        """
        self._solving_action = action

    def stop_and_remove_all_incidents(self) -> None:
        """
        Arrête et supprime tous les incidents associés à l'actif.
        :return: aucun
        """
        # Retrait (suppression) de tous les incidents en attente
        while not self._incidents.empty():
            self._incidents.get()
        # Arrêt et suppression de l'incident en cours, s'il y a lieu
        if self._active_incident:
            self._active_incident.stop()
            self._active_incident = None

    def update(self):
        """
        Met à jour l'actif.
        Si l'actif n'est pas affecté par un incident, vérifie si un incident est en attente. Si un incident est en
        attente, récupère cet indicent et l'active.
        Si l'actif est affecté par un incident, met à jour l'indicateur de minuterie et vérifie si l'incident est
        expiré. Si l'incident est expiré, prend action et supprime l'incident en cours.
        :return: aucun
        """
        if not self._active_incident:
            if not self._incidents.empty():
                try:
                    self._active_incident = self._incidents.get(block=False)
                except queue.Empty:
                    # aucune gestion d'exception nécessaire ici
                    return

                self._active_incident.start()
                self._timer_id = Asset.compute_timer_id(self._active_incident)
                if self._incoming_action:
                    self._incoming_action()
        else:
            self._timer_id = Asset.compute_timer_id(self._active_incident)
            if self._active_incident.has_expired():
                self._play_fail_sound()
                if self._expiring_action:
                    self._expiring_action()
                self._active_incident.stop()
                self._active_incident = None

    @staticmethod
    def compute_timer_id(incident: Incident) -> int:
        """
        Calcule l'index de l'image de minuterie qui correspond au pourcentage de temps restant.
        :param incident: l'incident pour lequel on calcule l'index
        :return: l'index de minuterie (timer_id)
        """
        percentage = incident.get_remaining_time_percentage()
        time_slice = math.ceil(percentage / settings.TIMER_PERCENTAGE_SLICE_SIZE)
        timer_id = (settings.NB_INCIDENT_TIMER_IMAGES - 1) - time_slice
        return timer_id

    def _play_fail_sound(self) -> None:
        """ Joue le son qui indique que l'incident a expiré sans avoir été résolu. """
        self._fail_sound.play()

    def _play_solve_sound(self) -> None:
        """ Joue le son qui indique que l'incident a été résolu. """
        self._solve_sound.play()

    @property
    def center_position(self) -> tuple:
        return self._center_position

    @property
    def name(self) -> str:
        return self._name

    @property
    def tile_position(self) -> tuple:
        return self._tile_position
