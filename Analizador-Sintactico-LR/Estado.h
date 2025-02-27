// Estado.h
#ifndef ESTADO_H
#define ESTADO_H

#include "ElementoPila.h"

class Estado : public ElementoPila {
private:
    int numero;
public:
    Estado(int numero) : numero(numero) {}
    void muestra() override {
        cout << "Estado: " << numero << endl;
    }
};

#endif // ESTADO_H