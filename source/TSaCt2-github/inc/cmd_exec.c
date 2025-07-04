/**
 * Print NET statistics
 * 
 */
void print_stats(void)
{
    // print stats
    *(Output::stats) << "Net statistics:" << std::endl;
    *(Output::stats) << "INPUTS: " << net->getIn() << std::endl;
    *(Output::stats) << "OUTPUTS: " << net->getOut() << std::endl;
    *(Output::stats) << "GATES: " << net->getGates() << std::endl;
    *(Output::stats) << "AVG_FANOUT: " << net->getAvgFanOut() << std::endl;
    *(Output::stats) << "NET_DEPTH: " << net->getNetDepth() << std::endl;
    *(Output::stats) << "SCOAP: " << net->getSumScoap() << std::endl;

    *(Output::stats) << "" << std::endl;
}

/**
 * Print NET representation to a LaTeX file
 * 
 */
void print_tex(void)
{
    // write net to tex
    NetWriter *netWriter;
    netWriter =
        new NetWriter(((new string(""))->append(*circuit)), net, library,
                      mapAlg);
    netWriter->write2TeX(color);
    delete(netWriter);
}

/**
 * Print Graphviz representation to a DOT file
 * 
 */
void print_dot(void)
{
    // write net to DOT
    NetWriter *netWriter;
    netWriter =
        new NetWriter(((new string(""))->append(*circuit)), net, library,
                      mapAlg);
    netWriter->write2Dot(color);
    delete(netWriter);
}

/**
 * Print Network detail to text file
 * 
 */
void print_dump(void)
{
    NetWriter *netWriter;
    netWriter =
        new NetWriter(((new string(""))->append(*circuit)), net, library,
                      mapAlg);
    netWriter->write2Dump(color);
    delete(netWriter);
}

/**
 * Print NET representation to a SPICE3 netlist file
 * 
 */
void print_ngSpice(void)
{
    // write net to tex
    NetWriter *netWriter;
    netWriter =
        new NetWriter(((new string(""))->append(*circuit)), net, library,
                      mapAlg);
    netWriter->write2ngSpice(color);
    delete(netWriter);
}

/**
 * Print NET representation to a BLIF file
 * 
 */
void print_blif(void)
{
    // write net to Blif
    NetWriter *netWriter;
    netWriter =
        new NetWriter(((new string(""))->append(*circuit)), net, library,
                      mapAlg);
    netWriter->write2Blif(color);
    delete(netWriter);
}

/**
 * Print NET representation to a SIM file (for IRSIM)
 * 
 */
void print_sim(void)
{
    // write net to Sim
    NetWriter *netWriter;
    netWriter =
        new NetWriter(((new string(""))->append(*circuit)), net, library,
                      mapAlg);
    netWriter->write2Sim(color);
    delete(netWriter);
}

/**
 * Print mapped NET representation to a BLIF file
 * 
 */
void print_mappedBlif(void)
{
    // write net to Blif
    NetWriter *netWriter;
    netWriter =
        new NetWriter(((new string(""))->append(*circuit)), net,
                      library, mapAlg);
    if (mapAlg == MAP_COMPLEMENTARY) {
        color = COLORS_DUALBASE;
        net->colorBaseGates(color);
        netWriter->write2MapBlif(color);
    } else {
        netWriter->write2MapBlif(color);
    }
    delete(netWriter);
}

/**
 * Mark input tree to a gate
 * 
 */
void cmd_markIn(void)
{
    int markIn_gate;

    if (!getNextWord(&cmd)) {
        print_help();
        exit(1);
    }

    if (sscanf(cmd, "%d", &markIn_gate) == 1) {
        color = COLORS_INTREE;
        net->colorInTree(net->getGate(markIn_gate), COLORS_INTREE);
    } else {
        print_help();
        exit(1);
    }
}


/**
 * Insert buffers, where scoap is maximum
 * 
 */
void cmd_InsertBuffsByScoap(void)
{
    int count;

    if (!getNextWord(&cmd)) {
        print_help();
        exit(1);
    }

    if (sscanf(cmd, "%d", &count) == 1) {
        if (count > 0) {
            net->InsertBuffsByScoap(count);
            // recompute net depth as new gates were inserted
            net->computeNetDepth();
        }
    } else {
        print_help();
        exit(1);
    }
}

/**
 * Mark output tree to a gate
 * 
 */
void cmd_markOut(void)
{
    int markOut_gate;

    if (!getNextWord(&cmd)) {
        print_help();
        exit(1);
    }

    if (sscanf(cmd, "%d", &markOut_gate) == 1) {
        color = COLORS_OUTTREE;
        net->colorOutTree(net->getGate(markOut_gate), COLORS_OUTTREE);
    } else {
        print_help();
        exit(1);
    }
}

/**
 * Mark output tree to a gate
 * 
 */
void cmd_dualred(void)
{
    int dualred_L;

    if (!getNextWord(&cmd)) {
        print_help();
        exit(1);
    }
    if (sscanf(cmd, "%d", &dualred_L) == 1) {
        // TODO this is to be ported rom the previous version -> it is not working now !!!
        dualred_L = 0;          // TODO force zero here ...
        net->convDualRail();
        net->dualRailReduction((dualRailRed_t) dualred_L);
    } else {
        print_help();
        exit(1);
    }
}

/**
 * Compute NET SCOAP
 * 
 */
void cmd_scoap(void)
{
    net->computeSumScoap();
}

/**
 * Compute In/Out trees for all gates
 * 
 */
void cmd_inOutTrees()
{
    net->computeInOutTrees();
}

/**
 * Compute NET average fan-out
 * 
 */
void cmd_fanout(void)
{
    net->computeAvgFanOut();
}

/**
 * Move inverters to AND ouputs (if trivially possible)
 * 
 */
void cmd_nand(void)
{
    net->convNAND();
}

/**
 * Move inverters to circuit IN/OUTs
 * 
 */
void cmd_move(void)
{
    net->moveInverters();
}

/**
 * Convert to dualRail
 * 
 */
void cmd_dual(void)
{
    net->convDualRail();
}

/**
 * Convert to dualRail with alternating spacer
 * 
 */
void cmd_dualAlt(void)
{
    net->convDualRail();
    net->enableAltSpacer();
}

/**
 * Simulate vector
 * 
 * @note this function is currently able to proces up to 32 inputs
 * @note for dual-rail nets, only one of the comlementary pair is required
 * 
 */
void cmd_simVect(void)
{
    int vector;

    if (!getNextWord(&cmd)) {
        print_help();
        exit(1);
    }
    if (sscanf(cmd, "%X", &vector) == 1) {
        net->simInVect(vector);
    } else {
        print_help();
        exit(1);
    }
}

/**
 * Print simulation output
 * 
 */
void cmd_printSimOut(void)
{
    net->printSimOut();
}

/**
 * Place net to rectangle (simple heuristic for physical placement)
 * 
 */
void cmd_place2net(void)
{
    net->place2Rect();
}

/**
 * Print circuit state based on simulation
 * 
 */
void cmd_writeHeatMap(void)
{
    // write net to tex
    NetWriter *netWriter;
    netWriter =
        new NetWriter(((new string(""))->append(*circuit)), net, NULL,
                      mapAlg);
    netWriter->writeHeatMap(color);
    delete(netWriter);
}
