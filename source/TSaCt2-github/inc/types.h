/**
* @file types.h
* @author Jan Bělohoubek
*
* @brief Data types
*
*/

#ifndef TYPES_H
#define TYPES_H

typedef unsigned char byte;

typedef enum colors_t {
    COLORS_EMPTY = 0,           //< 
    COLORS_INTREE = (1 << 0),   //< 
    COLORS_OUTTREE = (1 << 1),  //< 
    COLORS_DUALBASE = (1 << 2), //< Base part of the dual-rail circuit
} colors_t;

typedef enum gateFunction_t {
    BUFFER,                     //< Copy first input to output
    AND,                        //< logical AND of inputs to output
    OR,                         //< logical OR of inputs to output
    XOR                         //< logical XOR of inputs to output
} gateFunction_t;



typedef enum gatePlacement_t {
    INPUT,                      //< Net input
    INNER,                      //< Inner node
    OUTPUT                      //< Net Output
} gatePlacement_t;

typedef struct scoap_t {
    unsigned int cc0;           //< 0-controlability
    unsigned int cc1;           //< 1-controlability
    unsigned int co;            //< observability
} scoap_t;

typedef enum dualRailRed_t {
    MIN_INPUTS = 0,             //< Minimize primary inputs
    MIN_GATES = 1               //< Minimize # of gates
} dualRailRed_t;

typedef enum mapAlgorithm_t {
    MAP_DEFAULT = 0,            //< Default mapping - set to any value below !
    MAP_NEGATIVE = 0,           //< Preffer negative gates (NAND/NOR + NOT)
    MAP_POSITIVE = 1,           //< Preffer positive gates (AND/OR + NOT)
    MAP_NATURAL = 2,            //< Natural maping - map gates from the netlist to the closest gate in the defined library
    MAP_COMPLEMENTARY = 3,      //< Complementary maping - map gates from the netlist to the complementary/dual-rail gates from the defined library
} mapAlgorithm_t;

typedef enum libraryFormats_t {
    IRSIM = 0,                  //< IRSIM netlist .sim
    BLIF = 1,                   //< ordinary BLIF
    BLIFMAP = 2,                //< BLIF mapped logic .blif
    TEX = 3,                    //< LaTeX
    NGSPICE = 4,                //< ngSPICE
    LIBRARY_FORMATS_LAST        //< # of lib formats
} libraryFormats_t;

#endif
