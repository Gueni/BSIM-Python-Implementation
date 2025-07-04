/**
* @file netwriter.h
* @author Jan Bělohoubek
*
* @brief NetWriter
*
*/

#include <stdio.h>
#include <iostream>
#include <string>
#include <iostream>
#include <fstream>
#include <vector>
#include "booleannet.h"
#include "library.h"

#ifndef NETWRITER_H
#define NETWRITER_H

using namespace std;

/**
 * Writes the network defined in BooleanNet to file
 * 
 */
class NetWriter {
  private:
    string basename;
    BooleanNet *net;
    Library *gateLibrary;
    mapAlgorithm_t mapAlg;

  public:
     NetWriter(string basename, BooleanNet * net, string * library,
               mapAlgorithm_t mapAlg);

    void write2TeX(int color);
    void write2Dot(int color);
    void write2Dump(int color);
    void write2Blif(int color);
    void write2Sim(int color);
    void write2MapBlif(int color);
    void write2ngSpice(int color);

    void writeHeatMap(int color);

    // private helper functions
  private:
     string * getTeXPortName(Gate * gate);
    string *getBlifCover(Gate * gate);
    string *getFromLibrary(Gate * gate, libraryFormats_t cellType);
    string *getFromLibrary_negative(Gate * gate,
                                    libraryFormats_t cellType);
    string *getFromLibrary_positive(Gate * gate,
                                    libraryFormats_t cellType);
    string *getFromLibrary_complementary(Gate * gate,
                                         libraryFormats_t cellType);

    string findAndReplace(string * s, string toReplace,
                          string replaceWith);
    string findAndReplaceAll(string * s, string toReplace,
                             string replaceWith);

};

#endif                          /* NETWRITER_H */
