*Avances en la Construcción del Traductor*

Este es el primer avance del traductor, en el cual mediante el analizador_lexico y analizador_sintactico, usamos tokens para validar lineas de código. El funcionamiento es el siguiente:

El archivo   *tokens_def.py*   define la clase Token y las reglas de expresión regular para reconocer cada tipo de token. Luego,   *analizador_lexico.py*   usa esas definiciones para leer el código y producir una lista de tokens. A continuación,   *analizador_sintactico.py*   toma esos tokens y, basándose en una gramática, verifica la estructura del programa. Por último,   *main.py*   integra ambos analizadores para realizar todo el proceso de traducción.

![image](https://github.com/user-attachments/assets/0b812825-d11c-4b6f-94c9-abe0c6caed72)

*main.py*

![image](https://github.com/user-attachments/assets/7e38a476-3a99-49f6-b7c2-a030d5f9c12d)


*tokens_def.py*

![image](https://github.com/user-attachments/assets/03c642ef-c50a-4665-972d-ffd484da9bdd)
![image](https://github.com/user-attachments/assets/13df11d8-8882-43e2-bf30-ead90c810fd2)

*analizador_lexico.py*

![image](https://github.com/user-attachments/assets/b9d0ecad-6e5b-4e62-9075-0ada89ae7024)
 ![image](https://github.com/user-attachments/assets/a3149e02-679f-4e96-b535-34a437739c92)

*analizador_sintactico.py*

![image](https://github.com/user-attachments/assets/a7ea4997-f9d1-4a4c-a1bf-4ead0a7a6aa9)
![image](https://github.com/user-attachments/assets/8d1adbf4-852d-45ae-a5cd-64c8793772f9)
![image](https://github.com/user-attachments/assets/e3acd91a-9183-40c6-ab13-1e1f70a2e9d2)
![image](https://github.com/user-attachments/assets/c11b0697-d92a-47a8-b28b-7a7d36692947)





