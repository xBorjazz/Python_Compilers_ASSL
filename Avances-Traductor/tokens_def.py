# tokens_def.py
import re

class Token:
    """
    Representa un token individual.
    """
    def __init__(self, type_, value, line, column):
        self.type = type_    # tipo de token, por ejemplo 'IF', 'INT_LIT', 'IDENT', etc.
        self.value = value   # el lexema (texto) original del token
        self.line = line     # número de línea donde aparece el token
        self.column = column # número de columna donde aparece el token

    def __repr__(self):
        return f"Token({self.type}, '{self.value}', {self.line}, {self.column})"


# Lista de (nombre_de_token, regex) en el orden que deben probarse
TOKEN_SPECIFICATION = [
    # Palabras reservadas
    ('IF',       r'\bif\b'),
    ('ELSE',     r'\belse\b'),
    ('WHILE',    r'\bwhile\b'),
    ('PRINT',    r'\bprint\b'),
    ('INT',      r'\bint\b'),
    ('FLOAT',    r'\bfloat\b'),

    # Operadores y símbolos
    ('OP_EQ',    r'=='),
    ('OP_NEQ',   r'!='),
    ('OP_LEQ',   r'<='),
    ('OP_GEQ',   r'>='),
    ('OP_LT',    r'<'),
    ('OP_GT',    r'>'),
    ('ASSIGN',   r'='),

    ('PLUS',     r'\+'),
    ('MINUS',    r'\-'),
    ('MULT',     r'\*'),
    ('DIV',      r'\/'),

    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('LBRACE',   r'\{'),
    ('RBRACE',   r'\}'),
    ('SEMI',     r';'),

    # Literales numéricos
    ('FLOAT_LIT',r'\d+\.\d+'),
    ('INT_LIT',  r'\d+'),

    # Identificadores
    ('IDENT',    r'[a-zA-Z_]\w*'),

    # Comentarios de línea (ignorar)
    ('COMMENT',  r'(//[^\n]*|#[^\n]*)'),
    
    # Espacios en blanco (ignorar)
    ('SKIP', r'[ \t\r\n]+'),


    # Cualquier otro carácter no válido
    ('MISMATCH', r'.'),
]

# Construimos una única expresión regular con grupos nombrados
TOK_REGEX = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in TOKEN_SPECIFICATION)
COMPILED_REGEX = re.compile(TOK_REGEX)
