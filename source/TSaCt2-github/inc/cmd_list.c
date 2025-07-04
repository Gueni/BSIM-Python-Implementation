
#define CMD_LIST_CNT   (sizeof(cmd_list)/sizeof(cmd_list[0]))   //< # of commands in the list


/**
  * @brief Pointer to a void function returning void
  */
typedef void (*cmd_exec)(void);

/**
* @brief  cmd handler
*/
typedef struct cmd_handler_t {
    char *name;                 /*<! CMD name */
    char *descr;                /*<! CMD help */
    cmd_exec cmd;               /*<! CMD exec */
} cmd_handler_t;


/**
* @brief List of Commands
*/
cmd_handler_t cmd_list[] = {
    { ((char *) &("help")),
     ((char *) &("print help")),
     &print_help },

    { ((char *) &("stats")),
     ((char *) &("print statistics")),
     &print_stats },

    { ((char *) &("tex")),
     ((char *) &("print network to LaTeX format")),
     &print_tex },

    { ((char *) &("dot")),
     ((char *) &("print network to Graphviz DOT format")),
     &print_dot },

    { ((char *) &("dump")),
     ((char *) &("print network details to text file")),
     &print_dump },

    { ((char *) &("spice")),
     ((char *) &("print network to ngSPICE netlist")),
     &print_ngSpice },

    { ((char *) &("blif")),
     ((char *) &("print network to BLIF format")),
     &print_blif },

    { ((char *) &("sim")),
     ((char *) &("print network to SIM format (IRSIM)")),
     &print_sim },

    { ((char *) &("blifmap")),
     ((char *) &("map to two-input gates and write to blif")),
     &print_mappedBlif },

    { ((char *) &("markIn")),
     ((char *) &("G \t mark input tree (G is # of gates)")),
     &cmd_markIn },

    { ((char *) &("markOut")),
     ((char *) &("G \t mark output tree (G is # of gates)")),
     &cmd_markOut },

    { ((char *) &("scoap")),
     ((char *) &("compute network\'s SCOAP")),
     &cmd_scoap },

    { ((char *) &("inOutTree")),
     ((char *) &("compute IN/OUT tree for all gates")),
     &cmd_inOutTrees },

    { ((char *) &("fanout")),
     ((char *) &("compute network\'s average fan-out")),
     &cmd_fanout },

    { ((char *) &("nand")),
     ((char *) &("move inverters to AND-gate outputs")),
     &cmd_nand },


    { ((char *) &("buffByScoap")),
     ((char *) &("C \t Insert buffers to Scoap MAXs (C is # of buffers)")),
     &cmd_InsertBuffsByScoap },

    { ((char *) &("move")),
     ((char *) &("move inverters to AND-gate outputs")),
     &cmd_move },

    { ((char *) &("dual")),
     ((char *)
      &("convert the single-rail circuit to its dual-rail version")),
     &cmd_dual },

    { ((char *) &("dualAlt")),
     ((char *)
      &
      ("convert the single-rail circuit to its dual-rail version with alternating spacer")),
     &cmd_dualAlt },

    { ((char *) &("dualred")),
     ((char *)
      &
      (" L \t perform dual-rail reduction heuristic (L is a level of heuristic: 0 to minimize # of PIs; 1 to minimize # of gates)")),
     &cmd_dualred },

    { ((char *) &("place2rect")),
     ((char *) &("place NET to rectangle")),
     &cmd_place2net },

    { ((char *) &("simVect")),
     ((char *) &("VECT \t simulate given vector VECT")),
     &cmd_simVect },

    { ((char *) &("printSimOut")),
     ((char *) &("Print simmulation output")),
     &cmd_printSimOut },

    { ((char *) &("writeHeatMap")),
     ((char *)
      &
      ("Write heatMap describing circuit state based on the simulated input")),
     &cmd_writeHeatMap },
};
