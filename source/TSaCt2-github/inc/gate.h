/**
* @file gate.h
* @author Jan Bělohoubek
*
* @brief Gate
*
*/

#include <stdio.h>
#include <iostream>
#include <string>
#include <vector>
#include "model.h"
#include "types.h"

#ifndef GATE_H
#define GATE_H

using namespace std;

/**
 * Generic gate class
 * 
 * It defines: logic function, position in the boolean network, etc.
 * 
 * 
 */
class Gate {
  public:

  private:
    void constructGate(string gateName);
     std::vector < Gate * >inputs;      //< Predecessing gates -- the number is given by fanIn
     std::vector < bool >inputInverters;        //< Is input inverting?

     std::vector < Gate * >followingGates;      //< Following gates -- the number is given by fanOut
    bool outputInverter;        //< has the gate an inverting output?

    /* placement algorithm */
    bool placed;
    int placeX;
    int placeY;

    /* for input vector simulation */
    bool outputValue;           //< simulated output

    Gate *complementaryGate;    //< Gate with complementary (inverted) output

    // !!! gate properties !!!
    gateFunction_t gateFunction;        //< Logical gate function
    gatePlacement_t gatePlacement;      //< Gate placement inside the Logic net
    string *gateName;           //< Human readable gate alias
    Model *gateModel;           //< Gate model (physical)
    int depth;                  //< Max distance of gate from a primary input
    float delay;                //< Max distance of gate from a primary input (this number somehow expresses the time)
    scoap_t scoapParams;        //< Scoap parameters

    unsigned int inTreeSize;    //< Number of gates "under" this gate
    unsigned int outTreeSize;   //< Number of gates "after" this gate

    int color;                  //< "Color" parameter for subset-based algorithms; color is a bit-flag-based variable

  public:
     Gate(string gateName);     // Gate constructor

    void setFunction(gateFunction_t fn);
    gateFunction_t getFunction();
    string getFunctionName();

    void setPlacement(gatePlacement_t pl);
    gatePlacement_t getPlacement();

    // gate properties
    void setName(string gateName);
    string getName();

    // depth + delay
    bool setDepth(unsigned int d);
    int getDepth();
    void resetDepth();

    // Gate followers
    int getFanOut();
    void newFollow(Gate * follow);
    void remFollow(Gate * follow);
    Gate *getFollow(unsigned int i);
    bool isOutputInverting();
    void setOutputInverting();
    void setOutputNonInverting();

    // Gate predecessors
    int getFanIn();
    void newInput(Gate * pred, bool isInverting);
    void remInput(Gate * pred);
    Gate *getDriver(unsigned int i);
    void swapDriver(Gate * oldDriver, Gate * newDriver);
    bool isInputInverting(unsigned int i);
    void setInputInverting(unsigned int i);
    void setInputNonInverting(unsigned int i);

    // Complementary gate functions
    Gate *getComplement();
    void setComplement(Gate * gate);

    // Gate model
    void assignModel(Model * model);
    Model *getModel();

    // SCOAP
    void setControlability(unsigned int cc0, unsigned int cc1);
    void setObservability(unsigned int co0);
    void computeControlability();
    void computeObservability();
    unsigned int get0Controlability();
    unsigned int get1Controlability();
    unsigned int getObservability();

    // in/out gate trees
    unsigned int computeInTreeSize();
    unsigned int getInTreeSize();
    unsigned int computeOutTreeSize();
    unsigned int getOutTreeSize();

    //coloring
    bool hasColor(int color);
    void addColor(int color);

    // placement
    void placeGate(int x, int y);
    bool isPlaced();
    int getPlaceXCoord();
    int getPlaceYCoord();

    // simulation
    bool getOutputValue(void);
    void setOutputValue(bool newValue);
    void computeOutputValue(void);
};


/**
 * To compare two gates by using scoap
 * 
 */
class gateScoapComparator {
  public:
    int operator() (Gate * g0, Gate * g1) {
        return (g0->getObservability() * g0->get0Controlability() *
                g0->get1Controlability()) >
            (g1->getObservability() * g1->get0Controlability() *
             g1->get1Controlability());
}};

#endif
