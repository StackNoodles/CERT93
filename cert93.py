#! python3

import pygame
from error_codes import ERROR_CODES_TEXT, Error_codes
import incidents
import input_manager
import resources
import settings
import time

import win32api
import win32con
import win32gui

from tkinter import *
from tkinter import messagebox

from game import Game
from helper_tools import create_level_pickles


def __run_game() -> None:

    # Initialisation de l'engin de jeu (pygame)
    pygame.init()
    pygame.mixer.init()
    pygame.joystick.init()

    # Initialisation de la fenetre a la bonne taille, sans frame
    screen = pygame.display.set_mode(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.NOFRAME)
    # Definir le fuschia comme la couleur a rendre transparente (une couleur peu commune)
    fuchsia = (24, 32, 48)
    screen.fill(fuchsia)  # Remplir le background de fuschia

    # Recuperer le handle de la fenetre
    hwnd = pygame.display.get_wm_info()["window"]
    # Mettre la fenetre en mode layered (permet la transparence et meilleur pour les jeux/medias)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(
        hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)

    # Set les attribus suivants sur la fenetre layered:
    # la couleur cle est fuchsia, l'opacite de cette couleur est 0, et le mode est transparence par cle
    win32gui.SetLayeredWindowAttributes(
        hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)

    # Splash logo dev
    splash_screen("img\logo_stacknoodles.png", 2, screen)

    # Splash screen logo jeu
    splash_screen("img\logo_cert93.png", 3, screen)

    # Enlever les settings d'opacité à la fenêtre layered
    win32gui.SetLayeredWindowAttributes(
        hwnd, win32api.RGB(*fuchsia), 255, win32con.LWA_ALPHA)
    # Création de la fenêtre de jeu
    pygame.display.set_caption("CERT-93")
    screen = pygame.display.set_mode(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))

    # Initialisation des ressources spécifiques au jeu
    return_code = resources.init()
    if return_code != Error_codes.SUCCES:
        pygame.quit()
        messagebox.showerror(
            "ERREUR", ERROR_CODES_TEXT[return_code] + "\n(Code : " + str(return_code) + ")")
        quit()

    input_manager.init()
    incidents.init()

    game = Game(screen)
    game.run()

    pygame.quit()


def splash_screen(image_path: str, time_up: int, screen: pygame.display.set_mode) -> None:
    splash_image = pygame.image.load(image_path)

    origin_x = (settings.SCREEN_WIDTH/2) - (splash_image.get_width()/2)
    origin_y = (settings.SCREEN_HEIGHT/2) - (splash_image.get_height()/2)
    screen.blit(splash_image, (origin_x, origin_y))

    pygame.display.update()
    time.sleep(3)


if __name__ == '__main__':
    create_level_pickles(1)
    try :
        __run_game()
    except KeyboardInterrupt:
        pygame.quit()
        quit()
