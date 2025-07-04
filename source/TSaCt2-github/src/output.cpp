/**
* @file output.cpp
* @author Jan Bělohoubek
*
* @brief Output implementation
*
*/

#include <iostream>
#include <fstream>
#include <sstream>
#include "output.h"

using namespace std;

ofstream *Output::debug;        //< Debug output stream
ofstream *Output::trace;        //< Trace debug output stream
ofstream *Output::error;        //< Error output stream
ofstream *Output::stats;        //< Statistics output stream

bool Output::printDebug;        //< Print debug information?
bool Output::printTrace;        //< Print trace information?

Output::Output()
{
}

/**
 * Initialize output streams
 */
void Output::create(bool debug, bool trace)
{
    Output::printDebug = debug;
    if (Output::printDebug == false) {
        Output::debug = new std::ofstream();
        Output::debug->open("/dev/null");
    } else {
#if (DEBUG_SCREEN == 1)
        Output::debug = (ofstream *) & cout;
#else
        Output::debug = new std::ofstream();
        Output::debug->open(DEBUG_LOG_FILENAME);
#endif
    }

    Output::printTrace = trace;
    if (Output::printTrace == false) {
        Output::trace = new std::ofstream();
        Output::trace->open("/dev/null");
    } else {
#if (TRACE_SCREEN == 1)
        Output::trace = (ofstream *) & cout;
#else
        Output::trace = new std::ofstream();
        Output::trace->open(TRACE_LOG_FILENAME);
#endif
    }

#if (ERROR_SCREEN == 1)
    Output::error = (ofstream *) & cout;
#else
    Output::error = new std::ofstream();
    Output::error->open(ERROR_LOG_FILENAME);
#endif

#if (STATS_SCREEN == 1)
    Output::stats = (ofstream *) & cout;
#else
    Output::stats = new std::ofstream();
    Output::stats->open(STATS_LOG_FILENAME);
#endif
}

/**
 * Close all files
 */
void Output::close()
{
    if (Output::printDebug == true) {
#if (DEBUG_SCREEN != 1)
        Output::debug->close();
#endif
    }

    if (Output::printTrace == true) {
#if (TRACE_SCREEN != 1)
        Output::trace->close();
#endif
    }
#if (ERROR_SCREEN != 1)
    Output::error->close();
#endif

#if (STATS_SCREEN != 1)
    Output::stats->close();
#endif
}

/**
 * Flush debug files
 */
void Output::flush()
{
    if (Output::printDebug == true) {
        Output::debug->flush();
    }

    if (Output::printTrace == true) {
        Output::trace->flush();
    }
}

string Output::to_str(int val)
{
    stringstream stream;
    stream << val;
    return stream.str();
}
