"""
@author: Milton Jaramillo  
@since: 12-03-2025  
@summary: API diseñada para resolver la mayor cantidad de desafíos en 3 minutos, 
con el objetivo de ingresar a la empresa ADERESO.  
¡Vamos con todo, Milton! Tú puedes lograrlo eres el mejor :)  
"""
from flask import Flask
from flask_cors import CORS
from db import initialize_database
from models import create_tables
from routes import app
from controller.ApisInternal import ApisInternalController


initialize_database(app)
create_tables()
controller = ApisInternalController()
controller.create_indices()

if __name__ == "__main__":    
    app.run(debug=True)