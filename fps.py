import pygame

from threading import Thread, Event

DEFAULT_FONT_SIZE = 20


class FPS(Thread):
    """ Trames par seconde (frames per second - FPS). """

    def __init__(self) -> None:
        """
        Initialise une instance de FPS. Un objet FPS permet d'estimer le nombre de trames par seconde.
        """
        super().__init__()

        self.__tick = 0
        self.__fps = 0

        default_font_name = pygame.font.get_default_font()
        self.__font = pygame.font.Font(default_font_name, DEFAULT_FONT_SIZE)

        self.__surface = None

        self.__event = Event()  # événement servant à arrêter la tâche (va aussi la réveiller si nécessaire)

    def tick(self) -> None:
        """
        Méthode à appeler à chaque passage pour calculer le FPS.
        Incrémente un compteur (tick) à chaque appel. Le nombre de ticks en une seconde indique le nombre de trame
        affichée en une seconde (FPS) à condition d'appeler tick() à chaque trame.
        """
        self.__tick += 1

    def get(self) -> pygame.Surface:
        """
        Retourne une surface pour l'affichage des FPS.
        :return: la surface qui contient le texte (FPS)
        """
        fps_str = f"FPS = {self.__fps}"
        return self.__font.render(fps_str, True, (255, 255, 255))

    def run(self) -> None:
        """ Tâche de compilation du FPS. """

        while not self.__event.is_set():
            self.__event.wait(1)
            self.__fps = self.__tick  # sauvegarde le FPS obtenu pour la dernière seconde écoulée
            self.__tick = 0

    def stop(self) -> None:
        """ Arrête la tâche FPS. """
        self.__event.set()
