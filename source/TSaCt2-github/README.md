# TSaCt2

  The TSaCt2 tool is a simple framework for combinational circuit netlist manipulations. It was created during my Ph.D. time to support my experimental work. 
  
  The tool currently allows processing combinational circuits in the [AIG (And-Inverter Graph) format](http://fmv.jku.at/aiger/FORMAT-20070427.pdf) only. It can perform simple circuit analysis, such as computing [SCOAP](https://ieeexplore.ieee.org/abstract/document/1084687) score, circuit visualization, AIG-to-XXX format conversion, and very basic technology mapping using a simple template-based gate [library](mylib). The tool natively supports the dual-rail circuit representation (complementary gates) and conversion to two distinct dual-rail representations.
  
  The tool is written in the C-coders' C++ :-) and works with a straight-forward circuit representation: the circuit is represented as a graph composed of gates, where each node has several properties including logic function. Every *command* does a computation on a netlist or a simple netlist manipulation. 
  
  Be warned, that the command ordering *cares* - not any command combination makes sense, and not all commands are generic (e.g. *nand* command might be used only for the loaded AIG netlist collapsing, and it should NOT follow any other conversion).
  
  TSaCt2 can be used to convert the circuit AIG representation to several representations and formats for further processing or simulation. The circuit netlist for [ngSPICE](http://ngspice.sourceforge.net/) or [IRSIM](http://opencircuitdesign.com/irsim/) simulation may be dumped (no parasitics!). The most useful feature is the export to the (subset of) [BLIF](https://people.eecs.berkeley.edu/~alanmi/publications/other/blif.pdf) allowing to use TSaCt2 as a standard cell mapping tool e.g. for the [QFlow](http://opencircuitdesign.com/qflow/). TSaCt2 takes a circuit synthesized by [abc](https://github.com/berkeley-abc/abc), possibly converts it to single-rail or dual-rail, and maps it to the (simple) cell library -- see examples below. The aim behind this kind of straightforward conversions is to get distinct circuit representations for unbiased comparison.
  
  TSaCt2 is additionally able to dump the circuit into several formats for visual representation, namely LaTeX and DOT. Recently, the input vector simulation was added and now it is possible to visualize circuit static configuration to make an idea of how the input vector influences the circuit configuration (state) -- see examples below.
  
  At the beginning of my Ph.D. study time, I created a simple framework to support my early combinational circuit netlist experiments. I called the tool "Transformation, Synthesis and Comparison Tool". Even it does (almost) no synthesis :-) Later, the framework was completely rewritten due to the poor design, making it hard to extend. As a result, this TSaCt2 tool was created.
  
  **If you use the tool for your research, please include one of the papers mentioned in the acknowledgment into the list of references.**

## Features
  * works with combinational circuits only
  * accepts AAG sources -- the text representation of the AIGs (And-Inverter Graphs) used for circuit representation
  * export netlist to spice, irsim, BLIF, LaTeX, and DOT 
  * extensible and simple template-based library
  * dual-rail netlist conversion
  * basic technology mapping
  * circuit configuration visualization

## Build
```bash
make clean && make
make rmdoc && make doc
```

## Usage

```
Usage: 
        ./TSaCt2 -s SOURCE_FILE {-v | -vv} [-l mylib] [-m {positive | negative | complementary}] [-c "COMMANDS"]

Params: 
         -s     SOURCE_FILE      aag source file name
         -l     LIBRARY_NAME     cell library name
         -m     MAP_ALGORITHM    cell mapping algorithm
         -v                      activate trace debugging
         -vv                     activate detailed debugging
         -h                      print HELP
         -c     COMMANDS         the script to be executed (list of commands deliminated by ";")

Commands: 
         help                    print help
         stats                   print statistics
         tex                     print network to LaTeX format
         dot                     print network to Graphviz DOT format
         dump                    print network details to text file
         spice                   print network to ngSPICE netlist
         blif                    print network to BLIF format
         sim                     print network to SIM format (IRSIM)
         blifmap                 map to two-input gates and write to blif
         markIn          G       mark input tree (G is # of gates)
         markOut         G       mark output tree (G is # of gates)
         scoap                   compute network's SCOAP
         inOutTree               compute IN/OUT tree for all gates
         fanout                  compute network's average fan-out
         nand                    move inverters to AND-gate outputs
         buffByScoap     C       Insert buffers to Scoap MAXs (C is # of buffers)
         move                    move inverters to AND-gate outputs
         dual                    convert the single-rail circuit to its dual-rail version
         dualAlt                 convert the single-rail circuit to its dual-rail version with alternating spacer
         dualred          L      perform dual-rail reduction heuristic (L is a level of heuristic: 0 to minimize # of PIs; 1 to minimize # of gates)
         place2rect              place NET to rectangle
         simVect         VECT    simulate given vector VECT
         printSimOut             Print simulation output
         writeHeatMap            Write heatMap describing circuit state based on the simulated input

By Jan Bělohoubek, 2015 - 2021
jan.belohoubek@fit.cvut.cz
```

## Examples

### Dual-Rail Conversion and Technology Mapping

To get the conventional dual-rail implementation of the AES SBOX circuit, execute:

```bash
./TSaCt2 -s examples/sbox.aag -l mylib -m positive -c "dual;blifmap"
```

TSaCt2 loads the [sbox.aag](examples/sbox.aag) file containing the optimized AES SBOX circuit AIG representation. The *-l* option specifies the gate library path. The *-m* option is used to select the mapping algorithm. TSaCt2 supports mapping to *positive* gates (2-input AND and OR gates and inverters), *negative* gates (2-input NAND and NOR gates and inverters) or to *complementary* gates (dedicated dual-rail gates).

The command *dual* converts the circuit representation to the dual-rail representation (the circuit interface is changed!) and command *blifmap* maps the combinational circuit to 2-input AND and OR gates and the resulting circuit representation is written to *sbox.blif* file.

### Circuit Configuration Vizualization

To get the visualization (a movie) of all possible AES SBOX circuit configurations, execute:

```bash

mkdir -p img
mkdir -p csv

for i in $( seq 0 1 255 )
do
  inp=$( echo "obase=16; ${i}" | bc )
  TSaCt2 -s examples/sbox.aag -c "nand;simVect ${inp}; printSimOut;place2rect;writeHeatMap"
  gnuplot -c showHeatMapPlaced.gnuplot sbox.heat img/sbox_${i}.png
  mv sbox.heat csv/sbox_${i}.heat
done

ffmpeg -i img/sbox_%d.png sbox.mpeg
```

In each loop iteration, TSaCt2 loads the [sbox.aag](examples/sbox.aag) file containing the optimized AES SBOX circuit AIG representation. Command *nand* converts the network to the single-gate-type representation (two-input NANDs only); command *simVect* simulates the given input vector; command *printSimOut* dumpls the simmulation output; command *place2rect* computes position of each gate in the *optimal* rectangular area (no scale; pseudo-placament) and command *writeHeatMap* writes gate positions and configurations to a CSV file *sbox.heat*

The *showHeatMapPlaced.gnuplot* *gnuplot* script is used to generate a *nice* bitmap representation of the circuit configuration induced by the given input vector.

Finally, *ffmpeg* is used to join generated images to create a short [movie](examples/sbox.mpeg).

## Acknowledgement
The development of this tool has been incrementally supported by the grant GA16-05179S of the Czech Grant Agency, by CTU grants SGS14/105/OHK3/1T/18, SGS15/119/OHK3/1T/18, SGS16/121/OHK3/1T/18, SGS17/213/OHK3/3T/18 and the OP VVVMEYS funded project CZ.02.1.01/0.0/0.0/16019/0000765 “Research Center for Informatics”.

This tool was used for those papers (selected):

  * Bělohoubek, J.; Fišer, P.; Schmidt, J.: Error Masking Method Based On The Short-Duration Offline Test. In: Microprocessors and Microsystems (MICPRO), Elsevier, vol. 52, July 2017, pp. 236-250.
