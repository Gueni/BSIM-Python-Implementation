/**
* @file model.h
* @author Jan Bělohoubek
*
* @brief Model
*
*/

#include <stdio.h>
#include <iostream>
#include <string>
#include <iostream>
#include <fstream>

#ifndef MODEL_H
#define MODEL_H

using namespace std;

/**
 * Gate model
 * This class defines the gate model
 * 
 */
class Model {
  private:
    string modelName;           //< The model name
    float internalDelay;        //< Internal gate delay
    float prechargeDelay;       //< Internal gate delay during precharge (for dualRail gates only)
    float inputCapacity;        //< Input capacity of one gate input given by transistor gate sizes
    float outputCurrent;        //< Output current given by the gate
    float size;                 //< Gate size

  public:
     Model(string name, float InputCapacity = 0.0, float outputCurrent =
           0.0, float internalDelay = 0.0, float prechargeDelay =
           0.0, float size = 0.0);
    string getName();
    float getInputCapacity();
    float getOutputCurrent();
    float getInternalDelay();
    float getPrechargeDelay();
    float getSize();

};

#endif                          /* MODEL_H */
