import pygame
import time

from pygame.locals import JOYDEVICEADDED, JOYDEVICEREMOVED, JOYBUTTONUP, JOYBUTTONDOWN, JOYAXISMOTION

import settings


class PlayerInput:
    """ Entrées pour un joueur. """

    def __init__(self) -> None:
        self.__movement = (0.0, 0.0)  # mouvement sur l'axe horizontal (x) et sur l'axe vertical (y)
        self.__focus_next_button = False
        self.__focus_prev_button = False
        self.__solve_button = False

        self.__last_activity_time = time.time() - settings.INACTIVITY_THRESHOLD  # sert à détecter de l'activité

    def touch(self) -> None:
        """ Touche les entrées du joueur pour indiquer qu'il y a de l'activité. """
        self.__last_activity_time = time.time()

    @property
    def last_activity_time(self) -> float:
        return self.__last_activity_time

    @property
    def movement(self) -> tuple:
        return self.__movement

    @movement.setter
    def movement(self, new_movement: tuple) -> None:
        self.__movement = new_movement
        self.touch()

    @property
    def focus_next_button(self) -> bool:
        return self.__focus_next_button

    @focus_next_button.setter
    def focus_next_button(self, value: bool) -> None:
        self.__focus_next_button = value
        self.touch()

    @property
    def focus_prev_button(self) -> bool:
        return self.__focus_prev_button

    @focus_prev_button.setter
    def focus_prev_button(self, value: bool) -> None:
        self.__focus_prev_button = value
        self.touch()

    @property
    def solve_button(self) -> bool:
        return self.__solve_button

    @solve_button.setter
    def solve_button(self, value: bool) -> None:
        self.__solve_button = value
        self.touch()


class __InputManager:
    """ Gestionnaire d'entrée (clavier ou gamepads). """

    __PLAYER_ONE = 0
    __PLAYER_TWO = 1

    __DEAD_ZONE = 0.01

    __INVALID_INSTANCE_ID = -99  # identifiant (invalide) de contrôleur de jeu

    def __init__(self) -> None:
        """ Initialise le gestionnaire d'entrée (clavier ou gamepads). """
        self.__player_inputs = [PlayerInput(), PlayerInput()]
        self.__joysticks = None
        self.__player_one_instance_id = self.__INVALID_INSTANCE_ID
        self.__player_two_instance_id = self.__INVALID_INSTANCE_ID
        self.__assign_gamepads()

    def __assign_gamepads(self) -> None:

        if self.get_gamepad_count() == 1:
            # Un seul gamepad -> on l'assigne au joueur 1
            self.__joysticks = [pygame.joystick.Joystick(0), ]
            self.__player_one_instance_id = self.__joysticks[0].get_instance_id()
            self.__player_two_instance_id = self.__INVALID_INSTANCE_ID
        elif self.get_gamepad_count() == 2:
            # Deux gamepads -> on tente de préserver les identifiants connus
            self.__joysticks = [pygame.joystick.Joystick(i) for i in range(self.get_gamepad_count())]
            found_player_one_instance_id = False
            found_player_two_instance_id = False
            for joystick in self.__joysticks:
                if joystick.get_instance_id() == self.__player_one_instance_id:
                    found_player_one_instance_id = True
                elif joystick.get_instance_id() == self.__player_two_instance_id:
                    found_player_two_instance_id = True
            if not found_player_one_instance_id and found_player_two_instance_id:
                # identifiant du joueur 1 introuvé, mais celui du joueur 2 oui -> on préserve l'identifiant du joueur 2
                for joystick in self.__joysticks:
                    if joystick.get_instance_id() != self.__player_two_instance_id:
                        self.__player_one_instance_id = joystick.get_instance_id()
            elif found_player_one_instance_id and not found_player_two_instance_id:
                # identifiant du joueur 1 trouvé, mais pas celui du joueur 2 -> on préserve l'identifiant du joueur 1
                for joystick in self.__joysticks:
                    if joystick.get_instance_id() != self.__player_one_instance_id:
                        self.__player_two_instance_id = joystick.get_instance_id()
            elif not found_player_one_instance_id and not found_player_two_instance_id:
                # aucun identifiant trouvé -> on assigne de nouveaux identifiants
                self.__player_one_instance_id = self.__joysticks[0].get_instance_id()
                self.__player_two_instance_id = self.__joysticks[1].get_instance_id()

    @staticmethod
    def get_gamepad_count() -> int:
        """
        Retourne le nombre de gamepads présentement branchés.
        :return: nombre de gamepads branchés
        """
        return pygame.joystick.get_count()

    def manage_keyboard_event(self, event: pygame.event) -> None:
        """
        Gère un événement du clavier.
        :param event: l'événement généré par pygame
        :return: aucun
        """
        player_one_input = self.__player_inputs[self.__PLAYER_ONE]
        player_two_input = self.__player_inputs[self.__PLAYER_TWO]

        if event.type == pygame.KEYDOWN:
            # Événements liés au joueur 1
            input_x, input_y = player_one_input.movement

            if event.key == pygame.K_a:
                input_x = -1.0
            elif event.key == pygame.K_d:
                input_x = 1.0

            if event.key == pygame.K_w:
                input_y = -1.0
            elif event.key == pygame.K_s:
                input_y = 1.0

            player_one_input.movement = input_x, input_y

            if event.key == pygame.K_2:
                player_one_input.focus_next_button = True
                player_one_input.focus_prev_button = False
            elif event.key == pygame.K_1:
                player_one_input.focus_prev_button = True
                player_one_input.focus_next_button = False
            elif event.key == pygame.K_f:
                player_one_input.solve_button = True

            # Événements liés au joueur 2
            input_x, input_y = player_two_input.movement
            activity = False

            if event.key == pygame.K_LEFT:
                input_x = -1.0
                activity = True
            elif event.key == pygame.K_RIGHT:
                input_x = 1.0
                activity = True

            if event.key == pygame.K_UP:
                input_y = -1.0
                activity = True
            elif event.key == pygame.K_DOWN:
                input_y = 1.0
                activity = True

            if activity:
                player_two_input.movement = input_x, input_y

            if event.key == pygame.K_0:
                player_two_input.focus_next_button = True
                player_two_input.focus_prev_button = False
            elif event.key == pygame.K_9:
                player_two_input.focus_prev_button = True
                player_two_input.focus_next_button = False
            elif event.key == pygame.K_p:
                player_two_input.solve_button = True

        elif event.type == pygame.KEYUP:
            # Événements liés au joueur 1
            input_x, input_y = player_one_input.movement

            if event.key in [pygame.K_a, pygame.K_d]:
                input_x = 0.0

            if event.key in [pygame.K_w, pygame.K_s]:
                input_y = 0.0

            player_one_input.movement = input_x, input_y

            if event.key == pygame.K_2:
                player_one_input.focus_next_button = False
            elif event.key == pygame.K_1:
                player_one_input.focus_prev_button = False
            elif event.key == pygame.K_f:
                player_one_input.solve_button = False

            # Événements liés au joueur 2
            input_x, input_y = player_two_input.movement
            activity = False

            if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                input_x = 0.0
                activity = True

            if event.key in [pygame.K_UP, pygame.K_DOWN]:
                input_y = 0.0
                activity = True

            if activity:
                player_two_input.movement = input_x, input_y

            if event.key == pygame.K_0:
                player_two_input.focus_next_button = False
            elif event.key == pygame.K_9:
                player_two_input.focus_prev_button = False
            elif event.key == pygame.K_p:
                player_two_input.solve_button = False

    def manage_gamepad_event(self, event: pygame.event) -> None:
        """
        Gère un événement de contrôleur de jeu (gamepad).
        :param event: l'événement généré par pygame
        :return: aucun
        """
        # Admission exclusive des événements de contrôleurs de jeu (gamepads) au-delà de ce point
        if event.type not in [JOYDEVICEADDED, JOYDEVICEREMOVED, JOYBUTTONDOWN, JOYBUTTONUP, JOYAXISMOTION]:
            return

        # Vérification si il y a ajout ou retrait d'un contrôleur de jeu (gamepad)
        if event.type in [JOYDEVICEADDED, JOYDEVICEREMOVED]:
            self.__assign_gamepads()

        # Prise en charge d'un événement sur un des contrôleur de jeu (gamepad) branchés
        elif self.__joysticks:
            # Événements liés au joueur 1
            if event.instance_id == self.__player_one_instance_id:
                player_one_input = self.__player_inputs[self.__PLAYER_ONE]

                if event.type == JOYBUTTONDOWN:
                    if event.button == 5:
                        player_one_input.focus_next_button = True
                        player_one_input.focus_prev_button = False
                    elif event.button == 4:
                        player_one_input.focus_next_button = False
                        player_one_input.focus_prev_button = True

                    if event.button == 3:
                        player_one_input.solve_button = True

                if event.type == JOYBUTTONUP:
                    if event.button == 5:
                        player_one_input.focus_next_button = False
                    elif event.button == 4:
                        player_one_input.focus_prev_button = False

                    if event.button == 3:
                        player_one_input.solve_button = False

                if event.type == JOYAXISMOTION:
                    input_x, input_y = player_one_input.movement
                    previous_input_x, previous_input_y = player_one_input.movement
                    if event.axis == 0:  # axe horizontal
                        input_x = event.value
                    if event.axis == 4:  # axe vertical
                        input_y = event.value

                    # Application de la zone morte (dead zone)
                    if abs(input_x) < self.__DEAD_ZONE:
                        input_x = 0
                    if abs(input_y) < self.__DEAD_ZONE:
                        input_y = 0

                    # Application du mouvement si il y a un changement (va aussi toucher l'indicateur d'activité)
                    if input_x != previous_input_x or input_y != previous_input_y:
                        player_one_input.movement = input_x, input_y

            # Événements liés au joueur 2
            elif event.instance_id == self.__player_two_instance_id:
                player_two_input = self.__player_inputs[self.__PLAYER_TWO]

                if event.type == JOYBUTTONDOWN:
                    if event.button == 5:
                        player_two_input.focus_next_button = True
                        player_two_input.focus_prev_button = False
                    elif event.button == 4:
                        player_two_input.focus_next_button = False
                        player_two_input.focus_prev_button = True

                    if event.button == 3:
                        player_two_input.solve_button = True

                if event.type == JOYBUTTONUP:
                    if event.button == 5:
                        player_two_input.focus_next_button = False
                    elif event.button == 4:
                        player_two_input.focus_prev_button = False

                    if event.button == 3:
                        player_two_input.solve_button = False

                if event.type == JOYAXISMOTION:
                    input_x, input_y = player_two_input.movement
                    previous_input_x, previous_input_y = player_two_input.movement
                    if event.axis == 0:  # axe horizontal
                        input_x = event.value
                    if event.axis == 4:  # axe vertical
                        input_y = event.value

                    # Application de la zone morte (dead zone)
                    if abs(input_x) < self.__DEAD_ZONE:
                        input_x = 0
                    if abs(input_y) < self.__DEAD_ZONE:
                        input_y = 0

                    # Application du mouvement si il y a un changement (va aussi toucher l'indicateur d'activité)
                    if input_x != previous_input_x or input_y != previous_input_y:
                        player_two_input.movement = input_x, input_y

    def player_input(self, player_id: int) -> PlayerInput:
        """
        Retourne l'état des entrées pour le joueur spécifié (player_id)
        :param player_id: identification du joueur
        :return: l'objet PlayerInput décrivant les entrées pour le joueur spécifié
        """
        assert player_id in [self.__PLAYER_ONE, self.__PLAYER_TWO]
        return self.__player_inputs[player_id]


# ensemble des entrées pour les joueurs
inputs = None


def init() -> None:
    """ Initialise le gestionnaire d'entrées. """

    global inputs
    if not inputs:
        inputs = __InputManager()
