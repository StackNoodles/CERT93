from office import Office
from helpdesk import Helpdesk
from character import Character
from asset import Asset
import incidents
import pickle
import hashlib
import configparser



 
def check_checksum(filename: str) -> None:
    """
    Permet de valider le checksum du fichier config.ini pour savoir si c'est le même
    :param str: le nom du fichier
    """
    config = configparser.ConfigParser(inline_comment_prefixes="#")
    config.read("config/config.ini")
    try:
        with open(filename, "rb") as file_to_check:
            data = file_to_check.read()
            md5_returned = hashlib.md5(data).hexdigest()
            try:
                if md5_returned != config.get("Checksum", filename):
                    raise Exception("Fichier modifié")
            except configparser.NoOptionError:
                config['Checksum'][filename] = md5_returned
                with open('config/config.ini', 'w') as configfile:    # save
                    config.write(configfile)
    except OSError:
            print(f"Erreur de lecture : {filename}")
            return None

class Level:
    """ Un niveau. """

    def __init__(self, number: int) -> None:
        """
        Initialise un niveau (objet Level).
        :param number: numéro du niveau
        """
        self.__number = number

        # Construction du bureau
        self.__office = Office()
        floor_and_walls = self.__load_floor_and_walls(number)
        self.__office.build(floor_and_walls)

        # Ajout des actifs informationnels
        self.__assets = self.__load_assets(number)
        self.__helpdesk = self.__assets[0]
        for asset in self.__assets:
            self.__office.add_asset(asset)

        # Ajout des personnages
        self.__characters = self.__load_characters(number)
        for character in self.__characters:
            self.__office.add_character(character)

    def stop(self) -> None:
        """ Arrête l'exploitation de ce niveau et effectue les opérations de nettoyage nécessaire. """
        # Arrêt des éléments d'ambience dans le bureau
        self.__office.disable_ambience()

        # Interruption de la génération d'incidents
        incidents.spawner.pause()

        # Arrêt et suppression de tous les incidents des actifs
        for asset in self.__assets:
            asset.stop_and_remove_all_incidents()

        # Récupération des incidents en attente dans la queue du générateur d'incidents (donc nettoyage de la queue)
        incidents.spawner.get()
    
    
    @staticmethod
    def __load_assets(number: int) -> list or None:
        """
        Charge les actifs pour le niveau spécifié (number).
        :param number: numéro de niveau
        :return: liste d'actifs si l'opération est réussie, None sinon
        """
        assets_filename = f'bin/assets{number}.pickle'
        check_checksum(assets_filename)
        try:
            with open(assets_filename, "rb") as assets_file:
                assets_data = pickle.load(assets_file)
        except FileNotFoundError:
            print(f"Fichier introuvable : {assets_filename}")
            return None
        except OSError:
            print(f"Erreur de lecture : {assets_filename}")
            return None

        assets = []
        x = assets_data[0][0]
        y = assets_data[0][1]
        # les premières données sont pour le centre d'appels
        helpdesk = Helpdesk((x, y))
        assets.append(helpdesk)

        for i, asset_data in enumerate(assets_data[1:]):
            name = f'Asset {i}'
            asset_id = asset_data[0]
            x = asset_data[1]
            y = asset_data[2]
            tile_position = (x, y)
            asset = Asset(name, asset_id, tile_position)
            assets.append(asset)

        return assets

    @staticmethod
    def __load_characters(number: int) -> list or None:
        """
        Charge les personnages pour le niveau spécifié (number).
        :param number: numéro de niveau
        :return: liste de personnages si l'opération est réussie, None sinon
        """
        characters_filename = f'bin/characters{number}.pickle'
        check_checksum(characters_filename)
        try:
            with open(characters_filename, "rb") as characters_file:
                characters_data = pickle.load(characters_file)
        except FileNotFoundError:
            print(f"Fichier introuvable : {characters_filename}")
            return None
        except OSError:
            print(f"Erreur de lecture : {characters_filename}")
            return None

        characters = []
        characters_names = []

        # Verification de si le nom existe deja
        for character_data in characters_data:
            if character_data[0] in characters_names:
                # Si oui, on le rajoute quand meme et on ajouter un #x au nom
                characters_names.append(character_data[0])
                name = character_data[0]+"#" + \
                    characters_names.count(character_data[0])
            else:
                # Si non, on le rajouter et le donne tel quel
                name = character_data[0]
                characters_names.append(character_data[0])

            character_id = character_data[1]
            expertise = character_data[2]
            speed = character_data[3]
            x = character_data[4]
            y = character_data[5]
            tile_position = (x, y)
            character = Character(name, character_id,
                                  expertise, speed, tile_position)
            characters.append(character)

        return characters

    
    @staticmethod
    def __load_floor_and_walls(number: int) -> list or None:
        """
        Charge le plancher et les murs du bureau pour le niveau spécifié (number).
        :param number: numéro de niveau
        :return: grille représentant le plancher et les murs (liste de listes) si l'opération est réussie, None sinon
        """
        floor_and_walls_filename = f'bin/floor_and_walls{number}.pickle'
        check_checksum(floor_and_walls_filename)  
        
        try:
           
            with open(floor_and_walls_filename, "rb") as floor_and_walls_file:
                floor_and_walls = pickle.load(floor_and_walls_file)
                
        except FileNotFoundError:
            print(f"Fichier introuvable : {floor_and_walls_filename}")
            return None
        except OSError:
            print(f"Erreur de lecture : {floor_and_walls_filename}")
            return None

        return floor_and_walls
    
    @property
    def number(self) -> int:
        return self.__number

    @property
    def office(self) -> Office:
        return self.__office

    @property
    def characters(self) -> list:
        return self.__characters

    @property
    def assets(self) -> list:
        return self.__assets

    @property
    def helpdesk(self) -> Helpdesk:
        return self.__helpdesk
