/**
* @file main.cpp
* @author Jan Bělohoubek
*
* @brief MAIN
*
*/

#include <stdio.h>
#include <cstring>
#include <iostream>
#include <cstdlib>
#include <libgen.h>
#include "gate.h"
#include "aagloader.h"
#include "booleannet.h"
#include "netwriter.h"
#include "library.h"
#include "output.h"

using namespace std;

string *circuit;
string *library = NULL;
char *cmd = NULL;
BooleanNet *net;
int color = 0;
char *tsact2_cmd = NULL;
mapAlgorithm_t mapAlg = MAP_DEFAULT;    /* if option -m is ommited, use MAP_DEFAULT */

// private function prototypes
void print_help(void);

// include command handling helper functions
#include "cmd_helper.c"

// include command handling functions
#include "cmd_exec.c"

// include command list
#include "cmd_list.c"

/**
 * Print TSaCt2 help
 * 
 */
void print_help(void)
{
    std::cout << "Usage: " << std::endl;
    std::cout << "\t" << string(tsact2_cmd)
        << " -s SOURCE_FILE {-v | -vv} [-l mylib] [-m {positive | negative | complementary}] [-c COMMANDS]" << std::endl;
    std::cout << std::endl;
    std::cout << "Params: " << std::endl;
    std::cout << "\t -s \tSOURCE_FILE \t aag source file name"
        << std::endl;
    std::
        cout << "\t -l \tLIBRARY_NAME \t cell library name (custom format)"
        << std::endl;
    std::cout << "\t -m \tMAP_ALGORITHM \t cell mapping algorithm" << std::
        endl;
    std::cout << "\t -v \t\t\t activate trace debugging" << std::endl;
    std::cout << "\t -vv \t\t\t activate detailed debugging" << std::endl;
    std::cout << "\t -h \t\t\t print HELP" << std::endl;
    std::
        cout <<
        "\t -c \tCOMMANDS \t the script to be executed (list of commands deliminated by \";\")"
        << std::endl;
    std::cout << std::endl;
    std::cout << "Commands: " << std::endl;
    for (int i = 0; i < CMD_LIST_CNT; i++) {
        std::cout << "\t " << cmd_list[i].name
            << " \t\t\t " << cmd_list[i].descr << std::endl;
    }
    std::cout << std::endl;
    std::cout << "By Jan Bělohoubek, 2015 - 2021" << std::endl;
    std::cout << "jan.belohoubek@fit.cvut.cz" << std::endl;
    std::cout << std::endl;
}

/**
 * main()
 * 
 */
int main(int argc, char *argv[])
{

    char *src = NULL;
    char *lib = NULL;
    char *map = NULL;

    bool debug = false;
    bool trace = false;

    // save tsact cmd + path
    tsact2_cmd = argv[0];

    for (int i = 1; i != (unsigned int) argc; i++) {
        if (strcmp(argv[i], "-s") == 0) {
            if ((i + 1) != argc) {
                src = argv[++i];
                circuit = new string(basename(src));
                circuit->erase(circuit->size() + 1 - sizeof(".aag"),
                               sizeof(".aag") - 1);
            } else {
                print_help();
                return 1;
            }
        } else if (strcmp(argv[i], "-l") == 0) {
            if ((i + 1) != argc) {
                lib = argv[++i];
                library = new string(basename(lib));
            } else {
                print_help();
                return 1;
            }
        } else if (strcmp(argv[i], "-m") == 0) {
            if ((i + 1) != argc) {
                map = argv[++i];
                if (strcmp(map, "default") == 0) {
                    mapAlg = MAP_DEFAULT;
                } else if (strcmp(map, "negative") == 0) {
                    mapAlg = MAP_NEGATIVE;
                } else if (strcmp(map, "positive") == 0) {
                    mapAlg = MAP_POSITIVE;
                } else if (strcmp(map, "natural") == 0) {
                    mapAlg = MAP_NATURAL;
                } else if (strcmp(map, "complementary") == 0) {
                    mapAlg = MAP_COMPLEMENTARY;
                }
            } else {
                print_help();
                return 1;
            }
        } else if (strcmp(argv[i], "-v") == 0) {
            trace = true;
        } else if (strcmp(argv[i], "-vv") == 0) {
            trace = true;
            debug = true;
        } else if (strcmp(argv[i], "-c") == 0) {
            if ((i + 1) != argc) {
                cmd = argv[++i];
            } else {
                print_help();
                return 1;
            }
        }
    }

    if ((src == NULL)) {
        print_help();
        return 1;
    }

    if ((cmd == NULL)) {
        print_help();
        return 1;
    }

    Output();
    Output::create(debug, trace);

    AagLoader *loader = new AagLoader(src, &net);

    if (loader->isFileLoaded() == false) {
        *(Output::
          debug) << "File was not loaded successfully." << std::endl;
        return 1;
    }
    // compute important net characteristics
    net->computeNetDepth();

    // Process commands
    bool command_found;
    while (true) {
        command_found = false;

        size_t cmdlen = strcspn(cmd, "; ");

        *(Output::
          debug) << "CMD :: line = " << cmd << " :: length = " << cmdlen <<
    std::endl;

        for (int i = 0; i < CMD_LIST_CNT; i++) {
            if ((abs
                 (strncmp(cmd, cmd_list[i].name, strlen(cmd_list[i].name)))
                 == 0) && (strlen(cmd_list[i].name) == cmdlen)) {
                command_found = true;
                (cmd_list[i]).cmd();
                getNextCMD(&cmd);
                break;
            }
        }

        if (command_found == false) {
            // commands processed
            break;
        }
    }

    Output::close();
    return 0;
}
