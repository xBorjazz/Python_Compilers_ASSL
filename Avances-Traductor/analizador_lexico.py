# lexical_analyzer.py
from tokens_def import COMPILED_REGEX, Token

class Lexer:
    def __init__(self, code):
        self.code = code
        self.line_num = 1
        self.column_num = 1

    def tokenize(self):
        """
        Convierte el código fuente en una lista de objetos Token.
        Lanza excepciones en caso de errores léxicos.
        """
        tokens = []
        pos = 0
        while pos < len(self.code):
            # Intentamos hacer match en la posición actual
            match = COMPILED_REGEX.match(self.code, pos)
            if not match:
                # No hay coincidencia: error léxico.
                raise Exception(f"Error léxico en línea {self.line_num}, columna {self.column_num}")

            # Nombre del grupo que coincide (p.e. IF, ELSE, IDENT, etc.)
            token_type = match.lastgroup
            # Lexema del token
            token_value = match.group(token_type)

            if token_type == 'COMMENT':
                # Ignoramos comentarios, pero actualizamos la línea y columna si hay saltos de línea
                pass  
            elif token_type == 'SKIP':
                # Espacios o tabulaciones (se ignoran)
                pass
            elif token_type == 'MISMATCH':
                # Carácter o secuencia no válida
                raise Exception(f"Caracter inesperado '{token_value}' "
                                f"en línea {self.line_num}, columna {self.column_num}")
            else:
                # Creamos un token válido
                tokens.append(Token(token_type, token_value, self.line_num, self.column_num))

            # Avanzamos la posición al final de la coincidencia
            end_pos = match.end()
            consumed_len = end_pos - pos
            self.column_num += consumed_len

            # Contamos los saltos de línea para actualizar línea/columna
            for c in self.code[pos:end_pos]:
                if c == '\n':
                    self.line_num += 1
                    self.column_num = 1

            pos = end_pos
        
        return tokens


if __name__ == '__main__':
    # Ejemplo de uso
    code_example = r"""
int x = 10;     // Declaración con asignación
x = x + 5;      // Asignación
float y = 3.14; # Otro tipo de comentario
print(x);
"""
    lexer = Lexer(code_example)
    try:
        token_list = lexer.tokenize()
        print("Tokens generados:")
        for tk in token_list:
            print(tk)
    except Exception as e:
        print("Error léxico:", e)
