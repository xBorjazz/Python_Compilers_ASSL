// main.cpp
#include "Pila.h"
#include <iostream>
using namespace std;

void ejemplo() {
    Pila pila;
    Alumno* alumno;
    alumno = new Licenciatura("345678", "Computacion", 200);
    pila.push(alumno);
    pila.push(new Bachillerato("456789", "Preparatoria 12"));
    pila.push(new Licenciatura("456789", "Informatica", 50));
    pila.muestra();
    cout << "*********************************" << endl;
    pila.pop();
    pila.muestra();
}

int main() {
    ejemplo();
    return 0;
}
