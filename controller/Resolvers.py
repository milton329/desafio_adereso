import re
from .ApisInternal import ApisInternalController

class ResolversController():
    _star_wars_characters = None 

    def __init__(self):
        self.controller = ApisInternalController()
        if ResolversController._star_wars_characters is None:
            _, _, ResolversController._star_wars_characters = self.controller.get_star_wars_data()

    def clean_formula(self, formula):
        """Limpia y estandariza la fórmula para asegurar el formato correcto."""
        cleaned = re.sub(r'^.*?["]', '"', formula, flags=re.DOTALL).strip()    
        cleaned = cleaned.replace("“", '"').replace("”", '"').replace("'", '"')       
        if not cleaned.startswith('"'):
            match = re.search(r'"([^"]+)"\s*([-+*/])\s*"([^"]+)"', formula)
            if match:
                return f'"{match.group(1)}" {match.group(2)} "{match.group(3)}"'
        return cleaned

    def extract_entities_and_properties(self, formula):
        """Extrae los nombres de entidades y sus propiedades"""
        pattern = r'"([^"]+) de ([^"]+)"'
        matches = re.findall(pattern, formula)        
        entities_and_props = {}
        for match in matches:
            prop, entity = match
            prop_normalized = prop.lower()            
            if prop_normalized in ["altura", "height"]:
                prop_key = "height"
            elif prop_normalized in ["masa", "mass", "peso", "weight"]:
                prop_key = "mass" if entity in ResolversController._star_wars_characters else "weight"
            elif prop_normalized in ["población", "population"]:
                prop_key = "population"
            elif prop_normalized in ["experiencia base", "base experience", "base_experience"]:
                prop_key = "base_experience"
            elif prop_normalized in ["período de rotación", "rotation_period", "rotación"]:
                prop_key = "rotation_period"
            elif prop_normalized in ["diámetro", "diameter"]:
                prop_key = "diameter"
            elif prop_normalized in ["período orbital", "orbital_period"]:
                prop_key = "orbital_period"
            elif prop_normalized in ["superficie de agua", "surface_water"]:
                prop_key = "surface_water"
            else:
                prop_key = prop_normalized
                
            entities_and_props[f"{prop} de {entity}"] = {"entity": entity, "property": prop_key}        
        return entities_and_props

    def resolve_formula(self, formula):
        """Resuelve una fórmula matemática con nombres de entidades"""
        cleaned_formula = self.clean_formula(formula)
        entities_and_props = self.extract_entities_and_properties(cleaned_formula)        
        values = {}
        errors = []        
        for entity_str, info in entities_and_props.items():
            entity_name = info["entity"]
            property_name = info["property"]            
            pokemon_data = self.controller.get_pokemon(entity_name)
            if "error" not in pokemon_data and property_name in pokemon_data:
                values[entity_str] = pokemon_data[property_name]
                continue            
            character_data = self.controller.get_star_wars_character(entity_name)
            if "error" not in character_data and property_name in character_data:
                values[entity_str] = character_data[property_name]
                continue            
            planet_data = self.controller.get_star_wars_planet(entity_name)
            if "error" not in planet_data and property_name in planet_data:
                values[entity_str] = planet_data[property_name]
                continue            
            errors.append(f"No se pudo encontrar la entidad o propiedad: {entity_str}")        
        if errors:
            return {"error": errors[0], "all_errors": errors}        
        formula_with_values = cleaned_formula
        for entity_str, value in values.items():
            formula_with_values = formula_with_values.replace(f'"{entity_str}"', str(value))        
        try:
            result = eval(formula_with_values)
            return round(result, 10)
        except Exception as e:
            return {"error": f"Error al evaluar la fórmula: {str(e)}", "formula": formula_with_values, "values": values}
