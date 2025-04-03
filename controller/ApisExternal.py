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
                Dado el siguiente problema matemático en lenguaje natural, identifica las entidades y propiedades involucradas. Debes generar solamente una operación matemática, respetando el siguiente formato:
                resultado=Tipo["Entidad"]["Propiedad"] operacioˊn Tipo["Entidad"]["Propiedad"]\text{resultado} = \text{Tipo}["Entidad"]["Propiedad"] \, \text{operación} \, \text{Tipo}["Entidad"]["Propiedad"]resultado=Tipo["Entidad"]["Propiedad"]operacioˊnTipo["Entidad"]["Propiedad"] 
                ________________________________________
                Instrucciones detalladas:
                1.	Extrae las entidades mencionadas en el problema. Puede ser uno o más de los siguientes tipos:
                o	Pokemon
                o	StarWarsCharacter
                o	StarWarsPlanet
                2.	Identifica las propiedades mencionadas dentro del problema. Cada entidad tiene un conjunto de propiedades disponibles:
                o	StarWarsPlanet: "rotation_period", "orbital_period", "diameter", "surface_water", "population"
                o	StarWarsCharacter: "height", "mass"
                o	Pokemon: "base_experience", "height", "weight"
                3.	Detecta la operación matemática que se debe realizar entre estas propiedades (suma +, resta -, multiplicación *, división /).
                4.	Genera la ecuación en el siguiente formato:
                o	resultado = Tipo["Entidad"]["Propiedad"] OPERACIÓN Tipo["Entidad"]["Propiedad"]
                Problema: """},
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