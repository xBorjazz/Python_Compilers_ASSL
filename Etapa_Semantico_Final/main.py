import pandas as pd
from lexer import tokenize
from parser_lr import LRParser
from stack_trace import print_stack

def load_table(csv_file):
    df = pd.read_csv(csv_file, index_col=0)
    df = df.astype(str).fillna('')  # Solución al warning
    return df

def load_rules(filename):
    rules = {}
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) != 3:
                continue  # Saltar líneas mal formateadas
            try:
                rule_num = int(parts[0])
                size = int(parts[1])
                head = parts[2]
                rules[rule_num] = (size, head)
            except ValueError:
                continue
    return rules

def main():
    # Leer líneas de código desde archivo
    with open("codigo.txt", "r", encoding="utf-8") as f:
        code_lines = f.readlines()

    table = load_table("compilador.csv")
    rules = load_rules("compilador.lr")
    parser = LRParser(table, rules)

    for i, line in enumerate(code_lines, 1):
        line = line.strip()
        if not line:
            continue
        print(f"\n🟡 Línea {i}: {line}")
        try:
            tokens = tokenize(line)
            tokens.append(('$', 23))  # EOF
            parser.parse(tokens)
        except SyntaxError as e:
            print(f"❌ Error en la línea {i}: {e}")
        except Exception as e:
            print(f"❌ Error inesperado en la línea {i}: {e}")

if __name__ == "__main__":
    main()
