import math
import random

import resources
import settings

from asset import Asset
import incidents
from incidents import Incident, Expertise


class Helpdesk(Asset):
    """ Le centre d'appels (helpdesk). """

    def __init__(self, tile_position: tuple) -> None:
        """
        Initialise une instance du centre d'appels (objet Helpdesk) et le positionne dans le bureau.
        :param tile_position: position de tuile (x, y) dans le bureau
        """
        super().__init__('Helpdesk', settings.HELPDESK_ASSET_ID, tile_position)

        # contient la liste des expertises sollicitées par les incidents créés par le centre d'appels
        self.__incident_types = list(Expertise)
        # on ne crée pas d'incidents qui demandent une expertise de superhéro - à (presque) l'impossible nul n'est tenu
        self.__incident_types.remove(Expertise.SUPERHERO)
        # on ne crée pas non plus d'incidents pour le centre d'appels - il faut quand même s'aider...
        self.__incident_types.remove(Expertise.HELPDESK)

        self.__phone_sound = resources.sounds_collection.get('HELPDESK-PHONE-RING')
        self._solve_sound = resources.sounds_collection.get('HELPDESK-PHONE-HANGUP')

        # on veut que le téléphone sonne lorsqu'un incident arrive au centre d'appels
        self.set_incoming_action(self._ring_the_phone)

        # on veut que le téléphone cesse de sonner si la personne raccroche (incident expiré)
        self.set_expiring_action(self._stop_the_phone)

    def solve_incident(self) -> None:
        """
        Rédéfinition de Asset:solve_incident().
        Solutionne un incident du centre d'appels (helpdesk).
        :return: aucun
        """
        if self._active_incident:
            if self._solving_action:
                self._play_solve_sound()
                remaining_percentage = self._active_incident.get_remaining_time_percentage()
                self._solving_action(math.floor(remaining_percentage))
            self._stop_the_phone()
            self._active_incident.stop()
            self._active_incident = None

            # Redistribution de l'incident vers un actif autre que le centre d'appels
            # en le renvoyant à travers le spawner
            incident_type = random.choice(self.__incident_types)
            time_to_solve = random.randint(60, 300)
            incident = Incident(incident_type, time_to_solve)
            incidents.spawner.put(incident)

    def _ring_the_phone(self) -> None:
        """
        Joue la sonnerie du téléphone.
        :return: aucun
        """
        # si la sonnerie n'est pas déjà en train de joueur... (le téléphone n'a qu'une sonnerie)
        if self.__phone_sound.get_num_channels() == 0:
            self.__phone_sound.play(-1)

    def _stop_the_phone(self) -> None:
        """
        Arrête la sonnerie du téléphone.
        :return: aucun
        """
        self.__phone_sound.stop()
