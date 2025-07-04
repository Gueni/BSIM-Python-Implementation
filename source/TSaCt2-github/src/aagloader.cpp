/**
* @file aagloader.cpp
* @author Jan Bělohoubek
*
* @brief AagLoader implementation
*
*/


#include <iostream>
#include <fstream>
#include <string>
#include <stdlib.h>
#include "aagloader.h"
#include "booleannet.h"
#include "gate.h"
#include "output.h"

using namespace std;

/**
 * Load boolean network from file
 * 
 * @param filename aag file
 * @param net pointer for returning the loaded logical net
 */
AagLoader::AagLoader(const char *filename, BooleanNet ** net)
{
    *(Output::trace) << "AagLoader::AagLoader()" << std::endl;

    isLoaded = false;           // file is not loaded now!

    this->aagFile.open(filename, std::ofstream::in);
    if (!this->aagFile.is_open()) {
        *(Output::error) << "Cannot open file." << std::endl;
        return;
    }

    string line;

    if (!this->aagFile.eof()) {
        getline(this->aagFile, line, ' ');
        if (line.compare(0, 3, "aag") != 0) {
            *(Output::error) << "Incorrect format." << std::endl;
            return;
        }
    }

    if (!this->aagFile.eof()) {
        getline(this->aagFile, line, ' ');
        this->M = strtol(line.c_str(), 0, 10);
    } else {
        *(Output::error) << "Unexpected EOF (0)." << std::endl;
        return;
    }

    if (!this->aagFile.eof()) {
        getline(this->aagFile, line, ' ');
        this->I = strtol(line.c_str(), 0, 10);
    } else {
        *(Output::error) << "Unexpected EOF (1)." << std::endl;
        return;
    }

    if (!this->aagFile.eof()) {
        getline(this->aagFile, line, ' ');
        this->L = strtol(line.c_str(), 0, 10);
    } else {
        *(Output::error) << "Unexpected EOF (2)." << std::endl;
        return;
    }

    if (!this->aagFile.eof()) {
        getline(this->aagFile, line, ' ');
        this->O = strtol(line.c_str(), 0, 10);
    } else {
        *(Output::error) << "Unexpected EOF (3)." << std::endl;
        return;
    }

    if (!this->aagFile.eof()) {
        getline(this->aagFile, line, '\n');
        this->A = strtol(line.c_str(), 0, 10);
    } else {
        *(Output::error) << "Unexpected EOF (4)." << std::endl;
        return;
    }

    if (M != (I + L + A)) {
        *(Output::error) << "Incorrect magic numbers." << std::endl;
        return;
    }

    if (L != 0) {
        *(Output::error) <<
            "Latches present! This tool is not able to work with latches in AAG. Remove Latches from design!"
            << std::endl;
        return;
    }

    *(Output::debug) << "AAG header: aag " << M << " " << I << " " << L <<
        " " << O << " " << A << std::endl;

    // create Boolean net
    (*net) = new BooleanNet(I, O, A);

    // load input lines from AAG file
    *(Output::debug) << "AAG inputs:" << std::endl;
    for (int i = 0; i < I; i++) {
        if (!this->aagFile.eof()) {
            getline(this->aagFile, line);
            *(Output::debug) << " " << line << " : " <<
                (strtol(line.c_str(), 0, 10)) / 2 - 1 << std::endl;
        } else {
            return;
        }
    }

    *(Output::debug) << "  - Inputs loaded." << std::endl;

    // load outputs
    *(Output::debug) << "AAG outputs:" << std::endl;
    for (int i = 0; i < O; i++) {
        if (!this->aagFile.eof()) {
            getline(this->aagFile, line);
            int gateNr = (strtol(line.c_str(), 0, 10)); // output gate Number

            if ((gateNr == 1) || (gateNr == 0)) {       // constant FALSE/TRUE
                // remove this output ...
                *(Output::debug) << "Output is constant true or false." <<
                    std::endl;
                (*net)->remOutput(i);
                i--;
                O--;
            } else if ((gateNr / 2 <= I) && (gateNr % 2 == 1)) {
                *(Output::debug) << "Input nr. " << gateNr /
                    2 << " is connected to output using inverter." <<
                    std::endl;
                (*net)->getOutput(i)->
                    newInput((*net)->getInput(gateNr / 2 - 1),
                             /*isInverting */ true);
                (*net)->getInput(gateNr / 2 -
                                 1)->newFollow((*net)->getOutput(i));
            } else if (gateNr / 2 <= I) {
                *(Output::debug) << "Input nr. " << gateNr /
                    2 << " is directly connected to output." << std::endl;
                (*net)->getOutput(i)->
                    newInput((*net)->getInput(gateNr / 2 - 1),
                             /*isInverting */ false);
                (*net)->getInput(gateNr / 2 -
                                 1)->newFollow((*net)->getOutput(i));
            } else {
                if (gateNr % 2 == 1) {  // NAND
                    *(Output::debug) << "Output gate NAND is variable nr. "
                        << gateNr / 2 << std::endl;
                    (*net)->getOutput(i)->
                        newInput((*net)->getGate(gateNr / 2 - I - 1),
                                 /*isInverting */ true);
                    (*net)->getGate(gateNr / 2 - I -
                                    1)->newFollow((*net)->getOutput(i));
                } else {        //AND
                    *(Output::debug) << "Output gate AND is variable nr. "
                        << gateNr / 2 << std::endl;
                    (*net)->getOutput(i)->
                        newInput((*net)->getGate(gateNr / 2 - I - 1),
                                 /*isInverting */ false);
                    (*net)->getGate(gateNr / 2 - I -
                                    1)->newFollow((*net)->getOutput(i));
                }
            }
        } else {
            *(Output::debug) << "Unexpected EOF!" << std::endl;
            return;
        }
    }

    *(Output::debug) << "  - Outputs loaded." << std::endl;

    // load AND nodes
    *(Output::debug) << "Loading AAG AND nodes:" << std::endl;
    for (int i = 0; i < A; i++) {
        if (!this->aagFile.eof()) {
            getline(this->aagFile, line, ' ');
            int gateNr = (strtol(line.c_str(), 0, 10));
            getline(this->aagFile, line, ' ');
            int in1 = (strtol(line.c_str(), 0, 10));
            getline(this->aagFile, line);
            int in2 = (strtol(line.c_str(), 0, 10));

            // Gate logic function descr.
            *(Output::debug) << gateNr / 2 << "=" << in1 /
                2 << "AND" << in2 / 2 << std::endl;

            // are inputs inverting?
            bool isIn1Inverted = ((in1 % 2) == 1) ? true : false;
            bool isIn2Inverted = ((in2 % 2) == 1) ? true : false;

            // modify number dec inputs
            gateNr = gateNr / 2 - I - 1;

            // get gate 
            Gate *gate = (*net)->getGate(gateNr);
            gate->setFunction(AND);

            if (in1 <= (2 * I + 1)) {   // in1 is primary input
                gate->newInput((*net)->getInput(in1 / 2 - 1),
                               isIn1Inverted);
                (*net)->getInput(in1 / 2 - 1)->newFollow(gate);
            } else {            // it is gate output
                gate->newInput((*net)->getGate(in1 / 2 - I - 1),
                               isIn1Inverted);
                (*net)->getGate(in1 / 2 - I - 1)->newFollow(gate);
            }

            if (in2 <= (2 * I + 1)) {   // in2 is primary input
                gate->newInput((*net)->getInput(in2 / 2 - 1),
                               isIn2Inverted);
                (*net)->getInput(in2 / 2 - 1)->newFollow(gate);
            } else {            // it is gate output
                gate->newInput((*net)->getGate(in2 / 2 - I - 1),
                               isIn2Inverted);
                (*net)->getGate(in2 / 2 - I - 1)->newFollow(gate);
            }

        } else {
            *(Output::debug) << "Unexpected EOF!" << std::endl;
            return;
        }
    }

    *(Output::debug) << "  - Input File loaded." << std::endl;

    // file was loaded successfully

    isLoaded = true;
    *(Output::debug) << "  - AAG loader: all done." << std::endl;
    Output::flush();
}

AagLoader::~AagLoader()
{
    this->aagFile.close();
}

bool AagLoader::isFileLoaded()
{
    return isLoaded;
}
