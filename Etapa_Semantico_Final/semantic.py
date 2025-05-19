def semantic_analysis(tokens):
    # Muy básico, solo para validar que no sumes float con int
    for i in range(len(tokens) - 2):
        if tokens[i][0] == 'ID' and tokens[i+1][1] == '=':
            if tokens[i+2][0] == 'FLOAT':
                print(f"⚠️ Advertencia: Asignación de float a {tokens[i][1]}")
