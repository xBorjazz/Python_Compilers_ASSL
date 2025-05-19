import csv
import re


class Token:
    def __init__(self, type, value, line=0, column=0):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __str__(self):
        return f"Token({self.type}, '{self.value}', line={self.line}, col={self.column})"


class LexicalAnalyzer:
    def __init__(self):
        self.tokens = []
        self.current_position = 0
        
        # Definición de patrones para tokens
        self.token_patterns = [
            ('INT', r'int'),
            ('FLOAT', r'float'),
            ('RETURN', r'return'),
            ('ID', r'[a-zA-Z][a-zA-Z0-9_]*'),
            ('NUMBER', r'\d+(\.\d+)?'),
            ('PLUS', r'\+'),
            ('MINUS', r'-'),
            ('MULTIPLY', r'\*'),
            ('DIVIDE', r'/'),
            ('ASSIGN', r'='),
            ('SEMICOLON', r';'),
            ('COMMA', r','),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('LBRACE', r'\{'),
            ('RBRACE', r'\}'),
            ('WHITESPACE', r'[ \t\n]+'),
            ('COMMENT', r'//.*')
        ]
        self.token_regex = '|'.join('(?P<%s>%s)' % pair for pair in self.token_patterns)
        self.pattern = re.compile(self.token_regex)
        
    def tokenize(self, code):
        self.tokens = []
        line_num = 1
        line_start = 0
        
        for match in self.pattern.finditer(code):
            token_type = match.lastgroup
            token_value = match.group()
            column = match.start() - line_start
            
            if token_type == 'WHITESPACE':
                line_num += token_value.count('\n')
                if '\n' in token_value:
                    line_start = match.end() - token_value.rfind('\n') - 1
                continue
            elif token_type == 'COMMENT':
                continue
            else:
                self.tokens.append(Token(token_type, token_value, line_num, column))
                
        # Añadir un token de fin de archivo
        self.tokens.append(Token('EOF', '', line_num, 0))
        self.current_position = 0
        return self.tokens
    
    def next_token(self):
        if self.current_position < len(self.tokens):
            token = self.tokens[self.current_position]
            self.current_position += 1
            return token
        return None
    
    def peek_token(self):
        if self.current_position < len(self.tokens):
            return self.tokens[self.current_position]
        return None


class GrammarRule:
    def __init__(self, left, right):
        self.left = left
        self.right = right if right != ['ε'] else []  # Manejar epsilon producciones
    
    def __str__(self):
        right_str = ' '.join(self.right) if self.right else 'ε'
        return f"{self.left} → {right_str}"


class SyntaxAnalyzer:
    def __init__(self, grammar_file, parse_table_file):
        self.grammar = []
        self.parse_table = {}
        self.terminals = set()
        self.non_terminals = set()
        self.stack = ['$']  # Inicializar con el símbolo de fin de entrada
        self.input_tokens = []
        self.current_token_index = 0
        self.stack_trace = []
        
        self.load_grammar(grammar_file)
        self.load_parse_table(parse_table_file)
    
    def load_grammar(self, grammar_file):
        """Carga las reglas de gramática desde un archivo .inf"""
        try:
            with open(grammar_file, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parsear la regla de producción
                    parts = line.split('->')
                    if len(parts) != 2:
                        continue
                    
                    left = parts[0].strip()
                    right_parts = parts[1].strip().split()
                    
                    rule = GrammarRule(left, right_parts)
                    self.grammar.append(rule)
                    
                    # Actualizar terminales y no terminales
                    self.non_terminals.add(left)
                    for symbol in right_parts:
                        if not symbol.isupper() and symbol != 'ε':
                            self.terminals.add(symbol)
            
            print(f"Gramática cargada: {len(self.grammar)} reglas")
            for rule in self.grammar:
                print(rule)
        except Exception as e:
            print(f"Error al cargar la gramática: {e}")
    
    def load_parse_table(self, parse_table_file):
        """Carga la tabla de análisis sintáctico desde un archivo .csv"""
        try:
            with open(parse_table_file, 'r', newline='') as file:
                reader = csv.reader(file)
                headers = next(reader)  # Leer la primera fila como encabezados
                
                # Eliminar la primera columna que contiene los no terminales
                terminals = headers[1:]
                
                for row in reader:
                    non_terminal = row[0]
                    for i, cell in enumerate(row[1:]):
                        if cell and cell != '':
                            terminal = terminals[i]
                            self.parse_table[(non_terminal, terminal)] = cell
            
            print(f"Tabla de análisis cargada con {len(self.parse_table)} entradas")
        except Exception as e:
            print(f"Error al cargar la tabla de análisis: {e}")
    
    def analyze(self, tokens):
        """Realiza el análisis sintáctico usando la tabla de análisis LL(1)"""
        self.input_tokens = tokens
        self.current_token_index = 0
        self.stack = ['$', 'program']  # Empezar con el símbolo inicial
        self.stack_trace = []
        
        while len(self.stack) > 0:
            # Guardar el estado actual de la pila para el trace
            self.stack_trace.append(self.stack.copy())
            
            top = self.stack[-1]
            current_token = self.current_token() if self.current_token_index < len(tokens) else Token('EOF', '$')
            
            print(f"Pila: {self.stack}, Token: {current_token.type}:{current_token.value}")
            
            if top == '$' and current_token.type == 'EOF':
                # Análisis completado con éxito
                print("Análisis sintáctico completado con éxito")
                return True
            
            if top in self.terminals or top == '$':
                # Si el tope de la pila es un terminal, debe coincidir con el token actual
                if (top == current_token.value) or (top == '$' and current_token.type == 'EOF'):
                    self.stack.pop()
                    self.current_token_index += 1
                else:
                    print(f"Error sintáctico: Se esperaba '{top}', pero se encontró '{current_token.value}'")
                    return False
            else:
                # Si el tope es un no terminal, consultar la tabla de análisis
                token_type = current_token.type if current_token.type != 'ID' and current_token.type != 'NUMBER' else current_token.value
                table_key = (top, token_type)
                
                if table_key in self.parse_table:
                    production = self.parse_table[table_key]
                    self.stack.pop()
                    
                    # Expandir la producción y añadir a la pila en orden inverso
                    if production != 'ε':  # Si no es una producción epsilon
                        production_symbols = production.split()
                        for symbol in reversed(production_symbols):
                            self.stack.append(symbol)
                else:
                    print(f"Error sintáctico: No hay entrada en la tabla para ({top}, {token_type})")
                    return False
        
        return True
    
    def current_token(self):
        if self.current_token_index < len(self.input_tokens):
            return self.input_tokens[self.current_token_index]
        return Token('EOF', '$')
    
    def get_stack_trace(self):
        return self.stack_trace


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}
        self.function_table = {}
        self.current_scope = "global"
        self.errors = []
    
    def enter_scope(self, scope_name):
        self.current_scope = scope_name
    
    def exit_scope(self):
        self.current_scope = "global"
    
    def add_variable(self, name, var_type):
        key = f"{self.current_scope}.{name}"
        if key in self.symbol_table:
            self.errors.append(f"Error semántico: Variable '{name}' ya declarada en el ámbito '{self.current_scope}'")
            return False
        
        self.symbol_table[key] = {
            "name": name,
            "type": var_type,
            "scope": self.current_scope
        }
        return True
    
    def add_function(self, name, return_type, parameters):
        if name in self.function_table:
            self.errors.append(f"Error semántico: Función '{name}' ya declarada")
            return False
        
        self.function_table[name] = {
            "name": name,
            "return_type": return_type,
            "parameters": parameters
        }
        return True
    
    def get_variable_type(self, name):
        # Primero buscar en el ámbito actual
        key = f"{self.current_scope}.{name}"
        if key in self.symbol_table:
            return self.symbol_table[key]["type"]
        
        # Luego buscar en el ámbito global si no estamos ya en él
        if self.current_scope != "global":
            key = f"global.{name}"
            if key in self.symbol_table:
                return self.symbol_table[key]["type"]
        
        return None
    
    def check_function_call(self, name, arguments):
        if name not in self.function_table:
            self.errors.append(f"Error semántico: Función '{name}' no declarada")
            return False
        
        func_info = self.function_table[name]
        if len(arguments) != len(func_info["parameters"]):
            self.errors.append(f"Error semántico: Número incorrecto de argumentos para la función '{name}'")
            return False
        
        # Comprobar tipos de argumentos
        for i, (arg_type, param_type) in enumerate(zip(arguments, func_info["parameters"])):
            if not self.check_type_compatibility(arg_type, param_type):
                self.errors.append(f"Error semántico: Tipo incompatible en el argumento {i+1} para la función '{name}'")
                return False
        
        return True
    
    def check_type_compatibility(self, type1, type2):
        # Reglas simples de compatibilidad de tipos
        if type1 == type2:
            return True
        
        # Permitir conversión implícita de int a float
        if type1 == "int" and type2 == "float":
            return True
        
        return False
    
    def check_operation(self, left_type, operator, right_type):
        if left_type is None or right_type is None:
            return None
        
        # Operaciones aritméticas básicas
        if operator in ['+', '-', '*', '/']:
            if left_type == "int" and right_type == "int":
                return "int"
            elif left_type in ["int", "float"] and right_type in ["int", "float"]:
                return "float"
        
        # Operaciones de asignación
        elif operator == '=':
            if self.check_type_compatibility(right_type, left_type):
                return left_type
            else:
                self.errors.append(f"Error semántico: No se puede asignar valor de tipo '{right_type}' a variable de tipo '{left_type}'")
                return None
        
        self.errors.append(f"Error semántico: Operación no válida entre tipos '{left_type}' y '{right_type}'")
        return None
    
    def get_errors(self):
        return self.errors


class Translator:
    def __init__(self, grammar_file, parse_table_file):
        self.lexical_analyzer = LexicalAnalyzer()
        self.syntax_analyzer = SyntaxAnalyzer(grammar_file, parse_table_file)
        self.semantic_analyzer = SemanticAnalyzer()
    
    def process_code(self, code):
        print("=== Análisis Léxico ===")
        tokens = self.lexical_analyzer.tokenize(code)
        for token in tokens:
            print(token)
        
        print("\n=== Análisis Sintáctico ===")
        if self.syntax_analyzer.analyze(tokens):
            print("Código sintácticamente correcto")
            
            # Mostrar traza de la pila
            print("\n=== Traza de la Pila ===")
            stack_trace = self.syntax_analyzer.get_stack_trace()
            for i, stack in enumerate(stack_trace):
                print(f"${i}: {stack}")
            
            print("\n=== Análisis Semántico ===")
            # Aquí iría el código para el análisis semántico
            # Este es un placeholder para la implementación real
            
            return True
        else:
            print("Código con errores sintácticos")
            return False


# Ejemplo de uso
if __name__ == "__main__":
    # Archivos que contienen la gramática y la tabla de análisis
    grammar_file = "compilador.inf"
    parse_table_file = "compilador.csv"
    
    # Crear el traductor
    translator = Translator(grammar_file, parse_table_file)
    
    # Ejemplo 1
    code1 = """
    int main(){
        float a;
        int b;
        int c;
        c = a+b;
        c = suma(8,9);
    }
    """
    
    print("Analizando Ejemplo 1:")
    translator.process_code(code1)
    
    # Ejemplo 2
    code2 = """
    int a;
    int suma(int a, int b){
        return a+b;
    }
    int main(){
        float a;
        int b;
        int c;
        c = a+b;
        c = suma(8.5,9.9);
    }
    """
    
    print("\nAnalizando Ejemplo 2:")
    translator.process_code(code2)
