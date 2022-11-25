# Outils pour assister avec la construction des fichiers binaires utilisés par le jeu
# Ce code ne fait pas partie du produit final
import pickle

from expertise import Expertise


def create_level_pickles(number: int) -> None:
    map_filename = f'txt/level{number}.txt'

    fw_filename = f'bin/floor_and_walls{number}.pickle'
    c_filename = f'bin/characters{number}.pickle'
    a_filename = f'bin/assets{number}.pickle'

    map2pickles(map_filename, fw_filename, c_filename, a_filename)


def map2pickles(map_filename: str, fw_filename: str, c_filename: str, a_filename: str) -> None:

    try:
        with open(map_filename, "r") as map_file:
            contents = map_file.read()
    except FileNotFoundError:
        print(f"Fichier introuvable : {map_filename}")
        return

    lines = contents.split('\n')

    longest_line_length = 0
    for line in lines:
        if len(line) > longest_line_length:
            longest_line_length = len(line)

    floor_and_walls = [[-1 for _ in range(len(lines))] for _ in range(longest_line_length)]  # -1 -> pas de tuiles

    floor_and_walls_symbols = {' ': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
                               'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15}

    characters = []
    characters_symbols = {'S': 0, 'T': 1, 'U': 2, 'V': 3, 'W': 4, 'X': 5, 'Y': 6, 'Z': 7}

    assets = []
    assets_symbols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 9, 'z': 10}

    flood_origin = (0, 0)
    for y, line in enumerate(lines):
        for x, symbol in enumerate(line):
            if symbol != ' ':

                # TUILES
                if symbol in floor_and_walls_symbols:
                    floor_and_walls[x][y] = floor_and_walls_symbols[symbol]
                elif symbol == 'x':  # point d'origine du flood fill
                    flood_origin = (x, y)

                # PERSONNAGES
                elif symbol in characters_symbols:
                    speed = 150
                    if symbol == 'S':
                        name = 'Howard the Linux wizard'
                        expertise = Expertise.SERVER
                    elif symbol == 'T':
                        name = 'Amish the firefighter'
                        expertise = Expertise.DESKTOP
                    elif symbol == 'U':
                        name = 'Rajesh the telepath'
                        expertise = Expertise.HELPDESK
                    elif symbol == 'V':
                        name = 'Chuong the black belt'
                        expertise = Expertise.MANAGEMENT
                        speed = 100
                    elif symbol == 'W':
                        name = 'Alice the database mastermind'
                        expertise = Expertise.DATABASE
                    elif symbol == 'X':
                        name = 'The Hulk'
                        expertise = Expertise.SUPERHERO
                        speed = 250
                    elif symbol == 'Y':
                        name = 'Martin the cable guy'
                        expertise = Expertise.NETWORKING
                    else:
                        name = 'Sara the enthusiastic coder'
                        expertise = Expertise.PROGRAMMING

                    character_id = characters_symbols[symbol]
                    characters.append([name, character_id, expertise, speed, x, y])

                # ACTIFS
                elif symbol in assets_symbols:
                    if symbol == 'z':  # c'est le helpdesk
                        assets.insert(0, [x, y])
                    else:
                        asset_id = assets_symbols[symbol]
                        assets.append([asset_id, x, y])

    __flood_fill(flood_origin, 0, floor_and_walls)

    try:
        pickle.dump(floor_and_walls, open(fw_filename, "wb"))
    except OSError:
        print(f"Erreur lors de la création du cornichon : {fw_filename}")

    try:
        pickle.dump(characters, open(c_filename, "wb"))
    except OSError:
        print(f"Erreur lors de la création du cornichon : {c_filename}")

    try:
        pickle.dump(assets, open(a_filename, "wb"))
    except OSError:
        print(f"Erreur lors de la création du cornichon : {a_filename}")


__DELTAS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]


def __flood_fill(starting_point: tuple, symbol: int, office: list) -> None:
    x, y = starting_point
    if office[x][y] == -1:
        office[x][y] = symbol
        for delta in __DELTAS:
            __flood_fill((x + delta[0], y + delta[1]), symbol, office)
