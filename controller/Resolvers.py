import re
import operator
import unicodedata

def normalize_entity_name(name):
    """Convierte nombres como 'Pokémon' a 'Pokemon' eliminando tildes."""
    return unicodedata.normalize("NFKD", name).encode("ASCII", "ignore").decode("ASCII")


class ResolversController():
    def __init__(self, api_controller):
        self.api = api_controller
        self.operators = {
            "+": (1, operator.add),  # (precedence, function)
            "-": (1, operator.sub),
            "*": (2, operator.mul),
            "/": (2, operator.truediv)
        }

    def get_value(self, entity_type, entity_name, property_name):
        """Obtiene el valor de una entidad según su tipo, nombre y propiedad."""
        entity_type = normalize_entity_name(entity_type)  # Normalizar nombres como "Pokémon" → "Pokemon"

        entity_getters = {
            "StarWarsCharacter": self.api.get_star_wars_character,
            "StarWarsPlanet": self.api.get_star_wars_planet,
            "Pokemon": self.api.get_pokemon
        }

        if entity_type not in entity_getters:
            raise ValueError(f"Tipo de entidad desconocido: {entity_type}")

        entity_data = entity_getters[entity_type](entity_name)

        if "error" in entity_data or property_name not in entity_data:
            raise ValueError(f"No se pudo obtener {property_name} de {entity_name}")

        return entity_data[property_name]

    def evaluate_expression(self, expression):
        #print(f"Evaluando expresión: {expression}")
        tokens = self._tokenize(expression)
        #print(f"Tokens generados: {tokens}")
        try:
            output_queue, _ = self._shunting_yard(tokens)
            #print(f"Cola RPN: {output_queue}")
            result = self._evaluate_rpn(output_queue)
            #print(f"Resultado: {result}")
            return result
        except ValueError as e:
            print(f"Error al evaluar la expresión: {e}")
            return None

    def _tokenize(self, expression):
        """Divide la expresión en tokens."""
        tokens = []
        # Updated regex pattern to better match entity expressions
        pattern = r'([\w-]+)\["([^"]+)"\]\["([^"]+)"\]|[\+\-\*/()]|\d+(\.\d+)?|\s+'
        
        current_pos = 0
        expression_len = len(expression)
        
        while current_pos < expression_len:
            # Skip whitespace
            if expression[current_pos].isspace():
                current_pos += 1
                continue
                
            # Check for entity pattern
            entity_match = re.match(r'([\w-]+)\["([^"]+)"\]\["([^"]+)"\]', expression[current_pos:])
            if entity_match:
                tokens.append(entity_match.group(0))
                current_pos += len(entity_match.group(0))
                continue
                
            # Check for operators and parentheses
            if expression[current_pos] in '+-*/()':
                tokens.append(expression[current_pos])
                current_pos += 1
                continue
                
            # Check for numbers
            num_match = re.match(r'\d+(\.\d+)?', expression[current_pos:])
            if num_match:
                tokens.append(num_match.group(0))
                current_pos += len(num_match.group(0))
                continue
                
            # If nothing matched, move to next character
            current_pos += 1
        
        return tokens

    def _shunting_yard(self, tokens):
        """Algoritmo Shunting-Yard para convertir infix a postfix (RPN)."""
        output_queue = []
        operator_stack = []
        entity_pattern = r'([\w-]+)\["([^"\]]+)"\]\["([^"\]]+)"\]'

        for token in tokens:
            if re.match(entity_pattern, token):
                output_queue.append(token)
            elif token in self.operators:
                while operator_stack and operator_stack[-1] != '(' and self.operators[operator_stack[-1]][0] >= self.operators[token][0]:
                    output_queue.append(operator_stack.pop())
                operator_stack.append(token)
            elif token == '(':
                operator_stack.append(token)
            elif token == ')':
                while operator_stack and operator_stack[-1] != '(':
                    output_queue.append(operator_stack.pop())
                if operator_stack and operator_stack[-1] == '(':
                    operator_stack.pop()
                else:
                    print("Paréntesis desbalanceados")
            else:
                print(f"Token desconocido: {token}")

        while operator_stack:
            if operator_stack[-1] == '(':
                print("Paréntesis desbalanceados")
            output_queue.append(operator_stack.pop())

        return output_queue, operator_stack

    def _evaluate_rpn(self, rpn_queue):
        """Evalúa la expresión en Notación Polaca Inversa (RPN)."""
        stack = []
        entity_pattern = r'([\w-]+)\["([^"\]]+)"\]\["([^"\]]+)"\]'

        for token in rpn_queue:
            try:
                entity_match = re.match(entity_pattern, token)
                if entity_match:
                    entity_type, entity_name, property_name = entity_match.groups()
                    try:
                        value = self.get_value(entity_type, entity_name, property_name)
                        if not isinstance(value, (int, float)):
                            print(f"Advertencia: El valor de {entity_name}.{property_name} no es numérico: {value}")
                            # Intentar convertir a número si es posible
                            try:
                                value = float(value)
                            except (ValueError, TypeError):
                                raise ValueError(f"No se puede convertir {value} a número")
                        stack.append(value)
                    except ValueError as e:
                        print(f"Error al obtener {property_name} de {entity_name}: {e}")
                        return None
                elif token in self.operators:
                    if len(stack) < 2:
                        raise ValueError(f"No suficientes operandos para el operador '{token}'. Stack actual: {stack}")
                    operand2 = stack.pop()
                    operand1 = stack.pop()
                    _, operation = self.operators[token]
                    if operation == operator.truediv and operand2 == 0:
                        raise ValueError("Error: División por cero detectada.")
                    stack.append(operation(operand1, operand2))
                elif token.replace('.', '', 1).isdigit():  # Check if token is a number
                    stack.append(float(token))
                else:
                    raise ValueError(f"Token desconocido en la cola RPN: {token}")
            except Exception as e:
                print(f"Error al procesar token '{token}': {e}")
                return None

        if len(stack) == 1:
            return round(stack[0], 10)
        else:
            print(f"Expresión inválida: quedan {len(stack)} elementos en la pila: {stack}")
            return None