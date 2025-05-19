
import re

token_map = {
    'identificador': 0,
    'entero': 1,
    'real': 2,
    'cadena': 3,
    'tipo': 4,
    'opSuma': 5,
    'opMul': 6,
    'opRelac': 7,
    'opOr': 8,
    'opAnd': 9,
    'opNot': 10,
    'opIgualdad': 11,
    ';': 12,
    ',': 13,
    '(': 14,
    ')': 15,
    '{': 16,
    '}': 17,
    '=': 18,
    'if': 19,
    'while': 20,
    'return': 21,
    'else': 22,
    '$': 23
}

token_specification = [
    ('real', r'\b\d+\.\d+\b'),                        # 2
    ('entero', r'\b\d+\b'),                             # 1
    ('cadena', r'\"[^"\\n]*\"'),                       # 3
    ('tipo', r'\b(?:int|float|void)\b'),                 # 4
    ('opSuma', r'[+-]'),                                   # 5
    ('opMul', r'[*/]'),                                    # 6
    ('opRelac', r'(<=|>=|<|>)'),                           # 7
    ('opOr', r'\|\|'),                                   # 8
    ('opAnd', r'&&'),                                      # 9
    ('opNot', r'!'),                                       # 10
    ('opIgualdad', r'(==|!=)'),                            # 11
    (';', r';'),                                           # 12
    (',', r','),                                           # 13
    ('\(', r'\('),                                       # 14
    ('\)', r'\)'),                                       # 15
    ('\{', r'\{'),                                       # 16
    ('\}', r'\}'),                                       # 17
    ('=', r'='),                                           # 18
    ('if', r'\bif\b'),                                   # 19
    ('while', r'\bwhile\b'),                             # 20
    ('return', r'\breturn\b'),                           # 21
    ('else', r'\belse\b'),                               # 22
    ('\$', r'\$'),                                       # 23
    ('identificador', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),     # 0
    ('SKIP', r'[ \t]+'),                                  # espacios
    ('NEWLINE', r'\n'),                                   # saltos de línea
    ('MISMATCH', r'.'),                                    # cualquier otro
]

def tokenize(code):
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
    get_token = re.compile(tok_regex).match
    pos = 0
    tokens = []
    while pos < len(code):
        match = get_token(code, pos)
        if not match:
            raise RuntimeError(f'Error de tokenización en la posición {pos}')
        kind = match.lastgroup
        value = match.group()
        if kind == 'SKIP' or kind == 'NEWLINE':
            pass
        elif kind == 'MISMATCH':
            raise RuntimeError(f'Token inesperado: {value!r}')
        else:
            tokens.append((token_map.get(kind, kind), value))
        pos = match.end()
    return tokens
