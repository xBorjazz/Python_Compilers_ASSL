#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from tabulate import tabulate  # Para generar tablas bonitas en la salida

class Token:
    def __init__(self, tipo, valor, linea, columna):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.columna = columna
    
    def __str__(self):
        return f"Token({self.tipo}, '{self.valor}', {self.linea}, {self.columna})"

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
    
    def analizar(self):
        while self.posicion < len(self.codigo_fuente):
            caracter = self.codigo_fuente[self.posicion]
            
            # Ignorar espacios en blanco
            if caracter.isspace():
                if caracter == '\n':
                    self.linea += 1
                    self.columna = 1
                else:
                    self.columna += 1
                self.posicion += 1
                continue
            
            # Comentarios
            if caracter == '/' and self.posicion + 1 < len(self.codigo_fuente):
                if self.codigo_fuente[self.posicion + 1] == '/':
                    # Comentario de línea
                    self.posicion += 2
                    self.columna += 2
                    while (self.posicion < len(self.codigo_fuente) and 
                           self.codigo_fuente[self.posicion] != '\n'):
                        self.posicion += 1
                        self.columna += 1
                    continue
                elif self.codigo_fuente[self.posicion + 1] == '*':
                    # Comentario de bloque
                    self.posicion += 2
                    self.columna += 2
                    while self.posicion + 1 < len(self.codigo_fuente):
                        if (self.codigo_fuente[self.posicion] == '*' and 
                            self.codigo_fuente[self.posicion + 1] == '/'):
                            self.posicion += 2
                            self.columna += 2
                            break
                        if self.codigo_fuente[self.posicion] == '\n':
                            self.linea += 1
                            self.columna = 1
                        else:
                            self.columna += 1
                        self.posicion += 1
                    continue
            
            # Identificadores y palabras reservadas
            if caracter.isalpha() or caracter == '_':
                inicio = self.posicion
                col_inicio = self.columna
                while (self.posicion < len(self.codigo_fuente) and 
                       (self.codigo_fuente[self.posicion].isalnum() or 
                        self.codigo_fuente[self.posicion] == '_')):
                    self.posicion += 1
                    self.columna += 1
                
                valor = self.codigo_fuente[inicio:self.posicion]
                tipo = self.palabras_reservadas.get(valor, 'ID')
                self.tokens.append(Token(tipo, valor, self.linea, col_inicio))
                continue
            
            # Números
            if caracter.isdigit():
                inicio = self.posicion
                col_inicio = self.columna
                es_flotante = False
                
                while self.posicion < len(self.codigo_fuente):
                    if (self.codigo_fuente[self.posicion] == '.' and 
                        not es_flotante and 
                        self.posicion + 1 < len(self.codigo_fuente) and 
                        self.codigo_fuente[self.posicion + 1].isdigit()):
                        es_flotante = True
                        self.posicion += 1
                        self.columna += 1
                    elif self.codigo_fuente[self.posicion].isdigit():
                        self.posicion += 1
                        self.columna += 1
                    else:
                        break
                
                valor = self.codigo_fuente[inicio:self.posicion]
                tipo = 'NUM_FLOAT' if es_flotante else 'NUM_INT'
                self.tokens.append(Token(tipo, valor, self.linea, col_inicio))
                continue
            
            # Caracteres
            if caracter == "'":
                inicio = self.posicion
                col_inicio = self.columna
                self.posicion += 1
                self.columna += 1
                
                # Manejo de escape
                if (self.posicion < len(self.codigo_fuente) and 
                    self.codigo_fuente[self.posicion] == '\\'):
                    self.posicion += 2  # Saltar el carácter de escape y el siguiente
                    self.columna += 2
                elif self.posicion < len(self.codigo_fuente):
                    self.posicion += 1
                    self.columna += 1
                
                # Cerrar comilla
                if (self.posicion < len(self.codigo_fuente) and 
                    self.codigo_fuente[self.posicion] == "'"):
                    self.posicion += 1
                    self.columna += 1
                    valor = self.codigo_fuente[inicio:self.posicion]
                    self.tokens.append(Token('CARACTER', valor, self.linea, col_inicio))
                    continue
                else:
                    # Error: comilla sin cerrar
                    self.tokens.append(Token('ERROR', 'Comilla sin cerrar', self.linea, col_inicio))
                    continue
            
            # Operadores y puntuación
            operadores = {
                '+': 'OP_SUMA',
                '-': 'OP_RESTA',
                '*': 'OP_MULT',
                '/': 'OP_DIV',
                '=': 'OP_ASIG',
                '==': 'OP_IGUAL',
                '!=': 'OP_DIFERENTE',
                '<': 'OP_MENOR',
                '>': 'OP_MAYOR',
                '<=': 'OP_MENOR_IGUAL',
                '>=': 'OP_MAYOR_IGUAL',
                '(': 'PARENTESIS_IZQ',
                ')': 'PARENTESIS_DER',
                '{': 'LLAVE_IZQ',
                '}': 'LLAVE_DER',
                '[': 'CORCHETE_IZQ',
                ']': 'CORCHETE_DER',
                ';': 'PUNTO_COMA',
                ',': 'COMA'
            }
            
            # Operadores dobles
            if (caracter in ['=', '!', '<', '>'] and 
                self.posicion + 1 < len(self.codigo_fuente) and 
                self.codigo_fuente[self.posicion:self.posicion + 2] in operadores):
                valor = self.codigo_fuente[self.posicion:self.posicion + 2]
                self.tokens.append(Token(operadores[valor], valor, self.linea, self.columna))
                self.posicion += 2
                self.columna += 2
                continue
            
            # Operadores simples
            if caracter in operadores:
                self.tokens.append(Token(operadores[caracter], caracter, self.linea, self.columna))
                self.posicion += 1
                self.columna += 1
                continue
            
            # Caracteres no reconocidos
            self.tokens.append(Token('ERROR', caracter, self.linea, self.columna))
            self.posicion += 1
            self.columna += 1
        
        # Agregar token de fin de archivo
        self.tokens.append(Token('EOF', '', self.linea, self.columna))
        return self.tokens

class NodoAST:
    def __init__(self, tipo, valor=None, hijos=None):
        self.tipo = tipo
        self.valor = valor
        self.hijos = hijos if hijos is not None else []
    
    def agregar_hijo(self, hijo):
        self.hijos.append(hijo)
    
    def __str__(self):
        return f"{self.tipo}({self.valor})"

class AnalizadorSintactico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicion = 0
        self.token_actual = self.tokens[0]
        # Para el registro de la pila
        self.pila = []
        self.registro_pila = []
        self.contador_paso = 0
    
    def avanzar(self):
        self.posicion += 1
        if self.posicion < len(self.tokens):
            self.token_actual = self.tokens[self.posicion]
        return self.token_actual
    
    def emparejar(self, tipo_esperado):
        if self.token_actual.tipo == tipo_esperado:
            token = self.token_actual
            self.avanzar()
            return token
        else:
            raise SyntaxError(f"Error de sintaxis: Se esperaba {tipo_esperado} pero se encontró {self.token_actual.tipo} en línea {self.token_actual.linea}, columna {self.token_actual.columna}")
    
    def registrar_pila(self, accion, simbolo_entrada=""):
        """Registra el estado actual de la pila y la acción realizada"""
        self.contador_paso += 1
        entrada = simbolo_entrada if simbolo_entrada else (self.token_actual.valor if self.token_actual else "EOF")
        
        # Formatear pila como string para mostrar
        pila_str = ' '.join(str(item) for item in self.pila)
        
        self.registro_pila.append({
            'paso': self.contador_paso,
            'pila': pila_str,
            'entrada': entrada,
            'accion': accion,
            'salida': ""  # Se llenará cuando corresponda
        })
    
    def actualizar_salida(self, salida):
        """Actualiza la salida del último paso"""
        if self.registro_pila:
            self.registro_pila[-1]['salida'] = salida
    
    def apilar(self, elemento):
        """Apila un elemento y registra la acción"""
        self.pila.append(elemento)
        self.registrar_pila(f"Apilar {elemento}")
    
    def desapilar(self):
        """Desapila un elemento y registra la acción"""
        if self.pila:
            elemento = self.pila.pop()
            self.registrar_pila(f"Desapilar {elemento}")
            return elemento
        return None
    
    def programa(self):
        """
        programa : declaraciones
        """
        self.apilar('$')  # Símbolo de fondo de pila
        self.apilar('programa')
        
        raiz = NodoAST('programa')
        
        while self.pila[-1] != '$':
            simbolo = self.pila[-1]
            
            if simbolo == 'programa':
                self.desapilar()
                self.apilar('declaraciones')
                self.registrar_pila("programa -> declaraciones")
            
            elif simbolo == 'declaraciones':
                self.desapilar()
                if self.token_actual.tipo in ['TIPO_DATO', 'MAIN']:
                    decl = self.declaracion()
                    raiz.agregar_hijo(decl)
                    self.apilar('declaraciones')
                    self.registrar_pila("declaraciones -> declaracion declaraciones")
                else:
                    # declaraciones -> ε
                    self.registrar_pila("declaraciones -> ε")
            
            else:
                # Terminal esperado
                if simbolo == self.token_actual.tipo:
                    self.desapilar()
                    self.registrar_pila(f"Emparejar {simbolo}")
                    self.avanzar()
                else:
                    raise SyntaxError(f"Error de sintaxis: Se esperaba {simbolo} pero se encontró {self.token_actual.tipo}")
        
        # Verificar que hemos consumido todos los tokens
        if self.token_actual.tipo != 'EOF':
            raise SyntaxError(f"Error de sintaxis: Tokens no consumidos después de fin de programa")
        
        return raiz
    
    def declaracion(self):
        """
        declaracion : tipo_dato ID ';'
                    | tipo_dato ID '(' parametros ')' bloque
                    | tipo_dato 'main' '(' parametros ')' bloque
        """
        if self.token_actual.tipo == 'TIPO_DATO':
            tipo = self.emparejar('TIPO_DATO')
            
            # Función main
            if self.token_actual.tipo == 'MAIN':
                self.emparejar('MAIN')
                self.emparejar('PARENTESIS_IZQ')
                params = self.parametros()
                self.emparejar('PARENTESIS_DER')
                bloque_func = self.bloque()
                
                nodo = NodoAST('funcion_main', tipo.valor)
                nodo.agregar_hijo(NodoAST('parametros', hijos=params))
                nodo.agregar_hijo(bloque_func)
                return nodo
            
            # ID (variable o función)
            elif self.token_actual.tipo == 'ID':
                id_token = self.emparejar('ID')
                
                # Función
                if self.token_actual.tipo == 'PARENTESIS_IZQ':
                    self.emparejar('PARENTESIS_IZQ')
                    params = self.parametros()
                    self.emparejar('PARENTESIS_DER')
                    bloque_func = self.bloque()
                    
                    nodo = NodoAST('funcion', id_token.valor)
                    nodo.agregar_hijo(NodoAST('tipo', tipo.valor))
                    nodo.agregar_hijo(NodoAST('parametros', hijos=params))
                    nodo.agregar_hijo(bloque_func)
                    return nodo
                
                # Variable
                else:
                    self.emparejar('PUNTO_COMA')
                    nodo = NodoAST('declaracion_variable')
                    nodo.agregar_hijo(NodoAST('tipo', tipo.valor))
                    nodo.agregar_hijo(NodoAST('id', id_token.valor))
                    return nodo
            
            else:
                raise SyntaxError(f"Error de sintaxis: Se esperaba ID o MAIN pero se encontró {self.token_actual.tipo}")
        
        else:
            raise SyntaxError(f"Error de sintaxis: Se esperaba TIPO_DATO pero se encontró {self.token_actual.tipo}")
    
    def parametros(self):
        """
        parametros : tipo_dato ID (',' tipo_dato ID)*
                   | ε
        """
        params = []
        
        if self.token_actual.tipo == 'TIPO_DATO':
            tipo = self.emparejar('TIPO_DATO')
            id_token = self.emparejar('ID')
            
            param = NodoAST('parametro')
            param.agregar_hijo(NodoAST('tipo', tipo.valor))
            param.agregar_hijo(NodoAST('id', id_token.valor))
            params.append(param)
            
            while self.token_actual.tipo == 'COMA':
                self.emparejar('COMA')
                tipo = self.emparejar('TIPO_DATO')
                id_token = self.emparejar('ID')
                
                param = NodoAST('parametro')
                param.agregar_hijo(NodoAST('tipo', tipo.valor))
                param.agregar_hijo(NodoAST('id', id_token.valor))
                params.append(param)
        
        return params
    
    def bloque(self):
        """
        bloque : '{' sentencias '}'
        """
        self.emparejar('LLAVE_IZQ')
        sentencias = self.sentencias()
        self.emparejar('LLAVE_DER')
        
        nodo = NodoAST('bloque', hijos=sentencias)
        return nodo
    
    def sentencias(self):
        """
        sentencias : sentencia sentencias
                   | ε
        """
        sentencias = []
        
        while self.token_actual.tipo != 'LLAVE_DER' and self.token_actual.tipo != 'EOF':
            sentencia = self.sentencia()
            sentencias.append(sentencia)
        
        return sentencias
    
    def sentencia(self):
        """
        sentencia : declaracion_local
                  | asignacion
                  | llamada_funcion
                  | retorno
                  | sentencia_if
                  | sentencia_while
        """
        if self.token_actual.tipo == 'TIPO_DATO':
            return self.declaracion_local()
        elif self.token_actual.tipo == 'ID':
            if self.tokens[self.posicion + 1].tipo == 'OP_ASIG':
                return self.asignacion()
            else:
                return self.llamada_funcion()
        elif self.token_actual.tipo == 'RETURN':
            return self.retorno()
        elif self.token_actual.tipo == 'IF':
            return self.sentencia_if()
        elif self.token_actual.tipo == 'WHILE':
            return self.sentencia_while()
        else:
            raise SyntaxError(f"Error de sintaxis: Token inesperado {self.token_actual.tipo}")
    
    def declaracion_local(self):
        """
        declaracion_local : tipo_dato ID ';'
        """
        tipo = self.emparejar('TIPO_DATO')
        id_token = self.emparejar('ID')
        self.emparejar('PUNTO_COMA')
        
        nodo = NodoAST('declaracion_local')
        nodo.agregar_hijo(NodoAST('tipo', tipo.valor))
        nodo.agregar_hijo(NodoAST('id', id_token.valor))
        return nodo
    
    def asignacion(self):
        """
        asignacion : ID '=' expresion ';'
        """
        id_token = self.emparejar('ID')
        self.emparejar('OP_ASIG')
        expr = self.expresion()
        self.emparejar('PUNTO_COMA')
        
        nodo = NodoAST('asignacion')
        nodo.agregar_hijo(NodoAST('id', id_token.valor))
        nodo.agregar_hijo(expr)
        return nodo
    
    def llamada_funcion(self):
        """
        llamada_funcion : ID '(' argumentos ')' ';'
        """
        id_token = self.emparejar('ID')
        self.emparejar('PARENTESIS_IZQ')
        args = self.argumentos()
        self.emparejar('PARENTESIS_DER')
        self.emparejar('PUNTO_COMA')
        
        nodo = NodoAST('llamada_funcion', id_token.valor)
        nodo.agregar_hijo(NodoAST('argumentos', hijos=args))
        return nodo
    
    def argumentos(self):
        """
        argumentos : expresion (',' expresion)*
                   | ε
        """
        args = []
        
        if self.token_actual.tipo not in ['PARENTESIS_DER', 'EOF']:
            expr = self.expresion()
            args.append(expr)
            
            while self.token_actual.tipo == 'COMA':
                self.emparejar('COMA')
                expr = self.expresion()
                args.append(expr)
        
        return args
    
    def retorno(self):
        """
        retorno : 'return' expresion ';'
                | 'return' ';'
        """
        self.emparejar('RETURN')
        
        nodo = NodoAST('retorno')
        
        if self.token_actual.tipo != 'PUNTO_COMA':
            expr = self.expresion()
            nodo.agregar_hijo(expr)
        
        self.emparejar('PUNTO_COMA')
        return nodo
    
    def sentencia_if(self):
        """
        sentencia_if : 'if' '(' expresion ')' bloque
                      | 'if' '(' expresion ')' bloque 'else' bloque
        """
        self.emparejar('IF')
        self.emparejar('PARENTESIS_IZQ')
        condicion = self.expresion()
        self.emparejar('PARENTESIS_DER')
        bloque_if = self.bloque()
        
        nodo = NodoAST('sentencia_if')
        nodo.agregar_hijo(condicion)
        nodo.agregar_hijo(bloque_if)
        
        if self.token_actual.tipo == 'ELSE':
            self.emparejar('ELSE')
            bloque_else = self.bloque()
            nodo.agregar_hijo(bloque_else)
        
        return nodo
    
    def sentencia_while(self):
        """
        sentencia_while : 'while' '(' expresion ')' bloque
        """
        self.emparejar('WHILE')
        self.emparejar('PARENTESIS_IZQ')
        condicion = self.expresion()
        self.emparejar('PARENTESIS_DER')
        bloque = self.bloque()
        
        nodo = NodoAST('sentencia_while')
        nodo.agregar_hijo(condicion)
        nodo.agregar_hijo(bloque)
        return nodo
    
    def expresion(self):
        """
        expresion : termino (op_add termino)*
        op_add : '+' | '-'
        """
        izq = self.termino()
        
        while self.token_actual.tipo in ['OP_SUMA', 'OP_RESTA']:
            op = self.token_actual
            self.avanzar()
            der = self.termino()
            
            nuevo_nodo = NodoAST('expresion_binaria', op.tipo)
            nuevo_nodo.agregar_hijo(izq)
            nuevo_nodo.agregar_hijo(der)
            izq = nuevo_nodo
        
        return izq
    
    def termino(self):
        """
        termino : factor (op_mul factor)*
        op_mul : '*' | '/'
        """
        izq = self.factor()
        
        while self.token_actual.tipo in ['OP_MULT', 'OP_DIV']:
            op = self.token_actual
            self.avanzar()
            der = self.factor()
            
            nuevo_nodo = NodoAST('termino_binario', op.tipo)
            nuevo_nodo.agregar_hijo(izq)
            nuevo_nodo.agregar_hijo(der)
            izq = nuevo_nodo
        
        return izq
    
    def factor(self):
        """
        factor : ID
               | NUM_INT
               | NUM_FLOAT
               | CARACTER
               | '(' expresion ')'
               | llamada_funcion_expr
        """
        if self.token_actual.tipo == 'ID':
            # Verificar si es una llamada a función
            if self.posicion + 1 < len(self.tokens) and self.tokens[self.posicion + 1].tipo == 'PARENTESIS_IZQ':
                return self.llamada_funcion_expr()
            else:
                id_token = self.emparejar('ID')
                return NodoAST('id', id_token.valor)
        
        elif self.token_actual.tipo == 'NUM_INT':
            num = self.emparejar('NUM_INT')
            return NodoAST('num_int', num.valor)
        
        elif self.token_actual.tipo == 'NUM_FLOAT':
            num = self.emparejar('NUM_FLOAT')
            return NodoAST('num_float', num.valor)
        
        elif self.token_actual.tipo == 'CARACTER':
            car = self.emparejar('CARACTER')
            return NodoAST('caracter', car.valor)
        
        elif self.token_actual.tipo == 'PARENTESIS_IZQ':
            self.emparejar('PARENTESIS_IZQ')
            expr = self.expresion()
            self.emparejar('PARENTESIS_DER')
            return expr
        
        else:
            raise SyntaxError(f"Error de sintaxis: Token inesperado {self.token_actual.tipo} en factor")
    
    def llamada_funcion_expr(self):
        """
        llamada_funcion_expr : ID '(' argumentos ')'
        """
        id_token = self.emparejar('ID')
        self.emparejar('PARENTESIS_IZQ')
        args = self.argumentos()
        self.emparejar('PARENTESIS_DER')
        
        nodo = NodoAST('llamada_funcion_expr', id_token.valor)
        nodo.agregar_hijo(NodoAST('argumentos', hijos=args))
        return nodo
    
    def analizar(self):
        """Realiza el análisis sintáctico y devuelve el AST"""
        try:
            ast = self.programa()
            return ast, self.registro_pila
        except SyntaxError as e:
            print(f"Error sintáctico: {e}")
            return None, self.registro_pila

class TablaSimbolo:
    def __init__(self):
        self.tabla = {}
        self.nivel_actual = 0
        self.ambitos = [{}]  # Pila de ámbitos
    
    def entrar_ambito(self):
        self.nivel_actual += 1
        self.ambitos.append({})
    
    def salir_ambito(self):
        if self.nivel_actual > 0:
            self.ambitos.pop()
            self.nivel_actual -= 1
    
    def insertar(self, nombre, tipo, categoria="variable", valor=None):
        # Insertar en el ámbito actual
        simbolo = {
            "nombre": nombre,
            "tipo": tipo,
            "categoria": categoria,
            "ambito": self.nivel_actual,
            "valor": valor
        }
        
        self.ambitos[self.nivel_actual][nombre] = simbolo
        self.tabla[nombre] = simbolo
        return simbolo
    
    def buscar(self, nombre):
        # Buscar en todos los ámbitos, empezando por el actual
        for nivel in range(self.nivel_actual, -1, -1):
            if nombre in self.ambitos[nivel]:
                return self.ambitos[nivel][nombre]
        return None
    
    def actualizar(self, nombre, valor):
        simbolo = self.buscar(nombre)
        if simbolo:
            simbolo["valor"] = valor
            return True
        return False

class AnalizadorSemantico:
    def __init__(self, ast):
        self.ast = ast
        self.tabla_simbolos = TablaSimbolo()
        self.errores = []
        # Registro de operaciones semánticas
        self.registro_operaciones = []
        self.contador_paso = 0
    
    def registrar_operacion(self, operacion, detalles=""):
        """Registra una operación semántica"""
        self.contador_paso += 1
        self.registro_operaciones.append({
            'paso': self.contador_paso,
            'operacion': operacion,
            'detalles': detalles
        })
    
    def analizar(self):
        """Analiza semánticamente el AST"""
        if self.ast:
            self.analizar_nodo(self.ast)
            return len(self.errores) == 0, self.errores, self.registro_operaciones
        return False, ["AST inválido"], []
    
    def analizar_nodo(self, nodo):
        """Analiza un nodo del AST"""
        if nodo.tipo == 'programa':
            for hijo in nodo.hijos:
                self.analizar_nodo(hijo)
        
        elif nodo.tipo == 'funcion_main':
            # Registrar la función main
            self.registrar_operacion("Declaración de función", f"main: {nodo.valor}")
            self.tabla_simbolos.insertar('main', nodo.valor, 'funcion')
            
            # Entrar en el ámbito de la función
            self.tabla_simbolos.entrar_ambito()
            
            # Analizar parámetros
            for hijo in nodo.hijos:
                if hijo.tipo == 'parametros':
                    for param in hijo.hijos:
                        self.analizar_nodo(param)
                elif hijo.tipo == 'bloque':
                    self.analizar_nodo(hijo)
            
            # Salir del ámbito de la función
            self.tabla_simbolos.salir_ambito()
        
        elif nodo.tipo == 'funcion':
            # Verificar que no exista otra función con el mismo nombre
            if self.tabla_simbolos.buscar(nodo.valor):
                self.errores.append(f"Error semántico: La función '{nodo.valor}' ya está definida")
                self.registrar_operacion("Error", f"La función '{nodo.valor}' ya está definida")
            return
            
            # Registrar la función
            tipo = nodo.hijos[0].valor
            self.registrar_operacion("Declaración de función", f"{nodo.valor}: {tipo}")
            self.tabla_simbolos.insertar(nodo.valor, tipo, 'funcion')
            
            # Entrar en el ámbito de la función
            self.tabla_simbolos.entrar_ambito()
            
            # Analizar parámetros y bloque
            for hijo in nodo.hijos:
                self.analizar_nodo(hijo)
            
            # Salir del ámbito de la función
            self.tabla_simbolos.salir_ambito()
        
        elif nodo.tipo == 'parametro':
            tipo_nodo = None
            id_nodo = None
            
            for hijo in nodo.hijos:
                if hijo.tipo == 'tipo':
                    tipo_nodo = hijo
                elif hijo.tipo == 'id':
                    id_nodo = hijo
            
            if tipo_nodo and id_nodo:
                # Verificar que no exista otro parámetro con el mismo nombre
                if self.tabla_simbolos.buscar(id_nodo.valor):
                    self.errores.append(f"Error semántico: El parámetro '{id_nodo.valor}' ya está definido")
                    self.registrar_operacion("Error", f"El parámetro '{id_nodo.valor}' ya está definido")
                else:
                    self.registrar_operacion("Declaración de parámetro", f"{id_nodo.valor}: {tipo_nodo.valor}")
                    self.tabla_simbolos.insertar(id_nodo.valor, tipo_nodo.valor, 'parametro')
        
        elif nodo.tipo == 'bloque':
            for sentencia in nodo.hijos:
                self.analizar_nodo(sentencia)
        
        elif nodo.tipo == 'declaracion_variable' or nodo.tipo == 'declaracion_local':
            tipo_nodo = None
            id_nodo = None
            
            for hijo in nodo.hijos:
                if hijo.tipo == 'tipo':
                    tipo_nodo = hijo
                elif hijo.tipo == 'id':
                    id_nodo = hijo
            
            if tipo_nodo and id_nodo:
                # Verificar que no exista otra variable con el mismo nombre en el ámbito actual
                simbolo = self.tabla_simbolos.buscar(id_nodo.valor)
                if simbolo and simbolo['ambito'] == self.tabla_simbolos.nivel_actual:
                    self.errores.append(f"Error semántico: La variable '{id_nodo.valor}' ya está definida en este ámbito")
                    self.registrar_operacion("Error", f"La variable '{id_nodo.valor}' ya está definida en este ámbito")
                else:
                    self.registrar_operacion("Declaración de variable", f"{id_nodo.valor}: {tipo_nodo.valor}")
                    self.tabla_simbolos.insertar(id_nodo.valor, tipo_nodo.valor, 'variable')
        
        elif nodo.tipo == 'asignacion':
            id_nodo = nodo.hijos[0]
            expr_nodo = nodo.hijos[1]
            
            # Verificar que la variable esté definida
            simbolo = self.tabla_simbolos.buscar(id_nodo.valor)
            if not simbolo:
                self.errores.append(f"Error semántico: La variable '{id_nodo.valor}' no está definida")
                self.registrar_operacion("Error", f"La variable '{id_nodo.valor}' no está definida")
            else:
                # Verificar compatibilidad de tipos
                tipo_expr = self.inferir_tipo(expr_nodo)
                if tipo_expr and tipo_expr != simbolo['tipo']:
                    self.errores.append(f"Error semántico: Incompatibilidad de tipos en asignación a '{id_nodo.valor}'")
                    self.registrar_operacion("Error", f"Incompatibilidad de tipos en asignación a '{id_nodo.valor}'")
                else:
                    self.registrar_operacion("Asignación", f"{id_nodo.valor} = expresión")
                
                # Analizar la expresión
                self.analizar_nodo(expr_nodo)
        
        elif nodo.tipo == 'llamada_funcion' or nodo.tipo == 'llamada_funcion_expr':
            # Verificar que la función esté definida
            simbolo = self.tabla_simbolos.buscar(nodo.valor)
            if not simbolo or simbolo['categoria'] != 'funcion':
                self.errores.append(f"Error semántico: La función '{nodo.valor}' no está definida")
                self.registrar_operacion("Error", f"La función '{nodo.valor}' no está definida")
            else:
                self.registrar_operacion("Llamada a función", f"{nodo.valor}()")
                
                # Analizar argumentos
                for hijo in nodo.hijos:
                    if hijo.tipo == 'argumentos':
                        for arg in hijo.hijos:
                            self.analizar_nodo(arg)
        
        elif nodo.tipo == 'retorno':
            if nodo.hijos:
                # Verificar compatibilidad con el tipo de retorno de la función
                self.analizar_nodo(nodo.hijos[0])
                self.registrar_operacion("Retorno", "return expresión")
            else:
                self.registrar_operacion("Retorno", "return")
        
        elif nodo.tipo == 'sentencia_if':
            # Analizar condición
            self.analizar_nodo(nodo.hijos[0])
            self.registrar_operacion("Sentencia condicional", "if")
            
            # Analizar bloque if
            self.tabla_simbolos.entrar_ambito()
            self.analizar_nodo(nodo.hijos[1])
            self.tabla_simbolos.salir_ambito()
            
            # Analizar bloque else si existe
            if len(nodo.hijos) > 2:
                self.registrar_operacion("Sentencia condicional", "else")
                self.tabla_simbolos.entrar_ambito()
                self.analizar_nodo(nodo.hijos[2])
                self.tabla_simbolos.salir_ambito()
        
        elif nodo.tipo == 'sentencia_while':
            # Analizar condición
            self.analizar_nodo(nodo.hijos[0])
            self.registrar_operacion("Sentencia iterativa", "while")
            
            # Analizar bloque
            self.tabla_simbolos.entrar_ambito()
            self.analizar_nodo(nodo.hijos[1])
            self.tabla_simbolos.salir_ambito()
        
        elif nodo.tipo in ['expresion_binaria', 'termino_binario']:
            # Analizar operandos
            self.analizar_nodo(nodo.hijos[0])
            self.analizar_nodo(nodo.hijos[1])
            
            # Verificar compatibilidad de tipos
            tipo_izq = self.inferir_tipo(nodo.hijos[0])
            tipo_der = self.inferir_tipo(nodo.hijos[1])
            
            if tipo_izq and tipo_der and tipo_izq != tipo_der:
                self.errores.append(f"Error semántico: Incompatibilidad de tipos en operación binaria")
                self.registrar_operacion("Error", "Incompatibilidad de tipos en operación binaria")
            else:
                op = "+" if nodo.valor == "OP_SUMA" else "-" if nodo.valor == "OP_RESTA" else "*" if nodo.valor == "OP_MULT" else "/"
                self.registrar_operacion("Operación binaria", f"expresión {op} expresión")
        
        elif nodo.tipo == 'id':
            # Verificar que la variable esté definida
            simbolo = self.tabla_simbolos.buscar(nodo.valor)
            if not simbolo:
                self.errores.append(f"Error semántico: La variable '{nodo.valor}' no está definida")
                self.registrar_operacion("Error", f"La variable '{nodo.valor}' no está definida")
            else:
                self.registrar_operacion("Uso de variable", nodo.valor)
    
    def inferir_tipo(self, nodo):
        """Infiere el tipo de una expresión"""
        if nodo.tipo == 'id':
            simbolo = self.tabla_simbolos.buscar(nodo.valor)
            if simbolo:
                return simbolo['tipo']
            return None
        
        elif nodo.tipo == 'num_int':
            return 'int'
        
        elif nodo.tipo == 'num_float':
            return 'float'
        
        elif nodo.tipo == 'caracter':
            return 'char'
        
        elif nodo.tipo in ['expresion_binaria', 'termino_binario']:
            tipo_izq = self.inferir_tipo(nodo.hijos[0])
            tipo_der = self.inferir_tipo(nodo.hijos[1])
            
            # Reglas básicas de promoción de tipos
            if tipo_izq == 'float' or tipo_der == 'float':
                return 'float'
            elif tipo_izq == 'int' and tipo_der == 'int':
                return 'int'
            
            return None
        
        elif nodo.tipo == 'llamada_funcion_expr':
            simbolo = self.tabla_simbolos.buscar(nodo.valor)
            if simbolo and simbolo['categoria'] == 'funcion':
                return simbolo['tipo']
            return None
        
        return None

def mostrar_tabla_registros(registros, titulo):
    """Muestra una tabla bonita con los registros"""
    if registros:
        encabezados = registros[0].keys()
        tabla = [[registro[key] for key in encabezados] for registro in registros]
        print(f"\n{titulo}:")
        print(tabulate(tabla, headers=encabezados, tablefmt="grid"))
    else:
        print(f"\n{titulo}: No hay registros.")

def compilar(codigo_fuente):
    """Realiza todo el proceso de compilación"""
    # Análisis léxico
    lexico = AnalizadorLexico(codigo_fuente)
    tokens = lexico.analizar()
    
    # Mostrar tokens
    print("\nTokens generados:")
    for token in tokens:
        print(token)
    
    # Análisis sintáctico
    sintactico = AnalizadorSintactico(tokens)
    ast, registro_pila = sintactico.analizar()
    
    # Mostrar registro de la pila
    mostrar_tabla_registros(registro_pila, "Registro de la Pila")
    
    if not ast:
        print("\nError en el análisis sintáctico. No se puede continuar.")
        return False
    
    # Análisis semántico
    semantico = AnalizadorSemantico(ast)
    resultado, errores, registro_operaciones = semantico.analizar()
    
    # Mostrar registro de operaciones semánticas
    mostrar_tabla_registros(registro_operaciones, "Registro de Operaciones Semánticas")
    
    if not resultado:
        print("\nErrores semánticos:")
        for error in errores:
            print(f"- {error}")
        return False
    
    print("\nCompilación exitosa.")
    return True

# Ejemplo de código fuente para probar
codigo_ejemplo = """
int main() {
    int a;
    c = a + b;
}
"""

if __name__ == "__main__":
    # Para usar desde la línea de comandos
    import sys
    
    if len(sys.argv) > 1:
        # Leer archivo fuente
        try:
            with open(sys.argv[1], 'r') as archivo:
                codigo_fuente = archivo.read()
            compilar(codigo_fuente)
        except FileNotFoundError:
            print(f"Error: No se pudo encontrar el archivo '{sys.argv[1]}'")
    else:
        # Usar código de ejemplo
        print("Usando código de ejemplo:")
        print(codigo_ejemplo)
        compilar(codigo_ejemplo)
