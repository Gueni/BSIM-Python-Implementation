

/**
 * Find end of command
 * 
 * @note commands are terminated by ";" or by EOL, EOF, or by EOS ("\0")
 * 
 * @retval return number of characters from the beggining of the string, where EOC has been found
 */
static int find_EOC(char *cmd)
{
    int index = 0;
    while (true) {
        switch (*cmd) {
        case '\n':
        case '\r':
        case '\0':
        case ';':
            return index;
        default:
            cmd++;
            index++;
            break;
        }
    }
}

/**
 * Get pointer to the next CMD
 * 
 * @param cmd pointer to a command buffer
 * 
 * @retval true if next command available, alse return false
 */
static bool getNextCMD(char **cmd)
{
    *cmd += find_EOC(*cmd);

    while (!(((**cmd >= 'a') && (**cmd <= 'z')) ||
             ((**cmd >= 'A') && (**cmd <= 'Z')) ||
             ((**cmd >= '0') && (**cmd <= '9'))
           )) {
        if (**cmd == '\0') {
            // End of string
            return false;
        }
        (*cmd)++;
    }
    return true;
}

/**
 * Get pointer to the next word
 * 
 * @param cmd pointer to a command buffer
 * 
 * @retval true if next word is available, alse return false
 */
static bool getNextWord(char **cmd)
{
    while (**cmd != ' ') {
        if (**cmd == '\0') {
            // End of string
            return false;
        }
        (*cmd)++;
    }

    while (!(((**cmd >= 'a') && (**cmd <= 'z')) ||
             ((**cmd >= 'A') && (**cmd <= 'Z')) ||
             ((**cmd >= '0') && (**cmd <= '9')))) {
        if (**cmd == '\0') {
            // End of string
            return false;
        }
        (*cmd)++;
    }
    return true;
}
