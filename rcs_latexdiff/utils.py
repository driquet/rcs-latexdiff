import subprocess
import logging

logger = logging.getLogger("rcs-latexdiff.utils")

def run_command(command):
    """ Run a command and return its output

        :param command: Command to be executed
        :return: return code and the output produced by the command
        :rtype: list
        :warning: exit if it goes wrong

    """
    try:
        logger.debug("Run command: %s" % (command))
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = process.communicate()[0]
        retcode = process.returncode

        logger.debug("Return code: %d" % (retcode))
        return retcode, output

    except OSError, e:
        logger.info("Execution failed: %s" % (e))
        exit(1)

def write_file(content, filename):
    """ Write a file

        :param content:
        :param filename: name of the file

    """
    logger.debug("Writing content into %s" % filename)
    with open(filename, 'w') as f:
        f.write(content)
