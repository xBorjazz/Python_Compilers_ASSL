// Pila.cpp
#include "Pila.h"
#include <iostream>

void Pila::muestra() {
    list<Alumno*>::reverse_iterator it;
    Alumno* x;
    cout << "Pila: ";
    for (it = lista.rbegin(); it != lista.rend(); it++) {
        x = *it;
        x->muestra();
    }
    cout << endl;
}