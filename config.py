import os
from dotenv import load_dotenv
load_dotenv()

# Variables
OPENAI_PROXY_URL = os.getenv("OPENAI_PROXY_URL")
CHALLENGE_URL = os.getenv("CHALLENGE_URL")
API_KEY =  os.getenv("API_KEY")
HEADERS = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}
POKEAPI_URL = os.getenv("POKEAPI_URL")
SWAPI_PEOPLE_URL = os.getenv("SWAPI_PEOPLE_URL")
SWAPI_PLANETS_URL = os.getenv("SWAPI_PLANETS_URL")


# Conexión a BD de MySQL
DATABASE_PARAMS = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'port': int(os.getenv('DB_PORT', '3306')),
}