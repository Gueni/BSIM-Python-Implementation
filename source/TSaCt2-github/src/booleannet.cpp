/**
* @file booleannet.cpp
* @author Jan Bělohoubek
*
* @brief BooleanNet implementation
*
*/

#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include <string>
#include <stack>
#include "booleannet.h"
#include "gate.h"
#include "output.h"
#include "model.h"
#include <bits/stdc++.h>        // for maxHeap
using namespace std;

char tmp_buff[20];              // temporary buffer

/**
 * BooleanNet constructor
 * 
 * Initializes gate and input objects.
 * 
 * @param in number of inputs
 * @param out number of outputs
 * @param gates number of gates
 * 
 */
BooleanNet::BooleanNet(unsigned int in, unsigned int out,
                       unsigned int gates)
{
    this->netDepth = 0;
    this->netSumScoap = 0;
    this->netAvgFanOut = 0;

    this->gates.resize(gates, NULL);
    this->inputs.resize(in, NULL);
    this->outputs.resize(out, NULL);
    this->buffers.resize(0, NULL);

    this->netPlaced = false;

    for (int i = 0; i < this->inputs.size(); i++) {
        sprintf(tmp_buff, "INPUT_%d", i);
        this->inputs.at(i) = new Gate(tmp_buff);
        this->inputs.at(i)->setFunction(BUFFER);
        this->inputs.at(i)->setPlacement(INPUT);
        this->inputs.at(i)->setDepth(0);
    }

    for (int i = 0; i < this->gates.size(); i++) {
        sprintf(tmp_buff, "GATE_%d", i);
        this->gates.at(i) = new Gate(tmp_buff);
        this->gates.at(i)->setPlacement(INNER);
    }

    for (int i = 0; i < this->outputs.size(); i++) {
        sprintf(tmp_buff, "OUT_%d", i);
        this->outputs.at(i) = new Gate(tmp_buff);
        this->outputs.at(i)->setFunction(BUFFER);
        this->outputs.at(i)->setPlacement(OUTPUT);
    }
}

/**
 * Return the gate
 * 
 * @param gateNr gate number in the array of gates. Return NULL if out of the range
 */
Gate *BooleanNet::getGate(unsigned int gateNr)
{
    if (gateNr < this->gates.size()) {
        return this->gates.at(gateNr);
    } else {
        return NULL;
    }
}

/**
 * Return the input
 * 
 * @param inpNr input number in the array of inputs. Return NULL if out of the range
 */
Gate *BooleanNet::getInput(unsigned int inpNr)
{
    if (inpNr < this->inputs.size()) {
        return this->inputs.at(inpNr);
    } else {
        return NULL;
    }
}

/**
 * Remove output
 * 
 */
void BooleanNet::remOutput(unsigned int outNr)
{
    if (outNr < this->outputs.size()) {
        this->outputs.erase(this->outputs.begin() + outNr);
    }
}

/**
 * Return the output gate
 * 
 * @param outNr output number in the array of output gates. Return NULL if out of the range
 */
Gate *BooleanNet::getOutput(unsigned int outNr)
{
    if (outNr < this->outputs.size()) {
        return this->outputs.at(outNr);
    } else {
        return NULL;
    }
}

/**
 * Get number of inputs
 */
unsigned int BooleanNet::getIn()
{
    return this->inputs.size();
}

/**
 * Get number of outputs
 */
unsigned int BooleanNet::getOut()
{
    return this->outputs.size();
}

/**
 * Get number of gates
 */
unsigned int BooleanNet::getGates()
{
    return this->gates.size();
}

/**
 * Get average gate FanOut in the boolean net
 */
float BooleanNet::getAvgFanOut()
{
    return this->netAvgFanOut;
}

/**
 * Compute average gate FanOut in the boolean net
 */
float BooleanNet::computeAvgFanOut()
{
    int sum = 0;
    int cnt = 0;

    for (int i = 0; i < this->gates.size(); i++) {
        if (this->gates.at(i) != NULL) {
            *(Output::debug) << "FANOUT GATE " << this->gates.
                at(i)->getName() << ":" << this->gates.
                at(i)->getFanOut() << std::endl;
            sum += this->gates.at(i)->getFanOut();
            cnt++;
        }
    }

    this->netAvgFanOut = ((float) sum) / cnt;

    return this->netAvgFanOut;
}

/**
 * Compute BooleanNet depth
 * 
 * The netDepth is computed. The default netDepth value is 0
 */
void BooleanNet::computeNetDepth()
{
    *(Output::trace) << "BooleanNet::computeNetDepth()" << std::endl;
    for (int i = 0; i < this->outputs.size(); i++) {
        if (this->outputs.at(i)->getDepth() > this->netDepth) {
            this->netDepth = this->outputs.at(i)->getDepth();
        }
    }
}

/**
 * Return BooleanNet depth
 * 
 */
int BooleanNet::getNetDepth()
{
    return this->netDepth;
}

/**
 * Change gate to its equivalent
 * 
 */
void BooleanNet::changeToEqGate(Gate * gate)
{
    switch (gate->getFunction()) {
    case AND:
        gate->setFunction(OR);
        break;
    case OR:
        gate->setFunction(AND);
        break;
    }

    if (gate->isOutputInverting()) {
        gate->setOutputNonInverting();
    } else {
        gate->setOutputInverting();
    }

    for (int j = 0; j < gate->getFanIn(); j++) {
        if (gate->isInputInverting(j)) {
            gate->setInputNonInverting(j);
        } else {
            gate->setInputInverting(j);
        }
    }
}


/**
 * Merge two equivalent gates inside the network
 * 
 * @note check equivalency in calling function
 * 
 * @param gate0 will be removed
 * @param gate1 will be the successor of gate0 and gate1
 */
void BooleanNet::mergeEqGates(Gate * gate0, Gate * gate1)
{
    for (int i = 0; i < gate0->getFanIn(); i++) {
        gate0->getDriver(i)->remFollow(gate0);
    }

    for (int i = 0; i < gate0->getFanOut(); i++) {
        gate1->newFollow(gate0->getFollow(i));
        gate0->getFollow(i)->swapDriver(gate0, gate1);
    }

    for (int i = 0; i < this->gates.size(); i++) {
        if (this->gates.at(i) == gate0) {
            this->gates.erase(this->gates.begin() + i);
            break;
        }
    }

    delete(gate0);
}

/**
 * Perform the selected dual-rail Reduction heuristic
 * 
 * @param heuristicLevel selected heuristic
 */
void BooleanNet::dualRailReduction(dualRailRed_t heuristicLevel)
{
    // minimize # of primary inputs
    if (heuristicLevel == 0) {
        for (int i = 0; i < this->getOut(); i++) {
            this->getOutput(i);
        }
    }
}

/**
 * Convert the single-rail circuit to its dual-rail version
 * 
 */
void BooleanNet::convDualRail()
{
    *(Output::trace) << "BooleanNet::convDualRail()" << std::endl;

    std::vector < Gate * >newGates;
    std::vector < Gate * >newOutputs;
    std::vector < Gate * >newInputs;


    // duplicate gates
    for (int i = 0; i < this->gates.size(); i++) {
        Gate *gate;
        gate = new Gate("D_" + this->gates.at(i)->getName());

        gate->setFunction(convdual_getComplementaryGateFn
                          (this->gates.at(i)->getFunction()));
        gate->setPlacement(this->gates.at(i)->getPlacement());

        gate->setComplement(this->gates.at(i));
        this->gates.at(i)->setComplement(gate);

        if (this->gates.at(i)->isOutputInverting()) {
            gate->setOutputInverting();
        }

        for (int j = 0; j < this->gates.at(i)->getFanIn(); j++) {
            gate->newInput(this->gates.at(i)->getDriver(j),
                           (!this->gates.at(i)->isInputInverting(j)));
            this->gates.at(i)->getDriver(j)->newFollow(gate);
        }

        // save gate to newGates vector
        newGates.push_back(gate);
    }

    for (int i = 0; i < newGates.size(); i++) {
        this->gates.push_back(newGates.at(i));
    }

    // duplicate inputs
    for (int i = 0; i < this->inputs.size(); i++) {
        Gate *in = new Gate("D_" + this->inputs.at(i)->getName());
        in->setFunction(BUFFER);
        in->setPlacement(INPUT);
        in->newInput(this->inputs.at(i), false);
        this->inputs.at(i)->newFollow(in);
        in->setOutputInverting();
        in->resetDepth();

        in->setComplement(this->inputs.at(i));
        this->inputs.at(i)->setComplement(in);

        newInputs.push_back(in);
    }

    for (int i = 0; i < newInputs.size(); i++) {
        this->inputs.push_back(newInputs.at(i));
    }

    // duplicate outputs
    for (int i = 0; i < this->outputs.size(); i++) {
        Gate *out;
        out = new Gate("D_" + this->outputs.at(i)->getName());

        out->setFunction(this->outputs.at(i)->getFunction());
        out->setPlacement(this->outputs.at(i)->getPlacement());

        out->setComplement(this->outputs.at(i));
        this->outputs.at(i)->setComplement(out);

        out->newInput(this->outputs.at(i)->getDriver(0)->getComplement(),
                      false);
        this->outputs.at(i)->getDriver(0)->getComplement()->newFollow(out);

        if (this->outputs.at(i)->isInputInverting(0)) {
            this->outputs.at(i)->setInputNonInverting(0);
            this->outputs.at(i)->swapDriver( /*old= */ this->outputs.
                                            at(i)->getDriver(0),        /*new= */
                                            this->outputs.
                                            at(i)->getComplement()->
                                            getDriver(0));
            this->outputs.at(i)->
                getComplement()->swapDriver( /*old= */ this->outputs.
                                            at(i)->
                                            getComplement()->getDriver(0),      /*new= */
                                            this->outputs.at(i)->
                                            getDriver(0)->getComplement());

            this->outputs.at(i)->getDriver(0)->remFollow(this->
                                                         outputs.at
                                                         (i)->getComplement
                                                         ());
            this->outputs.at(i)->getDriver(0)->newFollow(this->
                                                         outputs.at(i));

            this->outputs.at(i)->getComplement()->
                getDriver(0)->remFollow(this->outputs.at(i));
            this->outputs.at(i)->getComplement()->
                getDriver(0)->newFollow(this->outputs.at(i)->
                                        getComplement());
        }

        newOutputs.push_back(out);
    }

    for (int i = 0; i < newOutputs.size(); i++) {
        this->outputs.push_back(newOutputs.at(i));
    }

    // remove inverters
    for (int i = 0; i < this->gates.size(); i++) {
        // move inverters
        if (this->gates.at(i)->isOutputInverting()) {
            for (int j = 0; j < this->gates.at(i)->getFanOut(); j++) {
                for (int k = 0;
                     k < this->gates.at(i)->getFollow(j)->getFanIn();
                     k++) {
                    if (this->gates.at(i)->getFollow(j)->getDriver(k) ==
                        this->gates.at(i)) {
                        if (this->gates.at(i)->getFollow(j)->
                            isInputInverting(k)) {
                            this->gates.at(i)->getFollow(j)->
                                setInputNonInverting(k);
                        } else {
                            this->gates.at(i)->getFollow(j)->
                                setInputInverting(k);
                        }
                    }
                }
            }
        }
        this->gates.at(i)->setOutputNonInverting();
    }

    for (int i = 0; i < this->gates.size(); i++) {
        // change Inputs
        for (int j = 0; j < this->gates.at(i)->getFanIn(); j++) {
            if (this->gates.at(i)->isInputInverting(j)) {
                this->gates.at(i)->setInputNonInverting(j);
                this->gates.at(i)->getDriver(j)->remFollow(this->
                                                           gates.at(i));
                this->gates.at(i)->swapDriver( /*old= */ this->gates.
                                              at(i)->getDriver(j),
                                              /*new= */
                                              this->gates.
                                              at(i)->getDriver
                                              (j)->getComplement());
                this->gates.at(i)->getDriver(j)->newFollow(this->
                                                           gates.at(i));
            }
        }
    }

    for (int i = 0; i < this->outputs.size(); i++) {
        // change Inputs
        for (int j = 0; j < this->outputs.at(i)->getFanIn(); j++) {
            if (this->outputs.at(i)->isInputInverting(j)) {
                this->outputs.at(i)->setInputNonInverting(j);
                this->outputs.at(i)->getDriver(j)->remFollow(this->
                                                             outputs.at
                                                             (i));
                this->outputs.at(i)->swapDriver( /*old= */ this->outputs.
                                                at(i)->getDriver(j),
                                                /*new= */
                                                this->outputs.
                                                at(i)->getDriver
                                                (j)->getComplement());
                this->outputs.at(i)->getDriver(j)->newFollow(this->
                                                             outputs.at
                                                             (i));
            }
        }
    }
}

/**
 * Enable alternating enable alternating spacer
 * 
 * @note the circuit must be converted to dual-rail -- before calling this function, call convDualRail()
 * 
 */
void BooleanNet::enableAltSpacer()
{
    *(Output::trace) << "BooleanNet::enableAltSpacer()" << std::endl;

    std::vector < Gate * >newBalancers;

    // convert to negative gates
    for (int i = 0; i < this->gates.size(); i++) {
        this->gates.at(i)->setOutputInverting();
    }

    // insert inverter-based balancing
    for (int i = 0; i < (this->gates.size() + 1) / 2; i++) {
        int unbalanced = 0;
        for (int j = 0; j < this->gates.at(i)->getFanOut(); j++) {
            if ((this->gates.at(i)->getFollow(j)->getDepth() % 2) ==
                (this->gates.at(i)->getDepth() % 2)) {
                unbalanced++;
            }
        }

        if (unbalanced == 0) {
            // all good ... 
        } else {
            // insert inverters 
            Gate *inv0 =
                new Gate(this->gates.at(i)->getName() + "_BALANCE0");
            Gate *inv1 =
                new Gate(this->gates.at(i)->getName() + "_BALANCE1");

            inv0->setComplement(inv1);
            inv1->setComplement(inv0);
            inv0->setFunction(BUFFER);
            inv1->setFunction(BUFFER);
            inv0->setOutputInverting();
            inv1->setOutputInverting();
            inv0->setPlacement(INNER);
            inv1->setPlacement(INNER);

            inv0->newInput(this->gates.at(i), false);
            this->gates.at(i)->newFollow(inv0);
            inv1->newInput(this->gates.at(i)->getComplement(), false);
            this->gates.at(i)->getComplement()->newFollow(inv1);

            newBalancers.push_back(inv0);
            newBalancers.push_back(inv1);

            for (int j = 0; j < this->gates.at(i)->getFanOut(); j++) {
                if ((this->gates.at(i)->getFollow(j)->getDepth() % 2) ==
                    (this->gates.at(i)->getDepth() % 2)) {
                    this->gates.at(i)->getFollow(j)->swapDriver( /*old= */ this->gates.at(i),   /*new= */
                                                                inv1);
                    this->gates.at(i)->getComplement()->
                        getFollow(j)->swapDriver( /*old= */ this->gates.
                                                 at(i)->
                                                 getComplement(), /*new= */
                                                 inv0);

                    inv0->newFollow(this->gates.at(i)->
                                    getComplement()->getFollow(j));
                    inv1->newFollow(this->gates.at(i)->getFollow(j));

                    this->gates.at(i)->remFollow(this->gates.
                                                 at(i)->getFollow(j));
                    this->gates.at(i)->getComplement()->
                        remFollow(this->gates.at(i)->getComplement
                                  ()->getFollow(j));
                    j--;
                }
            }
        }
    }

    for (int i = 0; i < newBalancers.size(); i++) {
        this->gates.push_back(newBalancers.at(i));
    }
}

/**
 * Return complementary gate function
 * 
 * @param fn the original gate function
 */
gateFunction_t BooleanNet::convdual_getComplementaryGateFn(gateFunction_t
                                                           fn)
{
    switch (fn) {
    case AND:
        return OR;
    case OR:
        return AND;
    case BUFFER:
    default:
        return BUFFER;
    }
}

/**
 * Convert AAG to NAND-based net (incl. buffers)
 * 
 * @note for constatant-output gates can alter the logic function. Remove those gates first! (E.g. 2-input AND with both inputs connected to the same signal, while one is inverted and another one is not inverted produces constant 0, after convNAND(), this will produce constant 1)
 * 
 * @note this function is not generic! It should be executed on the loaded AAG only, running it after booleannet altering leads to errors!
 * 
 */
void BooleanNet::convNAND()
{

    int invertedFollowers;

    *(Output::trace) << "BooleanNet::convNAND()" << std::endl;

    for (int i = 0; i < this->gates.size(); i++) {
        invertedFollowers = 0;

        for (int j = 0; j < this->gates.at(i)->getFanOut(); j++) {
            for (int k = 0;
                 k < this->gates.at(i)->getFollow(j)->getFanIn(); k++) {
                if (this->gates.at(i)->getFollow(j)->getDriver(k) ==
                    this->gates.at(i)) {
                    if (this->gates.at(i)->
                        getFollow(j)->isInputInverting(k)) {
                        invertedFollowers++;
                        // break must be here to enable routing output to multiple inputs of the following gate - e.g. traditional NAND gate to INVerter conversion
                        break;
                    }
                }
            }
        }

        *(Output::
          debug) << "BooleanNet::convNAND() :: GATE" << i << " has " <<
    invertedFollowers << " inverted followers" << std::endl;

        // move inverter to gate output
        if (invertedFollowers == this->gates.at(i)->getFanOut()) {
            for (int j = 0; j < this->gates.at(i)->getFanOut(); j++) {
                for (int k = 0;
                     k < this->gates.at(i)->getFollow(j)->getFanIn();
                     k++) {
                    if (this->gates.at(i)->getFollow(j)->getDriver(k) ==
                        this->gates.at(i)) {
                        this->gates.at(i)->
                            getFollow(j)->setInputNonInverting(k);
                    }
                }
            }
            if (this->gates.at(i)->isOutputInverting()) {
                this->gates.at(i)->setOutputNonInverting();
            } else {
                // merge inverters to AND gate (if possible)
                if (this->gates.at(i)->getFunction() == BUFFER) {
                    if (this->gates.at(i)->getFanIn() == 1) {
                        this->gates.at(i)->getDriver(0)->
                            setOutputInverting();
                    }
                } else {
                    this->gates.at(i)->setOutputInverting();
                }
            }
        }
    }
}

/**
 * Place buffers to most "SCOAP-intensive" places
 * 
 * @param places number of places from the "top" of the list
 * 
 */
void BooleanNet::InsertBuffsByScoap(unsigned int places)
{
    *(Output::
      trace) << "BooleanNet::breakByScoap(" << places << ")" << std::endl;

    priority_queue < Gate *, vector < Gate * >,
        gateScoapComparator > maxHeap;
    std::vector < Gate * >newBuffers;


    for (int i = 0; i < this->gates.size(); i++) {
        // prevent buffer chain creation
        if (gates.at(i)->getFunction() == BUFFER) {
            *(Output::
              debug) << "BooleanNet::breakByScoap(" << places <<
        ") :: skipGate 1 ::" << gates.at(i)->getName() << std::endl;
            continue;
        }
        if (gates.at(i)->getFanOut() == 1) {
            if (gates.at(i)->getFollow(0) == NULL) {
                *(Output::
                  debug) << "BooleanNet::breakByScoap(" << places <<
            ") :: skipGate 2::" << gates.at(i)->getName() << std::endl;
                continue;
            } else {
                if (gates.at(i)->getFollow(0)->getFunction() == BUFFER) {
                    *(Output::
                      debug) << "BooleanNet::breakByScoap(" << places <<
                ") :: skipGate  3 ::" << gates.at(i)->
                getName() << std::endl;
                    continue;
                }
            }
        }
        *(Output::
          debug) << "BooleanNet::breakByScoap(" << places <<
    ") :: insertGate  3 ::" << gates.at(i)->getName() << std::endl;

        maxHeap.push(gates.at(i));
    }



    for (int i = 0; (i < maxHeap.size()) && (i < places); i++) {
        *(Output::
          debug) << "BooleanNet::breakByScoap(" << places << ") :: " <<
    maxHeap.top()->getName() << std::endl;

        // insert inverters 
        Gate *buff = new Gate(maxHeap.top()->getName() + "_SCOAPBUFF");

        buff->setFunction(BUFFER);
        buff->setOutputNonInverting();
        buff->setPlacement(INNER);

        for (int j = 0; j < maxHeap.top()->getFanOut(); j++) {
            buff->newFollow(maxHeap.top()->getFollow(j));

            maxHeap.top()->getFollow(j)->swapDriver( /*old= */ maxHeap.
                                                    top(), /*new= */ buff);
        }

        while (maxHeap.top()->getFanOut()) {
            maxHeap.top()->remFollow(maxHeap.top()->getFollow(0));
        }
        maxHeap.top()->newFollow(buff);
        buff->newInput(maxHeap.top(), false);

        newBuffers.push_back(buff);

        maxHeap.pop();
        i--;                    // as heap size decreases, decrement i
    }

    for (int i = 0; i < newBuffers.size(); i++) {
        this->gates.push_back(newBuffers.at(i));
        this->buffers.push_back(newBuffers.at(i));
    }

}


/**
 * Move inverters to gate inputs/outputs to separate monotonic circuit
 * 
 */
void BooleanNet::moveInverters()
{
    bool run = true;

    *(Output::trace) << "BooleanNet::moveInverters()" << std::endl;

    while (run == true) {
        run = false;

        bool run2 = true;
        while (run2 == true) {
            run2 = false;

            if (moveout_changeToEqGates()) {
                moveout_shiftInvertersToOutputs();
                move_changeToEqGates();
            }

            if (move_shiftInverters(false)) {
                run2 = true;
                run = true;
            }
            if (move_changeToEqGates()) {
                run2 = true;
                run = true;
            }
        }

        // solve one conflict
        if (move_shiftInverters(true)) {
            run = true;
        }
    }

    // finalize
    move_shiftInvertersToInputBuffers();
    move_shiftInvertersInOutputBuffers();
}

/**
 * Shift inverters inside the net closer to circuit inputs
 * 
 * @param solveConflict try to solve one conflict
 * 
 * @retval true if changes were performed, else return false
 */
bool BooleanNet::move_shiftInverters(bool solveConflict)
{
    bool retval = false;

    *(Output::trace) << "BooleanNet::move_shiftInverters()" << std::endl;

    for (int i = 0; i < this->gates.size(); i++) {
        int invertedFollowers = 0;      // how many followers has inverted input?
        int invertedFollowersOutputs = 0;       // how many of them are primary outputs?
        for (int j = 0; j < this->gates.at(i)->getFanOut(); j++) {
            for (int k = 0;
                 k < this->gates.at(i)->getFollow(j)->getFanIn(); k++) {
                if (this->gates.at(i)->getFollow(j)->getDriver(k) ==
                    this->gates.at(i)) {
                    //link to driver found
                    if (this->gates.at(i)->
                        getFollow(j)->isInputInverting(k)) {
                        invertedFollowers++;
                        if (this->gates.at(i)->
                            getFollow(j)->getPlacement() == OUTPUT) {
                            invertedFollowersOutputs++;
                        }
                    }
                    break;
                }
            }
        }

        if ((invertedFollowers == this->gates.at(i)->getFanOut())
            && (invertedFollowers != invertedFollowersOutputs)) {
            if (this->gates.at(i)->isOutputInverting()) {
                this->gates.at(i)->setOutputNonInverting();
            } else {
                this->gates.at(i)->setOutputInverting();
            }

            if (this->gates.at(i)->getComplement() != NULL) {
                mergeEqGates(this->gates.at(i)->getComplement(),
                             this->gates.at(i));
                this->gates.at(i)->setComplement(NULL);
            }

            for (int j = 0; j < this->gates.at(i)->getFanOut(); j++) {
                for (int k = 0;
                     k < this->gates.at(i)->getFollow(j)->getFanIn();
                     k++) {
                    if (this->gates.at(i)->getFollow(j)->getDriver(k) ==
                        this->gates.at(i)) {
                        //link to driver found
                        this->gates.at(i)->
                            getFollow(j)->setInputNonInverting(k);
                    }
                }
            }
            // inverter(s) moved
            retval = true;
        } else if ((invertedFollowers != this->gates.at(i)->getFanOut()) && (invertedFollowers != 0)) { // conflict
            if (solveConflict == true) {
                Gate *gate;
                if (this->gates.at(i)->getComplement() == NULL) {
                    //solve conflict -> dupicate gate
                    gate = new Gate("D_" + this->gates.at(i)->getName());
                    gate->setFunction(this->gates.at(i)->getFunction());
                    gate->setPlacement(this->gates.at(i)->getPlacement());
                    gate->setComplement(this->gates.at(i));
                    this->gates.at(i)->setComplement(gate);
                    gate->setOutputInverting();
                    // place new gate to gates
                    this->gates.push_back(gate);
                    //duplicate drivers
                    for (int j = 0; j < this->gates.at(i)->getFanIn(); j++) {
                        gate->newInput(this->gates.at(i)->getDriver(j),
                                       this->gates.
                                       at(i)->isInputInverting(j));
                        this->gates.at(i)->getDriver(j)->newFollow(gate);
                    }
                } else {
                    gate = this->gates.at(i)->getComplement();
                }
                // change followers
                for (int j = 0; j < this->gates.at(i)->getFanOut(); j++) {
                    for (int k = 0;
                         k < this->gates.at(i)->getFollow(j)->getFanIn();
                         k++) {
                        if (this->gates.at(i)->
                            getFollow(j)->getDriver(k) ==
                            this->gates.at(i)) {
                            //link to driver found - move inverted outputs from original to duplicate
                            if (this->gates.at(i)->
                                getFollow(j)->isInputInverting(k)) {
                                gate->newFollow(this->gates.
                                                at(i)->getFollow(j));
                                this->gates.at(i)->
                                    getFollow(j)->swapDriver( /*old= */
                                                             this->gates.
                                                             at(i),
                                                             /*new= */
                                                             gate);
                                this->gates.at(i)->
                                    getFollow(j)->setInputNonInverting(k);
                                this->gates.at(i)->remFollow(this->
                                                             gates.at
                                                             (i)->getFollow
                                                             (j));
                                j--;
                            }
                            break;
                        }
                    }
                }

                // conflict solved
                retval = true;
                break;          // solve one conflict only once!
            }
        }
    }

    return retval;
}

/**
 * Shift inverters in the first level to input buffers
 * 
 */
void BooleanNet::move_shiftInvertersToInputBuffers()
{

    *(Output::trace) << "BooleanNet::move_shiftInvertersToInputBuffers()"
        << std::endl;

    for (int i = 0; i < this->inputs.size(); i++) {
        int invertedFollowers = 0;      // how many followers has inverted input?
        for (int j = 0; j < this->inputs.at(i)->getFanOut(); j++) {
            for (int k = 0;
                 k < this->inputs.at(i)->getFollow(j)->getFanIn(); k++) {
                if (this->inputs.at(i)->getFollow(j)->getDriver(k) ==
                    this->inputs.at(i)) {
                    //link to driver found
                    if (this->inputs.at(i)->
                        getFollow(j)->isInputInverting(k)) {
                        invertedFollowers++;
                    }
                    break;
                }
            }
        }

        *(Output::debug) << "Input " << this->inputs.
            at(i)->getName() << " has " << invertedFollowers <<
            " inverted followers" << std::endl;
        *(Output::debug) << "Input " << this->inputs.
            at(i)->getName() << " has " << this->inputs.
            at(i)->getFanOut() << " fanOut" << std::endl;

        if (invertedFollowers == this->inputs.at(i)->getFanOut()) {
            if (this->inputs.at(i)->isOutputInverting()) {
                this->inputs.at(i)->setOutputNonInverting();
            } else {
                this->inputs.at(i)->setOutputInverting();
            }

            for (int j = 0; j < this->inputs.at(i)->getFanOut(); j++) {
                for (int k = 0;
                     k < this->inputs.at(i)->getFollow(j)->getFanIn();
                     k++) {
                    if (this->inputs.at(i)->getFollow(j)->getDriver(k) ==
                        this->inputs.at(i)) {
                        //link to driver found
                        this->inputs.at(i)->
                            getFollow(j)->setInputNonInverting(k);
                    }
                }
            }
        } else if (invertedFollowers != 0) {    // conflict -> dupicate gate
            Gate *gate;
            if (this->inputs.at(i)->getComplement() == NULL) {
                gate = new Gate("D_" + this->inputs.at(i)->getName());
                gate->setFunction(BUFFER);
                gate->setPlacement(INPUT);
                gate->newInput(this->inputs.at(i), false);
                this->inputs.at(i)->newFollow(gate);
                gate->setOutputInverting();
                gate->resetDepth();
                // place new gate to gates
                this->inputs.push_back(gate);
            } else {
                gate = this->inputs.at(i)->getComplement();
            }
            // change followers
            for (int j = 0; j < this->inputs.at(i)->getFanOut(); j++) {
                for (int k = 0;
                     k < this->inputs.at(i)->getFollow(j)->getFanIn();
                     k++) {
                    if (this->inputs.at(i)->getFollow(j)->getDriver(k) ==
                        this->inputs.at(i)) {
                        //link to driver found - move inverted outputs from original to duplicate
                        if (this->inputs.at(i)->
                            getFollow(j)->isInputInverting(k)) {
                            gate->newFollow(this->inputs.
                                            at(i)->getFollow(j));
                            this->inputs.at(i)->
                                getFollow(j)->swapDriver( /*old= */ this->
                                                         inputs.at(i),
                                                         /*new= */ gate);
                            this->inputs.at(i)->
                                getFollow(j)->setInputNonInverting(k);
                            this->inputs.at(i)->remFollow(this->
                                                          inputs.at
                                                          (i)->getFollow
                                                          (j));
                            j--;
                        }
                        break;
                    }
                }
            }
        }
    }
}

/**
 * Change gates to their equivalents to move inverters closer to primary inputs
 * 
 * @retval true if some gates were changed, else return false
 */
bool BooleanNet::move_changeToEqGates()
{
    bool retval = false;

    *(Output::trace) << "BooleanNet::move_changeToEqGates()" << std::endl;

    for (int i = 0; i < this->gates.size(); i++) {
        if (this->gates.at(i)->isOutputInverting()) {
            switch (this->gates.at(i)->getFunction()) {
            case AND:
                this->gates.at(i)->setFunction(OR);
                break;
            case OR:
                this->gates.at(i)->setFunction(AND);
                break;
            }
            this->gates.at(i)->setOutputNonInverting();
            for (int j = 0; j < this->gates.at(i)->getFanIn(); j++) {
                if (this->gates.at(i)->isInputInverting(j)) {
                    this->gates.at(i)->setInputNonInverting(j);
                } else {
                    this->gates.at(i)->setInputInverting(j);
                }
            }
            // changes performed
            retval = true;
        }
    }

    return retval;
}


/**
 * Shift inverters in output buffers from buffer input to buffer output
 * 
 */
void BooleanNet::move_shiftInvertersInOutputBuffers()
{

    *(Output::trace) << "BooleanNet::move_shiftInvertersInOutputBuffers()"
        << std::endl;

    for (int i = 0; i < this->outputs.size(); i++) {
        if (this->outputs.at(i)->isInputInverting(0)) {
            this->outputs.at(i)->setInputNonInverting(0);
            this->outputs.at(i)->setOutputInverting();
        }
    }
}

/**
 * Change gates to their equivalents to move inverters closer to primary outputs
 * 
 * @retval true if some gates were changed, else return false
 */
bool BooleanNet::moveout_changeToEqGates()
{
    bool retval = false;

    *(Output::
      trace) << "BooleanNet::moveout_changeToEqGates()" << std::endl;

    for (int i = 0; i < this->gates.size(); i++) {
        if (!(this->gates.at(i)->isOutputInverting())) {
            int cnt = 0;
            for (int j = 0; j < this->gates.at(i)->getFanIn(); j++) {
                if (this->gates.at(i)->isInputInverting(j)) {
                    cnt++;
                }
            }

            if (cnt == this->gates.at(i)->getFanIn()) {
                switch (this->gates.at(i)->getFunction()) {
                case AND:
                    this->gates.at(i)->setFunction(OR);
                    break;
                case OR:
                    this->gates.at(i)->setFunction(AND);
                    break;
                }
                this->gates.at(i)->setOutputInverting();
                for (int j = 0; j < this->gates.at(i)->getFanIn(); j++) {
                    this->gates.at(i)->setInputNonInverting(j);
                }
            }
            // changes performed
            retval = true;
        }
    }

    return retval;
}

/**
 * Shift inverters to primary outputs
 * 
 */
void BooleanNet::moveout_shiftInvertersToOutputs()
{
    bool repeat = true;

    *(Output::trace) << "BooleanNet::moveout_shiftInvertersToOutputs()" <<
        std::endl;

    while (repeat == true) {
        repeat = false;
        for (int i = 0; i < this->outputs.size(); i++) {
            if (moveout_detectTreeOfInverters(this->outputs.at(i), 0) ==
                true) {
                // convert tree -> move inverters
                *(Output::debug) <<
                    "Repeat moveout_moveInvertersInTreeOfInverters(" << i
                    << ")" << std::endl;
                moveout_moveInvertersInTreeOfInverters(this->
                                                       outputs.at(i));
                repeat = true;
            }
        }
    }
}

/**
 * Detect tree of inverters movable to output
 * 
 * @param gate search the tree under this gate
 * @param depth stop searching in this depth
 * 
 * @retval invFound true if inverter tree detected, else return false
 */
bool BooleanNet::moveout_detectTreeOfInverters(Gate * gate, int depth)
{

    *(Output::trace) << "BooleanNet::moveout_detectTreeOfInverters(" <<
        gate->getName() << ") " << std::endl;

    if ((gate->getDepth() < depth) || (gate->getPlacement() == INPUT)) {
        return false;
    }

    for (int i = 0; i < gate->getFanIn(); i++) {
        if ((gate->isInputInverting(i))) {
            //all good
        } else if ((gate->getDriver(i) != NULL)) {
            if ((gate->getDriver(i)->isOutputInverting())
                && (gate->getDriver(i)->getFanOut() == 1)) {
                //all good
            } else if (gate->getDriver(i)->getFanOut() > 1) {
                return false;
            } else
                if (moveout_detectTreeOfInverters
                    (gate->getDriver(i), depth) == true) {
                //all good
            } else {
                return false;
            }
        } else {
            return false;
        }
    }

    return true;
}

/**
 * Move inverters in the tree of inverters
 * 
 * Note: call only when moveout_detectTreeOfInverters() returned true !!!
 * 
 * @param gate search the tree under this gate
 * 
 */
void BooleanNet::moveout_moveInvertersInTreeOfInverters(Gate * gate)
{

    *(Output::trace) <<
        "BooleanNet::moveout_moveInvertersInTreeOfInverters(" << gate->
        getName() << ") " << std::endl;

    for (int i = 0; i < gate->getFanIn(); i++) {
        if ((gate->isInputInverting(i))) {
            //all good
        } else {
            if ((gate->getDriver(i)->isOutputInverting())
                && (gate->getDriver(i)->getFanOut() == 1)) {
                //all good
                gate->getDriver(i)->setOutputNonInverting();
                gate->setInputInverting(i);

                if (gate->getDriver(i)->getComplement() != NULL) {
                    mergeEqGates(gate->getDriver(i)->getComplement(),
                                 gate->getDriver(i));
                    gate->getDriver(i)->setComplement(NULL);
                }
            } else {
                //all good
                *(Output::
                  debug) << "  from: " << gate->getName() << "to: " <<
            gate->getDriver(0)->getName() << " " << gate->
            getDriver(0)->isOutputInverting() << " " << gate->
            getDriver(0)->getFanOut() << std::endl;
                moveout_moveInvertersInTreeOfInverters(gate->getDriver(i));
                *(Output::
                  debug) << "  Rturned in: " << gate->getName() << "from: "
            << gate->getDriver(i)->getName() << std::endl;
                i--;
            }
        }
    }

    changeToEqGate(gate);
}

/**
 * Return Sum SCOAP characterising number
 * 
 * @retval SCOAP characteristic
 * 
 */
unsigned int BooleanNet::getSumScoap()
{
    return this->netSumScoap;
}

/**
 * Compute and return SCOAP characterising number
 * 
 * @retval SCOAP characteristic
 * 
 */
unsigned int BooleanNet::computeSumScoap()
{
    this->netSumScoap = 0;

    for (int i = 0; i < this->inputs.size(); i++) {
        this->inputs.at(i)->setControlability(1, 1);
    }

    for (int i = 0; i < this->buffers.size(); i++) {
        this->buffers.at(i)->setControlability(1, 1);
    }

    for (int i = 0; i < this->outputs.size(); i++) {
        this->outputs.at(i)->setObservability(0);
    }

    for (int i = 0; i < this->buffers.size(); i++) {
        this->buffers.at(i)->setObservability(0);
    }

    for (int i = 0; i < this->gates.size(); i++) {
        *(Output::
          debug) << "GATE_" << i << " SCOAP: CC0 = " << this->gates.at(i)->
    get0Controlability() << "; CC1 = " << this->gates.at(i)->
    get1Controlability() << "; CO = " << this->gates.
    at(i)->getObservability() << std::endl;

        this->netSumScoap +=
            this->gates.at(i)->get0Controlability() +
            this->gates.at(i)->get1Controlability();
        this->netSumScoap += this->gates.at(i)->getObservability();
    }

    return this->netSumScoap;
}

/**
 * Compute In/Out tree sizes for all gates
 * 
 */
void BooleanNet::computeInOutTrees()
{
    *(Output::trace) << "BooleanNet::computeInOutTrees()" << std::endl;

    for (int i = 0; i < this->inputs.size(); i++) {
        this->inputs.at(i)->computeOutTreeSize();
    }

    for (int i = 0; i < this->outputs.size(); i++) {
        this->outputs.at(i)->computeInTreeSize();
    }
}

/**
 * Mark segment of boolean from the selected gate to primary inputs
 * 
 * @param gate start from this gate and continue to primary inputs
 * @param color use this color to color the net segment
 */
void BooleanNet::colorInTree(Gate * gate, int color)
{
    *(Output::trace) << "BooleanNet::colorInTree()" << std::endl;

    std::stack < Gate * >gates;
    gates.push(gate);

    while (gates.size() > 0) {
        Gate *tmp = gates.top();
        gates.pop();

        tmp->addColor(color);

        for (int i = 0; i < tmp->getFanIn(); i++) {
            gates.push(tmp->getDriver(i));
        }
    }
}


/**
 * Mark segment of boolean from the selected gate to primary outputs
 * 
 * @param gate start from this gate and continue to primary outputs
 * @param color use this color to color the net segment
 */
void BooleanNet::colorOutTree(Gate * gate, int color)
{
    *(Output::trace) << "BooleanNet::colorOutTree()" << std::endl;

    std::stack < Gate * >gates;
    gates.push(gate);

    while (gates.size() > 0) {
        Gate *tmp = gates.top();
        gates.pop();

        tmp->addColor(color);

        for (int i = 0; i < tmp->getFanOut(); i++) {
            gates.push(tmp->getFollow(i));
        }
    }
}

/**
 * Mark segment of boolean net composing the base of the dual-rail circuit (mark only one gate of the complementary pair)
 * 
 * @note all inputs and outputs are colored as well, as those nodes are required allways
 * 
 * @param color use this color to color the net segment
 */
void BooleanNet::colorBaseGates(int color)
{
    *(Output::trace) << "BooleanNet::colorBaseGates()" << std::endl;

    for (int i = 0; i < this->gates.size(); i++) {
        if (this->gates.at(i)->getComplement() == NULL) {
            this->gates.at(i)->addColor(color);
        } else {
            if (this->gates.at(i)->getComplement()->hasColor(color) ==
                false) {
                this->gates.at(i)->addColor(color);
            }
        }
    }

    for (int i = 0; i < this->getIn(); i++) {
        this->getInput(i)->addColor(color);
    }

    for (int i = 0; i < this->getOut(); i++) {
        this->getOutput(i)->addColor(color);
    }
}


/**
 * Simulate input vector
 * 
 * @param inVect input vector
 */
void BooleanNet::simInVect(int inVect)
{
    *(Output::trace) << "BooleanNet::simInVect()" << std::endl;

    std::queue < Gate * >gates;

    for (int i = 0; (i < this->inputs.size()) && (i < 32); i++) {
        this->inputs.at(i)->setOutputValue(inVect & (1 << i));
        for (int j = 0; j < this->inputs.at(i)->getFanOut(); j++) {
            gates.push(this->inputs.at(i)->getFollow(j));
        }
    }

    while (gates.size() > 0) {
        Gate *tmp = gates.front();
        gates.pop();

        tmp->computeOutputValue();

        for (int i = 0; i < tmp->getFanOut(); i++) {
            gates.push(tmp->getFollow(i));
        }
    }
}

/**
 * Print simulation output
 * 
 * @note to get meaningful output, run simInVect() prior this function
 * 
 */
void BooleanNet::printSimOut()
{
    *(Output::trace) << "BooleanNet::printSimOut()" << std::endl;

    printf("Output: 0b");
    for (int i = 0; i < this->outputs.size(); i++) {
        printf("%d", ((int) this->outputs.at(i)->getOutputValue()));
    }
    printf("\n");
}


/**
 * Is the Net placed?
 * 
 */
bool BooleanNet::isPlaced()
{
    return this->netPlaced;
}

/**
 * Place net to rectangle
 * 
 * This function performs a simple placement heuristic:
 *   The gate positions are determined according to their depth in the circuit
 * 
 */
void BooleanNet::place2Rect()
{
    int edge = sqrt(this->gates.size());
    std::queue < Gate * >gates;

    /* current position */
    int currX = 0;
    int currY = 0;

    *(Output::trace) << "BooleanNet::place2Rect()" << std::endl;

    for (int i = 0; i < this->inputs.size(); i++) {
        for (int j = 0; j < this->inputs.at(i)->getFanOut(); j++) {
            if (this->inputs.at(i)->getFollow(j)->getDepth() == 1) {
                gates.push(this->inputs.at(i)->getFollow(j));
            }
        }
    }

    while (gates.size() > 0) {
        Gate *tmp = gates.front();
        gates.pop();

        /* chack if gate was visited */
        if (tmp->isPlaced()) {
            continue;
        }

        tmp->placeGate(currX, currY);
        currX = ((currX + 1) % edge);
        if (currX == 0) {
            currY++;
        }

        for (int i = 0; i < tmp->getFanOut(); i++) {
            if ((tmp->getDepth() + 1) == tmp->getFollow(i)->getDepth()) {
                gates.push(tmp->getFollow(i));
            }
        }
    }

    this->netPlaced = true;
}
