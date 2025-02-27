// NoTerminal.h
#ifndef NOTERMINAL_H
#define NOTERMINAL_H

#include "ElementoPila.h"

class NoTerminal : public ElementoPila {
private:
    string simbolo;
public:
    NoTerminal(string simbolo) : simbolo(simbolo) {}
    void muestra() override {
        cout << "No Terminal: " << simbolo << endl;
    }
};

#endif // NOTERMINAL_H