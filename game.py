import random

import pygame
import time

import incidents
import input_manager
import resources
import settings

from asset import Asset
from character import Character
from expertise import Expertise
from level import Level
from score import Score
from tools import find_distance
from fps import FPS
from player import Player
from view import View


class Game:
    """ Une partie. """

    def __init__(self, screen: pygame.Surface) -> None:
        """
        Initialise une instance de partie (objet Game).
        :param screen: surface représentant l'écran pygame
        """
        self.__screen = screen
        self.__backdrop_surface = pygame.image.load(settings.BACKDROP_FILENAME).convert()

        self.__running = False

        self.__score = Score()

        if input_manager.inputs.get_gamepad_count() == 2:
            self.__players = [Player(Player.PLAYER_ONE), Player(Player.PLAYER_TWO)]
        else:
            self.__players = [Player(Player.PLAYER_ONE)]

        self.__level = self.__load_level(2)
        self.__views = self.__setup_views(self.__level)

        self.__fps = FPS()

    def run(self) -> None:
        """ Exécute la partie (boucle de jeu). """
        self.__fps.start()
        previous_time = time.time()

        music = resources.sounds_collection.get('BACKGROUND-MUSIC')
        music.play(-1)

        self.__level.office.enable_ambience()
        incidents.spawner.start()

        self.__running = True
        while self.__running:
            now = time.time()
            delta_time = now - previous_time
            previous_time = now
            self.__fps.tick()

            self.__handle_events()
            if self.__running:
                self.__check_for_player_two()
                self.__handle_incidents()
                self.__update_game_elements(delta_time)
                self.__update_display()

        self.__level.stop()
        incidents.spawner.stop()

        music.stop()
        self.__fps.stop()

    def __load_level(self, number: int) -> Level:
        """
        Charge le niveau spécifié.
        :param number: numéro du niveau à charger
        :return: le niveau chargé
        """
        # Chargement du niveau de jeu
        level = Level(number)

        # Liaison des actifs au pointage
        for asset in level.assets:
            asset.set_solving_action(self.__score.add_points)

        return level

    def __setup_views(self, level: Level) -> dict:
        """
        Configure la ou les vues pour le niveau spécifié (level) en fonction des personnages du niveau.
        :param level: le niveau
        :return: dictionnaire contenant la ou les vues
        """
        views = {}
        # Le joueur 1 contrôle le premier personnage chargé
        self.__players[Player.PLAYER_ONE].character = level.characters[0]

        if len(self.__players) > 1:
            # Le joueur 2 contrôle le deuxième personnage chargé
            self.__players[Player.PLAYER_TWO].character = level.characters[1]

            # Deux joueurs, donc deux vues
            view = View(self.__screen, level.office, View.WIDTH_TWO_PLAYERS, View.HEIGHT)
            view.center_on_screen(self.__screen.get_width() / 4, self.__screen.get_height() / 2)
            views[Player.PLAYER_ONE] = view

            character = self.__players[Player.PLAYER_ONE].character
            view.center_in_office(character.feet_position)

            view = View(self.__screen, level.office, View.WIDTH_TWO_PLAYERS, View.HEIGHT)
            view.center_on_screen(3 * self.__screen.get_width() / 4, self.__screen.get_height() / 2)
            views[Player.PLAYER_TWO] = view

            character = self.__players[Player.PLAYER_TWO].character
            view.center_in_office(character.feet_position)
        else:
            # Un seul joueur, donc une seule vue
            view = View(self.__screen, level.office, View.WIDTH_ONE_PLAYER, View.HEIGHT)
            view.center_on_screen(self.__screen.get_width() / 2, self.__screen.get_height() / 2)
            views[Player.PLAYER_ONE] = view

            character = self.__players[Player.PLAYER_ONE].character
            view.center_in_office(character.feet_position)

        return views

    def __handle_events(self) -> None:
        """
        Gère les événements envoyés par l'engin pygame.
        :return: aucun
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__running = False
                return

            input_manager.inputs.manage_keyboard_event(event)
            input_manager.inputs.manage_gamepad_event(event)

    def __handle_incidents(self) -> None:
        """
        Gère les incidents envoyés par le générateur d'incidents.
        :return: aucun
        """
        for incident in incidents.spawner.get():
            if incident.expertise == Expertise.HELPDESK:
                self.__level.helpdesk.add_incident(incident)
            else:
                # Sélection d'un actif au hasard parmi tous les actifs autres que le centre d'appels
                asset = random.choice(self.__level.assets[1:])
                asset.add_incident(incident)

    def __check_for_player_two(self) -> None:
        """ Vérifie si le joueur 2 est actif et met à jour le nombre de joueurs en fonction du résultat. """
        # Vérification s'il y a de l'activité sur les entrées du joueur 2
        player_two_inputs = input_manager.inputs.player_input(1)
        now = time.time()
        if len(self.__players) == 1:
            if abs(now - player_two_inputs.last_activity_time) < settings.INACTIVITY_THRESHOLD:
                # Une activité récente a été détectée sur les entrées du joueur 2 -> on l'ajoute
                self.__add_player_two()
        else:
            if abs(now - player_two_inputs.last_activity_time) > settings.INACTIVITY_THRESHOLD:
                # Pas d'activité récente détectée sur les entrées du joueur 2 -> on le retire
                self.__remove_player_two()

    def __update_game_elements(self, delta_time: float) -> None:
        """
        Met à jour les éléments de jeu: changement de focus, déplacements, solution d'incidents, actifs.
        Cette méthode est appelée à chaque trame.
        :param delta_time: temps écoulé depuis la trame précédente
        :return: aucun
        """
        self.__change_focus_if_needed()
        self.__move_characters_if_needed(delta_time)
        self.__solve_incidents_if_needed()

        for asset in self.__level.assets:
            asset.update()

    def __update_display(self) -> None:
        """
        Met à jour l'affichage.
        Cette méthode est appelée à chaque trame.
        :return: aucun
        """
        # Affichage de l'image de fond
        self.__screen.blit(self.__backdrop_surface, (0, 0))

        # Affichade de la ou les vues sur le bureau (donc du bureau, des actifs et des personnages)
        for view in self.__views.values():
            view.draw()

        # Affichage du score
        self.__score.draw(self.__screen, (self.__screen.get_width() / 2, 20))

        # Affichage du FPS
        fps_surface = self.__fps.get()
        x = self.__screen.get_width() - fps_surface.get_width() - 10
        self.__screen.blit(fps_surface, (x, 10))

        # Basculement de tampon (donc affichage de l'écran)
        pygame.display.flip()

    def __add_player_two(self) -> None:
        """
        Ajoute le deuxième joueur à la partie en cours.
        :return: aucun
        """
        # Création du joueur 2
        player = Player(Player.PLAYER_TWO)
        self.__players.append(player)

        # Création de la vue pour le joueur 2
        view = View(self.__screen, self.__level.office, View.WIDTH_TWO_PLAYERS, View.HEIGHT)
        view.center_on_screen(3 * self.__screen.get_width() / 4, self.__screen.get_height() / 2)
        self.__views[Player.PLAYER_TWO] = view

        # Ajustement de la taille et de la position de la vue pour le joueur 1
        self.__views[Player.PLAYER_ONE].center_on_screen(self.__screen.get_width() / 4, self.__screen.get_height() / 2)
        self.__views[Player.PLAYER_ONE].resize(View.WIDTH_TWO_PLAYERS, View.HEIGHT)

        # Attribution d'un personnage au joueur 2
        for character in self.__level.characters:
            if character != self.__players[Player.PLAYER_ONE].character:
                self.__players[Player.PLAYER_TWO].character = character
                # Positionnement de la vue sur le personnage
                view = self.__views[Player.PLAYER_TWO]
                view.center_in_office(character.feet_position)
                break

    def __remove_player_two(self) -> None:
        """
        Retire le deuxième joueur de la partie en cours.
        :return: aucun
        """
        assert len(self.__players) > 1

        # Destruction de la vue du joueur 2
        del self.__views[Player.PLAYER_TWO]

        # Destruction du joueur 2 (virtuellement parlant ;-))
        del self.__players[Player.PLAYER_TWO]

        # Ajustement de la taille et de la position de la vue du joueur 1
        self.__views[Player.PLAYER_ONE].center_on_screen(self.__screen.get_width() / 2, self.__screen.get_height() / 2)
        self.__views[Player.PLAYER_ONE].resize(View.WIDTH_ONE_PLAYER, View.HEIGHT)

    def __change_focus_if_needed(self) -> None:
        """
        Fait passer le focus vers un autre personnage, si demandé et si possible.
        :return:
        """
        def change_focus(current_character: Character, index_delta: int) -> None:
            """
            Change le focus. Fonction interne.
            :param current_character: personnage ayant le focus présentement
            :param index_delta: sens de la recherche (1 pour rechercher le suivant, -1 pour rechercher le précédent)
            :return: aucun
            """
            nb_characters = len(self.__level.characters)

            # Sélection du prochain personnage disponible
            current_index = self.__level.characters.index(current_character)
            next_index = (current_index + index_delta + nb_characters) % nb_characters
            next_character = self.__level.characters[next_index]
            while next_character in [p.character for p in self.__players]:
                next_index = (next_index + index_delta + nb_characters) % nb_characters
                next_character = self.__level.characters[next_index]
            player.character = next_character

            # Repositionnement de la vue sur ce nouveau personnage
            new_character = player.character
            self.__views[player.number].center_in_office(new_character.feet_position)

        # Vérification s'il est possible d'effectuer le changement et si un changement est demandé
        if len(self.__level.characters) > len(self.__players):
            # il y a plus de personnages que de joueurs: il est donc possible de changer de personnage
            for player in self.__players:
                character = player.character
                inputs = input_manager.inputs.player_input(player.number)
                if inputs.focus_next_button:
                    inputs.focus_next_button = False
                    change_focus(character, 1)  # on avance jusqu'au prochain disponible
                elif inputs.focus_prev_button:
                    inputs.focus_prev_button = False
                    change_focus(character, -1)  # on recule jusqu'au prochain disponible

    def __move_characters_if_needed(self, delta_time: float) -> None:
        """
        Déplace les personnages si demandé, de façon uniforme peu importe le FPS.
        :param delta_time: temps écoulé depuis la dernière trame
        :return: aucun
        """
        for player in self.__players:
            # récupération du mouvement (généré par clavier ou gamepad) de ce joueur
            inputs = input_manager.inputs.player_input(player.number)
            movement = inputs.movement
            if abs(movement[0]) > 0.0 or abs(movement[1]) > 0.0:
                # il y a mouvement sur au moins un des deux axes
                character = player.character
                next_feet_position = character.compute_next_feet_position(movement, delta_time)
                if self.__level.office.in_navmesh(next_feet_position):
                    # déplacement du personnage
                    character.feet_position = next_feet_position
                    # repositionnement de la vue puisque le personnage s'est déplacé
                    self.__views[player.number].center_in_office(character.feet_position)

    def __solve_incidents_if_needed(self) -> None:
        """
        Solutionne les incidents si demandé
        :return: aucun
        """
        for player in self.__players:
            inputs = input_manager.inputs.player_input(player.number)
            if inputs.solve_button:
                inputs.solve_button = False
                character = player.character
                asset = self.__find_closest_actionable_asset(character)
                if asset:
                    asset.solve_incident()

    def __find_closest_actionable_asset(self, character: Character) -> Asset or None:
        """
        Trouve l'actif le plus près du personnage spécifié (character).
        :param character: personnage
        :return: l'actif si trouvé, None si aucun actif trouvé
        """
        asset_found = None
        distance_found = settings.ACTIONABLE_DISTANCE + 1

        for asset in self.__level.assets:
            distance = find_distance(asset.center_position, character.feet_position)
            if distance <= settings.ACTIONABLE_DISTANCE:
                if asset_found:
                    # un actif avait déjà été trouvé, on vérifie donc si celui-ci est plus proche du personnage
                    if distance < distance_found:
                        asset_found = asset
                        distance_found = distance
                else:
                    # c'est le premier actif à distance d'activation qui est trouvé
                    asset_found = asset
                    distance_found = distance

        return asset_found
