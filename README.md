*Avances en la Construcción del Traductor*

Este es el primer avance del traductor, en el cual mediante el analizador_lexico y analizador_sintactico, usamos tokens para validar lineas de código. El funcionamiento es el siguiente:

El archivo   *tokens_def.py*   define la clase Token y las reglas de expresión regular para reconocer cada tipo de token. Luego,   *analizador_lexico.py*   usa esas definiciones para leer el código y producir una lista de tokens. A continuación,   *analizador_sintactico.py*   toma esos tokens y, basándose en una gramática, verifica la estructura del programa. Por último,   *main.py*   integra ambos analizadores para realizar todo el proceso de traducción.

![image](https://github.com/user-attachments/assets/0b812825-d11c-4b6f-94c9-abe0c6caed72)

