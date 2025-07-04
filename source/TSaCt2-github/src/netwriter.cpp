/**
* @file netwriter.cpp
* @author Jan Bělohoubek
*
* @brief NetWriter implementation
*
*/

#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include <fstream>
#include <string>
#include <stack>
#include "netwriter.h"
#include "output.h"
#include "booleannet.h"
#include "gate.h"
#include "library.h"

using namespace std;

/**
 * NetWriter constructor
 * 
 * @param basename basename for the output file
 * @param net boolean network to write
 * @param lib gate library
 * @param mapAlg selected mapping algoritm
 * 
 */
NetWriter::NetWriter(string basename, BooleanNet * net, string * library,
                     mapAlgorithm_t mapAlg)
{
    *(Output::trace) << "NetWriter(" << basename << ")" << std::endl;
    this->basename = basename;
    this->net = net;
    this->mapAlg = mapAlg;
    if (library != NULL) {
        this->gateLibrary = new Library(*library);
    } else {
        this->gateLibrary = NULL;
    }
    /* Info - selected map alg. */
    if (this->mapAlg == MAP_NEGATIVE) {
        *(Output::trace) << "NetWriter::MapAlg=NEGATIVE" << std::endl;
    } else if (this->mapAlg == MAP_POSITIVE) {
        *(Output::trace) << "NetWriter::MapAlg=POSITIVE" << std::endl;
    } else if (this->mapAlg == MAP_NATURAL) {
        *(Output::trace) << "NetWriter::MapAlg=NATURAL" << std::endl;
    }
}

/**
 * Print boolean network to drawable tex file
 * 
 * @param color print gates denoted by selected color only (use 1 for all gates in the network)
 * 
 */
void NetWriter::write2TeX(int color)
{
    *(Output::trace) << "NetWriter::write2Tex()" << std::endl;
    std::vector < int >cnt(net->getNetDepth() + 1, 0);  // position counter for each depth
    std::vector < int >cnt2(net->getNetDepth() + 1, 0); // position counter for each depth

    // open output file
    std::string filename = basename;
    filename.append(".tex", 4);
    std::ofstream * outf = new std::ofstream();
    outf->open(filename.c_str());

    // head
    *outf << "\\documentclass{standalone}" << std::endl;
    *outf << "\\usepackage{circuitikz}" << std::endl;
    *outf << "\\begin{document}" << std::endl;
    *outf << "\\begin{circuitikz} \\draw" << std::endl;

    // print inputs
    for (int i = 0; i < this->net->getIn(); i++) {
        if (this->net->getInput(i) != NULL) {
            if (this->net->getInput(i)->hasColor(color)) {
                string *port =
                    this->getTeXPortName(this->net->getInput(i));

                *outf << "(" << 4 *
                    this->net->getInput(i)->getDepth() << "," << 4 *
                    ((cnt.at(this->net->getInput(i)->getDepth()))) <<
                    ") node[" << *port << ", color=blue] (" << this->net->
                    getInput(i)->getName() << ") {} node[yshift=-1.0cm] {"
                    << i << " (" << (2 * i + 2) << ")" "}" << std::endl;

                delete(port);

                (cnt.at(this->net->getInput(i)->getDepth()))++;
            }
        }
    }
    *(Output::debug) << "  - Inputs printed." << std::endl;

    // print outputs
    for (int i = 0; i < this->net->getOut(); i++) {
        if (this->net->getOutput(i) != NULL) {
            if (this->net->getOutput(i)->hasColor(color)) {
                string *port =
                    this->getTeXPortName(this->net->getOutput(i));

                *outf << "(" << 4 *
                    this->net->getOutput(i)->getDepth() << "," << 4 *
                    ((cnt.at(this->net->getOutput(i)->getDepth()))) <<
                    ") node[" << *port << ", color=blue] (" << this->net->
                    getOutput(i)->getName() << ")" <<
                    "{} node[yshift=-1.0cm] {}" << std::endl;

                delete(port);

                (cnt.at(this->net->getOutput(i)->getDepth()))++;
            }
        }
    }
    *(Output::debug) << "  - Outputs printed." << std::endl;

    // print gates
    for (int i = 0; i < this->net->getGates(); i++) {
        if (this->net->getGate(i) != NULL) {
            if (this->net->getGate(i)->hasColor(color)) {
                string *port = this->getTeXPortName(this->net->getGate(i));

                *outf << "(" << 4 *
                    this->net->getGate(i)->getDepth() << "," << 4 *
                    ((cnt.at(this->net->getGate(i)->getDepth()))) <<
                    ") node[" << *port << ", color=blue] (" << this->net->
                    getGate(i)->getName() <<
                    ") {} node[yshift=-1.0cm,xshift=-0.6cm] {" << i << " ("
                    << (2 *
                        (i + this->net->getIn() +
                         1)) << ")" << "}" << std::endl;

                *outf << "node[yshift=-1.5cm,xshift=-0.6cm] {SCOAP: " <<
                    this->net->
                    getGate(i)->get0Controlability() << "/" << this->net->
                    getGate(i)->get1Controlability() << "/" << this->net->
                    getGate(i)->getObservability() << "}" << std::endl;

                *outf << "node[yshift=0.2cm,xshift=0.8cm] {FO = " <<
                    this->net->getGate(i)->getFanOut() << "}" << std::endl;

                delete(port);

                (cnt.at(this->net->getGate(i)->getDepth()))++;
            }
        }
    }
    *(Output::debug) << "  - Gates printed." << std::endl;

    *outf << ";\\draw[thick]" << std::endl;

    // print edges
    for (int i = 0; i < this->net->getGates(); i++) {
        if (this->net->getGate(i) != NULL) {
            if (this->net->getGate(i)->hasColor(color)) {
                for (int j = 0; j < this->net->getGate(i)->getFanIn(); j++) {
                    if (this->net->getGate(i)->getDriver(j) != NULL) {
                        if (this->net->getGate(i)->
                            getDriver(j)->hasColor(color)) {
                            *outf << ";\\draw[color=red, thick]";

                            if (this->net->getGate(i)->getFunction() ==
                                BUFFER) {
                                *outf << "(" << this->net->
                                    getGate(i)->getDriver(j)->getName() <<
                                    ".out) -- (" << this->net->
                                    getGate(i)->getName() << ".in)" <<
                                    std::endl;

                                // print inverters
                                if (this->net->
                                    getGate(i)->isInputInverting(j)) {
                                    *outf << ";\\draw (" << this->
                                        net->getGate(i)->getName() <<
                                        ".in) [xshift=0.12cm,thick,color=blue,fill=white]circle (0.1cm);"
                                        << std::endl;
                                }
                            } else {
                                *outf << "(" << this->net->
                                    getGate(i)->getDriver(j)->getName() <<
                                    ".out) -- (" << this->net->
                                    getGate(i)->getName() << ".in " << j +
                                    1 << ")" << std::endl;

                                // print inverters
                                if (this->net->
                                    getGate(i)->isInputInverting(j)) {
                                    *outf << ";\\draw (" << this->
                                        net->getGate(i)->getName() <<
                                        ".in " << j +
                                        1 <<
                                        ") [xshift=0.12cm,thick,color=blue,fill=white]circle (0.1cm);"
                                        << std::endl;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    *(Output::debug) << "  - Edges printed." << std::endl;

    // print input connections
    for (int i = 0; i < this->net->getIn(); i++) {
        if (this->net->getInput(i) != NULL) {
            if (this->net->getInput(i)->hasColor(color)) {
                if (this->net->getInput(i)->getFanIn() == 1) {
                    *outf << ";\\draw[color=blue, thick]";
                    *outf << "(" << this->net->getInput(i)->
                        getDriver(0)->getName() << ".out) -- (" << this->
                        net->getInput(i)->getName() << ".in" << ")" <<
                        std::endl;
                }
            }
        }
    }
    *(Output::debug) << "  - Input connections printed." << std::endl;

    // print output edges
    for (int i = 0; i < this->net->getOut(); i++) {
        if (this->net->getOutput(i) != NULL) {
            if (this->net->getOutput(i)->hasColor(color)) {
                *outf << ";\\draw[color=red, thick]";
                *outf << "(" << this->net->getOutput(i)->
                    getDriver(0)->getName() << ".out) -- (" << this->net->
                    getOutput(i)->getName() << ".in" << ")" << std::endl;

                // print inverters
                if (this->net->getOutput(i)->isInputInverting(0)) {
                    *outf << ";\\draw (" << this->net->
                        getOutput(i)->getName() << ".in" <<
                        ") [xshift=0.12cm,thick,color=blue,fill=white]circle (0.1cm);"
                        << std::endl;
                }
            }
        }
    }
    *(Output::debug) << "  - Edges printed." << std::endl;

    // foot
    *outf << ";\\end{circuitikz}" << std::endl;
    *outf << "\\end{document}" << std::endl;

    outf->close();
    Output::flush();
}

/**
 * Print boolean network to Graphviz DOT file
 * 
 * @param color print gates denoted by selected color only
 * 
 */
void NetWriter::write2Dot(int color)
{
    *(Output::trace) << "NetWriter::write2Dot()" << std::endl;

    // open output file
    std::string filename = basename;
    filename.append(".dot", 4);
    std::ofstream * outf = new std::ofstream();
    outf->open(filename.c_str());

    vector < std::string > ranks(this->net->getNetDepth() + 1);

    // head
    *outf << "graph circ {" << std::endl;
    *outf << "  splines=ortho;" << std::endl;
    *outf << "  nodesep=0.005;" << std::endl;
    *outf << "  rankdir=\"RL\";" << std::endl;
    *outf << "" << std::endl;
    *outf << "  node [shape=box width=1.5];" << std::endl;

    *outf << "" << std::endl;
    *outf << "  # Circuit inputs:" << std::endl;
    // print inputs
    for (int i = 0; i < this->net->getIn(); i++) {
        if (this->net->getInput(i) != NULL) {
            if (this->net->getInput(i)->hasColor(color)) {

                *outf << "  " + this->net->getInput(i)->getName() +
                    " [label=\"" + this->net->getInput(i)->getName() +
                    "\" shape=circle];" << std::endl;

                // append to the rang to get the same depth
                ranks[0].append(this->net->getInput(i)->getName());
                ranks[0].append(" ", 1);
            }
        }
    }

    *(Output::debug) << "  - Inputs printed." << std::endl;

    *outf << "" << std::endl;
    *outf << "  # Circuit outputs:" << std::endl;
    // print outputs
    for (int i = 0; i < this->net->getOut(); i++) {
        if (this->net->getOutput(i) != NULL) {
            if (this->net->getOutput(i)->hasColor(color)) {

                *outf << "  " + this->net->getOutput(i)->getName() +
                    " [label=\"" + this->net->getOutput(i)->getName() +
                    "\" shape=circle];" << std::endl;

                // append to the rang to get the same depth
                ranks[this->net->getNetDepth()].append(this->net->
                                                       getOutput(i)->
                                                       getName());
                ranks[this->net->getNetDepth()].append(" ", 1);

                for (int j = 0; j < this->net->getOutput(i)->getFanIn();
                     j++) {
                    if (this->net->getOutput(i)->getDriver(j) != NULL) {
                        if (this->net->getOutput(i)->
                            getDriver(j)->hasColor(color)) {

                            *outf << "  " +
                                this->net->getOutput(i)->getName() +
                                " -- " +
                                this->net->getOutput(i)->getDriver(j)->
                                getName() + " [";

                            if ((this->net->getOutput(i)->
                                 isInputInverting(j) ^ this->net->
                                 getOutput(i)->getDriver(j)->
                                 isOutputInverting()) == true) {
                                if (this->net->getOutput(i)->getDriver(j)->
                                    isOutputInverting()) {
                                    *outf <<
                                        " dir=forward arrowhead=\"odot\"";
                                } else {
                                    *outf <<
                                        " dir=back arrowtail=\"odot\"";
                                }
                            }

                            *outf << "];" << std::endl;

                        }
                    }
                }

            }
        }
    }

    *(Output::debug) << "  - Outputs printed." << std::endl;

    *outf << "" << std::endl;
    *outf << "  # Circuit gates:" << std::endl;

    // print gates
    for (int i = 0; i < this->net->getGates(); i++) {
        if (this->net->getGate(i) != NULL) {
            if (this->net->getGate(i)->hasColor(color)) {
                *outf << "  " + this->net->getGate(i)->getName() +
                    " [label=<" +
                    this->net->getGate(i)->getFunctionName() +
                    "<BR /><FONT POINT-SIZE=\"10\">" +
                    this->net->getGate(i)->getName() +
                    "</FONT>>];" << std::endl;

                // append to the rang to get the same depth
                ranks[this->net->getGate(i)->getDepth()].append(this->net->
                                                                getGate
                                                                (i)->
                                                                getName());
                ranks[this->net->getGate(i)->getDepth()].append(" ", 1);

                for (int j = 0; j < this->net->getGate(i)->getFanIn(); j++) {
                    if (this->net->getGate(i)->getDriver(j) != NULL) {
                        if (this->net->getGate(i)->
                            getDriver(j)->hasColor(color)) {

                            *outf << "  " +
                                this->net->getGate(i)->getName() + " -- " +
                                this->net->getGate(i)->getDriver(j)->
                                getName() + " [";

                            if ((this->net->getGate(i)->
                                 isInputInverting(j) ^ this->net->
                                 getGate(i)->getDriver(j)->
                                 isOutputInverting()) == true) {
                                if (this->net->getGate(i)->getDriver(j)->
                                    isOutputInverting()) {
                                    *outf <<
                                        " dir=forward arrowhead=\"odot\"";
                                } else {
                                    *outf <<
                                        " dir=back arrowtail=\"odot\"";
                                }
                            }

                            *outf << "];" << std::endl;

                        }
                    }
                }

            }
        }
    }

    *(Output::debug) << "  - Gates printed." << std::endl;

    *outf << "" << std::endl;
    *outf << "  # Gate levels (ranks):" << std::endl;

    // print ranks
    for (int i = 0; i <= this->net->getNetDepth(); i++) {
        *outf << "  { rank=same; " + ranks[i] + " };" << std::endl;
    }

    *(Output::debug) << "  - Gate ranks printed." << std::endl;

    // foot
    *outf << "}" << std::endl;

    outf->close();
    Output::flush();
}

/**
 * Print boolean network to text file
 * 
 * @param color print gates denoted by selected color only
 * 
 */
void NetWriter::write2Dump(int color)
{
    *(Output::trace) << "NetWriter::write2Dump()" << std::endl;

    // open output file
    std::string filename = basename;
    filename.append(".txt", 4);
    std::ofstream * outf = new std::ofstream();
    outf->open(filename.c_str());

    vector < std::string > ranks(this->net->getNetDepth() + 1);

    // head
    *outf << "TSaCt2 dump file" << std::endl;
    *outf << "" << std::endl;
    *outf << "Circuit inputs:" << std::endl;
    // print inputs
    for (int i = 0; i < this->net->getIn(); i++) {
        if (this->net->getInput(i) != NULL) {
            if (this->net->getInput(i)->hasColor(color)) {
                *outf << "  - " << this->net->getInput(i)->
                    getName() << std::endl;
                *outf << "    * SCOAP: " << this->net->getInput(i)->
                    get0Controlability() << "/" << this->net->getInput(i)->
                    get1Controlability() << "/" << this->net->getInput(i)->
                    getObservability() << std::endl;
                *outf << "    * OUT TREE: " << this->net->getInput(i)->
                    getOutTreeSize() << std::endl;
            }
        }
    }

    *(Output::debug) << "  - Inputs printed." << std::endl;

    *outf << "" << std::endl;
    *outf << "Circuit outputs:" << std::endl;
    // print outputs
    for (int i = 0; i < this->net->getOut(); i++) {
        if (this->net->getOutput(i) != NULL) {
            if (this->net->getOutput(i)->hasColor(color)) {
                *outf << "  - " << this->net->getOutput(i)->
                    getName() << std::endl;
                *outf << "    * SCOAP: " << this->net->getOutput(i)->
                    get0Controlability() << "/" << this->net->
                    getOutput(i)->get1Controlability() << "/" << this->
                    net->getOutput(i)->getObservability() << std::endl;
                *outf << "    * IN TREE: " << this->net->getOutput(i)->
                    getInTreeSize() << std::endl;
            }
        }
    }

    *(Output::debug) << "  - Outputs printed." << std::endl;

    *outf << "" << std::endl;
    *outf << "Circuit gates:" << std::endl;

    // print gates
    for (int i = 0; i < this->net->getGates(); i++) {
        if (this->net->getGate(i) != NULL) {
            if (this->net->getGate(i)->hasColor(color)) {
                *outf << "  - " << this->net->getGate(i)->
                    getName() << std::endl;
                *outf << "    * SCOAP: " << this->net->getGate(i)->
                    get0Controlability() << "/" << this->net->getGate(i)->
                    get1Controlability() << "/" << this->net->getGate(i)->
                    getObservability() << std::endl;
                *outf << "    * OUT TREE: " << this->net->getGate(i)->
                    getOutTreeSize() << std::endl;
                *outf << "    * IN TREE: " << this->net->getGate(i)->
                    getInTreeSize() << std::endl;
            }
        }
    }

    *(Output::debug) << "  - Gates printed." << std::endl;

    *outf << "" << std::endl;

    outf->close();
    Output::flush();
}

/**
 * Print boolean network to blif file
 * 
 * @note just single-output gates are supported by the BLIF format
 *
 * @param color print gates denoted by selected color only (use 1 for all gates in the network)
 * 
 */
void NetWriter::write2Blif(int color)
{
    *(Output::trace) << "NetWriter::write2Blif()" << std::endl;

    // open output file
    std::string filename = basename;
    filename.append(".blif", 5);
    std::ofstream * outf = new std::ofstream();
    outf->open(filename.c_str());

    // print header  
    *outf << ".model " << basename << std::endl;
    *(Output::debug) << "  - Model name printed." << std::endl;

    // print inputs
    *outf << ".inputs";
    for (int i = 0; i < this->net->getIn(); i++) {
        if (this->net->getInput(i)->hasColor(color)) {
            if (this->net->getInput(i)->getFanIn() != 0) {
                //it is not primary input -- input INVERTER!
                continue;
            } else {
                *outf << " " << this->net->getInput(i)->getName();
            }
        }
    }

    *outf << std::endl;
    *(Output::debug) << "  - Inputs enumerated." << std::endl;

    // print outputs
    *outf << ".outputs";
    for (int i = 0; i < this->net->getOut(); i++) {
        if (this->net->getOutput(i)->hasColor(color)) {
            *outf << " " << this->net->getOutput(i)->getName();
        }
    }

    *outf << std::endl;
    *(Output::debug) << "  - Outputs enumerated." << std::endl;

    // print input inverters
    for (int i = 0; i < this->net->getIn(); i++) {
        if (this->net->getInput(i)->hasColor(color)) {
            if (this->net->getInput(i)->getFanIn() != 0) {
                *outf << ".names";

                for (int j = 0; j < this->net->getInput(i)->getFanIn();
                     j++) {
                    *outf << " " << this->net->getInput(i)->
                        getDriver(j)->getName();
                }
                *outf << " " << this->net->getInput(i)->getName();

                *outf << std::endl;
                *outf << "" <<
                    *(this->getBlifCover(this->net->getInput(i)));
                *outf << std::endl;
            } else {
                continue;
            }
        }
    }

    // print all gate models
    for (int i = 0; i < this->net->getGates(); i++) {
        if (this->net->getGate(i)->hasColor(color)) {
            *outf << ".names";

            for (int j = 0; j < this->net->getGate(i)->getFanIn(); j++) {
                *outf << " " << this->net->getGate(i)->
                    getDriver(j)->getName();
            }
            *outf << " " << this->net->getGate(i)->getName();

            *outf << std::endl;
            *outf << "" << *(this->getBlifCover(this->net->getGate(i)));
            *outf << std::endl;
        }
    }

    // print all gate outputs
    for (int i = 0; i < this->net->getOut(); i++) {
        if (this->net->getOutput(i)->hasColor(color)) {
            *outf << ".names";

            for (int j = 0; j < this->net->getOutput(i)->getFanIn(); j++) {
                *outf << " " << this->net->getOutput(i)->
                    getDriver(j)->getName();
            }
            *outf << " " << this->net->getOutput(i)->getName();

            *outf << std::endl;
            *outf << "" << *(this->getBlifCover(this->net->getOutput(i)));
            *outf << std::endl;
        }
    }

    *(Output::debug) << "  - All gate models printed." << std::endl;

    *outf << ".end" << std::endl;
    outf->close();
    *(Output::debug) << "  - Writing file finished." << std::endl;

    Output::flush();
}

/**
 * Print boolean network to sim file fo IRSIM
 * 
 * SIM file format was defined by Berkeley and Standford. See @url{http://opencircuitdesign.com/irsim/}
 *
 * @note This function is able to write any two-input AND/OR and one-input NOT Gate to SIM
 * 
 * @param color print gates denoted by selected color only (use 1 for all gates in the network)
 * 
 */
void NetWriter::write2Sim(int color)
{
    *(Output::trace) << "NetWriter::write2Sim()" << std::endl;

    if (this->gateLibrary == NULL) {
        *(Output::error) <<
            "No gate library available; use \"-l\" to specify existing gate library!"
            << std::endl;
        return;
    }

    if (this->gateLibrary->loadModels(IRSIM) != true) {
        *(Output::
          error) << "Loading basic IRSIM models failed!" << std::endl;
        return;
    }
    // open output file
    std::string filename = basename;
    filename.append(".sim", 4);
    std::ofstream * outf = new std::ofstream();
    outf->open(filename.c_str());

    // print header  
    *outf << "|Name: " << basename << std::endl;
    *outf << "|units: 100 tech: scmos " << std::endl;
    *outf << "|  " << std::endl;

    //print inputs
    *outf << "|vector in_0 INPUT_0:" << (this->net->getIn() / 2 -
                                         1) << std::endl;
    *outf << "|vector in_1 D_INPUT_0:" << (this->net->getIn() / 2 -
                                           1) << std::endl;
    *outf << "|vector in INPUT_0:" << (this->net->getIn() -
                                       1) << std::endl;
    // print outputs
    *outf << "|vector out_0 OUT_0:" << (this->net->getOut() / 2 -
                                        1) << std::endl;
    *outf << "|vector out_1 D_OUT_0:" << (this->net->getOut() / 2 -
                                          1) << std::endl;
    *outf << "|vector out OUT_0:" << (this->net->getOut() -
                                      1) << std::endl;

    *outf << "|  " << std::endl;
    *outf << "|type gate source drain length width  " << std::endl;
    *outf << "|---- ---- ------ ----- ------ -----  " << std::
        endl << std::endl;

    *(Output::debug) << "  - Head printed." << std::endl;

    // print all gate models
    for (int i = 0; i < this->net->getGates(); i++) {
        if (this->net->getGate(i)->hasColor(color)) {
            *outf << std::endl;
            *outf << "" <<
                *(this->getFromLibrary(this->net->getGate(i), IRSIM));
            *outf << std::endl;
        }
    }

    // print all gate outputs
    for (int i = 0; i < this->net->getOut(); i++) {
        if (this->net->getOutput(i)->hasColor(color)) {
            *outf << "| output " << i;

            *outf << std::endl;
            *outf << "" << *(this->getFromLibrary(this->net->getOutput(i),
                                                  IRSIM));
            *outf << std::endl;
        }
    }

    *(Output::debug) << "  - All gate models printed." << std::endl;

    *outf << "| EOF" << std::endl;
    outf->close();
    *(Output::debug) << "  - Writing file finished." << std::endl;

    Output::flush();
}

/**
 * Print boolean network to ngSPICE netlist
 * 
 * @param color print gates denoted by selected color only (use 1 for all gates in the network)
 * 
 */
void NetWriter::write2ngSpice(int color)
{
    *(Output::trace) << "NetWriter::write2ngSpice()" << std::endl;

    if (this->gateLibrary == NULL) {
        *(Output::error) <<
            "No gate library available; use \"-l\" to specify existing gate library!"
            << std::endl;
        return;
    }

    if (this->gateLibrary->loadModels(NGSPICE) != true) {
        *(Output::
          error) << "Loading basic NGSPICE models failed!" << std::endl;
        return;
    }
    // open output file
    std::string filename = basename;
    filename.append(".spice", 6);
    std::ofstream * outf = new std::ofstream();
    outf->open(filename.c_str());

    // print header  
    *outf << "* SPICE3 netlist of " << basename << " created by TSaCt2" <<
        std::endl;
    *(Output::debug) << "  - Model name printed." << std::endl;

    // print inputs
    *outf << "* " << std::endl;
    *outf << "* *** input inverters *** " << std::endl;
    *outf << "* " << std::endl;
    for (int i = 0; i < this->net->getIn(); i++) {
        if (this->net->getInput(i)->hasColor(color)) {
            if (this->net->getInput(i)->getFanIn() == 1) {
                // input inverter!
                *outf << "* BEGIN :: Input " << this->net->getInput(i)->
                    getName() << std::endl << std::endl;
                *outf << "" <<
                    *(this->getFromLibrary
                      (this->net->getInput(i), NGSPICE));
                *outf << "* END :: Input " << this->net->getInput(i)->
                    getName() << std::endl << std::endl;
            } else {
                // this is just a wire; do nothing!
                continue;
            }
        }
    }
    *outf << std::endl;
    *(Output::debug) << "  - Inputs printed." << std::endl;

    // print outputs
    *outf << "* " << std::endl;
    *outf << "* *** output inverters *** " << std::endl;
    *outf << "* " << std::endl;
    for (int i = 0; i < this->net->getOut(); i++) {
        if (this->net->getOutput(i)->hasColor(color)) {
            // output inverter!
            *outf << "* BEGIN :: Output " << this->net->getOutput(i)->
                getName() << std::endl << std::endl;
            *outf << "" <<
                *(this->getFromLibrary(this->net->getOutput(i), NGSPICE));
            *outf << "* END :: Output " << this->net->getOutput(i)->
                getName() << std::endl << std::endl;
        }
    }
    *outf << std::endl;
    *(Output::debug) << "  - Outputs printed." << std::endl;

    *outf << "* " << std::endl;
    *outf << "* *** gates ***" << std::endl;
    *outf << "* " << std::endl;
    // print all gate models
    for (int i = 0; i < this->net->getGates(); i++) {
        if (this->net->getGate(i)->hasColor(color)) {
            *outf << "* BEGIN :: Gate " << this->net->getGate(i)->
                getName() << std::endl << std::endl;
            *outf << "" <<
                *(this->getFromLibrary(this->net->getGate(i), NGSPICE));
            *outf << "* END :: Gate " << this->net->getGate(i)->
                getName() << std::endl << std::endl;
        }
    }

    *(Output::debug) << "  - All gates printed." << std::endl;

    *outf << ".end" << std::endl;
    outf->close();
    *(Output::debug) << "  - Writing file finished." << std::endl;

    Output::flush();
}

/**
 * Print boolean network to mapped BLIF file for QFLOW
 * 
 * See @url{http://opencircuitdesign.com/qflow/}
 *
 * @note This function is able to write any two-input AND/OR and one-input NOT
 * 
 * @param color print gates denoted by selected color only (use 1 for all gates in the network)
 * 
 */
void NetWriter::write2MapBlif(int color)
{
    *(Output::trace) << "NetWriter::write2MappedBlif()" << std::endl;

    if (this->gateLibrary == NULL) {
        *(Output::error) <<
            "No gate library available; use \"-l\" to specify existing gate library!"
            << std::endl;
        return;
    }

    if (this->gateLibrary->loadModels(BLIFMAP) != true) {
        *(Output::
          error) << "Loading basic BLIFMAP models failed!" << std::endl;
        return;
    }
    // open output file
    std::string filename = basename;
    filename.append(".blif", 5);
    std::ofstream * outf = new std::ofstream();
    outf->open(filename.c_str());

    // print header  
    *outf << ".model " << basename << std::endl;
    *(Output::debug) << "  - Model name printed." << std::endl;

    // print inputs
    *outf << ".inputs";
    for (int i = 0; i < this->net->getIn(); i++) {
        if (this->net->getInput(i)->hasColor(color)) {
            if (this->net->getInput(i)->getFanIn() != 0) {
                //it is not primary input -- input INVERTER!
                continue;
            } else {
                *outf << " " << this->net->getInput(i)->getName();

                // dual-rail
                if (this->net->getInput(i)->getComplement() != NULL) {
                    *outf << " " << this->net->
                        getInput(i)->getComplement()->getName();
                }
            }
        }
    }

    *outf << std::endl;
    *(Output::debug) << "  - Inputs enumerated." << std::endl;

    // print outputs
    *outf << ".outputs";
    for (int i = 0; i < this->net->getOut(); i++) {
        if (this->net->getOutput(i)->hasColor(color)) {
            if (this->net->getOutput(i)->isOutputInverting()) {
                *outf << " " << this->net->getOutput(i)->getName();
            } else {
                *outf << " " << this->net->getOutput(i)->getDriver(0)->
                    getName();
            }
        }
    }

    *outf << std::endl;

    *(Output::debug) << "  - Head printed." << std::endl;

    // print all gate models
    for (int i = 0; i < this->net->getGates(); i++) {
        if (this->net->getGate(i)->hasColor(color)) {
            *outf << std::endl;
            *outf << "" << *(this->getFromLibrary(this->net->getGate(i),
                                                  BLIFMAP));
            *outf << std::endl;
        }
    }

    // print all gate outputs
    for (int i = 0; i < this->net->getOut(); i++) {
        if (this->net->getOutput(i)->hasColor(color)) {
            *outf << "# output " << i;

            *outf << std::endl;
            *outf << "" << *(this->getFromLibrary(this->net->getOutput(i),
                                                  BLIFMAP));
            *outf << std::endl;
        }
    }

    *(Output::debug) << "  - All gate models printed." << std::endl;

    *outf << ".end" << std::endl;
    outf->close();
    *(Output::debug) << "  - Writing file finished." << std::endl;

    Output::flush();
}

/**
 * Return the TeX port name for gate
 * 
 * @param gate
 */
string *NetWriter::getTeXPortName(Gate * gate)
{
    switch (gate->getFunction()) {
    case AND:
        if (gate->isOutputInverting()) {
            return new string("nand port");
        } else {
            return new string("and port");
        }
    case OR:
        if (gate->isOutputInverting()) {
            return new string("nor port");
        } else {
            return new string("or port");
        }
    case XOR:
        if (gate->isOutputInverting()) {
            return new string("nxor port");
        } else {
            return new string("xor port");
        }
    default:
    case BUFFER:
        if (gate->isOutputInverting()) {
            return new string("not port");
        } else {
            return new string("buffer");
        }
    }
}

/**
 * Return Blif output cover
 * 
 * Return the output cover as defined for the BLIF format (\ref https://www.ece.cmu.edu/~ee760/760docs/blif.pdf)
 * 
 * @note This function suports AND, OR, BUFFER functions including in/out gate INVERTERS only!
 * 
 * @param gate
 */
string *NetWriter::getBlifCover(Gate * gate)
{
    string *cover = new string("");

    if (gate->getFunction() == AND) {
        for (int i = 0; i < gate->getFanIn(); i++) {
            if (gate->isInputInverting(i)) {
                cover->append("0", 1);
            } else {
                cover->append("1", 1);
            }
        }
        if (gate->isOutputInverting()) {
            cover->append(" O", 2);
        } else {
            cover->append(" 1", 2);
        }
    } else if (gate->getFunction() == OR) {
        for (int i = 0; i < gate->getFanIn(); i++) {
            if (gate->isInputInverting(i)) {
                cover->append("1", 1);
            } else {
                cover->append("0", 1);
            }
        }
        if (gate->isOutputInverting()) {
            cover->append(" 1", 2);
        } else {
            cover->append(" 0", 2);
        }
    } else if (gate->getFunction() == BUFFER) {
        for (int i = 0; i < gate->getFanIn(); i++) {
            if (gate->isInputInverting(i)) {
                cover->append("0", 1);
            } else {
                cover->append("1", 1);
            }
        }
        if (gate->isOutputInverting()) {
            cover->append(" 0", 2);
        } else {
            cover->append(" 1", 2);
        }
    } else {
        // unsupported funtion
        cover->append("ERROR", 5);
    }

    return cover;
}

string NetWriter::findAndReplace(string * s, string toReplace,
                                 string replaceWith)
{
    return (s->replace
            (s->find(toReplace), toReplace.length(), replaceWith));
}

string NetWriter::findAndReplaceAll(string * s, string toReplace,
                                    string replaceWith)
{
    while (s->find(toReplace) != string::npos) {
        findAndReplace(s, toReplace, replaceWith);
    }
    return *s;
}


/**
 * Return cell definition for defined gate
 * 
 * @note This function is able to write any two-input NAND/NOR and one-input NOT Gate to SIM
 * 
 * @param gate
 * @param cellType Type of cells (e.g. IRSIM, BLIF, ...)
 *
 * @retval gate representation in the given format 
 */
string *NetWriter::getFromLibrary_negative(Gate * gate,
                                           libraryFormats_t cellType)
{
    *(Output::trace) << "NetWriter::getFromLibrary_negative()" << std::
        endl;

    string *descr = new string("");

    if (gate->getFanIn() > 2) {
        *(Output::
          error) << "Two-input gates only supported! Convert NET first!" <<
    std::endl;
        exit(1);
    }

    if ((this->gateLibrary->nand[cellType] == NULL)
        || (this->gateLibrary->nor[cellType] == NULL)
        || (this->gateLibrary->inv[cellType] == NULL)) {
        *(Output::
          error) << "NAND, NOR and INV cells not in the library!" << std::
    endl;
        exit(1);
    }

    if ((gate->getFunction() == AND) || (gate->getFunction() == OR)) {
        if (gate->getFunction() == AND) {
            descr->append(*(this->gateLibrary->nand[cellType]));
        } else {
            descr->append(*(this->gateLibrary->nor[cellType]));
        }

        this->findAndReplaceAll(descr, string("[NAME]"),
                                gate->getName() + "_I0");

        if (gate->isOutputInverting()) {
            this->findAndReplaceAll(descr, string("[IOUT_0]"),
                                    gate->getName());
        } else {
            this->findAndReplaceAll(descr, string("[IOUT_0]"),
                                    gate->getName() + "_I0_OUT");
        }

        if (gate->isInputInverting(0)) {
            this->findAndReplaceAll(descr, string("[IN_0]"),
                                    gate->getName() + "_I1_OUT");
        } else {
            this->findAndReplaceAll(descr, string("[IN_0]"),
                                    gate->getDriver(0)->getName());
        }

        if (gate->isInputInverting(1)) {
            this->findAndReplaceAll(descr, string("[IN_1]"),
                                    gate->getName() + "_I2_OUT");
        } else {
            this->findAndReplaceAll(descr, string("[IN_1]"),
                                    gate->getDriver(1)->getName());
        }

        if (gate->isOutputInverting() == false) {
            descr->append(*(this->gateLibrary->inv[cellType]));
            this->findAndReplaceAll(descr, string("[NAME]"),
                                    gate->getName() + "_I3");
            this->findAndReplaceAll(descr, string("[IN_0]"),
                                    gate->getName() + "_I0_OUT");
            this->findAndReplaceAll(descr, string("[IOUT_0]"),
                                    gate->getName());
        }

        if (gate->isInputInverting(0)) {
            descr->append(*(this->gateLibrary->inv[cellType]));
            this->findAndReplaceAll(descr, string("[NAME]"),
                                    gate->getName() + "_I1");
            this->findAndReplaceAll(descr, string("[IN_0]"),
                                    gate->getDriver(0)->getName());
            this->findAndReplaceAll(descr, string("[IOUT_0]"),
                                    gate->getName() + "_I1_OUT");
        }

        if (gate->isInputInverting(1)) {
            descr->append(*(this->gateLibrary->inv[cellType]));
            this->findAndReplaceAll(descr, string("[NAME]"),
                                    gate->getName() + "_I2");
            this->findAndReplaceAll(descr, string("[IN_0]"),
                                    gate->getDriver(1)->getName());
            this->findAndReplaceAll(descr, string("[IOUT_0]"),
                                    gate->getName() + "_I2_OUT");
        }
    } else {                    // (gate->getFunction() == BUFFER)
        if ((gate->isOutputInverting() && (!gate->isInputInverting(0))) || ((!gate->isOutputInverting()) && gate->isInputInverting(0))) {       // Inverter
            descr->append(*(this->gateLibrary->inv[cellType]));

            this->findAndReplaceAll(descr, string("[NAME]"),
                                    gate->getName());
            this->findAndReplaceAll(descr, string("[IN_0]"),
                                    gate->getDriver(0)->getName());
            this->findAndReplaceAll(descr, string("[IOUT_0]"),
                                    gate->getName());
        } else {                // buffer
            /*descr->append(*(this->gateLibrary->inv[cellType]));

               this->findAndReplaceAll(descr, string("[NAME]"),
               gate->getName() + "_I0");
               this->findAndReplaceAll(descr, string("[IN_0]"),
               gate->getDriver(0)->getName());
               this->findAndReplaceAll(descr, string("[IOUT_0]"),
               gate->getName() + "_I0_OUT");

               descr->append(*(this->gateLibrary->inv[cellType]));
               this->findAndReplaceAll(descr, string("[NAME]"),
               gate->getName() + "_I1");
               this->findAndReplaceAll(descr, string("[IN_0]"),
               gate->getName() + "_I0_OUT");
               this->findAndReplaceAll(descr, string("[IOUT_0]"),
               gate->getName()); */
        }
    }

    return descr;
}

/**
 * Return cell definition for defined gate
 * 
 * @note This function is able to write any two-input AND/OR and one-input NOT Gate to SIM
 * 
 * @param gate
 * @param cellType Type of cells (e.g. IRSIM, BLIF, ...)
 *
 * @retval gate representation in the given format 
 */
string *NetWriter::getFromLibrary_positive(Gate * gate,
                                           libraryFormats_t cellType)
{
    string *descr = new string("");

    *(Output::trace) << "NetWriter::getFromLibrary_positive()" << std::
        endl;

    if (gate->getFanIn() > 2) {
        *(Output::
          error) << "Two-input gates only supported! Convert NET first!" <<
    std::endl;
        exit(1);
    }

    if ((this->gateLibrary->aand[cellType] == NULL)
        || (this->gateLibrary->oor[cellType] == NULL)
        || (this->gateLibrary->inv[cellType] == NULL)) {
        *(Output::
          error) << "AND, OR and INV cells not in the library!" << std::
    endl;
        exit(1);
    }

    if ((gate->getFunction() == AND) || (gate->getFunction() == OR)) {
        if (gate->getFunction() == AND) {
            descr->append(*(this->gateLibrary->aand[cellType]));
        } else {
            descr->append(*(this->gateLibrary->oor[cellType]));
        }

        this->findAndReplaceAll(descr, string("[NAME]"),
                                gate->getName() + "_I0");

        if (gate->isOutputInverting() == false) {
            this->findAndReplaceAll(descr, string("[OUT_0]"),
                                    gate->getName());
        } else {
            this->findAndReplaceAll(descr, string("[OUT_0]"),
                                    gate->getName() + "_I0_OUT");
        }

        if (gate->isInputInverting(0)) {
            this->findAndReplaceAll(descr, string("[IN_0]"),
                                    gate->getName() + "_I1_OUT");
        } else {
            this->findAndReplaceAll(descr, string("[IN_0]"),
                                    gate->getDriver(0)->getName());
        }

        if (gate->isInputInverting(1)) {
            this->findAndReplaceAll(descr, string("[IN_1]"),
                                    gate->getName() + "_I2_OUT");
        } else {
            this->findAndReplaceAll(descr, string("[IN_1]"),
                                    gate->getDriver(1)->getName());
        }

        if (gate->isOutputInverting() == true) {
            descr->append(*(this->gateLibrary->inv[cellType]));
            this->findAndReplaceAll(descr, string("[NAME]"),
                                    gate->getName() + "_I3");
            this->findAndReplaceAll(descr, string("[IN_0]"),
                                    gate->getName() + "_I0_OUT");
            this->findAndReplaceAll(descr, string("[IOUT_0]"),
                                    gate->getName());
        }

        if (gate->isInputInverting(0)) {
            descr->append(*(this->gateLibrary->inv[cellType]));
            this->findAndReplaceAll(descr, string("[NAME]"),
                                    gate->getName() + "_I1");
            this->findAndReplaceAll(descr, string("[IN_0]"),
                                    gate->getDriver(0)->getName());
            this->findAndReplaceAll(descr, string("[IOUT_0]"),
                                    gate->getName() + "_I1_OUT");
        }

        if (gate->isInputInverting(1)) {
            descr->append(*(this->gateLibrary->inv[cellType]));
            this->findAndReplaceAll(descr, string("[NAME]"),
                                    gate->getName() + "_I2");
            this->findAndReplaceAll(descr, string("[IN_0]"),
                                    gate->getDriver(1)->getName());
            this->findAndReplaceAll(descr, string("[IOUT_0]"),
                                    gate->getName() + "_I2_OUT");
        }
    } else {                    // (gate->getFunction() == BUFFER)
        if ((gate->isOutputInverting() && (!gate->isInputInverting(0))) || ((!gate->isOutputInverting()) && gate->isInputInverting(0))) {       // Inverter
            descr->append(*(this->gateLibrary->inv[cellType]));

            this->findAndReplaceAll(descr, string("[NAME]"),
                                    gate->getName());
            this->findAndReplaceAll(descr, string("[IN_0]"),
                                    gate->getDriver(0)->getName());
            this->findAndReplaceAll(descr, string("[OUT_0]"),
                                    gate->getName());
        } else {
            /* It's just a wire ... */
        }
    }

    return descr;
}

/**
 * Return cell definition for defined gate
 * 
 * @note This function is able to write any two-input AND/NAND gate
 * 
 * @param gate
 * @param cellType Type of cells (e.g. IRSIM, BLIF, ...)
 *
 * @retval gate representation in the given format 
 */
string *NetWriter::getFromLibrary_complementary(Gate * gate,
                                                libraryFormats_t cellType)
{
    string *descr = new string("");

    Gate *complement = gate->getComplement();

    *(Output::
      trace) << "NetWriter::getFromLibrary_complementary()" << std::endl;

    if (complement == NULL) {
        *(Output::
          error) <<
    "Gate has no complement! Convert NET to dual-rail first!" << std::endl;
        exit(1);
    }

    if (gate->getFanIn() > 2) {
        *(Output::
          error) << "Two-input gates only supported! Convert NET first!" <<
    std::endl;
        exit(1);
    }

    if ((this->gateLibrary->cand[cellType] == NULL)
        || (this->gateLibrary->cor[cellType] == NULL)) {
        *(Output::
          error) << "cAND or cOR cells not in the library!" << std::endl;
        exit(1);
    }

    /* 2-logical-input AND and OR are only supported functions */
    if ((gate->getFunction() == AND) || (gate->getFunction() == OR)) {
        if (gate->getFunction() == AND) {
            descr->append(*(this->gateLibrary->cand[cellType]));
        } else {
            descr->append(*(this->gateLibrary->cor[cellType]));
        }

        this->findAndReplaceAll(descr, string("[NAME]"), gate->getName());

        if (gate->isOutputInverting()) {
            this->findAndReplaceAll(descr, string("[IOUT_0]"),
                                    gate->getName());
            this->findAndReplaceAll(descr, string("[OUT_0]"),
                                    complement->getName());
        } else {
            this->findAndReplaceAll(descr, string("[IOUT_0]"),
                                    complement->getName());
            this->findAndReplaceAll(descr, string("[OUT_0]"),
                                    gate->getName());
        }

        if (gate->isInputInverting(0)) {
            this->findAndReplaceAll(descr, string("[IN_0]"),
                                    complement->getDriver(0)->getName());
            this->findAndReplaceAll(descr, string("[IIN_0]"),
                                    gate->getDriver(0)->getName());
        } else {
            this->findAndReplaceAll(descr, string("[IN_0]"),
                                    gate->getDriver(0)->getName());
            this->findAndReplaceAll(descr, string("[IIN_0]"),
                                    complement->getDriver(0)->getName());
        }

        if (gate->isInputInverting(1)) {
            this->findAndReplaceAll(descr, string("[IN_1]"),
                                    complement->getDriver(1)->getName());
            this->findAndReplaceAll(descr, string("[IIN_1]"),
                                    gate->getDriver(1)->getName());
        } else {
            this->findAndReplaceAll(descr, string("[IN_1]"),
                                    gate->getDriver(1)->getName());
            this->findAndReplaceAll(descr, string("[IIN_1]"),
                                    complement->getDriver(1)->getName());
        }
    } else {                    // (gate->getFunction() == BUFFER)
        if (gate->isOutputInverting() == false) {
            *(Output::debug) << "Skip buffer: " << gate->
                getName() << std::endl;
        } else {
            *(Output::error) << "Buffer " << gate->
                getName() << " is an inverting gate!" << std::endl;
            exit(1);
        }
    }

    return descr;
}

/**
 * Return cell definition for defined gate
 * 
 * @note This function performs gate mapping depending on the map algorithm slection
 * 
 * @param gate
 * @param cellType Type of cells (e.g. IRSIM, BLIF, ...)
 *
 * @retval gate representation in the given format 
 */
string *NetWriter::getFromLibrary(Gate * gate, libraryFormats_t cellType)
{
    *(Output::trace) << "NetWriter::getFromLibrary()" << std::endl;

    if (this->mapAlg == MAP_NEGATIVE) {
        return this->getFromLibrary_negative(gate, cellType);
    } else if (this->mapAlg == MAP_POSITIVE) {
        return this->getFromLibrary_positive(gate, cellType);
    } else if (this->mapAlg == MAP_NATURAL) {
        if (gate->isOutputInverting()) {
            return this->getFromLibrary_negative(gate, cellType);
        } else {
            return this->getFromLibrary_positive(gate, cellType);
        }
    } else if (this->mapAlg == MAP_COMPLEMENTARY) {
        return this->getFromLibrary_complementary(gate, cellType);
    } else {
        /* This should newer happen - if this happens, set MAP_DEFAULT to any valid mapping alg. */
        *(Output::
          error) << "Unknown mapping algorithm - misconfiguration!" <<
    std::endl;
        exit(1);
    }
}

/**
 * Print circuit state based on the input vector simulation 
 * 
 * @note to get meaningful output, run net->simInVect() prior this function
 * 
 * @param color print gates denoted by selected color only (use 1 for all gates in the network)
 * 
 */
void NetWriter::writeHeatMap(int color)
{
    *(Output::trace) << "NetWriter::writeHeatMap()" << std::endl;
    std::vector < int >cnt(net->getNetDepth() + 1, 0);  // position counter for each depth

    // open output file
    std::string filename = basename;
    filename.append(".heat", 5);
    std::ofstream * outf = new std::ofstream();
    outf->open(filename.c_str());

    // head
    if (net->isPlaced() == true) {
        *outf << "gate name; x; y; gate state;" << std::endl;
    } else {
        *outf << "gate name; depth; cnt; gate state;" << std::endl;
    }

    // print gates
    for (int i = 0; i < this->net->getGates(); i++) {
        if (this->net->getGate(i) != NULL) {
            if (this->net->getGate(i)->hasColor(color)) {

                if (net->isPlaced() == true) {
                    *outf << this->net->getGate(i)->
                        getName() << "; " << this->net->getGate(i)->
                        getPlaceXCoord() << "; " << this->net->getGate(i)->
                        getPlaceYCoord() << "; ";
                } else {
                    *outf << this->net->getGate(i)->
                        getName() << "; " << this->net->getGate(i)->
                        getDepth() << "; " << cnt.at(this->net->
                                                     getGate(i)->
                                                     getDepth()) << "; ";

                    /* next gate in this depth printed */
                    (cnt.at(this->net->getGate(i)->getDepth()))++;
                }
                uint8_t state = 0;
                for (int j = 0; j < this->net->getGate(i)->getFanIn(); j++) {
                    if (this->net->getGate(i)->getDriver(j)->
                        getOutputValue()) {
                        state = state | (0x01 << j);
                    }
                }

                *outf << ((int) state) << "; " << std::endl;

            }
        }
    }
    *(Output::debug) << "  - Gates printed." << std::endl;



    outf->close();
    Output::flush();
}
