#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import csv
from tabulate import tabulate  # Para generar tablas bonitas en la salida

# --- Token Class ---
class Token:
    def __init__(self, tipo, valor, linea, columna):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.columna = columna

    def __str__(self):
        return f"Token({self.tipo}, '{self.valor}', {self.linea}, {self.columna})"

    def __repr__(self):
        return str(self)

# --- Lexer Class ---
class AnalizadorLexico:
    def __init__(self, codigo_fuente):
        self.codigo_fuente = codigo_fuente
        self.posicion = 0
        self.linea = 1
        self.columna = 1
        self.tokens = []
        self.palabras_reservadas = {
            'int': 'TIPO_DATO',
            'char': 'TIPO_DATO',
            'float': 'TIPO_DATO',
            'void': 'TIPO_DATO',
            'main': 'MAIN',
            'if': 'IF',
            'else': 'ELSE',
            'while': 'WHILE',
            'return': 'RETURN'
        }

        # Define patrones de tokens (orden importa: más específicos primero)
        self.patrones = [
            (r'\s+', None),  # Ignorar espacios en blanco, incluyendo saltos de línea
            (r'//.*', None), # Comentarios de línea
            (r'/\*.*?\*/', None, re.DOTALL), # Comentarios de bloque (.*? para no ser greedy)
            (r'(int|char|float|void)\b', 'TIPO_DATO'),
            (r'(main|if|else|while|return)\b', lambda val: val.upper()), # Palabras reservadas genéricas
            (r'[a-zA-Z_][a-zA-Z0-9_]*', 'ID'),
            (r'\d+\.\d+', 'NUM_FLOAT'),
            (r'\d+', 'NUM_INT'),
            (r'"[^"]*"', 'CADENA'), # Strings
            (r"'([^'\\]|\\.)'", 'CARACTER'), # Caracteres (incluyendo escapes)
            (r'<=', 'OP_RELAC'),
            (r'>=', 'OP_RELAC'),
            (r'==', 'OP_IGUALDAD'),
            (r'!=', 'OP_IGUALDAD'),
            (r'<', 'OP_RELAC'),
            (r'>', 'OP_RELAC'),
            (r'\+', 'OP_SUMA'),
            (r'-', 'OP_RESTA'),
            (r'\*', 'OP_MULT'),
            (r'/', 'OP_DIV'),
            (r'=', 'OP_ASIG'),
            (r'\(', 'PARENTESIS_IZQ'),
            (r'\)', 'PARENTESIS_DER'),
            (r'{', 'LLAVE_IZQ'),
            (r'}', 'LLAVE_DER'),
            (r';', 'PUNTO_COMA'),
            (r',', 'COMA'),
            # Agregar otros operadores o puntuación según la gramática si son necesarios
        ]

    def analizar(self):
        """Realiza el análisis léxico y devuelve la lista de tokens."""
        lineas = self.codigo_fuente.splitlines()
        self.codigo_fuente = self.codigo_fuente + '\n' # Asegurar que termina con newline para comentarios

        for self.linea, linea_texto in enumerate(lineas, 1):
            self.columna = 1
            linea_texto = linea_texto + '\n' # Procesar línea por línea

            while self.columna -1 < len(linea_texto): # -1 porque columna es 1-based

                found_match = False
                for pattern in self.patrones:
                    regex = re.compile(pattern[0])
                    match = regex.match(linea_texto, self.columna -1) # Match desde la columna actual

                    if match:
                        found_match = True
                        valor = match.group(0)
                        token_type_def = pattern[1]
                        flags = pattern[2] if len(pattern) > 2 else 0

                        if token_type_def is not None: # No es espacio o comentario
                            tipo = None
                            if isinstance(token_type_def, str):
                                tipo = token_type_def
                            elif callable(token_type_def):
                                tipo = token_type_def(valor)

                            # Manejo de palabras reservadas que no están en la lista directa
                            if tipo == 'ID' and valor in self.palabras_reservadas:
                                tipo = self.palabras_reservadas[valor]

                            self.tokens.append(Token(tipo, valor, self.linea, self.columna))

                        # Actualizar posición y columna
                        chars_consumed = len(valor)
                        self.columna += chars_consumed
                        self.posicion += chars_consumed # Mantener posición global si es necesario, aunque no se usa mucho

                        # Si el patrón era para toda la línea (como comentarios de línea), salir del inner loop
                        if flags == re.DOTALL and valor.endswith('\n'):
                             break

                        break # Pasar al siguiente carácter de la línea actual

                if not found_match:
                     # Carácter no reconocido en la línea actual
                    error_char = linea_texto[self.columna -1]
                    print(f"Error léxico: Carácter inesperado '{error_char}' en línea {self.linea}, columna {self.columna}", file=sys.stderr)
                    self.columna += 1 # Avanzar para intentar encontrar más errores
                    # En un compilador real, podrías querer salir o intentar recuperarte

        # Agregar token de fin de archivo
        self.tokens.append(Token('EOF', '', self.linea, self.columna))
        return self.tokens


# --- AST Node Class ---
class NodoAST:
    # Atributos semánticos
    tipoDato = None # Para inferencia/verificación de tipos ('i', 'f', 'c', 'v', None)
    # tablasimbolos y ambito no serán estáticos en Python como en C++,
    # se pasarán durante la validación o se accederán desde el AnalizadorSemantico

    def __init__(self, tipo, valor=None, hijos=None):
        self.tipo = tipo
        self.valor = valor
        self.hijos = hijos if hijos is not None else []
        self.tipoDato = None # Inicializar tipoDato aquí

    def agregar_hijo(self, hijo):
        if hijo is not None:
             self.hijos.append(hijo)

    def __str__(self):
        return f"{self.tipo}{f'({self.valor})' if self.valor is not None else ''}"

    def __repr__(self):
        return self.__str__()

    # Método virtual (adaptado a Python) para validación semántica
    def validaTipos(self, tabla_simbolos, errores):
        """
        Método para validación semántica de este nodo y sus hijos.
        Debe ser sobreescrito en nodos específicos (expresiones, declaraciones, etc.).
        """
        # Implementación base: simplemente valida hijos
        # print(f"Validando nodo {self.tipo}") # Debugging
        for hijo in self.hijos:
            if hijo: # Asegurarse de que el hijo no sea None
                 hijo.validaTipos(tabla_simbolos, errores)


# --- Symbol Table Class ---
class TablaSimbolo:
    def __init__(self, errores_list):
        # Usando un stack para manejar ámbitos anidados
        self.ambitos = [{}] # El primer dict es el ámbito global
        self.errores_list = errores_list # Lista compartida de errores

    def entrar_ambito(self, nombre_ambito="local"):
        """Crea un nuevo ámbito en el stack."""
        self.ambitos.append({})
        # print(f"Entrando a ámbito: {nombre_ambito}, Nivel: {len(self.ambitos) - 1}") # Debugging

    def salir_ambito(self):
        """Remueve el ámbito actual del stack."""
        if len(self.ambitos) > 1: # No salir del ámbito global
            # print(f"Saliendo de ámbito, Nivel: {len(self.ambitos) - 1}") # Debugging
            self.ambitos.pop()
        # else:
            # print("Advertencia: Intentando salir del ámbito global.") # Debugging


    def insertar(self, nombre, tipo, categoria, token=None):
        """
        Inserta un símbolo en el ámbito actual.
        Retorna True si la inserción fue exitosa (no redeclaración), False en caso contrario.
        """
        ambito_actual = self.ambitos[-1]
        nivel_actual = len(self.ambitos) - 1

        if nombre in ambito_actual:
            # Error: Redeclaración en el ámbito actual
            error_msg = f"Error semántico: Redeclaración de '{nombre}' en el ámbito actual."
            if token:
                 error_msg += f" (Línea: {token.linea}, Columna: {token.columna})"
            self.errores_list.append(error_msg)
            # print(error_msg) # Debugging
            return False
        else:
            ambito_actual[nombre] = {
                "nombre": nombre,
                "tipo": tipo, # Tipo de dato ('int', 'float', etc.)
                "categoria": categoria, # 'variable', 'funcion', 'parametro'
                "nivel": nivel_actual,
                # Puedes agregar más info como parámetros para funciones, etc.
            }
            # print(f"Insertado: {nombre} ({categoria}: {tipo}) en nivel {nivel_actual}") # Debugging
            return True

    def buscar(self, nombre):
        """
        Busca un símbolo desde el ámbito actual hacia arriba (global).
        Retorna el diccionario del símbolo si lo encuentra, None en caso contrario.
        """
        for i in range(len(self.ambitos) -1, -1, -1):
            if nombre in self.ambitos[i]:
                # print(f"Encontrado: {nombre} en nivel {i}") # Debugging
                return self.ambitos[i][nombre]
        # print(f"No encontrado: {nombre}") # Debugging
        return None

    def buscar_en_ambito_actual(self, nombre):
        """Busca un símbolo solo en el ámbito actual."""
        ambito_actual = self.ambitos[-1]
        return ambito_actual.get(nombre)


    def muestra(self):
        """Muestra el contenido de la tabla de símbolos por ámbitos."""
        print("\nTabla de Símbolos:")
        for i, ambito in enumerate(self.ambitos):
            print(f"--- Ámbito Nivel {i} ---")
            if not ambito:
                print("  (Vacío)")
            else:
                for nombre, simbolo in ambito.items():
                    print(f"  {nombre}: {simbolo}")
        print("--------------------")


# --- Semantic Analysis Logic in AST Nodes ---

# Sobreescribir validaTipos en nodos relevantes

def get_char_tipo(tipo_str):
    """Convierte el tipo string a char ('i', 'f', 'c', 'v')."""
    if tipo_str == 'int': return 'i'
    if tipo_str == 'float': return 'f'
    if tipo_str == 'char': return 'c'
    if tipo_str == 'void': return 'v'
    return None # Tipo desconocido

# Nodo para tipo de dato
class NodoTipoDato(NodoAST):
    def __init__(self, valor, token=None):
         super().__init__('tipo', valor)
         self.token = token

    def validaTipos(self, tabla_simbolos, errores):
        self.tipoDato = get_char_tipo(self.valor)
        # No valida hijos, es un nodo hoja de tipo


# Nodos de Declaración
class NodoDeclaracionVariable(NodoAST):
    def __init__(self, tipo_nodo, id_nodo):
        super().__init__('declaracion_variable')
        self.agregar_hijo(tipo_nodo) # hijo[0] = tipo
        self.agregar_hijo(id_nodo)   # hijo[1] = id

    def validaTipos(self, tabla_simbolos, errores):
        # Validar hijos primero para que tengan tipoDato
        self.hijos[0].validaTipos(tabla_simbolos, errores) # Valida tipo
        # No validar id_nodo aquí, solo se usa su valor

        tipo_str = self.hijos[0].valor # 'int', 'float', etc.
        id_nombre = self.hijos[1].valor # Nombre de la variable
        id_token = getattr(self.hijos[1], 'token', None) # Obtener token original si está guardado

        # Insertar en la tabla de símbolos del ámbito actual
        # La función insertar ya maneja la verificación de redeclaración y añade error
        tabla_simbolos.insertar(id_nombre, tipo_str, 'variable', token=id_token)

class NodoDeclaracionFuncion(NodoAST):
    def __init__(self, tipo_nodo, id_nodo, parametros_nodo, bloque_nodo):
        super().__init__('funcion', id_nodo.valor) # Valor es el nombre de la función
        self.agregar_hijo(tipo_nodo)      # hijo[0] = tipo retorno
        # No agregamos id_nodo como hijo directo del AST para no duplicar
        self.id_nombre = id_nodo.valor
        self.agregar_hijo(parametros_nodo) # hijo[1] = parametros
        self.agregar_hijo(bloque_nodo)     # hijo[2] = bloque
        self.return_type_str = tipo_nodo.valor # Guardar el tipo de retorno

    def validaTipos(self, tabla_simbolos, errores):
        # Validar el tipo de retorno
        self.hijos[0].validaTipos(tabla_simbolos, errores)
        return_char_tipo = self.hijos[0].tipoDato # 'i', 'f', 'v', etc.

        # Verificar si la función ya está declarada en el ámbito global
        # Asumimos que las funciones se declaran en el ámbito global
        simbolo_existente = tabla_simbolos.buscar(self.id_nombre)
        if simbolo_existente and simbolo_existente['nivel'] == 0: # Nivel 0 es global
             errores.append(f"Error semántico: La función '{self.id_nombre}' ya está definida.")
             # No insertar si ya existe para evitar conflictos, pero continuar análisis


        # Insertar la función en la tabla de símbolos (ámbito global)
        # Nota: Esto solo inserta la función, no sus parámetros o variables locales aún.
        # La inserción debe ocurrir ANTES de entrar al ámbito de la función.
        if not simbolo_existente or simbolo_existente['nivel'] != 0: # Insertar solo si no estaba definida globalmente
             tabla_simbolos.insertar(self.id_nombre, self.return_type_str, 'funcion') # Guardar tipo de retorno string

        # Entrar al ámbito de la función
        tabla_simbolos.entrar_ambito(self.id_nombre)

        # Validar parámetros (se insertarán en el nuevo ámbito)
        self.hijos[1].validaTipos(tabla_simbolos, errores) # Valida nodo 'parametros'

        # Validar el bloque de la función
        self.hijos[2].validaTipos(tabla_simbolos, errores) # Valida nodo 'bloque'

        # Salir del ámbito de la función
        tabla_simbolos.salir_ambito()

class NodoFuncionMain(NodoDeclaracionFuncion): # main es un tipo especial de función
     def __init__(self, tipo_nodo, id_nodo, parametros_nodo, bloque_nodo):
         super().__init__(tipo_nodo, id_nodo, parametros_nodo, bloque_nodo)
         self.tipo = 'funcion_main' # Sobreescribir tipo
         self.id_nombre = 'main' # Nombre fijo

     def validaTipos(self, tabla_simbolos, errores):
         # Validar tipo de retorno (debería ser int o void según convenciones, pero la gramática permite 'tipo')
         self.hijos[0].validaTipos(tabla_simbolos, errores)
         return_char_tipo = self.hijos[0].tipoDato

         # Insertar 'main' en la tabla de símbolos (ámbito global)
         # main no debería tener redeclaración si la gramática es correcta
         tabla_simbolos.insertar('main', self.return_type_str, 'funcion') # Guardar tipo de retorno string

         # Entrar al ámbito de main
         tabla_simbolos.entrar_ambito('main')

         # Validar parámetros (main usualmente no tiene o tiene un formato específico, la gramática permite 'parametros')
         self.hijos[1].validaTipos(tabla_simbolos, errores) # Valida nodo 'parametros'

         # Validar el bloque de main
         self.hijos[2].validaTipos(tabla_simbolos, errores) # Valida nodo 'bloque'

         # Salir del ámbito de main
         tabla_simbolos.salir_ambito()


class NodoParametros(NodoAST):
     def __init__(self, parametros_nodos):
         super().__init__('parametros', hijos=parametros_nodos)

     def validaTipos(self, tabla_simbolos, errores):
         # Los parámetros se insertan en la tabla de símbolos del ámbito de la función que los contiene
         for param_nodo in self.hijos:
             param_nodo.validaTipos(tabla_simbolos, errores) # Valida cada nodo 'parametro'


class NodoParametro(NodoAST):
     def __init__(self, tipo_nodo, id_nodo):
         super().__init__('parametro')
         self.agregar_hijo(tipo_nodo) # hijo[0] = tipo
         self.agregar_hijo(id_nodo)   # hijo[1] = id

     def validaTipos(self, tabla_simbolos, errores):
         # Validar hijos
         self.hijos[0].validaTipos(tabla_simbolos, errores) # Valida tipo
         # No validar id_nodo

         tipo_str = self.hijos[0].valor
         id_nombre = self.hijos[1].valor
         id_token = getattr(self.hijos[1], 'token', None) # Obtener token original

         # Insertar en la tabla de símbolos del ámbito actual (que debería ser el de la función)
         # La función insertar ya maneja la verificación de redeclaración dentro del ámbito
         tabla_simbolos.insertar(id_nombre, tipo_str, 'parametro', token=id_token)


class NodoBloque(NodoAST):
    def __init__(self, sentencias_nodos):
        super().__init__('bloque', hijos=sentencias_nodos)

    def validaTipos(self, tabla_simbolos, errores):
        # Entrar a un nuevo ámbito para el bloque (si no es el bloque principal de una función)
        # Sin embargo, la gramática parece manejar variables locales dentro del BloqFunc,
        # sugiriendo que el ámbito de la función es suficiente. Si hubiera bloques anidados {}
        # dentro de sentencias, cada uno necesitaría su propio ámbito.
        # Para esta gramática, asumir que variables locales están en el ámbito de la función.
        # Si el parser crea NodoBloque para {} dentro de if/while, SÍ necesitamos nuevo ámbito.
        # Vamos a entrar a ámbito aquí, y salir después de validar hijos. Esto maneja bloques anidados correctamente.

        # Ojo: Esto puede duplicar la entrada/salida de ámbito para el bloque principal de una función
        # si el parser crea un Bloque para BloqFunc. Revisar la lógica del parser.
        # Si BloqFunc ::= { DefLocales }, el parser crea un NodoBloque. La entrada/salida YA
        # se hace en NodoDeclaracionFuncion. Entonces, NO debemos entrar/salir aquí si es el bloque raíz de una función.
        # ¿Cómo saber si es el bloque raíz de una función? Es complicado sin más contexto del AST.
        # Una alternativa es que el parser NO cree un nodo Bloque para BloqFunc, sino que ponga las sentencias/declaraciones locales directamente como hijos de la función.
        # Dado el parser actual (compilador2.py), sí crea un nodo Bloque. Ajustemos: si es el bloque principal de función, el ámbito ya se manejó. Si no, es un bloque anidado.
        # Esto es difícil de determinar solo desde el nodo Bloque.

        # Aproximación 1 (Simple): Entrar y salir de ámbito para CADA nodo Bloque. Esto puede crear demasiados ámbitos pequeños pero es seguro para variables locales dentro de {}.
        # tabla_simbolos.entrar_ambito() # <-- Descomentar si cada {} crea un nuevo ámbito

        # Validar sentencias dentro del bloque
        for sentencia_nodo in self.hijos:
             if sentencia_nodo:
                  sentencia_nodo.validaTipos(tabla_simbolos, errores)

        # tabla_simbolos.salir_ambito() # <-- Descomentar si cada {} crea un nuevo ámbito


# Nodos de Sentencia
class NodoAsignacion(NodoAST):
     def __init__(self, id_nodo, expresion_nodo):
         super().__init__('asignacion')
         self.agregar_hijo(id_nodo)      # hijo[0] = id (variable)
         self.agregar_hijo(expresion_nodo) # hijo[1] = expresion

     def validaTipos(self, tabla_simbolos, errores):
         # Validar la expresión primero para obtener su tipoDato
         self.hijos[1].validaTipos(tabla_simbolos, errores)
         tipo_expr = self.hijos[1].tipoDato # Tipo inferido de la expresión

         # Validar la variable (hijo[0] es el nodo ID)
         id_nodo = self.hijos[0]
         var_nombre = id_nodo.valor
         var_token = getattr(id_nodo, 'token', None)

         # Buscar la variable en la tabla de símbolos (en cualquier ámbito visible)
         simbolo_var = tabla_simbolos.buscar(var_nombre)

         if not simbolo_var:
             errores.append(f"Error semántico: Uso de variable no declarada '{var_nombre}'.")
             # No podemos verificar tipos si la variable no existe
             self.tipoDato = None # No se pudo determinar el tipo del resultado de la asignación (que es void o el tipo asignado)
         else:
             tipo_var_str = simbolo_var['tipo'] # Tipo declarado de la variable
             tipo_var_char = get_char_tipo(tipo_var_str) # Tipo char de la variable

             # Verificar compatibilidad de tipos (reglas de conversión simples)
             es_compatible = False
             if tipo_expr is not None and tipo_var_char is not None:
                 if tipo_var_char == tipo_expr: # Tipos idénticos
                     es_compatible = True
                 elif tipo_var_char == 'f' and tipo_expr == 'i': # int a float es válido
                     es_compatible = True
                 # Podrías añadir más reglas de conversión aquí (ej: int a char si cabe)

             if not es_compatible:
                  errores.append(f"Error semántico: Incompatibilidad de tipos en asignación a '{var_nombre}'. Se esperaba '{tipo_var_str}', pero la expresión es de tipo '{tipo_expr}'.")
                  self.tipoDato = None # Error de tipo, resultado desconocido
             else:
                 self.tipoDato = tipo_var_char # El resultado de la asignación es el tipo de la variable
                 # Podrías incluso almacenar el valor si haces análisis de flujo de datos
                 # simbolo_var['valor'] = ... # Requeriría evaluar la expresión (análisis de constantes)


class NodoLlamadaFuncion(NodoAST): # Para sentencias como func();
     def __init__(self, id_nodo, argumentos_nodo):
         super().__init__('llamada_funcion', id_nodo.valor) # Valor es el nombre de la función
         self.agregar_hijo(argumentos_nodo) # hijo[0] = argumentos
         self.function_name = id_nodo.valor
         self.name_token = getattr(id_nodo, 'token', None)

     def validaTipos(self, tabla_simbolos, errores):
         # Validar argumentos primero
         self.hijos[0].validaTipos(tabla_simbolos, errores) # Valida nodo 'argumentos'

         # Buscar la función en la tabla de símbolos
         simbolo_func = tabla_simbolos.buscar(self.function_name)

         if not simbolo_func or simbolo_func.get('categoria') != 'funcion':
             errores.append(f"Error semántico: Llamada a identificador no declarado o que no es función '{self.function_name}'.")
             self.tipoDato = 'v' # Tipo void para llamadas fallidas o sin retorno conocido
             # No podemos verificar argumentos si la función no existe/no es función
         else:
             func_return_type_str = simbolo_func['tipo'] # Tipo de retorno declarado
             self.tipoDato = get_char_tipo(func_return_type_str) # Establecer tipoDato del nodo llamada

             # TODO: Verificar número y tipo de argumentos
             # Esto requiere que la tabla de símbolos almacene la signatura de la función (tipos de parámetros)
             # Y comparar con los tipoDato inferidos de los nodos de argumentos (hijos[0].hijos)
             expected_params = [] # Necesitas obtener esto del simbolo_func
             provided_args = self.hijos[0].hijos # Lista de nodos de argumento

             # if len(provided_args) != len(expected_params):
             #     errores.append(f"Error semántico: Número incorrecto de argumentos para la función '{self.function_name}'. Se esperaba {len(expected_params)}, se encontraron {len(provided_args)}.")
             # else:
             #     for i, arg_node in enumerate(provided_args):
             #         expected_type = expected_params[i]['tipo'] # Tipo esperado del parámetro
             #         provided_type = arg_node.tipoDato # Tipo inferido del argumento
             #         if provided_type is not None and expected_type is not None and provided_type != expected_type:
             #             # Podrías permitir conversiones (int a float), ajustar la comparación aquí
             #             errores.append(f"Error semántico: Tipo de argumento incorrecto en la llamada a '{self.function_name}'. El argumento {i+1} esperaba '{expected_type}', se encontró '{provided_type}'.")


class NodoRetorno(NodoAST):
     def __init__(self, expresion_nodo=None):
         super().__init__('retorno')
         if expresion_nodo:
             self.agregar_hijo(expresion_nodo) # hijo[0] = expresion (opcional)

     def validaTipos(self, tabla_simbolos, errores):
         returned_type_char = 'v' # Tipo por defecto si no hay expresión de retorno

         if self.hijos: # Hay expresión de retorno
             self.hijos[0].validaTipos(tabla_simbolos, errores) # Validar la expresión
             returned_type_char = self.hijos[0].tipoDato # Tipo inferido de la expresión

         # TODO: Verificar compatibilidad con el tipo de retorno de la función actual
         # Necesitas saber en qué función estás. Esto podría requerir:
         # 1. Almacenar el tipo de retorno de la función actual en la tabla de símbolos al entrar a su ámbito.
         # 2. O pasar el tipo de retorno de la función como argumento a validaTipos de nodos dentro de ella.
         # Una forma simple para empezar es buscar la función contenedora (la más cercana hacia arriba)
         # buscando un símbolo de 'categoria' == 'funcion'.

         enclosing_func_name = None
         for i in range(len(tabla_simbolos.ambitos) -1, -1, -1):
             for name, simbolo in tabla_simbolos.ambitos[i].items():
                  if simbolo.get('categoria') == 'funcion':
                       enclosing_func_name = name
                       break
             if enclosing_func_name: break # Encontró la función contenedora

         if enclosing_func_name:
             func_symbol = tabla_simbolos.buscar(enclosing_func_name) # Buscar para obtener el tipo
             if func_symbol:
                 expected_return_type_str = func_symbol['tipo']
                 expected_return_type_char = get_char_tipo(expected_return_type_str)

                 if returned_type_char is not None and expected_return_type_char is not None:
                     # Verificar compatibilidad (ej: int es compatible con float de retorno)
                     is_compatible = False
                     if returned_type_char == expected_return_type_char:
                          is_compatible = True
                     elif expected_return_type_char == 'f' and returned_type_char == 'i': # Retornar int en float es válido
                         is_compatible = True
                     # Podrías añadir más reglas

                     if not is_compatible:
                         errores.append(f"Error semántico: Tipo de retorno incompatible en función '{enclosing_func_name}'. Se esperaba '{expected_return_type_str}', se retornó tipo '{returned_type_char}'.")

         elif returned_type_char != 'v' :
               # Retorno con valor fuera de una función (o en función void no marcada como tal)
               errores.append("Error semántico: Sentencia 'return' con valor fuera de una función o en una función declarada como 'void'.")


class NodoSentenciaIf(NodoAST):
    def __init__(self, condicion_nodo, bloque_if_nodo, bloque_else_nodo=None):
        super().__init__('sentencia_if')
        self.agregar_hijo(condicion_nodo)  # hijo[0] = condicion
        self.agregar_hijo(bloque_if_nodo) # hijo[1] = bloque if
        self.agregar_hijo(bloque_else_nodo) # hijo[2] = bloque else (puede ser None)

    def validaTipos(self, tabla_simbolos, errores):
        # Validar la condición
        self.hijos[0].validaTipos(tabla_simbolos, errores)
        tipo_condicion = self.hijos[0].tipoDato

        # Verificar si la condición es de un tipo válido para una expresión booleana
        # Asumimos que 'int' es válido (0=false, !=0=true) o podrías tener un tipo 'bool'
        if tipo_condicion is not None and tipo_condicion not in ['i', 'f', 'c']: # Permitir numéricos como booleanos, ajustar según reglas
             errores.append(f"Error semántico: La condición del 'if' debe ser un tipo numérico o booleano, se encontró tipo '{tipo_condicion}'.")

        # Validar el bloque if (crea su propio ámbito)
        tabla_simbolos.entrar_ambito("if")
        self.hijos[1].validaTipos(tabla_simbolos, errores)
        tabla_simbolos.salir_ambito()

        # Validar el bloque else si existe (crea su propio ámbito)
        if len(self.hijos) > 2 and self.hijos[2]:
             tabla_simbolos.entrar_ambito("else")
             self.hijos[2].validaTipos(tabla_simbolos, errores)
             tabla_simbolos.salir_ambito()


class NodoSentenciaWhile(NodoAST):
     def __init__(self, condicion_nodo, bloque_nodo):
         super().__init__('sentencia_while')
         self.agregar_hijo(condicion_nodo) # hijo[0] = condicion
         self.agregar_hijo(bloque_nodo)    # hijo[1] = bloque

     def validaTipos(self, tabla_simbolos, errores):
         # Validar la condición
         self.hijos[0].validaTipos(tabla_simbolos, errores)
         tipo_condicion = self.hijos[0].tipoDato

         # Verificar si la condición es de un tipo válido
         if tipo_condicion is not None and tipo_condicion not in ['i', 'f', 'c']: # Permitir numéricos
             errores.append(f"Error semántico: La condición del 'while' debe ser un tipo numérico o booleano, se encontró tipo '{tipo_condicion}'.")

         # Validar el bloque (crea su propio ámbito)
         tabla_simbolos.entrar_ambito("while")
         self.hijos[1].validaTipos(tabla_simbolos, errores)
         tabla_simbolos.salir_ambito()


# Nodos de Expresión
class NodoExpresionBinaria(NodoAST): # opSuma, opResta, opRelac, opIgualdad, opAnd, opOr
     def __init__(self, tipo_op, izq_nodo, der_nodo):
         super().__init__('expresion_binaria', tipo_op) # Valor es el tipo de operador
         self.agregar_hijo(izq_nodo) # hijo[0] = operando izquierdo
         self.agregar_hijo(der_nodo) # hijo[1] = operando derecho

     def validaTipos(self, tabla_simbolos, errores):
         # Validar ambos operandos primero
         self.hijos[0].validaTipos(tabla_simbolos, errores)
         self.hijos[1].validaTipos(tabla_simbolos, errores)

         tipo_izq = self.hijos[0].tipoDato
         tipo_der = self.hijos[1].tipoDato
         operador = self.valor # 'OP_SUMA', 'OP_RELAC', etc.

         # Inferir tipoDato de este nodo y verificar compatibilidad
         self.tipoDato = None # Inicializar

         if tipo_izq is None or tipo_der is None:
             # Error ya reportado en los hijos (variable no declarada, etc.)
             return

         # Reglas de promoción y verificación de tipos (simplificadas)
         if operador in ['OP_SUMA', 'OP_RESTA', 'OP_MULT', 'OP_DIV']: # Operadores aritméticos (NodoTerminoBinario también usa esto)
              if tipo_izq == 'f' or tipo_der == 'f':
                  self.tipoDato = 'f' # Float si al menos uno es float
              elif tipo_izq == 'i' and tipo_der == 'i':
                  self.tipoDato = 'i' # Int si ambos son int
              elif tipo_izq == 'c' and tipo_der == 'c' and operador in ['OP_SUMA', 'OP_RESTA']:
                   # Permitir suma/resta de chars (ej: 'a' + 1) -> resulta en int
                   # Esto es una simplificación, podrías tener reglas más estrictas
                   self.tipoDato = 'i'
              else:
                  errores.append(f"Error semántico: Tipos incompatibles para operación aritmética '{operador}' entre '{tipo_izq}' y '{tipo_der}'.")
                  self.tipoDato = None # Tipo desconocido debido al error

         elif operador in ['OP_RELAC', 'OP_IGUALDAD']: # Operadores relacionales/igualdad
             # Usualmente comparan tipos compatibles y el resultado es booleano (podemos representarlo como 'i')
             if tipo_izq == tipo_der or (tipo_izq in ['i', 'f'] and tipo_der in ['i', 'f']): # Permitir comparar int/float
                 self.tipoDato = 'i' # Resultado booleano representado como int (1 o 0)
             else:
                  errores.append(f"Error semántico: Tipos incompatibles para operación de comparación '{operador}' entre '{tipo_izq}' y '{tipo_der}'.")
                  self.tipoDato = None

         elif operador in ['OP_AND', 'OP_OR']: # Operadores lógicos
             # Usualmente operan sobre booleanos (representados como 'i')
             if tipo_izq == 'i' and tipo_der == 'i': # Asumiendo int como booleano
                 self.tipoDato = 'i' # Resultado booleano
             else:
                 # Podrías permitir otros tipos convertibles a booleano si las reglas lo permiten
                 errores.append(f"Error semántico: Tipos incompatibles para operación lógica '{operador}' entre '{tipo_izq}' y '{tipo_der}'. Se esperaban booleanos (int).")
                 self.tipoDato = None

         elif operador == 'OP_NOT': # Operador lógico unario (no binario, este nodo no debería usarlo)
             # Este caso no debería ocurrir para NodoExpresionBinaria
             pass # Manejar en NodoExpresionUnaria si existe


class NodoTerminoBinario(NodoExpresionBinaria): # opMul, opDiv
     def __init__(self, tipo_op, izq_nodo, der_nodo):
          super().__init__(tipo_op, izq_nodo, der_nodo)
          self.tipo = 'termino_binario' # Sobreescribir tipo


class NodoExpresionUnaria(NodoAST): # opSuma (unario), opResta (unario), opNot
     def __init__(self, tipo_op, operando_nodo):
         super().__init__('expresion_unaria', tipo_op) # Valor es el tipo de operador
         self.agregar_hijo(operando_nodo) # hijo[0] = operando

     def validaTipos(self, tabla_simbolos, errores):
         self.hijos[0].validaTipos(tabla_simbolos, errores)
         tipo_operando = self.hijos[0].tipoDato
         operador = self.valor # 'OP_SUMA', 'OP_RESTA', 'OP_NOT'

         self.tipoDato = None # Inicializar

         if tipo_operando is None:
             return # Error ya reportado en el operando

         if operador in ['OP_SUMA', 'OP_RESTA']: # +expr, -expr
             if tipo_operando in ['i', 'f']:
                 self.tipoDato = tipo_operando # El tipo se mantiene
             else:
                 errores.append(f"Error semántico: Operador unario '{operador}' no aplicable al tipo '{tipo_operando}'.")
                 self.tipoDato = None

         elif operador == 'OP_NOT': # !expr
             if tipo_operando == 'i': # Asumiendo int como booleano
                 self.tipoDato = 'i' # Resultado booleano
             else:
                 # Podrías permitir otros tipos convertibles
                 errores.append(f"Error semántico: Operador lógico unario '!' no aplicable al tipo '{tipo_operando}'. Se esperaba booleano (int).")
                 self.tipoDato = None


class NodoId(NodoAST):
     def __init__(self, valor, token=None):
         super().__init__('id', valor)
         self.token = token # Guardar el token original para errores

     def validaTipos(self, tabla_simbolos, errores):
         # Buscar el identificador en la tabla de símbolos
         simbolo = tabla_simbolos.buscar(self.valor)

         if not simbolo:
             errores.append(f"Error semántico: Uso de identificador no declarado '{self.valor}'.")
             self.tipoDato = None # Tipo desconocido si no está declarado
         else:
             self.tipoDato = get_char_tipo(simbolo['tipo']) # Establecer tipoDato basado en la tabla de símbolos
             # Puedes verificar aquí si la categoría es 'variable', 'funcion', etc.
             # if simbolo['categoria'] != 'variable':
             #      errores.append(f"Error semántico: Se esperaba una variable, pero '{self.valor}' es de categoría '{simbolo['categoria']}'.")


class NodoNumInt(NodoAST):
     def __init__(self, valor, token=None):
         super().__init__('num_int', valor)
         self.token = token

     def validaTipos(self, tabla_simbolos, errores):
         self.tipoDato = 'i' # Entero


class NodoNumFloat(NodoAST):
     def __init__(self, valor, token=None):
         super().__init__('num_float', valor)
         self.token = token

     def validaTipos(self, tabla_simbolos, errores):
         self.tipoDato = 'f' # Flotante


class NodoCaracter(NodoAST):
     def __init__(self, valor, token=None):
         super().__init__('caracter', valor)
         self.token = token

     def validaTipos(self, tabla_simbolos, errores):
         self.tipoDato = 'c' # Carácter

class NodoCadena(NodoAST):
     def __init__(self, valor, token=None):
         super().__init__('cadena', valor)
         self.token = token

     def validaTipos(self, tabla_simbolos, errores):
         self.tipoDato = 's' # Cadena (si tu gramática la soporta en expresiones)


class NodoArgumentos(NodoAST):
    def __init__(self, argumentos_nodos):
        super().__init__('argumentos', hijos=argumentos_nodos)

    def validaTipos(self, tabla_simbolos, errores):
        # Validar cada argumento para inferir su tipoDato
        for arg_nodo in self.hijos:
            if arg_nodo:
                 arg_nodo.validaTipos(tabla_simbolos, errores)


class NodoLlamadaFuncionExpr(NodoLlamadaFuncion): # Para llamadas dentro de expresiones como func() + 1
     def __init__(self, id_nodo, argumentos_nodo):
         super().__init__(id_nodo, argumentos_nodo)
         self.tipo = 'llamada_funcion_expr' # Sobreescribir tipo


# --- Parser Class ---
# Adaptar el parser para construir el nuevo tipo de nodos AST

class AnalizadorSintactico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicion = 0
        self.token_actual = self.tokens[0]
        self.pila = [] # Para registro de la pila
        self.registro_pila = []
        self.contador_paso = 0

    def avanzar(self):
        self.posicion += 1
        if self.posicion < len(self.tokens):
            self.token_actual = self.tokens[self.posicion]
        else:
             self.token_actual = Token('EOF', '', self.token_actual.linea, self.token_actual.columna + 1) # Asegurar EOF al final
        return self.token_actual

    def emparejar(self, tipo_esperado):
        if self.token_actual.tipo == tipo_esperado:
            token = self.token_actual
            self.avanzar()
            return token
        else:
            raise SyntaxError(f"Error de sintaxis: Se esperaba {tipo_esperado} pero se encontró {self.token_actual.tipo} ('{self.token_actual.valor}') en línea {self.token_actual.linea}, columna {self.token_actual.columna}")

    def registrar_pila(self, accion, simbolo_entrada=None):
        """Registra el estado actual de la pila y la acción realizada"""
        self.contador_paso += 1
        entrada = simbolo_entrada if simbolo_entrada is not None else (self.token_actual.valor if self.token_actual.tipo != 'EOF' else "EOF")

        # Formatear pila como string para mostrar (muestra solo tipos/nombres)
        pila_str = ' '.join(str(item) for item in self.pila)

        self.registro_pila.append({
            'paso': self.contador_paso,
            'pila': pila_str,
            'entrada': entrada,
            'accion': accion,
            'salida': "" # Se llenará manualmente si es necesario (ej: reducciones)
        })

    def apilar(self, elemento):
        """Apila un elemento (token o nombre de no terminal) y registra la acción."""
        # Al apilar un token, podrías apilar el objeto Token completo si necesitas sus atributos (valor, línea, columna)
        # Para la pila mostrada, solo apilamos el tipo del token o el nombre del no terminal.
        # Sin embargo, para construir el AST, necesitamos el objeto Token o el nodo AST.
        # Vamos a apilar el tipo/nombre para el registro, pero la lógica interna del parser
        # debe manejar los objetos Token/NodoAST para la construcción del AST.
        # Esto complica el registro exacto de "la pila" versus la pila interna del parser.

        # Adaptación: Registrar el push conceptualmente, pero el push real ocurre en el algoritmo LR (no implementado aquí con la tabla CSV).
        # Dado que el usuario proporcionó un parser recursivo en compilador2.py, adaptaré a ESE parser y su registro de pila.
        # El registro de pila en compilador2.py es conceptual y NO refleja un parser Shift-Reduce real con tabla.
        # Refleja una traza de ejecución de un parser recursivo descendente.
        # Mmmm, el registro de pila en la imagen y la descripción inicial SÍ parece LR.
        # La segunda implementación (compilador2.py) ignora la tabla CSV/INF y es recursiva.
        # La solicitud es adaptar compilador2.py (parser recursivo) PERO con el registro de pila LR de la imagen.
        # Esto es una inconsistencia. Voy a seguir la estructura de compilador2.py (parser recursivo)
        # para la lógica de análisis y construcción del AST/semántico, y MANTENER el registro de pila conceptual
        # del parser recursivo que ya estaba. Implementar el parser LR shift-reduce desde cero con la tabla CSV es un proyecto más grande.
        # Si el usuario INSISTE en la traza de pila LR con el parser recursivo, es conceptualmente incorrecto,
        # pero se podría SIMULAR una traza LR a partir de las llamadas recursivas/emparejamientos,
        # aunque no sería el proceso real del parser recursivo.

        # Ok, volvamos a la idea original del parser LR (primer código) que SÍ usa la tabla CSV y pila.
        # El problema es que compilador2.py es un parser recursivo y no usa tabla ni pila LR para el análisis en sí.
        # Adaptaré el *análisis semántico* del PDF al *primer código* (con tabla CSV/INF y pila LR) porque eso es lo que el usuario pidió inicialmente Y lo que la traza de pila de la imagen sugiere.
        # Descartamos `compilador2.py` como base del parser, usamos la base del primer código.

        # ********************************************************************
        # REINICIAR ESTRATEGIA: USAR LA BASE DEL PRIMER CÓDIGO (PARSER LR)
        # ********************************************************************
        pass # Esto era de AnalizadorSintactico en compilador2.py, no aplica al parser LR.

# --- Parser Class (Based on the first implementation, LR) ---
# Need to reintegrate the LR parser logic and add AST node creation during reductions.

class Parser:
    def __init__(self, lexer, grammar, parsing_table):
        self.lexer = lexer
        self.grammar = grammar
        self.parsing_table = parsing_table
        self.symbol_table = TablaSimbolo(errores_list=[]) # Symbol table for semantic analysis
        self.errors = self.symbol_table.errores_list # Use the same error list
        self.stack = [0] # Stack of states for LR parsing
        self.symbol_stack = [] # Stack to hold symbols (tokens or AST nodes) for AST building
        self.tokens = [] # To be filled by lexer
        self.token_index = 0
        self.current_token = None # Current lookahead token
        self.ast_root = None # Root of the generated AST

    def parse(self):
        print("Starting LR parsing...")
        print(f"{'Stack (States)':<20} | {'Stack (Symbols)':<30} | {'Input':<30} | Action")

        try:
            self.tokens = self.lexer.tokenize()
            self.current_token = self.tokens[self.token_index]
        except Exception as e:
             print(f"Lexical analysis failed: {e}", file=sys.stderr)
             return False # Stop if lexing fails


        while True:
            current_state = self.stack[-1]
            token_type = self.current_token.type

            # Print current stack and input
            stack_state_str = ' '.join(map(str, self.stack))
            stack_symbol_str = ' '.join(map(str, self.symbol_stack)) # Show symbols on stack
            input_str = ' '.join([t.value for t in self.tokens[self.token_index:]])
            print(f"{stack_state_str:<20} | {stack_symbol_str:<30.30} | {input_str:<30.30} | ", end="") # Adjusted spacing


            action = self.parsing_table.get_action(current_state, token_type)

            if action is None:
                self.report_error(f"Syntax error: No action defined for state {current_state} and token {token_type} ('{self.current_token.value}')")
                return False # Error
            elif action == 'acc':
                print("Accept")
                print("Parsing successful!")
                # The root of the AST should be the single symbol left on the symbol stack
                if len(self.symbol_stack) == 1:
                    self.ast_root = self.symbol_stack[0]
                    print("\nAST built. Starting semantic analysis...")
                    self.perform_semantic_analysis() # Perform semantic analysis after successful parse
                    return not self.errors # Return True if no semantic errors
                else:
                    self.report_error("Parser finished with multiple symbols on stack.")
                    return False # Should not happen on a correct parse

            elif action.startswith('d'):
                state_to_push = int(action[1:])
                print(f"Shift {state_to_push}")
                self.stack.append(state_to_push) # Push state
                self.symbol_stack.append(self.current_token) # Push token object onto symbol stack
                self.token_index += 1 # Move to next token
                if self.token_index < len(self.tokens):
                    self.current_token = self.tokens[self.token_index]
                # else: current_token remains EOF

            elif action.startswith('r'):
                rule_number = int(action[1:])
                rule = self.grammar.get_rule(rule_number)
                if rule is None:
                     self.report_error(f"Grammar error: Rule R{rule_number} not found.")
                     return False

                lhs, rhs = rule
                len_rhs = len(rhs)

                print(f"Reduce R{rule_number}: <{lhs}> ::= {' '.join(rhs)}")

                # Pop 2 * len(rhs) elements from state stack
                if len(self.stack) < 2 * len_rhs:
                     self.report_error(f"Parser error: State stack underflow during reduction R{rule_number}.")
                     return False
                for _ in range(2 * len_rhs):
                    self.stack.pop()

                # Pop len(rhs) elements from symbol stack
                if len(self.symbol_stack) < len_rhs:
                     self.report_error(f"Parser error: Symbol stack underflow during reduction R{rule_number}.")
                     return False
                # Get the symbols/nodes that are being reduced
                reduced_symbols = [self.symbol_stack.pop() for _ in range(len_rhs)][::-1] # Pop in reverse, then reverse back to correct order

                # *** AST Node Creation and Semantic Actions During Reduction ***
                new_node = self.create_ast_node_and_semantic_action(rule_number, lhs, reduced_symbols)
                # ************************************************************

                new_current_state = self.stack[-1]
                goto_state = self.parsing_table.get_goto(new_current_state, lhs)

                if goto_state is None:
                     self.report_error(f"Parsing error: No goto defined for state {new_current_state} and non-terminal <{lhs}>")
                     return False

                self.stack.append(goto_state) # Push goto state
                self.symbol_stack.append(new_node) # Push the new AST node onto the symbol stack


            else:
                self.report_error(f"Unknown action '{action}' in parsing table.")
                return False # Error

        # Should not reach here unless there's an error or accept
        return False # Indicate failure if loop exits without accept/error


    def report_error(self, message):
        # Add line/column information from the current token
        error_message = f"{message} at token '{self.current_token.value}' ({self.current_token.type}) Line: {self.current_token.linea}, Col: {self.current_token.columna}"
        print(f"Error: {error_message}", file=sys.stderr)
        self.errors.append(error_message)


    def create_ast_node_and_semantic_action(self, rule_number, lhs, reduced_symbols):
        """
        Creates AST node for the reduction and performs associated semantic actions (like symbol table insertion).
        Returns the new AST node to be pushed onto the symbol stack.
        reduced_symbols: List of tokens or nodes popped from the symbol stack corresponding to the RHS of the rule.
        """
        # This is where you map grammar rules to AST node creation and initial semantic actions
        # based on the PDF's concepts (though validaTipos is the main pass).

        new_node = NodoAST(lhs) # Default node type is the LHS non-terminal
        # Add children in order of the RHS
        for symbol in reduced_symbols:
            new_node.agregar_hijo(symbol) # Add tokens or existing nodes as children

        # --- Specific AST Node Creation / Semantic Actions based on Rules ---
        # Map grammar rules (R#) to specific semantic logic and node types

        # Example Rules from your .inf and grammar structure:
        # R1 <programa> ::= <Definiciones>
        # R3 <Definiciones> ::= <Definicion> <Definiciones>
        # R4 <Definicion> ::= <DefVar>
        # R5 <Definicion> ::= <DefFunc>
        # R6 <DefVar> ::= tipo identificador <ListaVar> ;
        # R9 <DefFunc> ::= tipo identificador ( <Parametros> ) <BloqFunc>
        # R11 <Parametros> ::= tipo identificador <ListaParam>
        # R14 <BloqFunc> ::= { <DefLocales> }
        # R21 <Sentencia> ::= identificador = <Expresion> ;
        # R22 <Sentencia> ::= if ( <Expresion> ) <SentenciaBloque> <Otro>
        # R23 <Sentencia> ::= while ( <Expresion> ) <Bloque>
        # R24 <Sentencia> ::= return <ValorRegresa> ;
        # R25 <Sentencia> ::= <LlamadaFunc> ;
        # R27 <Otro> ::= else <SentenciaBloque>
        # R28 <Bloque> ::= { <Sentencias> }
        # R30 <ValorRegresa> ::= <Expresion>
        # R32 <Argumentos> ::= <Expresion> <ListaArgumentos>
        # R35 <Termino> ::= <LlamadaFunc>
        # R36 <Termino> ::= identificador
        # R37 <Termino> ::= entero
        # R38 <Termino> ::= real
        # R39 <Termino> ::= cadena
        # R40 <LlamadaFunc> ::= identificador ( <Argumentos> )
        # R41 <SentenciaBloque> ::= <Sentencia>
        # R42 <SentenciaBloque> ::= <Bloque>
        # R43 <Expresion> ::= ( <Expresion> )
        # R44 <Expresion> ::= opSuma <Expresion> (unary +)
        # R45 <Expresion> ::= opNot <Expresion> (unary !)
        # R46 <Expresion> ::= <Expresion> opMul <Expresion>
        # R47 <Expresion> ::= <Expresion> opSuma <Expresion> (binary +)
        # R48 <Expresion> ::= <Expresion> opRelac <Expresion>
        # R49 <Expresion> ::= <Expresion> opIgualdad <Expresion>
        # R50 <Expresion> ::= <Expresion> opAnd <Expresion>
        # R51 <Expresion> ::= <Expresion> opOr <Expresion>
        # R52 <Expresion> ::= <Termino>


        if rule_number == 6: # R6 <DefVar> ::= tipo identificador <ListaVar> ;
             # reduced_symbols: [tipo_token, id_token, ListaVar_node, semi_token]
             tipo_token = reduced_symbols[0]
             id_token = reduced_symbols[1]
             # ListaVar_node = reduced_symbols[2] # Can contain more ids if R8 is used
             # Create a node for variable declaration
             new_node = NodoDeclaracionVariable(NodoTipoDato(tipo_token.value, tipo_token), NodoId(id_token.value, id_token))
             # Note: Handling multiple variables from ListaVar in R8 reduction is needed if supported.

        elif rule_number == 9: # R9 <DefFunc> ::= tipo identificador ( <Parametros> ) <BloqFunc>
             # reduced_symbols: [tipo_token, id_token, lparen_token, Parametros_node, rparen_token, BloqFunc_node]
             tipo_token = reduced_symbols[0]
             id_token = reduced_symbols[1]
             parametros_node = reduced_symbols[3]
             bloqfunc_node = reduced_symbols[5] # This is likely the NodoBloque
             # Check if this is the main function
             if id_token.value == 'main':
                 new_node = NodoFuncionMain(NodoTipoDato(tipo_token.value, tipo_token), NodoId(id_token.value, id_token), parametros_node, bloqfunc_node)
             else:
                 new_node = NodoDeclaracionFuncion(NodoTipoDato(tipo_token.value, tipo_token), NodoId(id_token.value, id_token), parametros_node, bloqfunc_node)

        elif rule_number == 11: # R11 <Parametros> ::= tipo identificador <ListaParam>
             # This rule starts the parameters list. Need to collect params from ListaParam reductions.
             # This is tricky with pure bottom-up. Typically, semantic attributes would pass parameter info up.
             # For now, let's create a base node, and R13 reductions will add to it.
             # A better way: R11 and R13 reductions create parameter nodes, and R9 collects them.
             tipo_token = reduced_symbols[0]
             id_token = reduced_symbols[1]
             lista_param_node = reduced_symbols[2] # Can be NodoAST('<ListaParam>')

             param_node = NodoParametro(NodoTipoDato(tipo_token.value, tipo_token), NodoId(id_token.value, id_token))

             # How to add this parameter to the <Parametros> node?
             # The <Parametros> node is created by R9. The structure implies R11 reduces to <Parametros>.
             # Let's assume R11 reduces to a <Parametros> node containing the first parameter and the rest from <ListaParam>.
             # And R13 reduces to <ListaParam> containing the next parameter and the rest.
             # This requires careful construction.

             # Alternative simple approach for Parametros/ListaParam:
             # R10 <Parametros> ::= \e -> NodoParametros([])
             # R11 <Parametros> ::= tipo identificador <ListaParam> -> Collect the first param + params from ListaParam_node
             # R12 <ListaParam> ::= \e -> [] (empty list or None)
             # R13 <ListaParam> ::= , tipo identificador <ListaParam> -> Collect this param + params from ListaParam_node

             # Let's adjust rule handling based on this revised view:
             # R10 <Parametros> ::= \e -> Returns NodoParametros([])
             if rule_number == 10:
                  new_node = NodoParametros([])
             # R12 <ListaParam> ::= \e -> Returns an empty list (semantic value)
             elif rule_number == 12:
                  new_node = [] # Semantic value is a list of parameter nodes

             # R13 <ListaParam> ::= , tipo identificador <ListaParam>
             # reduced_symbols: [comma_token, tipo_token, id_token, ListaParam_node]
             elif rule_number == 13:
                  tipo_token = reduced_symbols[1]
                  id_token = reduced_symbols[2]
                  lista_param_rec_nodes = reduced_symbols[3] # This is the list from recursive <ListaParam>

                  current_param_node = NodoParametro(NodoTipoDato(tipo_token.value, tipo_token), NodoId(id_token.value, id_token))
                  new_node = [current_param_node] + lista_param_rec_nodes # Combine lists


             # R11 <Parametros> ::= tipo identificador <ListaParam>
             # reduced_symbols: [tipo_token, id_token, ListaParam_node]
             elif rule_number == 11:
                  tipo_token = reduced_symbols[0]
                  id_token = reduced_symbols[1]
                  lista_param_nodes = reduced_symbols[2] # This is the list from <ListaParam> reduction

                  first_param_node = NodoParametro(NodoTipoDato(tipo_token.value, tipo_token), NodoId(id_token.value, id_token))
                  new_node = NodoParametros([first_param_node] + lista_param_nodes) # Create the Parametros node with collected params

             # R14 <BloqFunc> ::= { <DefLocales> }
             # This reduces to the main block of a function.
             # The parser might create a generic block node for this.
             # We need DefLocales to return the list of statement/declaration nodes.
             # R15 <DefLocales> ::= \e -> []
             # R16 <DefLocales> ::= <DefLocal> <DefLocales> -> [<DefLocal_node>] + <DefLocales_rec>

             # Let's assume DefLocales reduces to a list of nodes
             elif rule_number == 15: # R15 <DefLocales> ::= \e
                  new_node = [] # Semantic value is a list of nodes
             elif rule_number == 16: # R16 <DefLocales> ::= <DefLocal> <DefLocales>
                  # reduced_symbols: [DefLocal_node, DefLocales_rec_nodes]
                  def_local_node = reduced_symbols[0]
                  def_locales_rec_nodes = reduced_symbols[1]
                  new_node = [def_local_node] + def_locales_rec_nodes

             # R17 <DefLocal> ::= <DefVar>
             elif rule_number == 17: # R17 <DefLocal> ::= <DefVar>
                 # reduced_symbols: [DefVar_node]
                 new_node = reduced_symbols[0] # DefLocal is just the DefVar node

             # R18 <DefLocal> ::= <Sentencia>
             elif rule_number == 18: # R18 <DefLocal> ::= <Sentencia>
                 # reduced_symbols: [Sentencia_node]
                 new_node = reduced_symbols[0] # DefLocal is just the Sentencia node


             # R28 <Bloque> ::= { <Sentencias> }
             # Let's assume Sentencias reduces to a list of nodes.
             # R19 <Sentencias> ::= \e -> []
             # R20 <Sentencias> ::= <Sentencia> <Sentencias> -> [<Sentencia_node>] + <Sentencias_rec>

             elif rule_number == 19: # R19 <Sentencias> ::= \e
                  new_node = [] # Semantic value is a list of nodes
             elif rule_number == 20: # R20 <Sentencias> ::= <Sentencia> <Sentencias>
                  # reduced_symbols: [Sentencia_node, Sentencias_rec_nodes]
                  sentencia_node = reduced_symbols[0]
                  sentencias_rec_nodes = reduced_symbols[1]
                  new_node = [sentencia_node] + sentencias_rec_nodes

             elif rule_number == 28: # R28 <Bloque> ::= { <Sentencias> }
                  # reduced_symbols: [lbrace_token, Sentencias_nodes, rbrace_token]
                  sentencias_nodes = reduced_symbols[1] # Get the list of sentences
                  new_node = NodoBloque(sentencias_nodes) # Create the Block node


             # R21 <Sentencia> ::= identificador = <Expresion> ;
             elif rule_number == 21:
                 # reduced_symbols: [id_token, assign_token, Expresion_node, semi_token]
                 id_token = reduced_symbols[0]
                 expresion_node = reduced_symbols[2]
                 new_node = NodoAsignacion(NodoId(id_token.value, id_token), expresion_node)

             # R22 <Sentencia> ::= if ( <Expresion> ) <SentenciaBloque> <Otro>
             # Assuming <Otro> reduces to the else block node (or None)
             elif rule_number == 22:
                  # reduced_symbols: [if_token, lparen, Expresion_node, rparen, SentenciaBloque_node, Otro_node]
                  condicion_node = reduced_symbols[2]
                  sentencia_bloque_node = reduced_symbols[4]
                  otro_node = reduced_symbols[5] # This is the else part

                  # Need to unwrap SentenciaBloque and Otro to get the actual block/statement
                  # R41 <SentenciaBloque> ::= <Sentencia>
                  # R42 <SentenciaBloque> ::= <Bloque>
                  # R26 <Otro> ::= \e -> None (or a specific 'empty' node)
                  # R27 <Otro> ::= else <SentenciaBloque>

                  # Let's assume SentenciaBloque reduces to the actual statement/block node
                  # and Otro reduces to the else block/statement node or None
                  bloque_if_node = sentencia_bloque_node # Assuming SentenciaBloque reduction passes up the node
                  bloque_else_node = otro_node if isinstance(otro_node, NodoAST) else None # Check if Otro reduction returned a node

                  new_node = NodoSentenciaIf(condicion_node, bloque_if_node, bloque_else_node)

             # R23 <Sentencia> ::= while ( <Expresion> ) <Bloque>
             elif rule_number == 23:
                  # reduced_symbols: [while_token, lparen, Expresion_node, rparen, Bloque_node]
                  condicion_node = reduced_symbols[2]
                  bloque_node = reduced_symbols[4]
                  new_node = NodoSentenciaWhile(condicion_node, bloque_node)

             # R24 <Sentencia> ::= return <ValorRegresa> ;
             # Assuming ValorRegresa reduces to the expression node or None
             elif rule_number == 24:
                  # reduced_symbols: [return_token, ValorRegresa_node, semi_token]
                  valor_regresa_node = reduced_symbols[1] # This is the expression node or None
                  new_node = NodoRetorno(valor_regresa_node)

             # R25 <Sentencia> ::= <LlamadaFunc> ;
             elif rule_number == 25:
                  # reduced_symbols: [LlamadaFunc_node, semi_token]
                  llamada_func_node = reduced_symbols[0] # This is the function call node
                  # Re-wrap as a statement node if needed, or maybe the LlamadaFunc node suffices
                  new_node = llamada_func_node # Use the existing node

             # R26 <Otro> ::= \e
             elif rule_number == 26:
                  new_node = None # Represent epsilon as None or a dedicated Empty node

             # R27 <Otro> ::= else <SentenciaBloque>
             elif rule_number == 27:
                  # reduced_symbols: [else_token, SentenciaBloque_node]
                  sentencia_bloque_node = reduced_symbols[1] # Get the block/statement node
                  new_node = sentencia_bloque_node # The else part is just the block/statement

             # R30 <ValorRegresa> ::= <Expresion>
             elif rule_number == 30:
                  # reduced_symbols: [Expresion_node]
                  new_node = reduced_symbols[0] # ValorRegresa is just the expression node

             # R29 <ValorRegresa> ::= \e
             elif rule_number == 29:
                  new_node = None # Represents no return value

             # R31 <Argumentos> ::= \e
             elif rule_number == 31:
                  new_node = NodoArgumentos([]) # Represents empty arguments

             # R32 <Argumentos> ::= <Expresion> <ListaArgumentos>
             # R33 <ListaArgumentos> ::= \e -> []
             # R34 <ListaArgumentos> ::= , <Expresion> <ListaArgumentos> -> [Expresion_node] + list from recursive ListaArgumentos

             # Let's assume ListaArgumentos reduces to a list of nodes
             elif rule_number == 33: # R33 <ListaArgumentos> ::= \e
                  new_node = [] # Semantic value is a list of argument expression nodes
             elif rule_number == 34: # R34 <ListaArgumentos> ::= , <Expresion> <ListaArgumentos>
                  # reduced_symbols: [comma_token, Expresion_node, ListaArgumentos_rec_nodes]
                  expresion_node = reduced_symbols[1]
                  lista_args_rec_nodes = reduced_symbols[2]
                  new_node = [expresion_node] + lista_args_rec_nodes

             elif rule_number == 32: # R32 <Argumentos> ::= <Expresion> <ListaArgumentos>
                  # reduced_symbols: [Expresion_node, ListaArgumentos_nodes]
                  first_expr_node = reduced_symbols[0]
                  lista_args_nodes = reduced_symbols[1]
                  new_node = NodoArgumentos([first_expr_node] + lista_args_nodes)


             # R35 <Termino> ::= <LlamadaFunc>
             elif rule_number == 35:
                 # reduced_symbols: [LlamadaFunc_node]
                 # Need to distinguish between statement call and expression call
                 # Grammar has <LlamadaFunc> used in <Sentencia> (R25) and <Termino> (R35).
                 # Let's create a specific node for expression calls.
                 # The LlamadaFunc_node created by R40 needs to be wrapped or be of a type that signifies its context.
                 # Let's modify R40 creation and use it here.
                 new_node = reduced_symbols[0] # Assuming R40 creates the correct node type


             # R40 <LlamadaFunc> ::= identificador ( <Argumentos> )
             elif rule_number == 40:
                 # reduced_symbols: [id_token, lparen, Argumentos_node, rparen]
                 id_token = reduced_symbols[0]
                 argumentos_node = reduced_symbols[2] # This is the NodoArgumentos
                 # Determine if this is a statement call or an expression call.
                 # This context is available at the *reduction* site (R25 vs R35).
                 # However, the node is created *here* at R40.
                 # A common approach is to create a generic call node here, and the parent rule (R25/R35) handles its context.
                 # Or, create a specific node type if the grammar structure guarantees it.
                 # Let's create a generic NodoLlamada for now, and maybe differentiate later if needed.
                 # Given R35, this rule *is* for a call used in an expression context.
                 new_node = NodoLlamadaFuncionExpr(NodoId(id_token.value, id_token), argumentos_node)


             # R41 <SentenciaBloque> ::= <Sentencia>
             elif rule_number == 41:
                  # reduced_symbols: [Sentencia_node]
                  new_node = reduced_symbols[0] # SentenciaBloque is just the Sentencia node

             # R42 <SentenciaBloque> ::= <Bloque>
             elif rule_number == 42:
                  # reduced_symbols: [Bloque_node]
                  new_node = reduced_symbols[0] # SentenciaBloque is just the Bloque node

             # R43 <Expresion> ::= ( <Expresion> )
             elif rule_number == 43:
                  # reduced_symbols: [lparen, Expresion_node, rparen]
                  new_node = reduced_symbols[1] # The node for the inner expression

             # R44 <Expresion> ::= opSuma <Expresion> (unary + or -)
             # Assuming opSuma token can be '+' or '-' and opNot is '!'
             # The grammar uses opSuma for both binary and unary +/-, and opNot for !.
             # R44 is specifically unary +/-, R47 is binary.
             # The parser table distinguishes these based on context.
             elif rule_number == 44: # Unary opSuma
                  # reduced_symbols: [opSuma_token, Expresion_node]
                  op_token = reduced_symbols[0]
                  expresion_node = reduced_symbols[1]
                  new_node = NodoExpresionUnaria(op_token.type, expresion_node) # Use opSuma type

             # R45 <Expresion> ::= opNot <Expresion> (unary !)
             elif rule_number == 45: # Unary opNot
                  # reduced_symbols: [opNot_token, Expresion_node]
                  op_token = reduced_symbols[0]
                  expresion_node = reduced_symbols[1]
                  new_node = NodoExpresionUnaria(op_token.type, expresion_node) # Use opNot type


             # R46 <Expresion> ::= <Expresion> opMul <Expresion>
             elif rule_number == 46:
                  # reduced_symbols: [Expresion_izq_node, opMul_token, Expresion_der_node]
                  izq_node = reduced_symbols[0]
                  op_token = reduced_symbols[1]
                  der_node = reduced_symbols[2]
                  new_node = NodoTerminoBinario(op_token.type, izq_node, der_node) # Use opMul type

             # R47 <Expresion> ::= <Expresion> opSuma <Expresion> (binary + or -)
             elif rule_number == 47: # Binary opSuma
                  # reduced_symbols: [Expresion_izq_node, opSuma_token, Expresion_der_node]
                  izq_node = reduced_symbols[0]
                  op_token = reduced_symbols[1]
                  der_node = reduced_symbols[2]
                  new_node = NodoExpresionBinaria(op_token.type, izq_node, der_node) # Use opSuma type

             # R48 <Expresion> ::= <Expresion> opRelac <Expresion>
             elif rule_number == 48:
                 # reduced_symbols: [Expresion_izq_node, opRelac_token, Expresion_der_node]
                 izq_node = reduced_symbols[0]
                 op_token = reduced_symbols[1]
                 der_node = reduced_symbols[2]
                 new_node = NodoExpresionBinaria(op_token.type, izq_node, der_node) # Use opRelac type

             # R49 <Expresion> ::= <Expresion> opIgualdad <Expresion>
             elif rule_number == 49:
                 # reduced_symbols: [Expresion_izq_node, opIgualdad_token, Expresion_der_node]
                 izq_node = reduced_symbols[0]
                 op_token = reduced_symbols[1]
                 der_node = reduced_symbols[2]
                 new_node = NodoExpresionBinaria(op_token.type, izq_node, der_node) # Use opIgualdad type


             # R50 <Expresion> ::= <Expresion> opAnd <Expresion>
             elif rule_number == 50:
                 # reduced_symbols: [Expresion_izq_node, opAnd_token, Expresion_der_node]
                 izq_node = reduced_symbols[0]
                 op_token = reduced_symbols[1]
                 der_node = reduced_symbols[2]
                 new_node = NodoExpresionBinaria(op_token.type, izq_node, der_node) # Use opAnd type

             # R51 <Expresion> ::= <Expresion> opOr <Expresion>
             elif rule_number == 51:
                 # reduced_symbols: [Expresion_izq_node, opOr_token, Expresion_der_token]
                 izq_node = reduced_symbols[0]
                 op_token = reduced_symbols[1]
                 der_node = reduced_symbols[2]
                 new_node = NodoExpresionBinaria(op_token.type, izq_node, der_node) # Use opOr type


             # R52 <Expresion> ::= <Termino>
             elif rule_number == 52:
                  # reduced_symbols: [Termino_node]
                  new_node = reduced_symbols[0] # Expresion is just the Termino node

             # R36 <Termino> ::= identificador
             elif rule_number == 36:
                 # reduced_symbols: [id_token]
                 id_token = reduced_symbols[0]
                 new_node = NodoId(id_token.value, id_token) # Create Id node

             # R37 <Termino> ::= entero
             elif rule_number == 37:
                 # reduced_symbols: [entero_token]
                 entero_token = reduced_symbols[0]
                 new_node = NodoNumInt(entero_token.value, entero_token) # Create Int node

             # R38 <Termino> ::= real
             elif rule_number == 38:
                 # reduced_symbols: [real_token]
                 real_token = reduced_symbols[0]
                 new_node = NodoNumFloat(real_token.value, real_token) # Create Float node

             # R39 <Termino> ::= cadena
             elif rule_number == 39:
                 # reduced_symbols: [cadena_token]
                 cadena_token = reduced_symbols[0]
                 new_node = NodoCadena(cadena_token.value, cadena_token) # Create String node


             # R1 <programa> ::= <Definiciones>
             # The root of the AST will be the node produced by this rule
             elif rule_number == 1:
                  # reduced_symbols: [Definiciones_node]
                  new_node = reduced_symbols[0] # Program root is the Definiciones node

             # R2 <Definiciones> ::= \e
             # R3 <Definiciones> ::= <Definicion> <Definiciones>
             # These rules build the list of definitions. Need to handle list concatenation.
             # Assume Definiciones reduces to a list of definition nodes.
             elif rule_number == 2: # R2 <Definiciones> ::= \e
                  new_node = [] # Semantic value is an empty list of definitions
             elif rule_number == 3: # R3 <Definiciones> ::= <Definicion> <Definiciones>
                  # reduced_symbols: [Definicion_node, Definiciones_rec_nodes]
                  definicion_node = reduced_symbols[0]
                  definiciones_rec_nodes = reduced_symbols[1]
                  # Check if the single definition is main, it might need special handling at the root
                  # For simplicity, just add to the list
                  new_node = [definicion_node] + definiciones_rec_nodes


             # R4 <Definicion> ::= <DefVar>
             elif rule_number == 4:
                 # reduced_symbols: [DefVar_node]
                 new_node = reduced_symbols[0] # Definicion is just the DefVar node

             # R5 <Definicion> ::= <DefFunc>
             elif rule_number == 5:
                 # reduced_symbols: [DefFunc_node]
                 new_node = reduced_symbols[0] # Definicion is just the DefFunc node


             # --- Rules that might not create a new AST node but pass a value/list ---
             # (e.g., ListaVar, ListaParam, DefLocales, Sentencias, Argumentos)
             # These are handled above by returning lists or existing nodes.

        # For rules not explicitly handled above, return the default node (LHS with children)
        # This is a fallback, ideally all relevant rules create specific node types or pass values.

        return new_node


    def perform_semantic_analysis(self):
        """Initiates the semantic analysis pass over the AST."""
        print("\nPerforming semantic analysis...")

        if self.ast_root is None:
            print("Semantic analysis skipped: No AST was built.")
            return

        # Enter the global scope before validating the root
        self.symbol_table.entrar_ambito("global")

        # Start the recursive validation from the root of the AST
        # Pass the symbol table and the shared errors list
        self.ast_root.validaTipos(self.symbol_table, self.errors)

        # Exit global scope (at the very end of analysis)
        self.symbol_table.salir_ambito()

        # Display symbol table (optional)
        # self.symbol_table.muestra()

        print("\nSemantic analysis finished.")
        if self.errors:
            print("Semantic errors found:")
            for error in self.errors:
                print(f"- {error}")
        else:
            print("No semantic errors found.")


# --- Grammar Class ---
# (Keep the same as before)
class Grammar:
    def __init__(self, inf_filepath):
        self.rules = {} # {rule_number: (lhs_non_terminal, [rhs_symbols])}
        self.token_map = {} # {token_name: token_id}
        self.id_to_token_map = {} # {token_id: token_name}
        self._load_grammar(inf_filepath)

    def _load_grammar(self, inf_filepath):
        with open(inf_filepath, 'r') as f:
            lines = f.readlines()

        parsing_tokens = True
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if parsing_tokens and '\t' in line:
                parts = line.split('\t')
                if len(parts) == 2:
                    name, id_str = parts
                    try:
                        token_id = int(id_str.strip())
                        self.token_map[name.strip()] = token_id
                        self.id_to_token_map[token_id] = name.strip()
                    except ValueError:
                         parsing_tokens = False # Assume rules start now
                else:
                     parsing_tokens = False

            if not parsing_tokens and line.startswith('R'):
                parts = line.split('::=')
                if len(parts) == 2:
                    rule_part = parts[0].strip()
                    production_part = parts[1].strip()

                    rule_match = re.match(r'R(\d+)\s*<([a-zA-Z_][a-zA-Z0-9_]*)>', rule_part)
                    if rule_match:
                        rule_number = int(rule_match.group(1))
                        lhs = rule_match.group(2)

                        rhs_symbols = production_part.split()
                        if rhs_symbols == ['\\e']:
                            rhs_symbols = []

                        self.rules[rule_number] = (lhs, rhs_symbols)
                    else:
                         print(f"Warning: Skipping malformed rule line in .inf: {line}", file=sys.stderr)
                else:
                    print(f"Warning: Skipping malformed line in .inf (missing ::=): {line}", file=sys.stderr)

    def get_rule(self, rule_number):
        return self.rules.get(rule_number)

    def get_token_map(self):
        return self.token_map

    def get_id_to_token_map(self):
        return self.id_to_token_map


# --- ParsingTable Class ---
# (Keep the same as before)
class ParsingTable:
    def __init__(self, csv_filepath):
        self.action_table = {} # {(state, terminal_name): action_string}
        self.goto_table = {} # {(state, non_terminal_name): next_state}
        self.symbol_to_col = {} # {symbol_name: column_index}
        self.col_to_symbol = {} # {column_index: symbol_name}
        self._load_table(csv_filepath)

    def _load_table(self, csv_filepath):
        with open(csv_filepath, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)

            for i, symbol in enumerate(header):
                self.symbol_to_col[symbol.strip()] = i
                self.col_to_symbol[i] = symbol.strip()

            for row in reader:
                if not row: continue
                try:
                    state = int(row[0].strip())
                except ValueError:
                    print(f"Warning: Skipping row in CSV with non-integer state: {row[0]}", file=sys.stderr)
                    continue

                for i in range(1, len(row)):
                    if i >= len(header):
                         print(f"Warning: Row {state} has more columns than header.", file=sys.stderr)
                         break
                    cell = row[i].strip()
                    if cell:
                        symbol = self.col_to_symbol.get(i)
                        if symbol is None:
                             print(f"Warning: Skipping cell at state {state}, column {i} with no header symbol.", file=sys.stderr)
                             continue

                        # Terminals vs Non-terminals heuristic or list from grammar
                        # Using the list of terminals from the INF file for better accuracy
                        terminals_list = ['identificador', 'entero', 'real', 'cadena', 'tipo', 'opSuma', 'opMul', 'opRelac', 'opOr', 'opAnd', 'opNot', 'opIgualdad', ';', ',', '(', ')', '{', '}', '=', 'if', 'while', 'return', 'else', '$'] # From inf
                        if symbol in terminals_list:
                            self.action_table[(state, symbol)] = cell
                        else:
                            try:
                                self.goto_table[(state, symbol)] = int(cell)
                            except ValueError:
                                print(f"Warning: Skipping non-integer goto value '{cell}' for state {state}, symbol {symbol}.", file=sys.stderr)

    def get_action(self, state, terminal_name):
        return self.action_table.get((state, terminal_name))

    def get_goto(self, state, non_terminal_name):
        return self.goto_table.get((state, non_terminal_name))


# --- Main Function ---
def compilar(codigo_fuente, inf_filepath, csv_filepath):
    """Realiza todo el proceso de compilación."""
    print("--- Iniciando Proceso de Compilación ---")

    try:
        # 1. Análisis Léxico
        print("\n--- Análisis Léxico ---")
        # Need token_map from grammar first
        grammar = Grammar(inf_filepath)
        token_map = grammar.get_token_map()
        lexer = AnalizadorLexico(codigo_fuente)
        tokens = lexer.analizar()

        print("\nTokens generados:")
        for token in tokens:
            print(token)
        print("--- Fin Análisis Léxico ---")

        # 2. Análisis Sintáctico (con construcción de AST y registro de pila)
        print("\n--- Análisis Sintáctico ---")
        parsing_table = ParsingTable(csv_filepath)
        parser = Parser(lexer, grammar, parsing_table)
        # The parser.parse() method now builds the AST and performs semantic analysis
        syntax_success = parser.parse() # parse() now returns True if syntax & semantic pass

        # Display final errors if any occurred during parsing or semantic analysis
        if parser.errors:
             print("\nCompilacion tuvo errores.")
             return False
        else:
             print("\nCompilacion exitosa.")
             return True


    except FileNotFoundError as e:
        print(f"Error: Archivo no encontrado - {e}", file=sys.stderr)
        return False
    except SyntaxError as e:
        print(f"Error de sintaxis: {e}", file=sys.stderr)
        return False
    except Exception as e:
        # Catch any other unexpected errors during parsing/semantic analysis
        print(f"Ocurrió un error inesperado durante el análisis: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc() # Print traceback for debugging
        return False


def main():
    # Define paths to your grammar files
    inf_filepath = 'compilador.inf'
    csv_filepath = 'compilador.csv'
    # lr_filepath = 'your_grammar.lr' # Not used in this LR implementation

    # Example code snippets
    example1 = """
int main(){
    float a;
    int b;
    int c;
    c = a+b;
    c = suma(8,9);
}
"""

    example2 = """
int a;
int suma(int a, int b){
    return a+b;
}
int main(){
    float a;
    int b;
    int c;
    c = a+b;
    c = suma(8.5,9.9); // Semantic error: assigning float (result of suma) to int c
}
"""
    example3_redeclaration = """
int main() {
    int x;
    float x; // Redeclaration error
    int y;
}
"""

    example4_undeclared = """
int main() {
    a = 10; // Undeclared variable error
    int b;
    c = 20; // Undeclared variable error
}
"""
    example5_type_mismatch_binary = """
int main() {
    int x = 5;
    float y = 2.0;
    int z = x + y; // Type mismatch error (int + float -> float, cannot assign to int)
}
"""
    example6_function_call_error = """
void foo(int a, float b) {}
int main() {
    foo(1.0, 2); // Type mismatch in arguments
    bar(); // Undeclared function
}
"""


    # --- Choose the example to compile ---
    # source_code = example1
    source_code = example2
    # source_code = example3_redeclaration
    # source_code = example4_undeclared
    # source_code = example5_type_mismatch_binary
    # source_code = example6_function_call_error
    # ------------------------------------

    # --- Option 1: Compile hardcoded example ---
    print("Usando código de ejemplo:")
    print("```c")
    print(source_code.strip())
    print("```")
    compilar(source_code, inf_filepath, csv_filepath)

    # --- Option 2: Compile code from a file passed as a command-line argument ---
    # Uncomment the following block if you want to run by passing a file path
    # import sys
    # if len(sys.argv) > 1:
    #     file_path = sys.argv[1]
    #     try:
    #         with open(file_path, 'r') as file:
    #             source_code_from_file = file.read()
    #         print(f"Compilando archivo: {file_path}")
    #         compilar(source_code_from_file, inf_filepath, csv_filepath)
    #     except FileNotFoundError:
    #         print(f"Error: No se pudo encontrar el archivo '{file_path}'", file=sys.stderr)
    # else:
    #     print("Uso: python tu_compilador.py [archivo_fuente.c]", file=sys.stderr)
    #     print("Ejecutando ejemplo hardcoded en su lugar...", file=sys.stderr)
    #     print("```c")
    #     print(source_code.strip())
    #     print("```")
    #     compilar(source_code, inf_filepath, csv_filepath)


if __name__ == "__main__":
    main()