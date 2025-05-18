# main.py
from analizador_lexico import Lexer
from analizador_sintactico import Parser

def main():
    # Ejemplo de código a analizar:
    code = """
    int x = 10;
    if (x </ 20) {
        print(x);
    }
    """

    # 1) Analizar léxicamente
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    print("Tokens obtenidos:")
    for tk in tokens:
        print(tk)

    # 2) Analizar sintácticamente
    parser = Parser(tokens)
    try:
        parser.parse()
        print("Análisis sintáctico exitoso. El código es válido.")
    except Exception as e:
        print("Error sintáctico:", e)

if __name__ == "__main__":
    main()
