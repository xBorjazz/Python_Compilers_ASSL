from graphviz import Digraph

def generate_tree(input_file, output_image):
    # Lee el archivo de entrada
    
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]

    # Crea el árbol con Graphviz
    dot = Digraph(comment='Árbol del Esquema')
    dot.node('root', 'Programa')  # Nodo raíz

    for i, line in enumerate(lines):
        tokens = line.split()
        type_ = tokens[0]
        name = tokens[1]
        rules = tokens[2:]

        # Nodo principal para cada definición
        parent_id = f'node_{i}'
        dot.node(parent_id, name)
        dot.edge('root', parent_id)

        # Agrega el tipo como hijo
        type_id = f'{parent_id}_type'
        dot.node(type_id, type_)
        dot.edge(parent_id, type_id)

        # Agrega las reglas como hijos
        for j, rule in enumerate(rules):
            rule_id = f'{parent_id}_rule_{j}'
            dot.node(rule_id, rule)
            dot.edge(parent_id, rule_id)

    # Guarda el árbol como imagen
    dot.render(output_image, format='png', cleanup=True)
    print(f"Árbol generado y guardado como {output_image}.png")

# Configuración
INPUT_FILE = 'example.txt'
OUTPUT_IMAGE = 'tree.png'
generate_tree(INPUT_FILE, OUTPUT_IMAGE)