import pygame

from threading import Thread, Event

from expertise import Expertise

DEFAULT_FONT_SIZE = 20


class MessageIncident(Thread):
    """ Trames par seconde (frames per second - FPS). """

    def __init__(self) -> None:
        """
        Initialise une instance de FPS. Un objet FPS permet d'estimer le nombre de trames par seconde.
        """
        super().__init__()

        default_font_name = pygame.font.get_default_font()
        self.__font = pygame.font.Font(default_font_name, DEFAULT_FONT_SIZE)

        self.__surface = None
        self.__message_incident = ""
        # événement servant à arrêter la tâche (va aussi la réveiller si nécessaire)
        self.__event = Event()

    def get(self, expertise:Expertise) -> pygame.Surface:
        """
        Retourne une surface pour l'affichage des FPS.
        :return: la surface qui contient le texte (FPS)
        """
        
        self.__message_incident = expertise
        self.fps_str = f"incident: {str(self.__message_incident.name)}"
        return self.fps_str

    def run(self) -> None:
        """ Tâche de compilation du FPS. """
        for i in range(5):
            print("messaging " + str(self.__message_incident))
            self.__event.wait(1)

        self.fps_str = f""
        self.stop


    def stop(self) -> None:
        """ Arrête la tâche FPS. """
        self.__event.set()
