import pygame
import time

from pygame.locals import JOYDEVICEADDED, JOYDEVICEREMOVED, JOYBUTTONUP, JOYBUTTONDOWN, JOYAXISMOTION

import settings


class PlayerInput:
    """ Entrées pour un joueur. """

    def __init__(self) -> None:
        # mouvement sur l'axe horizontal (x) et sur l'axe vertical (y)
        self.__movement = (0.0, 0.0)
        self.__focus_next_button = False
        self.__focus_prev_button = False
        self.__solve_button = False
        self.__show_name =False

        # sert à détecter de l'activité
        self.__last_activity_time = time.time() - settings.INACTIVITY_THRESHOLD

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

    @property
    def show_name(self) -> bool:
        return self.__show_name

    @show_name.setter
    def show_name(self, value: bool) -> None:
        self.__show_name = value
        self.touch()

class __InputManager:
    """ Gestionnaire d'entrée (clavier ou gamepads). """
    __INPUT_KEYBOARD_PLAYER_ONE = {'up': pygame.K_w, 'down': pygame.K_s, 'right': pygame.K_d, 'left': pygame.K_a,
                                   'switch_plus': pygame.K_2, 'switch_minus': pygame.K_1, 'action': pygame.K_f, 'show_name':pygame.K_n}

    __INPUT_KEYBOARD_PLAYER_TWO = {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'right': pygame.K_RIGHT, 'left': pygame.K_LEFT,
                                   'switch_plus': pygame.K_0, 'switch_minus': pygame.K_9, 'action': pygame.K_p, 'show_name':pygame.K_n}

    __PLAYER_ONE = 0
    __PLAYER_TWO = 1

    __DEAD_ZONE = 0.05

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
            self.__joysticks = [pygame.joystick.Joystick(
                i) for i in range(self.get_gamepad_count())]
            found_player_one_instance_id = False
            found_player_two_instance_id = False
            for joystick in self.__joysticks:
                if joystick.get_instance_id() == self.__player_one_instance_id:
                    found_player_one_instance_id = True
                elif joystick.get_instance_id() == self.__player_two_instance_id:
                    found_player_two_instance_id = True
            if not found_player_one_instance_id and found_player_two_instance_id:
                # identifiant du joueur 1 introuvé, mais celui du joueur 2 oui -> on préserve l'identifiant du joueur 2
                self.player_in_game(
                    self.__player_two_instance_id, self.__player_one_instance_id)

            elif found_player_one_instance_id and not found_player_two_instance_id:
                # identifiant du joueur 1 trouvé, mais pas celui du joueur 2 -> on préserve l'identifiant du joueur 1
                self.player_in_game(
                    self.__player_one_instance_id, self.__player_two_instance_id)

            elif not found_player_one_instance_id and not found_player_two_instance_id:
                # aucun identifiant trouvé -> on assigne de nouveaux identifiants
                self.__player_one_instance_id = self.__joysticks[0].get_instance_id(
                )
                self.__player_two_instance_id = self.__joysticks[1].get_instance_id(
                )

    def player_in_game(self, player_found, player_not_found):
        for joystick in self.__joysticks:
            if joystick.get_instance_id() != player_found:
                player_not_found = joystick.get_instance_id()

    @staticmethod
    def get_gamepad_count() -> int:
        """
        Retourne le nombre de gamepads présentement branchés.
        :return: nombre de gamepads branchés
        """
        return pygame.joystick.get_count()

    def manage_keyboard_event(self, event: pygame.event) -> bool:
        """
        Gère un événement du clavier.
        :param event: l'événement généré par pygame
        :return: aucun
        """
        player_one_input = self.__player_inputs[self.__PLAYER_ONE]
        player_two_input = self.__player_inputs[self.__PLAYER_TWO]

        if event.type == pygame.KEYDOWN:
            # Événements liés au joueur 1
            self.trigger_event_keyboard_down(
                event, player_one_input, self.__INPUT_KEYBOARD_PLAYER_ONE)

            # Événements liés au joueur 2
            self.trigger_event_keyboard_down(
                event, player_two_input, self.__INPUT_KEYBOARD_PLAYER_TWO)

        elif event.type == pygame.KEYUP:
            # Événements liés au joueur 1
            self.trigger_event_keyboard_up(
                event, player_one_input, self.__INPUT_KEYBOARD_PLAYER_ONE)

            # Événements liés au joueur 2
            self.trigger_event_keyboard_up(
                event, player_two_input, self.__INPUT_KEYBOARD_PLAYER_TWO)
        return True

    def trigger_event_keyboard_down(self, event, player_input, INPUT_KEYBOARD):
        """
        Gère les evenements liée aux touches du clavié appuyée d'un joueur
        param: event: l'événement généré par pygame,
                      player_input : movement d'un joueur,
                      INPUT_KEYBOARD : touche possible d'un joueur
        return : aucun
        """
        input_x, input_y = player_input.movement
        activity = False

        if event.key == INPUT_KEYBOARD['left']:
            input_x = -1.0
            activity = True
        elif event.key == INPUT_KEYBOARD['right']:
            input_x = 1.0
            activity = True

        if event.key == INPUT_KEYBOARD['up']:
            input_y = -1.0
            activity = True
        elif event.key == INPUT_KEYBOARD['down']:
            input_y = 1.0
            activity = True

        if activity:
            player_input.movement = input_x, input_y

        if event.key == INPUT_KEYBOARD['switch_plus']:
            player_input.focus_next_button = True
            player_input.focus_prev_button = False
        elif event.key == INPUT_KEYBOARD['switch_minus']:
            player_input.focus_prev_button = True
            player_input.focus_next_button = False
        elif event.key == INPUT_KEYBOARD['action']:
            player_input.solve_button = True
        elif event.key == INPUT_KEYBOARD['show_name']:
            player_input.show_name = True

    def trigger_event_keyboard_up(self, event, player_input, INPUT_KEYBROAD):
        """
        Gère les evenements liée aux touches du clavié relachée d'un joueur
        param: event: l'événement généré par pygame,
                      player_input : movement d'un joueur,
                      INPUT_KEYBOARD : touche possible d'un joueur
        return : aucun
        """
        input_x, input_y = player_input.movement
        activity = False

        if event.key in [INPUT_KEYBROAD['left'], INPUT_KEYBROAD['right']]:
            input_x = 0.0
            activity = True

        if event.key in [INPUT_KEYBROAD['up'], INPUT_KEYBROAD['down']]:
            input_y = 0.0
            activity = True

        if activity:
            player_input.movement = input_x, input_y

        if event.key == INPUT_KEYBROAD['switch_plus']:
            player_input.focus_next_button = False
        elif event.key == INPUT_KEYBROAD['switch_minus']:
            player_input.focus_prev_button = False
        elif event.key == INPUT_KEYBROAD['action']:
            player_input.solve_button = False
        elif event.key == INPUT_KEYBROAD['show_name']:
            player_input.show_name = False
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

                self.trigger_event_gamepad(event, player_one_input)

            # Événements liés au joueur 2
            elif event.instance_id == self.__player_two_instance_id:
                player_two_input = self.__player_inputs[self.__PLAYER_TWO]

                self.trigger_event_gamepad(event, player_two_input)

    def trigger_event_gamepad(self, event: pygame.event, player_input):
        """
        Gère les evenements liée aux touches du gamepad d'un joueur
        param: event: l'événement généré par pygame,
                      player_input : movement d'un joueur,
        return : aucun
        """
        if event.type == JOYBUTTONDOWN:
            print(event.button)
            if event.button == settings.NEXT_BUTTON:
                player_input.focus_next_button = True
                player_input.focus_prev_button = False
            elif event.button == settings.PREV_BUTTON:
                player_input.focus_next_button = False
                player_input.focus_prev_button = True

            if event.button == settings.SOLVE_BUTTON:
                player_input.solve_button = True

            if event.button == settings.SHOW_NAME_BUTTON:
                player_input.show_name = True

        if event.type == JOYBUTTONUP:
            print(event.button)
            if event.button == settings.NEXT_BUTTON:
                player_input.focus_next_button = False
            elif event.button == settings.PREV_BUTTON:
                player_input.focus_prev_button = False

            if event.button == settings.SOLVE_BUTTON:
                player_input.solve_button = False

            if event.button == settings.SHOW_NAME_BUTTON:
                player_input.show_name = False

        if event.type == JOYAXISMOTION:
            print(event.axis)
            input_x, input_y = player_input.movement
            previous_input_x, previous_input_y = player_input.movement
            if event.axis == settings.HORIZONTAL_AXIS:  # axe horizontal
                input_x = event.value
            if event.axis == settings.VERTICAL_AXIS:  # axe vertical
                input_y = event.value

            # Application de la zone morte (dead zone)
            if abs(input_x) < self.__DEAD_ZONE:
                input_x = 0
            if abs(input_y) < self.__DEAD_ZONE:
                input_y = 0

            # Application du mouvement si il y a un changement (va aussi toucher l'indicateur d'activité)
            if input_x != previous_input_x or input_y != previous_input_y:
                player_input.movement = input_x, input_y

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
