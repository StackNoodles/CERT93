#! python3

import pygame
from error_codes import ERROR_CODES_TEXT, Error_codes
import incidents
import input_manager
import resources
import settings
import time

from tkinter import *
from tkinter import messagebox

from game import Game
from helper_tools import create_level_pickles

def __run_game() -> None:

    # Initialisation de l'engin de jeu (pygame)
    pygame.init()
    pygame.mixer.init()
    pygame.joystick.init()

    # Création de la fenêtre de jeu
    pygame.display.set_caption("CERT-93")
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))

    # Initialisation des ressources spécifiques au jeu
    return_code = resources.init()
    if return_code != Error_codes.SUCCES:
        pygame.quit()
        messagebox.showerror("ERREUR", ERROR_CODES_TEXT[return_code] + "\n(Code : " + str(return_code) + ")")
        quit()
        
    input_manager.init()
    incidents.init()

    game = Game(screen)
    game.run()

    pygame.quit()


if __name__ == '__main__':
    try :
        __run_game()
    except KeyboardInterrupt:
        pygame.quit()
        quit()
    #create_level_pickles(3)
