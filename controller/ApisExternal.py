import os
from flask import Flask, request
import requests
from config import POKEAPI_URL, SWAPI_PEOPLE_URL, SWAPI_PLANETS_URL, OPENAI_PROXY_URL, HEADERS, CHALLENGE_URL

class ApisExternalController():

    def challenge_resolver_prueba(self,endpoint,  body):
        """ obetener preguntas para test y real """
        response = requests.post(CHALLENGE_URL+endpoint, headers=HEADERS,json=body)      
        if response.status_code == 200:
            return response
        else:
            return {"error": "No se pudo resolver el problema"}
    
    def challenge_obetener_prueba(self, endpoint):
        """ obetener preguntas para test y real """
        response = requests.get(CHALLENGE_URL+endpoint, headers=HEADERS)      
        if response.status_code == 200:
            return response
        else:
            return {"error": "No se pudo obtener el problema"}

    def call_openai_proxy(self, user_message: str):
        """ Consultar a chatgpt :) sin esto nada seria posible  """
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "developer", "content": """
                IMPORTANTE: Debes generar SOLAMENTE una operación matemática con el siguiente formato exacto:                
                "Propiedad de Entidad" operador "Propiedad de Entidad"                
                Por ejemplo: "Población de Tatooine" - "Altura de Luke Skywalker"                
                No incluyas ningún texto adicional, explicaciones ni frases como "La operación matemática es:" 
                Utiliza exclusivamente los nombres y propiedades de las entidades mencionadas en el problema.
                Usa únicamente caracteres ascii estándar (no uses comillas especiales).                
                Propiedades disponibles:
                - Para planetas (StarWarsPlanet): población (population), período de rotación (rotation_period), 
                período orbital (orbital_period), diámetro (diameter), agua superficial (surface_water)
                - Para personajes (StarWarsCharacter): altura (height), masa (mass)
                - Para Pokémon: experiencia base (base_experience), altura (height), peso (weight)
                """},
                {"role": "user", "content": user_message}
            ]
        }        
        response = requests.post(OPENAI_PROXY_URL, json=payload, headers=HEADERS)        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Error en el servicio de OpenAI", "status_code": response.status_code, "details": response.text}
    
    def get_pokemon(self, name):
        response = requests.get(f"{POKEAPI_URL}{name.lower()}")
        if response.status_code == 200:
            data = response.json()
            return {
                "name": data["name"],
                "base_experience": data["base_experience"],
                "height": data["height"],
                "weight": data["weight"]
            }
        return {"error": "Pokemon not found"}

    def get_star_wars_character(self, name):
        response = requests.get(f"{SWAPI_PEOPLE_URL}?search={name}")
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                character = results[0]
                homeworld_response = requests.get(character["homeworld"])
                homeworld_name = homeworld_response.json().get("name", "Unknown") if homeworld_response.status_code == 200 else "Unknown"
                return {
                    "name": character["name"],
                    "height": self.safe_int(character["height"]),
                    "mass": self.safe_int(character["mass"]),
                    "homeworld": homeworld_name
                }
        return {"error": "Character not found"}

    def get_star_wars_planet(self, name):
        response = requests.get(f"{SWAPI_PLANETS_URL}?search={name}")
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                planet = results[0]
                return {
                    "name": planet["name"],
                    "rotation_period": self.safe_int(planet["rotation_period"]),
                    "orbital_period": self.safe_int(planet["orbital_period"]),
                    "diameter": self.safe_int(planet["diameter"]),
                    "surface_water": self.safe_int(planet["surface_water"]),
                    "population": self.safe_int(planet["population"])
                }
        return {"error": "Planet not found"}

    def safe_int(self, value, default=0):
        """ Convierte un valor a entero si es posible, de lo contrario devuelve el valor por defecto. """
        try:
            return int(value)
        except ValueError:
            return default