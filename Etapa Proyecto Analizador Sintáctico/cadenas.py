import re

def identificar_elemento(elemento):
    # Quitar espacios en blanco al inicio y al final
    elemento = elemento.strip()
    
    # Verificar si es un entero
    if re.fullmatch(r"[+-]?\d+", elemento):
        return f"{elemento}: int"
    
    # Verificar si es un número flotante válido
    elif re.fullmatch(r"[+-]?(\d+\.\d*|\.\d+)", elemento):
        return f"{elemento}: float"
    
    # Verificar si es un identificador válido
    elif re.fullmatch(r"[a-zA-Z_]\w*", elemento):
        return f"{elemento}: id"
    
    # Si no cumple con ninguno de los anteriores, es un error
    else:
        return f"{elemento}: error"

def procesar_entrada(entrada):
    # Dividir la entrada en elementos separados por comas
    elementos = entrada.split(" ")
    # Evaluar cada elemento y devolver el resultado
    resultados = [identificar_elemento(elemento) for elemento in elementos]
    return "\n".join(resultados)

# Solicitar la entrada al usuario
entrada = input("Introduce los valores separados por espacios: ")
print(procesar_entrada(entrada))

