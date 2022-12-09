import math
from multiprocessing import Event
import random
import sys
from threading import Thread

import pygame
import time

import incidents
from incidents import Incident
import input_manager
import progress_bar
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
from countdown import Countdown

from pygame.locals import JOYDEVICEADDED, JOYDEVICEREMOVED, JOYBUTTONUP, JOYBUTTONDOWN, JOYAXISMOTION, KEYUP, KEYDOWN


class Game:
    """ Une partie. """

    def __init__(self, screen: pygame.Surface) -> None:
        """
        Initialise une instance de partie (objet Game).
        :param screen: surface représentant l'écran pygame
        """
        self.__screen = screen
        self.__backdrop_surface = pygame.image.load(
            settings.BACKDROP_FILENAME).convert()

        self.__failed_incident_max = 0

        self.__running = False

        self.__display_name = False

        self.__score = Score()
        self.__music = resources.sounds_collection.get('BACKGROUND-MUSIC')
        self.__arrow = resources.arrow.get()

        self.__countdown = Countdown()

        if input_manager.inputs.get_gamepad_count() == 2:
            self.__players = [Player(Player.PLAYER_ONE),
                              Player(Player.PLAYER_TWO)]
        else:
            self.__players = [Player(Player.PLAYER_ONE)]
        # On commence au lvl 1
        self.__level_num = 1
        self.__level = self.__load_level(self.__level_num)
        self.__views = self.__setup_views(self.__level)

        self.__fps = FPS()
        self.__notification_full_time = 5000
        self.__notification_fade_time = 3000

        self.__incident_timer = pygame.time.get_ticks()
        self.__new_level_notif_time = 2000
        self.__new_level_notification = pygame.time.get_ticks()+self.__new_level_notif_time

        self.__active_tiles = []

        self.__is_paused = False

    def end_screen(self, image_path: str, sleep_time: int):
        image = pygame.image.load(image_path)
        origin_x = (settings.SCREEN_WIDTH / 2) - \
            (image.get_width() / 2)
        origin_y = (settings.SCREEN_HEIGHT / 2) - \
            (image.get_height() / 2)
        self.__screen.blit(image, (origin_x, origin_y))

        pygame.display.update()
        time.sleep(sleep_time)

    def run(self) -> None:
        """ Exécute la partie (boucle de jeu). """
        self.__fps.start()
        self.__countdown.start()

        victoire = False
        defaite = False
        new_level = False
        previous_time = time.time()
        self.__music.play(-1)

        self.__level.office.enable_ambience()
        incidents.spawner.start()

        while victoire == False and defaite == False:

            if new_level:
                self.__level.office.enable_ambience()
                self.__countdown.reset_timer()
                incidents.spawner.unpause()
                incidents.spawner.reset()
                self.__new_level_notification = pygame.time.get_ticks()+self.__new_level_notif_time
                self.__current_incident = ""
                self.__failed_incident_max = 0
                new_level = False

            self.__running = True
            while self.__running:
                now = time.time()
                delta_time = now - previous_time
                previous_time = now
                self.__fps.tick()

                self.__handle_events()
                if self.__running:
                    if not self.__is_paused:
                        self.__check_for_player_two()
                        self.__handle_incidents()
                    self.__failed_incident_max += self.__update_game_elements(
                        delta_time)
                    self.__update_display()

                if (self.__countdown.timeout() and self.__failed_incident_max < settings.MAX_MISTAKES):  # passe de niveau
                    self.__running = False
                    self.__level_num += 1
                    new_level = True
                elif self.__failed_incident_max >= settings.MAX_MISTAKES:
                    # Ecran defaite (game over)
                    self.end_screen("img\game_over.png", 5)

                    self.__running = False
                    defaite = True

            self.__level.stop()

            if self.__level_num <= settings.MAX_MISTAKES:
                self.__level = self.__load_level(self.__level_num)
                self.__views = self.__setup_views(self.__level)
            else:
                victoire = True
                # Ecran victoire
                self.end_screen("img\mission_complete.png", 5)

        self.quit_game()

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
        views[Player.PLAYER_ONE] = self.__set_view(level, Player.PLAYER_ONE)

        if len(self.__players) > 1:
            # Le joueur 2 contrôle le deuxième personnage chargé
            self.__players[Player.PLAYER_TWO].character = level.characters[1]

            # Deux joueurs, donc deuxieme vue
            views[Player.PLAYER_TWO] = self.__set_view(
                level, Player.PLAYER_TWO)

        return views

    def __set_view(self, level: Level, index: int) -> View:

        view_width = View.WIDTH_ONE_PLAYER
        multiplier = 1
        # Si la liste de joueurs est plus grande que 1, alors on set le view_width à 2 joueurs
        if len(self.__players) > 1:
            view_width = View.WIDTH_TWO_PLAYERS
            # S'il s'agit du player2 on set le multiplier à 3
            if index == 1:
                multiplier = 3
        # On set la view
        view = View(self.__screen, level.office, view_width, View.HEIGHT)
        view.center_on_screen((multiplier * self.__screen.get_width() /
                               2 * len(self.__players), self.__screen.get_height() / 2))
        character = self.__players[index].character
        view.center_in_office(character.feet_position)

        return view

    def quit_game(self):
        incidents.spawner.stop()
        self.__music.stop()
        self.__fps.stop()
        self.__countdown.stop()

        pygame.quit()
        sys.exit()

    def __handle_events(self) -> None:
        """
        Gère les événements envoyés par l'engin pygame.
        :return: aucun
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__running = False
                self.quit_game()

            if event.type in [KEYDOWN, KEYUP]:
                input_manager.inputs.manage_keyboard_event(event)

            elif event.type in [JOYDEVICEADDED, JOYDEVICEREMOVED, JOYBUTTONDOWN, JOYBUTTONUP, JOYAXISMOTION]:
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

                self.__current_incident = "THERE IS A " + \
                    str(incident.expertise.name) + " INCIDENT AT DESK N°" + \
                    asset.name.replace('Asset ', '')
                self.__incident_timer = pygame.time.get_ticks() + self.__notification_full_time
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

    def __update_game_elements(self, delta_time: float) -> int:
        """
        Met à jour les éléments de jeu: changement de focus, déplacements, solution d'incidents, actifs.
        Cette méthode est appelée à chaque trame.
        :param delta_time: temps écoulé depuis la trame précédente
        :return: aucun
        """
        timeoutIndicents = 0

        self.__pause_game_if_needed()

        self.__execute_tile_action_if_needed()
        self.__display_name_action()

        if not self.__is_paused:
            self.__change_focus_if_needed()
            self.__move_characters_if_needed(delta_time)
            self.__solve_incidents_if_needed()
            for asset in self.__level.assets:
                timeoutIndicents += asset.update()

        return timeoutIndicents

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
            view.draw(self.__display_name)

        # Affichage du countdown
        countdown_surface = self.__countdown.get()
        self.__screen.blit(countdown_surface, (10, 10))

        # Affichage du score
        score_surface = self.__value_display(self.__score.get_score_display())
        self.__screen.blit(score_surface, ((
            self.__screen.get_width() / 2)-(score_surface.get_width()/2), 10))

        # Affichage des user errors
        color = (255, 255, 255)
        if (self.__failed_incident_max) > (settings.MAX_MISTAKES-2):
            color = (255, 0, 0)
        user_errors_surface = self.__font.render(
            f"MISTAKES MADE : {self.__failed_incident_max} / {settings.MAX_MISTAKES}", True, color)
        self.__screen.blit(user_errors_surface, (self.__screen.get_width(
        )-user_errors_surface.get_width()-10, 10))

        # Affichage du FPS
        fps_surface = self.__fps.get()
        self.__screen.blit(
            fps_surface, (10, self.__screen.get_height()-fps_surface.get_height()-10))

        # Affichage nouvel incident
        if pygame.time.get_ticks() < self.__incident_timer:
            incident_surface = self.__font.render(
                self.__current_incident, True, (255, 45, 40))

            display_time_left = self.__incident_timer - pygame.time.get_ticks()

            if (display_time_left < self.__notification_fade_time):
                alpha = (display_time_left)/(self.__notification_fade_time/255)
                incident_surface.set_alpha(alpha)

            self.__screen.blit(incident_surface, ((self.__screen.get_width(
            ) / 2)-(incident_surface.get_width()/2), (self.__screen.get_height() / 10)),)

        # Affichage des barres de progression
        for view, player in zip(self.__views.values(), self.__players):
            for character in self.__level.characters:
                if character.progress_bar:
                    self.__update_progress_bar(view, player, character)

        # Affichage notif nouveau niveau
        if self.__new_level_notification > pygame.time.get_ticks():
            self.__display_title("LEVEL " + str(self.__level_num))

        # Affichage du texte de pause
        if self.__is_paused:
            self.__display_title("PAUSE")

        # Affichage fleches directionnelles
        self.__update_arrow()

        # Basculement de tampon (donc affichage de l'écran)
        pygame.display.flip()

    def __update_progress_bar(self, view: View, player: Player, character: Character) -> None:
        # Calculs des vecteurs
        vector_x = character.feet_position[0] - \
            player.character.feet_position[0]
        vector_y = character.feet_position[1] - \
            player.character.feet_position[1]

        # Coordonées de la barre en fonction de l'ecran
        if view == self.__views[0]:
            multiplier = 1
        else:
            multiplier = 3
        bar_x = (multiplier * self.__screen.get_width() /
                 (2 * len(self.__players))) + vector_x
        bar_y = (self.__screen.get_height() / 2) + vector_y

        # Affichage si la barre est dans l'ecran
        if not (character.feet_position[0] > player.character.feet_position[0] + view.view_width / 2 or
                character.feet_position[1] > player.character.feet_position[1] + view.view_heigth / 2 or
                character.feet_position[0] < player.character.feet_position[0] - view.view_width / 2 or
                character.feet_position[1] < player.character.feet_position[1] - view.view_heigth / 2):
            progress_bar_id = progress_bar.compute_progress_bar_id(
                character.progress_bar)
            progress_bar_surface = resources.progress_bar_collection.get(
                progress_bar_id)
            self.__screen.blit(progress_bar_surface, (
                bar_x - character.icon.get_width() / 2, bar_y - character.icon.get_width() * 2))

    def __display_title(self, title: str) -> None:
        """Affiche un gros titre blanc"""
        text_font = pygame.font.Font(pygame.font.get_default_font(), 120)
        outline_font = pygame.font.Font(pygame.font.get_default_font(), 120)

        outline_surface = outline_font.render(title, True, (0, 0, 0))
        title_surface = text_font.render(title, True, (210, 210, 190))

        self.__screen.blit(outline_surface, ((self.__screen.get_width(
        ) / 2)-(outline_surface.get_width()/2) - 10, (self.__screen.get_height() / 5) + 10),)
        self.__screen.blit(title_surface, ((self.__screen.get_width(
        ) / 2)-(title_surface.get_width()/2), (self.__screen.get_height() / 5)),)

    def __update_arrow(self) -> None:
        """
        Actualise la fleche directionnelle vers les incidents et personnages hors de l'ecran.
        :return: aucun
        """
        if not self.__views:
            return

        for view, player in zip(self.__views.values(), self.__players):

            # Vers les personnages
            for character in self.__level.characters:
                self.__draw_arrow(character.feet_position,
                                  player, view, character.icon)

            # Vers les incidents des assets
            for asset in self.__level.assets:
                if asset.active_incident:
                    self.__draw_arrow(asset.center_position,
                                      player, view, asset.image_incident)

    def __draw_arrow(self, position: tuple, player: Player, view: View, icon: pygame.Surface) -> None:
        """
        Dessine une fleche sur un ecran donné en fonction d'une position cible
        :param position: La position cible vers laquelle orienter la fleche
        :param player: Le joueur de qui part la fleche
        :param view: La vue sur laquelle afficher la fleche
        :param icon: L'icone à afficher avec la fleche
        :return: aucun
        """
        # Si la position cible est hors de l'ecran
        if (position[0] > player.character.feet_position[0] + view.view_width / 2 or
            position[1] > player.character.feet_position[1] + view.view_heigth / 2 or
            position[0] < player.character.feet_position[0] - view.view_width / 2 or
                position[1] < player.character.feet_position[1] - view.view_heigth / 2):

            # Calcul de la position de la position cible en fonction du centre de chaque ecran
            # On veut limiter la fleches aux limites de l'ecran

            # Calculs des vecteurs
            vector_x = position[0] - player.character.feet_position[0]
            vector_y = position[1] - player.character.feet_position[1]

            # Largeur
            if vector_x < -view.view_width / 2:
                vector_x = - view.view_width / 2
            elif vector_x > view.view_width / 2:
                # - 15 pour raprocher la fleche de l'ecran
                vector_x = view.view_width / 2 - 15

            # Hauteur
            if vector_y < -view.view_heigth / 2:
                vector_y = - view.view_heigth / 2
            elif vector_y > view.view_heigth / 2:
                # - 15 pour raprocher la fleche de l'ecran
                vector_y = view.view_heigth / 2 - 15

            # Calcul de l'angle de rotation
            # - car sens anti horaire, +90 car atan2 par de la droite alors qu'on veut partir du top
            angle = - (math.degrees(math.atan2(vector_y, vector_x)) + 90)

            # Rotation de la fleche en fonction de l'angle
            rotated_arrow = pygame.transform.rotate(self.__arrow, angle)

            # Coordonées de la fleche en fonction de l'ecran
            if view == self.__views[0]:
                multiplier = 1
            else:
                multiplier = 3
            arrow_x = (multiplier * self.__screen.get_width() /
                       (2 * len(self.__players))) + vector_x
            arrow_y = (self.__screen.get_height() / 2) + vector_y

            # Coordonées pour l'icone (décalée de quelques %tages des bords de l'ecran, trouver une solution plus jolie si possible)
            icon_x = arrow_x - vector_x * 0.05
            icon_y = arrow_y - vector_y * 0.07

            # Affichage
            self.__screen.blit(icon, (icon_x, icon_y))
            self.__screen.blit(rotated_arrow, (arrow_x, arrow_y))

    def __value_display(self, string_display) -> pygame.Surface:
        default_font_name = pygame.font.get_default_font()

        self.__font = pygame.font.Font(default_font_name, 20)

        return self.__font.render(string_display, True,
                                  (255, 255, 255))

    def __add_player_two(self) -> None:
        """
        Ajoute le deuxième joueur à la partie en cours.
        :return: aucun
        """
        # Création du joueur 2
        player = Player(Player.PLAYER_TWO)
        self.__players.append(player)

        # Création de la vue pour le joueur 2
        view = View(self.__screen, self.__level.office,
                    View.WIDTH_TWO_PLAYERS, View.HEIGHT)
        view.center_on_screen(
            (3 * self.__screen.get_width() / 4, self.__screen.get_height() / 2))
        self.__views[Player.PLAYER_TWO] = view

        # Ajustement de la taille et de la position de la vue pour le joueur 1
        self.__views[Player.PLAYER_ONE].center_on_screen(
            (self.__screen.get_width() / 4, self.__screen.get_height() / 2))
        self.__views[Player.PLAYER_ONE].resize(
            View.WIDTH_TWO_PLAYERS, View.HEIGHT)

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
        self.__views[Player.PLAYER_ONE].center_on_screen(
            (self.__screen.get_width() / 2, self.__screen.get_height() / 2))
        self.__views[Player.PLAYER_ONE].resize(
            View.WIDTH_ONE_PLAYER, View.HEIGHT)

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
            next_index = (current_index + index_delta +
                          nb_characters) % nb_characters
            next_character = self.__level.characters[next_index]
            while next_character in [p.character for p in self.__players]:
                next_index = (next_index + index_delta +
                              nb_characters) % nb_characters
                next_character = self.__level.characters[next_index]
            player.character = next_character

            # Repositionnement de la vue sur ce nouveau personnage
            new_character = player.character
            self.__views[player.number].center_in_office(
                new_character.feet_position)

        # Vérification s'il est possible d'effectuer le changement et si un changement est demandé
        if len(self.__level.characters) > len(self.__players):
            # il y a plus de personnages que de joueurs: il est donc possible de changer de personnage
            for player in self.__players:
                character = player.character
                inputs = input_manager.inputs.player_input(player.number)
                if inputs.focus_next_button:
                    inputs.focus_next_button = False
                    # on avance jusqu'au prochain disponible
                    change_focus(character, 1)
                elif inputs.focus_prev_button:
                    inputs.focus_prev_button = False
                    # on recule jusqu'au prochain disponible
                    change_focus(character, -1)

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
                if character.is_locked:
                    return

                next_feet_position = character.compute_next_feet_position(
                    movement, delta_time)
                if self.__level.office.in_navmesh(next_feet_position):
                    # déplacement du personnage
                    character.feet_position = next_feet_position
                    # repositionnement de la vue puisque le personnage s'est déplacé
                    self.__views[player.number].center_in_office(
                        character.feet_position)

    # Probablement améliorable
    def __execute_tile_action_if_needed(self) -> None:
        """
        Execute l'action de la tuile sous le personnage si necessaire.
        :return: aucun
        """
        # On regarde pour chaque joueur si leur personnage est sur une tuile à action, et on execute l'action si oui.
        for player in self.__players:
            character_position = player.character.feet_position
            tile_under_character = self.__level.office.get_tile(
                character_position)

            if tile_under_character not in self.__active_tiles and tile_under_character.action is not None:
                tile_under_character.action()
                # On ajoute la tuile sur laquelle est le personnages dans les tuiles actives.
                self.__active_tiles.append(tile_under_character)

        # On regarde pour chaque tuile un personnage est dessus, si aucun ne l'est on la retire des tuiles actives.
        for tile in self.__active_tiles:
            still_active = False

            for player in self.__players:
                character_position = player.character.feet_position
                tile_under_character = self.__level.office.get_tile(
                    character_position)

                if tile_under_character == tile:
                    still_active = True

            if not still_active:
                self.__active_tiles.remove(tile)

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
                if asset and asset.active_incident and not asset.active_incident.is_paused:
                    # Le helpdesk n'as pas de temps de resolution
                    if asset.name != "Helpdesk":
                        if character.progress_bar:
                            self.__stop_solving_incident(
                                character, asset.active_incident)
                        else:
                            self.__solving_incident(
                                character, asset.active_incident)
                    else:
                        asset.solve_incident()

        for asset in self.__level.assets:
            for char in self.__level.characters:
                if char.current_working_incident and asset.active_incident:
                    if char.current_working_incident == asset.active_incident:
                        if char.progress_bar and char.progress_bar.is_solved:
                            self.__stop_solving_incident(
                                char, asset.active_incident)
                            asset.solve_incident()

    def __solving_incident(self, character: Character, incident: Incident) -> None:
        """
        Bloque un personnage et lui fait attendre le temps de resolution de l'incident
        :param character: Le personnage qui resoud l'incident
        :param incident: L'incident à résoudre
        :return: aucun
        """
        incident.pause()
        character.add_progress_bar(incident)

    def __stop_solving_incident(self, character: Character, incident: Incident) -> None:
        """
        Arrete la resolution de l'incident
        :param character: Le personnage qui resoud l'incident
        :param incident: L'incident en train d'être résolu
        :return: aucun
        """
        incident.unpause()
        character.remove_progress_bar()

    def __find_closest_actionable_asset(self, character: Character) -> Asset or None:
        """
        Trouve l'actif le plus près du personnage spécifié (character).
        :param character: personnage
        :return: l'actif si trouvé, None si aucun actif trouvé
        """
        asset_found = None
        distance_found = settings.ACTIONABLE_DISTANCE + 1

        for asset in self.__level.assets:
            distance = find_distance(
                asset.center_position, character.feet_position)
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

    def __pause_game_if_needed(self) -> None:
        """
        Pause tout les incidents, les mouvements, le timer et les taches
        :return: aucun
        """
        if self.__check_pause_pressed():
            # On syncronise les pauses des joueurs
            for player in self.__players:
                inputs = input_manager.inputs.player_input(player.number)
                inputs.pause = self.__is_paused

            if self.__is_paused:
                self.__countdown.pause()
                incidents.spawner.pause()
                for asset in self.__level.assets:
                    if asset.active_incident:
                        asset.pause_incident()
                for character in self.__level.characters:
                    if character.progress_bar:
                        character.progress_bar.pause()
            else:
                self.__countdown.unpause()
                incidents.spawner.unpause()
                for asset in self.__level.assets:
                    if asset.active_incident:
                        asset.unpause_incident()
                for character in self.__level.characters:
                    if character.progress_bar:
                        character.progress_bar.unpause()

    def __check_pause_pressed(self) -> bool:
        """Verifie si un des deux joueurs a changé l'état de pause"""
        inputs = []
        for player in self.__players:
            inputs.append(input_manager.inputs.player_input(player.number))
            for input in inputs:
                if self.__is_paused and input.pause == False:
                    self.__is_paused = False
                    return True
                elif not self.__is_paused and input.pause == True:
                    self.__is_paused = True
                    return True
        return False

    def __display_name_action(self) -> None:
        """
        Affiche le nom des perssonages et des actifs
        :return: aucun
        """
        for player in self.__players:
            inputs = input_manager.inputs.player_input(player.number)
            if inputs.show_name:
                self.__display_name = True
            else:
                self.__display_name = False
