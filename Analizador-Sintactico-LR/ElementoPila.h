// ElementoPila.h
#ifndef ELEMENTOPILA_H
#define ELEMENTOPILA_H

#include <iostream>
using namespace std;

class ElementoPila {
public:
    virtual void muestra() = 0;
    virtual ~ElementoPila() {}
};

#endif // ELEMENTOPILA_H