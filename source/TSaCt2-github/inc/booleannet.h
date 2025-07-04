/**
* @file booleannet.h
* @author Jan Bělohoubek
*
* @brief BooleanNet
*
*/

#include <stdio.h>
#include <iostream>
#include <string>
#include <iostream>
#include <fstream>
#include <vector>
#include "gate.h"
#include "model.h"

#ifndef BOOLEANNET_H
#define BOOLEANNET_H

using namespace std;
typedef unsigned char byte;

/**
 * Boolean network class
 * 
 * This class defines a boolean network
 * 
 * @todo remove gates from vecotr, when merged
 * 
 */
class BooleanNet {
  private:
    std::vector < Gate * >gates;        //< array of net gates
    std::vector < Gate * >inputs;       //< array of net inputs
    std::vector < Gate * >outputs;      //< array of pointers to net outputs
    std::vector < Gate * >buffers;      //< array of buffers

    unsigned int netDepth;
    float netAvgFanOut;
    unsigned int netSumScoap;
    bool netPlaced;             //< net is placed or not


  public:
     BooleanNet(unsigned int in, unsigned int out, unsigned int gates);

    Gate *getGate(unsigned int gateNr);
    Gate *getInput(unsigned int inpNr);
    Gate *getOutput(unsigned int outNr);
    void remOutput(unsigned int outNr);

    unsigned int getGates();
    unsigned int getIn();
    unsigned int getOut();

    float computeAvgFanOut();
    float getAvgFanOut();

    void computeNetDepth();
    int getNetDepth();

    float computeNetDelay();

    unsigned int computeSumScoap();
    unsigned int getSumScoap();

    void computeInOutTrees();

    void colorInTree(Gate * gate, int color);
    void colorOutTree(Gate * gate, int color);
    void colorBaseGates(int color);

    void moveInverters();

    void convDualRail();

    void convNAND();

    void enableAltSpacer();

    void dualRailReduction(dualRailRed_t heuristicLevel);

    void InsertBuffsByScoap(unsigned int places);

    void simInVect(int inVect);
    void printSimOut();
    void printSimState();

    bool isPlaced();
    void place2Rect();

  private:
    void mergeEqGates(Gate * gate0, Gate * gate1);

    // net manipulations
    void changeToEqGate(Gate * gate);

    bool move_shiftInverters(bool solveConflict);
    bool move_changeToEqGates();
    void move_shiftInvertersToInputBuffers();
    void move_shiftInvertersInOutputBuffers();

    bool moveout_changeToEqGates();
    bool moveout_detectTreeOfInverters(Gate * gate, int depth);
    void moveout_moveInvertersInTreeOfInverters(Gate * gate);
    void moveout_shiftInvertersToOutputs();

    gateFunction_t convdual_getComplementaryGateFn(gateFunction_t fn);
};

#endif                          /* BOOLEANNET_H */
