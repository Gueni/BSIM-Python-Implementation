/**
* @file output.h
* @author Jan Bělohoubek
*
* @brief Output
*
*/

#include <iostream>
#include <fstream>

#ifndef OUTPUT_H
#define OUTPUT_H


#define DEBUG_SCREEN             1      //< If 1, print to stdout
#define DEBUG_LOG_FILENAME       "debug.txt"    //< If DEBUG_SCREEN == 0, print to this file

#define TRACE_SCREEN             1      //< If 1, print to stdout
#define TRACE_LOG_FILENAME       "trace.txt"    //< If TRACE_SCREEN == 0, print to this file

#define ERROR_SCREEN             1      //< If 1, print to stdout
#define ERROR_LOG_FILENAME       "error.txt"    //< If ERROR_SCREEN == 0, print to this file

#define STATS_SCREEN             0      //< If 1, print to stdout
#define STATS_LOG_FILENAME       "stats.txt"    //< If STATS_SCREEN == 0, print to this file

using namespace std;

/**
 * Output
 * This class manages program output streams
 * 
 */
class Output {
  public:
    Output();
    static void create(bool debug, bool trace);
    static void close();
    static void flush();

    static ofstream *debug;
    static ofstream *trace;
    static ofstream *error;
    static ofstream *stats;

    static string to_str(int val);

  private:
    static bool printDebug;
    static bool printTrace;
};

#endif                          /* OUTPUT_H */
