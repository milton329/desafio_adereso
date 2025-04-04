import os
from flask import Flask, request
import requests
from config import POKEAPI_URL, SWAPI_PEOPLE_URL, SWAPI_PLANETS_URL, OPENAI_PROXY_URL, HEADERS, CHALLENGE_URL

import time
from typing import Dict, Any
import orjson

# # Crear un objeto de sesión para reutilizar conexiones
# session = requests.Session()
# response = session.get(OPENAI_PROXY_URL, headers=HEADERS)

class ApisExternalController():
    def __init__(self):
        # Inicializar la sesión HTTP al crear la instancia
        self.session = requests.Session()
        # Suponiendo que estas variables están definidas en la clase o se pasan al constructor
        self.OPENAI_PROXY_URL = OPENAI_PROXY_URL  # Reemplaza con tu URL real
        self.HEADERS = HEADERS

    def process_response(response):
        """Procesar respuesta HTTP de manera más eficiente"""
        if response.status_code == 200:
            # orjson es significativamente más rápido que json estándar
            return orjson.loads(response.content)
        return {"error": "Error en la respuesta", "status_code": response.status_code}

    def challenge_resolver_prueba(self, endpoint, body):
        """ obtener preguntas para test y real """
        # Usar la sesión de la clase para mantener conexiones abiertas
        # Si no existe, crear una nueva sesión
        if not hasattr(self, 'session'):
            self.session = requests.Session()
        
        # Cabeceras optimizadas para el rendimiento
        headers = {
            'Content-Type': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        
        # Añadir las cabeceras de autenticación existentes
        if hasattr(self, 'HEADERS'):
            headers.update(self.HEADERS)
        else:
            # Si no está definido en la clase, usar la constante HEADERS
            headers.update(HEADERS)
        
        try:
            # Medir el tiempo de respuesta para diagnóstico
            import time
            start_time = time.time()
            
            # Hacer la llamada a la API usando la sesión
            url = CHALLENGE_URL + endpoint
            response = self.session.post(url, json=body, headers=headers, timeout=10)
            
            # Registrar tiempo de respuesta
            elapsed_time = time.time() - start_time
            #print(f"Tiempo de respuesta de Challenge: {elapsed_time:.2f} segundos")
            
            if response.status_code == 200:
                return response
            else:
                return {
                    "error": "No se pudo resolver el problema",
                    "status_code": response.status_code,
                    "details": response.text
                }
        except requests.exceptions.Timeout:
            return {"error": "Timeout al conectar con el servicio"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Error de conexión: {str(e)}"}
    
    def challenge_obetener_prueba(self, endpoint):
        """Obtener preguntas para test y real con sesión optimizada"""
        
        # Usar la sesión de la clase para mantener conexiones abiertas
        if not hasattr(self, 'session'):
            self.session = requests.Session()
        
        # Cabeceras optimizadas
        headers = {
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        
        # Añadir cabeceras de autenticación si existen
        if hasattr(self, 'HEADERS'):
            headers.update(self.HEADERS)
        else:
            headers.update(HEADERS)
        
        try:
            start_time = time.time()  # Medir tiempo de respuesta
            
            # Hacer la petición GET con la sesión
            url = CHALLENGE_URL + endpoint
            response = self.session.get(url, headers=headers, timeout=10)
            
            elapsed_time = time.time() - start_time
            # print(f"Tiempo de respuesta de Challenge: {elapsed_time:.2f} segundos")
            
            if response.status_code == 200:
                return response
            else:
                return {
                    "error": "No se pudo obtener el problema",
                    "status_code": response.status_code,
                    "details": response.text
                }
        
        except requests.exceptions.Timeout:
            return {"error": "Timeout al conectar con el servicio"}
        
        except requests.exceptions.RequestException as e:
            return {"error": f"Error de conexión: {str(e)}"}

    def call_openai_proxy(self, user_message: str)-> Dict[str, Any]:
        """ Consultar a chatgpt :) sin esto nada seria posible  """
        # Cabeceras optimizadas para el rendimiento
        headers = {
            'Content-Type': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        
        # Añadir las cabeceras de autenticación si existen
        if hasattr(self, 'HEADERS') and self.HEADERS:
            headers.update(self.HEADERS)

        payload = {
            "model": "gpt-4-turbo",
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
            ],
            "temperature": 0.0
        }        
        try:
            # Medir el tiempo de respuesta para diagnóstico
            start_time = time.time()
            
            # Hacer la llamada a la API usando la sesión
            response = self.session.post(self.OPENAI_PROXY_URL, json=payload, headers=headers, timeout=10)
            
            # Registrar tiempo de respuesta
            elapsed_time = time.time() - start_time
            #print(f"Tiempo de respuesta de OpenAI: {elapsed_time:.2f} segundos")
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": "Error en el servicio de OpenAI", 
                    "status_code": response.status_code, 
                    "details": response.text
                }
        except requests.exceptions.Timeout:
            return {"error": "Timeout al conectar con OpenAI"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Error de conexión: {str(e)}"}
    
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