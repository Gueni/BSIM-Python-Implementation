/**
* @file gate.cpp
* @author Jan Bělohoubek
*
* @brief Gate implementation
*
*/

#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <string>
#include <vector>
#include "gate.h"
#include "output.h"
#include "model.h"

using namespace std;

/**
  * @brief Gate constructor
  * 
  */
Gate::Gate(string gateName)
{
    this->gateName = new std::string(gateName);
    this->depth = 0;            // all gates are initialized as inputs
    this->delay = 0;            // 
    this->gateFunction = BUFFER;        // buffer by default 
    this->gatePlacement = INNER;        // inner gate by default
    this->outputValue = false;  // 0 is invalid - just to have a fixed init value
    this->gateModel = NULL;     // no model
    this->complementaryGate = NULL;     // no complement

    *(Output::debug) << "Creating gate " << gateName << std::endl;

    this->inputs.resize(0, NULL);
    this->inputInverters.resize(0, NULL);
    this->followingGates.resize(0, NULL);
    this->outputInverter = false;       // gate is a non-inverting gate

    this->scoapParams.cc0 = __INT_MAX__;
    this->scoapParams.cc1 = __INT_MAX__;
    this->scoapParams.co = __INT_MAX__;

    this->color = COLORS_EMPTY;

    /* placement */
    this->placed = false;
    this->placeX = 0;
    this->placeY = 0;

}

/**
 * Get placed coordinate X
 * 
 * @retval true if gate is placed, else return false
 * 
 */
bool Gate::isPlaced()
{
    return this->placed;
}

/**
 * Get placed coordinate X
 * 
 * @retval x x-coordinate
 * 
 */
int Gate::getPlaceXCoord()
{
    if (this->placed) {
        return this->placeX;
    } else {
        return -1;
    }
}

/**
 * Get placed coordinate Y
 * 
 * @retval y y-coordinate
 * 
 */
int Gate::getPlaceYCoord()
{
    if (this->placed) {
        return this->placeY;
    } else {
        return -1;
    }
}

/**
 * Set the gate physical placement
 * 
 * @param x x-coordinate
 * @param y y-coordinate
 * 
 * 
 */
void Gate::placeGate(int x, int y)
{
    this->placed = true;
    this->placeX = x;
    this->placeY = y;
}

/**
 * Set the gate logical placement
 * 
 * @param pl gate location
 */
void Gate::setPlacement(gatePlacement_t pl)
{
    this->gatePlacement = pl;
}

/**
 * Get the gate logical placement
 * 
 */
gatePlacement_t Gate::getPlacement()
{
    return this->gatePlacement;
}

/**
 * Set the gate logical function
 * 
 * @param fn gate function; \ref gateFunction_t
 */
void Gate::setFunction(gateFunction_t fn)
{
    this->gateFunction = fn;
}

/**
 * Get the gate logical function
 * 
 */
gateFunction_t Gate::getFunction()
{
    return this->gateFunction;
}

/**
 * Set the gate readable name
 */
void Gate::setName(string gateName)
{
    this->gateName = new std::string(gateName);
}

/**
 * Get the gate readable name
 */
string Gate::getName()
{
    return *(this->gateName);
}

/**
 * Get the gate function name
 */
string Gate::getFunctionName()
{
    switch (this->getFunction()) {
    case AND:
        return "AND";
    case OR:
        return "OR";
    case XOR:
        return "XOR";
    default:
    case BUFFER:
        return "BUFF";
    }
}

/**
 * Get current gate output - for simulation
 * 
 * @retval gate current output (computed)
 * 
 */
bool Gate::getOutputValue(void)
{
    return this->outputValue;
}

/**
 * Force new gate output
 * 
 * @note this function is to be used for primary input pre-setting
 * @note this function may be used for fault injection 
 * 
 * @param newOutput new gate output value
 * 
 */
void Gate::setOutputValue(bool newOutput)
{
    this->outputValue = newOutput;
}

/**
 * Compute function output based on gate input vector
 * 
 */
void Gate::computeOutputValue(void)
{
    bool result;

    switch (this->getFunction()) {
    case AND:
        result = true;
        for (int i = 0; i < this->getFanIn(); i++) {
            result =
                result & (this->getDriver(i)->getOutputValue() ^ this->
                          isInputInverting(i));
        }
    case OR:
        result = false;
        for (int i = 0; i < this->getFanIn(); i++) {
            result =
                result | (this->getDriver(i)->getOutputValue() ^ this->
                          isInputInverting(i));
        }
    case XOR:
        result = false;
        for (int i = 0; i < this->getFanIn(); i++) {
            result =
                result ^ (this->getDriver(i)->getOutputValue() ^ this->
                          isInputInverting(i));
        }
    default:
    case BUFFER:
        result =
            result ^ (this->getDriver(0)->getOutputValue() ^ this->
                      isInputInverting(0));
    }

    if (this->isOutputInverting()) {
        this->outputValue = !result;
    } else {
        this->outputValue = result;
    }
}

/**
 * Set gate depth
 * Set gate depth to new depth if the new depth is greather than the actual depth 
 * (the maximum depth is preserved). Set depth recursively for all followeing gates.
 * 
 * @param d depth to set
 * 
 * @retval true if depth was updated, else return false
 */
bool Gate::setDepth(unsigned int d)
{
    if (this->depth < d) {
        this->depth = d;
    } else {
        return false;
    }

    for (int i = 0; i < followingGates.size(); i++) {
        followingGates.at(i)->setDepth(this->depth + 1);
    }
    return true;
}

/**
 * Set gate depth to 0
 * 
 */
void Gate::resetDepth()
{
    this->depth = 0;
}

/**
 * Get gate depth
 */
int Gate::getDepth()
{
    return this->depth;
}

/**net
 * Get gate fan-out
 */
int Gate::getFanOut()
{
    return this->followingGates.size();
}

/**
 * Set new following gate
 */
void Gate::newFollow(Gate * follow)
{
    if (follow == NULL) {
        return;
    }

    this->followingGates.insert(this->followingGates.begin(), follow);
}

/**
 * Remove following gate
 */
void Gate::remFollow(Gate * follow)
{
    if (follow == NULL) {
        return;
    }

    for (int i = 0; i < this->followingGates.size(); i++) {
        if (this->followingGates.at(i) == follow) {
            this->followingGates.erase(this->followingGates.begin() + i);
        }
    }
}

/**
 * Get following gate.
 * The gate is given by iterator i
 */
Gate *Gate::getFollow(unsigned int i)
{
    if (this->followingGates.size() <= i) {
        return NULL;
    }

    return this->followingGates.at(i);
}

/**
 * Set the inverting output for the gate
 * 
 */
void Gate::setOutputInverting()
{
    this->outputInverter = true;
}

/**
 * Set the non-inverting output for the gate
 * 
 */
void Gate::setOutputNonInverting()
{
    this->outputInverter = false;
}

/**
 * Has the gate inverting output
 * 
 * @retval true if output is inverting
 */
bool Gate::isOutputInverting()
{
    return outputInverter;
}

/**
 * Get gate fan-in
 */
int Gate::getFanIn()
{
    return this->inputs.size();
}

/**
 * Set new predecessing gate and input properties
 */
void Gate::newInput(Gate * pred, bool isInverting)
{
    if (pred == NULL) {
        return;
    }

    this->inputs.insert(this->inputs.begin(), pred);
    this->inputInverters.insert(this->inputInverters.begin(), isInverting);

    if (pred != NULL) {
        this->setDepth(pred->getDepth() + 1);
    }
}

/**
 * Remove predecessing gate
 */
void Gate::remInput(Gate * pred)
{
    if (pred == NULL) {
        return;
    }

    for (int i = 0; i < this->inputs.size(); i++) {
        if (this->inputs.at(i) == pred) {
            this->inputs.erase(this->inputs.begin() + i);
            this->inputInverters.erase(this->inputInverters.begin() + i);
        }
    }
}

/**
 * Get gate driving input
 *
 * @param i index of the input
 * 
 * @retval gate pointer tothe gate
 */
Gate *Gate::getDriver(unsigned int i)
{
    if (this->inputs.size() <= i) {
        return NULL;
    }

    return this->inputs.at(i);
}


/**
 * Replace old driver by a new driver
 *
 * @param oldDriver
 * @param newDriver
 * 
 */
void Gate::swapDriver(Gate * oldDriver, Gate * newDriver)
{
    for (int i = 0; i < this->inputs.size(); i++) {
        if (this->inputs.at(i) == oldDriver) {
            this->inputs.at(i) = newDriver;

            if (newDriver != NULL) {
                this->setDepth(newDriver->getDepth() + 1);
            }

            break;
        }
    }
}

/**
 * Is input inverting?
 *
 * @param i index of the input
 * 
 * @retval true if input is inverting
 */
bool Gate::isInputInverting(unsigned int i)
{
    if (this->inputInverters.size() <= i) {
        return false;
    }

    return this->inputInverters.at(i);
}

/**
 * Set input inverting
 *
 * @param i index of the input
 * 
 */
void Gate::setInputInverting(unsigned int i)
{
    if (this->inputInverters.size() > i) {
        this->inputInverters.at(i) = true;
    }
}

/**
 * Set input non-inverting
 *
 * @param i index of the input
 * 
 */
void Gate::setInputNonInverting(unsigned int i)
{
    if (this->inputInverters.size() > i) {
        this->inputInverters.at(i) = false;
    }
}


/**
 * Get complementary gate
 * 
 * @retval gate pointer if complementary gate exist, else NULL
 */
Gate *Gate::getComplement()
{
    return this->complementaryGate;
}

/**
 * Assign the gate model
 */
void Gate::setComplement(Gate * gate)
{
    this->complementaryGate = gate;
}


/**
 * Assign the gate model
 */
void Gate::assignModel(Model * model)
{
    this->gateModel = model;
}

/**
 * Get the current gate model
 */
Model *Gate::getModel()
{
    return this->gateModel;
}

/**
 * Set gate controlabilty
 */
void Gate::setControlability(unsigned int cc0, unsigned int cc1)
{
    this->scoapParams.cc0 = cc0;
    this->scoapParams.cc1 = cc1;

    for (int i = 0; i < this->getFanOut(); i++) {
        this->getFollow(i)->computeControlability();
    }
}

/**
 * Compute&get size of the input tree
 */
unsigned int Gate::computeInTreeSize()
{
    unsigned int inTreeSize = 0;

    for (int i = 0; i < this->getFanIn(); i++) {
        if (this->getDriver(i) != NULL) {
            inTreeSize += this->getDriver(i)->computeInTreeSize() + 1;
        } else {
            inTreeSize += 0;
        }
    }

    this->inTreeSize = inTreeSize;

    return inTreeSize;
}

/**
 * Get size of the input tree
 */
unsigned int Gate::getInTreeSize()
{
    return this->inTreeSize;
}

/**
 * Compute&get size of the output tree
 */
unsigned int Gate::computeOutTreeSize()
{
    unsigned int outTreeSize = 0;

    for (int i = 0; i < this->getFanOut(); i++) {
        if (this->getFollow(i) != NULL) {
            outTreeSize += this->getFollow(i)->computeOutTreeSize() + 1;
        } else {
            outTreeSize += 0;
        }
    }

    this->outTreeSize = outTreeSize;

    return outTreeSize;
}

/**
 * Get size of the output tree
 */
unsigned int Gate::getOutTreeSize()
{
    return this->outTreeSize;
}

/**
 * Compute gate controlabilty based on the gate drivers
 * 
 * @todo This is just for AND/OR gates (plus inverters)
 * 
 */
void Gate::computeControlability()
{
    unsigned int cc0;
    unsigned int cc1;

    *(Output::trace) << "computeControlability( " << this->
        getName() << ")" << std::endl;

    switch (this->getFunction()) {
    case AND:
        cc0 = __INT_MAX__;
        cc1 = 0;
        break;
    case OR:
        cc0 = 0;
        cc1 = __INT_MAX__;
        break;
    default:
    case BUFFER:
        cc0 = 0;
        cc1 = 0;
        break;
    }

    bool change = false;        // was controlability changed?

    for (int i = 0; i < this->getFanIn(); i++) {
        switch (this->getFunction()) {
        case AND:
            if (this->isInputInverting(i)) {
                if (this->getDriver(i)->get1Controlability() < cc0) {
                    cc0 = this->getDriver(i)->get1Controlability();
                }
                cc1 += this->getDriver(i)->get0Controlability();
            } else {
                if (this->getDriver(i)->get0Controlability() < cc0) {
                    cc0 = this->getDriver(i)->get0Controlability();
                }
                cc1 += this->getDriver(i)->get1Controlability();
            }
            break;
        case OR:
            if (this->isInputInverting(i)) {
                if (this->getDriver(i)->get0Controlability() < cc1) {
                    cc1 = this->getDriver(i)->get0Controlability();
                }
                cc0 += this->getDriver(i)->get1Controlability();
            } else {
                if (this->getDriver(i)->get1Controlability() < cc1) {
                    cc1 = this->getDriver(i)->get1Controlability();
                }
                cc0 += this->getDriver(i)->get0Controlability();
            }
            break;
        default:
        case BUFFER:
            if (this->isInputInverting(i)) {
                cc0 += this->getDriver(i)->get1Controlability();
                cc1 += this->getDriver(i)->get0Controlability();
            } else {
                cc0 += this->getDriver(i)->get0Controlability();
                cc1 += this->getDriver(i)->get1Controlability();
            }
            break;
        }

    }

    if (this->isOutputInverting()) {
        if (this->scoapParams.cc0 > cc1 + 1) {
            this->scoapParams.cc0 = cc1 + 1;
            change = true;
        }
        if (this->scoapParams.cc1 > cc0 + 1) {
            this->scoapParams.cc1 = cc0 + 1;
            change = true;
        }
    } else {
        if (this->scoapParams.cc0 > cc0 + 1) {
            this->scoapParams.cc0 = cc0 + 1;
            change = true;
        }
        if (this->scoapParams.cc1 > cc1 + 1) {
            this->scoapParams.cc1 = cc1 + 1;
            change = true;
        }
    }

    // propagate changes recursivelly
    // the recursion is limited by circuit depth and gate fanIn/Out,
    // which is low for common circuits
    if (change == true) {
        for (int i = 0; i < this->getFanOut(); i++) {
            this->getFollow(i)->computeControlability();
        }
    }
}

/**
 * Set gate observability
 * 
 */
void Gate::setObservability(unsigned int co)
{
    this->scoapParams.co = co;

    for (int i = 0; i < this->getFanIn(); i++) {
        this->getDriver(i)->computeObservability();
    }
}

/**
 * Compute gate output observability based on the gate followers
 * 
 * @todo This is just for AND/OR gates (plus inverters)
 * 
 */
void Gate::computeObservability()
{
    unsigned int coNext;
    unsigned int ccSum;
    bool change = false;        // was observability changed?

    for (int i = 0; i < this->getFanOut(); i++) {
        coNext = 0;
        ccSum = 0;

        switch (this->getFollow(i)->getFunction()) {
        case AND:
            for (int j = 0; j < this->getFollow(i)->getFanIn(); j++) {
                if (this->getFollow(i)->getDriver(j) == this) {
                    continue;
                } else {
                    if (this->getFollow(i)->isInputInverting(j)) {
                        ccSum +=
                            this->getFollow(i)->
                            getDriver(j)->get1Controlability();
                    } else {
                        ccSum +=
                            this->getFollow(i)->
                            getDriver(j)->get0Controlability();
                    }
                }
            }

            coNext = this->getFollow(i)->getObservability() + ccSum + 1;
            break;
        case OR:
            for (int j = 0; j < this->getFollow(i)->getFanIn(); j++) {
                if (this->getFollow(i)->getDriver(j) == this) {
                    continue;
                } else {
                    if (this->getFollow(i)->isInputInverting(j)) {
                        ccSum +=
                            this->getFollow(i)->
                            getDriver(j)->get0Controlability();
                    } else {
                        ccSum +=
                            this->getFollow(i)->
                            getDriver(j)->get1Controlability();
                    }
                }
            }

            coNext = this->getFollow(i)->getObservability() + ccSum + 1;
            break;

        default:
        case BUFFER:
            coNext = this->getFollow(i)->getObservability() + 1;
            break;
        }

        // resolve branches - see the SCOAP method
        if (coNext < this->scoapParams.co) {
            this->scoapParams.co = coNext;
            change = true;
        }

    }

    // propagate changes recursivelly
    // the recursion is limited by circuit depth and gate fanIn/Out,
    // which is low for common circuits
    if (change == true) {
        for (int i = 0; i < this->getFanIn(); i++) {
            this->getDriver(i)->computeObservability();
        }
    }
}

/**
 * Get gate 0-controlabilty
 */
unsigned int Gate::get0Controlability()
{
    return this->scoapParams.cc0;
}


/**
 * Get gate 1-controlabilty
 */
unsigned int Gate::get1Controlability()
{
    return this->scoapParams.cc1;
}

/**
 * Get gate observability
 */
unsigned int Gate::getObservability()
{
    return this->scoapParams.co;
}

/**
 * Is gate colored?
 * 
 * @param color one gate color or the product of multiple colors; if 0, return always true
 * 
 * @retval true if is colored by using the selected color(s), else return false
 * 
 */
bool Gate::hasColor(int color)
{
    if (color == 0) {
        return true;
    }

    if ((this->color & color) == 0) {
        return false;
    } else {
        return true;
    }
}


/**
 * Add gate color
 * 
 * @param color note the gate by using this color
 * 
 */
void Gate::addColor(int color)
{
    this->color |= color;
}
