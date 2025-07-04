/**
* @file library.h
* @author Jan Bělohoubek
*
* @brief A cell library
*
*/

#include <stdio.h>
#include <iostream>
#include <string>
#include "types.h"

#ifndef LIBRARY_H
#define LIBRARY_H

using namespace std;

/**
 * A library class
 * 
 * It defines: cell library for different gates and output formats
 * 
 * 
 */

class Library {
  public:

  private:
    string * libName;           //< Human readable library name

    string cellFormats_s[LIBRARY_FORMATS_LAST] = { string("irsim"), string("blif"), string("blifmap"), string("tex"), string("ngspice") };      //< Directory names inside the library containing the cell types; \ref libraryFormats_t

    string cellNames_s[LIBRARY_FORMATS_LAST] = { string("IRSIM"), string("BLIF"), string("BLIFMAP"), string("TEX"), string("ngSPICE") };        //< Cell format namesrepresenting the cell types; \ref libraryFormats_t

    string *getCellTemplate(gateFunction_t fn, byte nonInvertedInputs,
                            byte invertedInputs, byte nonInvertedOutputs,
                            byte invertedOutputs,
                            libraryFormats_t cellType);

  public:
    bool hasFormat[LIBRARY_FORMATS_LAST];       //< Contains the library cells in given formats

    /* Basic gates */
    string *inv[LIBRARY_FORMATS_LAST];  //< INV gate templates
    string *nand[LIBRARY_FORMATS_LAST]; //< NAND gate templates
    string *aand[LIBRARY_FORMATS_LAST]; //< AND gate templates
    string *nor[LIBRARY_FORMATS_LAST];  //< NOR gate templates
    string *oor[LIBRARY_FORMATS_LAST];  //< OR gate templates

    /* Complementary gates */
    string *cand[LIBRARY_FORMATS_LAST]; //< complementary AND gate templates
    string *cor[LIBRARY_FORMATS_LAST];  //< complementary AND gate templates

    Library(string libName);
    bool loadModels(libraryFormats_t cellType);


};

#endif
