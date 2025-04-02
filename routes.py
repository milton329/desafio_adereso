# routes.py
from flask import Flask, request, jsonify
import requests
import time

from controller.ApisExternal import ApisExternalController
from controller.ApisInternal import ApisInternalController
from controller.Resolvers import ResolversController

app = Flask(__name__)

'''
@author: Milton Jaramillo
@since: 12-03-2025
@summary: Servicio para resolver pruebas tanto test como start y resolverlas de manera cíclica hasta finalizar los 3 minutos
'''

@app.route("/resolver_comparar_test", methods=["GET"])
def resolver_comparar_test():
    controller_apiexternal = ApisExternalController()
    controller_resolvers = ResolversController()
    """Ejecuta una prueba en test y devuelve el resultado para saber como estamos para poder comparar :) """
    response = controller_apiexternal.challenge_obetener_prueba("test")    
    if response.status_code == 200:
        data = response.json()
        problem_id = data.get("id")
        problem_text = data.get("problem")
        solution = data.get("solution")                 
        if problem_id and problem_text:
            ai_response = controller_apiexternal.call_openai_proxy(problem_text)            
            formula = ai_response.get("choices", [{}])[0].get("message", {}).get("content", "")
            result = controller_resolvers.resolve_formula(formula)
            valor_enviar = result if isinstance(result, (int, float)) else 0                       
            body = {"problem_id": problem_id,"answer": valor_enviar}
            return {
                "problem": problem_text,
                "formula": controller_resolvers.clean_formula(formula),
                "result_test": solution,
                "result_propio": result,
                "body": body,
            }    
    return {"error": "No se pudo obtener el problema"}

# Variables globales para mantener el estado del problema actual
problem_id_global = None
problem_text_global = None

def resolver_prueba(problem_id, problem_text):
    global problem_id_global, problem_text_global
    controller_apiexternal = ApisExternalController()
    controller_resolvers = ResolversController()    
    if problem_id and problem_text:
        ai_response = controller_apiexternal.call_openai_proxy(problem_text)            
        formula = ai_response.get("choices", [{}])[0].get("message", {}).get("content", "")
        result = controller_resolvers.resolve_formula(formula)
        valor_enviar = result if isinstance(result, (int, float)) else 0
        body = {"problem_id": problem_id, "answer": valor_enviar}
        solution_response = controller_apiexternal.challenge_resolver_prueba("solution", body)        
        if solution_response.status_code == 200:
            result_problema = solution_response.json()
            print("ID Next --- > ", problem_id)
            return solution_response.json()
    return {"error": "No se pudo resolver el problema"}

@app.route("/resolver_prueba_ciclo", methods=["GET"])
def resolver_prueba_ciclo():   
    """Ejecuto una sola sección, honestamente no habia visto los datos de next_problem ofrezco disculpas Carlos :)"""
    # Inicializar variables globales
    global problem_id_global, problem_text_global
    controller_apiexternal = ApisExternalController()
    response = controller_apiexternal.challenge_obetener_prueba("start")
    if response.status_code == 200:
        data_problema = response.json()
        problem_id_global = data_problema.get("id")
        problem_text_global = data_problema.get("problem")
        all_results = []
        count = 0
        while True:  # Bucle infinito hasta que no haya más problemas
            count += 1
            result = resolver_prueba(problem_id_global, problem_text_global)
            all_results.append(result)
            # Si el mensaje es "Time limit exceeded.", detener el ciclo
            if isinstance(result, dict) and result.get("message") == "Time limit exceeded.":
                print(f"¡Límite de tiempo alcanzado después de {count} pruebas!")
                break 
            # Verificar si "next_problem" existe y no es None
            next_problem = result.get("next_problem")
            if next_problem:
                next_id = next_problem.get("id")
                next_text = next_problem.get("problem")
                if next_id and next_text:
                    problem_id_global = next_id
                    problem_text_global = next_text
                else:
                    print("No hay más problemas disponibles, terminando el bucle.")
                    break
            else:
                print("No se recibió el siguiente problema, terminando el bucle.")
                break
        return jsonify({
            "tests_realizados": count,
            "results": all_results
        })    
    return jsonify({"error": "No se pudo inicializar la sesión de la prueba :("})
   

'''
@author: Milton Jaramillo
@since: 12-03-2025
@summary: Servicio para consultar Apis externas, pokemon, star_wars, planets
'''

@app.route("/api_externa/pokemon/<name>", methods=["GET"])
def api_externa_pokemon(name):
    controller = ApisExternalController()
    return jsonify(controller.get_pokemon(name))

@app.route("/api_externa/people/<name>", methods=["GET"])
def api_externa_people(name):
    controller = ApisExternalController()
    return jsonify(controller.get_star_wars_character(name))

@app.route("/api_externa/planets/<name>", methods=["GET"])
def api_externa_planets(name):
    controller = ApisExternalController()
    return jsonify(controller.get_star_wars_planet(name))

'''
@author: Milton Jaramillo
@since: 12-03-2025
@summary: Servicio para consultar Apis internamente con el JSON en memoria, pokemon, star_wars, planets
'''

@app.route("/pokemon/<name>", methods=["GET"])
def pokemon(name):
    controller = ApisInternalController()
    return jsonify(controller.get_pokemon(name))

@app.route("/people/<name>", methods=["GET"])
def people(name):
    controller = ApisInternalController()
    return jsonify(controller.get_star_wars_character(name))

@app.route("/planets/<name>", methods=["GET"])
def planets(name):
    controller = ApisInternalController()
    return jsonify(controller.get_star_wars_planet(name))
