/**
* @file aagloader.h
* @author Jan Bělohoubek
*
* @brief AagLoader
*
*/


#include <stdio.h>
#include <iostream>
#include <string>
#include <iostream>
#include <fstream>
#include "gate.h"
#include "booleannet.h"

#ifndef AAGLOADER_H
#define AAGLOADER_H

using namespace std;

/**
 * AAgLoader class
 * This class loads the aag file to boolean network
 * 
 */
class AagLoader {
  private:
    ifstream aagFile;
    int M;
    int I;
    int L;
    int O;
    int A;
    bool isLoaded;

  public:
     AagLoader(const char *filename, BooleanNet ** net);
    ~AagLoader();
    bool isFileLoaded();
};

#endif                          /* AAGLOADER_H */
