from .DataLoader import DataLoaderController

class ApisInternalController():
    controller = DataLoaderController()
    # Variables de clase para carga perezosa (lazy loading)
    _star_wars_people = None
    _star_wars_planets = None
    _star_wars_characters = None
    _pokemon_data = None

    # Índices para búsquedas rápidas
    _people_index = None
    _planets_name_index = None
    _planets_id_index = None
    _pokemon_index = None

    # Función para crear índices para búsquedas rápidas
    def create_indices(self):
        """Crea índices para búsquedas rápidas de personajes, planetas y pokémon."""
        if (self.__class__._people_index is None or self.__class__._planets_name_index is None or 
            self.__class__._planets_id_index is None or self.__class__._pokemon_index is None):            
            people_data, planets_data, _ = self.get_star_wars_data()
            pokemon_data = self.get_pokemon_data()            
            self.__class__._people_index = {}
            self.__class__._planets_name_index = {}
            self.__class__._planets_id_index = {}
            self.__class__._pokemon_index = {}            
            for person in people_data.get("results", []):
                self.__class__._people_index[person["name"].lower()] = person                
            for planet in planets_data.get("results", []):
                self.__class__._planets_name_index[planet["name"].lower()] = planet
                planet_id = planet["url"].split("/")[-2] if planet["url"].endswith("/") else planet["url"].split("/")[-1]
                self.__class__._planets_id_index[planet_id] = planet                
            for pokemon in pokemon_data.get("results", []):
                self.__class__._pokemon_index[pokemon["name"].lower()] = pokemon                
        return (self.__class__._people_index, self.__class__._planets_name_index, 
                self.__class__._planets_id_index, self.__class__._pokemon_index)

    def get_pokemon(self, name):
        """Obtener información de Pokémon desde los datos JSON locales."""
        name_lower = name.lower()        
        # Obtener índices
        _, _, _, pokemon_index = self.create_indices()        
        # Buscar el Pokémon en el índice
        if name_lower in pokemon_index:
            pokemon = pokemon_index[name_lower]
            return {
                "name": pokemon["name"],
                "base_experience": pokemon.get("base_experience"),
                "height": pokemon.get("height"),
                "weight": pokemon.get("weight")
            }            
        # Obtener datos completos si es necesario
        pokemon_data = self.get_pokemon_data()
        
        # Si la estructura es diferente y Pokemon están almacenados directamente en el JSON
        if "name" in pokemon_data and pokemon_data["name"].lower() == name_lower:
            return {
                "name": pokemon_data["name"],
                "base_experience": pokemon_data.get("base_experience"),
                "height": pokemon_data.get("height"),
                "weight": pokemon_data.get("weight")
            }            
        return {"error": f"Pokemon '{name}' not found"}

    def get_star_wars_character(self, name):
        """Obtener información de Star Wars desde los datos JSON locales."""
        # Intentar manejar variaciones comunes de títulos
        search_name = name
        if name.startswith("Almirante ") or name.startswith("Admiral ") or name.startswith("General "):
            search_name = name.split(" ", 1)[1]  # Quitar el título            
        search_name_lower = search_name.lower()        
        # Obtener índices
        people_index, _, planets_id_index, _ = self.create_indices()        
        # Buscar el personaje en el índice
        character = None
        if search_name_lower in people_index:
            character = people_index[search_name_lower]
        else:
            # Búsqueda parcial si no se encuentra el nombre exacto
            for person_name, person in people_index.items():
                if search_name_lower in person_name:
                    character = person
                    break                    
        if character:
            # Obtener el planeta natal del personaje
            homeworld_url = character["homeworld"]
            homeworld_id = homeworld_url.split("/")[-2] if homeworld_url.endswith("/") else homeworld_url.split("/")[-1]            
            homeworld_name = "Unknown"
            if homeworld_id in planets_id_index:
                homeworld_name = planets_id_index[homeworld_id]["name"]            
            return {
                "name": character["name"],
                "height": self.safe_int(character["height"]),
                "mass": self.safe_int(character["mass"]) if character["mass"] != "unknown" else 0,
                "homeworld": homeworld_name
            }            
        return {"error": f"Character '{name}' not found"}

    def get_star_wars_planet(self, name):
        """Obtener información de Planetas de Star Wars desde los datos JSON locales."""
        name_lower = name.lower()        
        # Obtener índices
        _, planets_name_index, _, _ = self.create_indices()        
        # Buscar el planeta en el índice
        if name_lower in planets_name_index:
            planet = planets_name_index[name_lower]
            return {
                "name": planet["name"],
                "rotation_period": self.safe_int(planet["rotation_period"]),
                "orbital_period": self.safe_int(planet["orbital_period"]),
                "diameter": self.safe_int(planet["diameter"]),
                "surface_water": self.safe_int(planet["surface_water"]),
                "population": self.safe_int(planet["population"])
            }            
        # Búsqueda parcial si no se encuentra el nombre exacto
        for planet_name, planet in planets_name_index.items():
            if name_lower in planet_name:
                return {
                    "name": planet["name"],
                    "rotation_period": self.safe_int(planet["rotation_period"]),
                    "orbital_period": self.safe_int(planet["orbital_period"]),
                    "diameter": self.safe_int(planet["diameter"]),
                    "surface_water": self.safe_int(planet["surface_water"]),
                    "population": self.safe_int(planet["population"])
                }
                
        return {"error": f"Planet '{name}' not found"}
    def safe_int(self, value, default=0):
        """ Convierte un valor a entero si es posible, de lo contrario devuelve el valor por defecto. """
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    # Funciones para obtener datos con carga perezosa
    def get_star_wars_data(self):
        """Obtiene los datos de Star Wars con carga perezosa."""
        if self.__class__._star_wars_people is None or self.__class__._star_wars_planets is None:
            self.__class__._star_wars_people, self.__class__._star_wars_planets, characters = self.__class__.controller.load_star_wars_data()
            self.__class__._star_wars_characters = characters
        return self.__class__._star_wars_people, self.__class__._star_wars_planets, self.__class__._star_wars_characters

    def get_pokemon_data(self):
        """Obtiene los datos de Pokemon con carga perezosa."""
        if self.__class__._pokemon_data is None:
            self.__class__._pokemon_data = self.__class__.controller.load_pokemon_data()
        return self.__class__._pokemon_data