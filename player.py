import input_manager

from character import Character


class Player:
    """ Un joueur. """
    PLAYER_ONE = 0
    PLAYER_TWO = 1

    def __init__(self, number: int) -> None:
        assert number in [Player.PLAYER_ONE, Player.PLAYER_TWO]

        self.__number = number
        self.__character = None

    def movement(self) -> tuple:
        input = input_manager.inputs.player_input(self.number)
        return input.movement

    @property
    def character(self) -> Character:
        return self.__character

    @character.setter
    def character(self, new_character: Character) -> None:
        self.__character = new_character

    @property
    def number(self) -> int:
        return self.__number
