// Terminal.h
#ifndef TERMINAL_H
#define TERMINAL_H

#include "ElementoPila.h"

class Terminal : public ElementoPila {
private:
    string simbolo;
public:
    Terminal(string simbolo) : simbolo(simbolo) {}
    void muestra() override {
        cout << "Terminal: " << simbolo << endl;
    }
};

#endif // TERMINAL_H