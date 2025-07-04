/**
* @file library.cpp
* @author Jan Bělohoubek
*
* @brief Library implementation
*
*/

#include <sys/types.h>
#include <sys/stat.h>
#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <string>
#include <sstream>
#include "library.h"
#include "output.h"

using namespace std;

/**
 * Library constructor
 * 
 */
Library::Library(string libName)
{
    this->libName = new std::string(libName);

    for (int i = 0; i < LIBRARY_FORMATS_LAST; i++) {
        this->hasFormat[i] = false;
    }

    *(Output::debug) << "Opening library " << libName << std::endl;

    struct stat s;
    if (stat(libName.c_str(), &s) == 0) {
        if (s.st_mode & S_IFDIR) {
            *(Output::debug) << "Loading library " << libName << " ... " <<
                std::endl;

            for (int i = 0; i < LIBRARY_FORMATS_LAST; i++) {
                if (stat
                    ((libName + string("/") + cellFormats_s[i]).c_str(),
                     &s) == 0) {
                    if (s.st_mode & S_IFDIR) {
                        *(Output::
                          debug) << cellNames_s[i] << " templates in " <<
                    libName << " exist " << std::endl;
                        this->hasFormat[i] = true;
                    }
                }
            }

            //ALL done
            return;
        }
    }

    *(Output::debug) << "Library " << libName << " does not exist!" <<
        std::endl;

}

inline string getFunctionName(gateFunction_t fn)
{
    switch (fn) {
    case AND:
        return string("AND");
    case OR:
        return string("OR");
    case XOR:
        return string("XOR");
    default:
        return string("BUFFER");
    }
}

string i2str(int nr)
{
    ostringstream stream;
    stream << nr;
    return stream.str();
}

/**
  * Load single cell template from file
  *
  * @param fn gate gate function
  * @param nonInvertedInputs # of noninverted gate inputs
  * @param invertedInputs # of inverted gate inputs
  * @param nonInvertedOutputs # of noninverted gate outputs
  * @param invertedOutputs # of inverted gate outputs
  * @param cellType Type of cells (e.g. IRSIM, BLIF, ...)
  * 
  */
string *Library::getCellTemplate(gateFunction_t fn, byte nonInvertedInputs,
                                 byte invertedInputs,
                                 byte nonInvertedOutputs,
                                 byte invertedOutputs,
                                 libraryFormats_t cellType)
{
    struct stat s;

    string filename =
        getFunctionName(fn).append("_") +
        i2str(nonInvertedInputs).append("_") +
        i2str(invertedInputs).append("_") +
        i2str(nonInvertedOutputs).append("_") + i2str(invertedOutputs);
    string path =
        *(this->libName) + string("/") + cellFormats_s[cellType] +
        string("/") + filename;

    if (stat(path.c_str(), &s) == 0) {
        if (s.st_mode & S_IFREG) {
            std::ifstream infile(path.c_str());
            *(Output::debug) << "Template " << filename << " exist " <<
                std::endl;
            string tmp;
            string *ret = new string("");
            while (!infile.eof()) {
                getline(infile, tmp);
                ret->append(tmp).append("\n");
            }
            return ret;
        }
    }

    *(Output::debug) << "No such cell template: " << filename << std::endl;
    return (string *) NULL;
}

/**
  * Load known models (NAND, NOR, INV)
  * 
  * @param cellType Type of cells (e.g. IRSIM, BLIF, ...)
  * 
  * @retval true if success, else return false
  * 
  */
bool Library::loadModels(libraryFormats_t cellType)
{
    if (this->hasFormat[cellType] == false) {
        return false;
    }

    this->inv[cellType] =
        this->getCellTemplate( /* gateFunction_t fn         = */ BUFFER,
                              /* byte noninvertedInputs    = */ 1,
                              /* byte invertedInputs       = */ 0,
                              /* byte noninvertedOutputs   = */ 0,
                              /* byte invertedOutputs      = */ 1,
                              /* libraryFormats_t cellType = */ cellType);

    this->aand[cellType] =
        this->getCellTemplate( /* gateFunction_t fn         = */ AND,
                              /* byte noninvertedInputs    = */ 2,
                              /* byte invertedInputs       = */ 0,
                              /* byte noninvertedOutputs   = */ 1,
                              /* byte invertedOutputs      = */ 0,
                              /* libraryFormats_t cellType = */ cellType);

    this->nand[cellType] =
        this->getCellTemplate( /* gateFunction_t fn         = */ AND,
                              /* byte noninvertedInputs    = */ 2,
                              /* byte invertedInputs       = */ 0,
                              /* byte noninvertedOutputs   = */ 0,
                              /* byte invertedOutputs      = */ 1,
                              /* libraryFormats_t cellType = */ cellType);

    this->nor[cellType] =
        this->getCellTemplate( /* gateFunction_t fn         = */ OR,
                              /* byte noninvertedInputs    = */ 2,
                              /* byte invertedInputs       = */ 0,
                              /* byte noninvertedOutputs   = */ 0,
                              /* byte invertedOutputs      = */ 1,
                              /* libraryFormats_t cellType = */ cellType);

    this->oor[cellType] =
        this->getCellTemplate( /* gateFunction_t fn         = */ OR,
                              /* byte noninvertedInputs    = */ 2,
                              /* byte invertedInputs       = */ 0,
                              /* byte noninvertedOutputs   = */ 1,
                              /* byte invertedOutputs      = */ 0,
                              /* libraryFormats_t cellType = */ cellType);

    this->cand[cellType] =
        this->getCellTemplate( /* gateFunction_t fn         = */ AND,
                              /* byte noninvertedInputs    = */ 2,
                              /* byte invertedInputs       = */ 2,
                              /* byte noninvertedOutputs   = */ 1,
                              /* byte invertedOutputs      = */ 1,
                              /* libraryFormats_t cellType = */ cellType);
    this->cor[cellType] =
        this->getCellTemplate( /* gateFunction_t fn         = */ OR,
                              /* byte noninvertedInputs    = */ 2,
                              /* byte invertedInputs       = */ 2,
                              /* byte noninvertedOutputs   = */ 1,
                              /* byte invertedOutputs      = */ 1,
                              /* libraryFormats_t cellType = */ cellType);

    if (((this->inv[cellType]) && (this->nand[cellType])
         && (this->nor[cellType])) || ((this->inv[cellType])
                                       && (this->aand[cellType])
                                       && (this->oor[cellType]))
        || ((this->cand[cellType]) && (this->cor[cellType]))) {
        /* all supported combinations for map-functions are/should be enumerated */
        return true;
    } else {
        return false;
    }

}
