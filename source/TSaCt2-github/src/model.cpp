/**
* @file model.cpp
* @author Jan Bělohoubek
*
* @brief Model implementation
*
*/

#include <stdio.h>
#include <iostream>
#include <string>
#include "model.h"

using namespace std;

/**
 * Model constructor
 * 
 * @param name model name (use logic function names, such as AND, OR, XOR, ...)
 * @param inputCapacity the capacity of one gate input
 * @param outputCurrent the minimal gate output current when the gate output is stable
 * @param internalDelay additional delay caused by internal capacity charging
 * @param prechargeDelay this is non-zero for precharge gates only. Time to precharge the gate internal capacity using the precharge transistor(s) (the output charging not included)
 * @param size gate size
 */
Model::Model(string name, float inputCapacity, float outputCurrent,
             float internalDelay, float prechargeDelay, float size)
{
    this->modelName = name;
    this->internalDelay = internalDelay;
    this->prechargeDelay = prechargeDelay;
    this->inputCapacity = inputCapacity;
    this->outputCurrent = outputCurrent;
    this->size = size;
}

/**
 * Return model name
 */
string Model::getName()
{
    return this->modelName;
}

/**
 * Return the capacity of one gate input
 */
float Model::getInputCapacity()
{
    return this->inputCapacity;
}

/**
 * Return the output current of the gate
 */
float Model::getOutputCurrent()
{
    return this->outputCurrent;
}

/**
 * Return the delay caused by input gate capacity charging by gate input transistors
 */
float Model::getInternalDelay()
{
    return this->internalDelay;
}

/**
 * Return the delay caused by input gate capacity charging by gate precharge transistors
 */
float Model::getPrechargeDelay()
{
    return this->prechargeDelay;
}

/**
 * Return gate size
 */
float Model::getSize()
{
    return this->size;
}
