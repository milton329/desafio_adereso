
import datetime
from peewee import (Model, CharField, IntegerField, FloatField, ForeignKeyField, DateTimeField, OperationalError)
from db import db

class StarWarsPlanet(Model):
    name = CharField(unique=True, null=False)
    rotation_period = IntegerField(null=False)
    orbital_period = IntegerField(null=False)
    diameter = IntegerField(null=False)
    surface_water = IntegerField(null=False)
    population = IntegerField(null=False)
    
    class Meta:
        database = db

class StarWarsCharacter(Model):
    name = CharField(unique=True, null=False)
    height = IntegerField(null=False)
    mass = IntegerField(null=False)
    homeworld = ForeignKeyField(StarWarsPlanet, backref='residents')
    
    class Meta:
        database = db

class Pokemon(Model):
    name = CharField(unique=True, null=False)
    base_experience = IntegerField(null=False)
    height = IntegerField(null=False)
    weight = IntegerField(null=False)
    
    class Meta:
        database = db

def create_tables():
    try:
        with db:
            db.create_tables([StarWarsPlanet, StarWarsCharacter, Pokemon])
    except OperationalError:
        print("Error creando tablas.")
