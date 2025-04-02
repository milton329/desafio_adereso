import json

class DataLoaderController():

    def load_star_wars_data(self):
        """Carga los datos de personajes y planetas de Star Wars desde archivos JSON locales."""
        try:
            with open("data/people.json", "r", encoding="utf-8") as file:
                people_data_raw = json.load(file)
                people_data = {"results": people_data_raw} if isinstance(people_data_raw, list) else people_data_raw
        except FileNotFoundError:
            people_data = {"results": []}
            print("Error: No se encontró el archivo people.json")        
        try:
            with open("data/planets.json", "r", encoding="utf-8") as file:
                planets_data_raw = json.load(file)
                planets_data = {"results": planets_data_raw} if isinstance(planets_data_raw, list) else planets_data_raw
        except FileNotFoundError:
            planets_data = {"results": []}
            print("Error: No se encontró el archivo planets.json")        
        try:
            with open("data/star_wars_characters.json", "r", encoding="utf-8") as file:
                characters = set(json.load(file))
        except FileNotFoundError:
            characters = set()        
        return people_data, planets_data, characters

    def load_pokemon_data(self):
        """Carga los datos de Pokemon desde archivos JSON locales."""
        try:
            with open("data/pokemon_data.json", "r", encoding="utf-8") as file:
                pokemon_data_raw = json.load(file)
                pokemon_data = {"results": pokemon_data_raw} if isinstance(pokemon_data_raw, list) else pokemon_data_raw
        except FileNotFoundError:
            pokemon_data = {"results": []}
            print("Error: No se encontró el archivo pokemon_data.json")        
        return pokemon_data