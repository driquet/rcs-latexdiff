from __future__ import print_function, absolute_import

import subprocess
import logging
import re

logger = logging.getLogger("rcs-latexdiff.utils")

def run_command(command, path=""):
    """ Run a command and return its output

        :param path: where to execute the command
        :param command: Command to be executed
        :return: return code and the output produced by the command
        :rtype: list
        :warning: exit if it goes wrong

    """
    try:
        # Forge command
        if path not in ['', '.']:
            command = '(cd {} && {})'.format(path, command)

        logger.debug("Run command: %s" % (command))
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = process.communicate()[0].decode('utf-8')
        retcode = process.returncode

        logger.debug("Return code: %d" % (retcode))
        return retcode, output

    except OSError as e:
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

def remove_latex_comments(content):
    # If a line contains only a comment, remove the line completely
    content = re.sub(r'^[ \t]*%.*\r?\n', '', content, flags=re.MULTILINE)
    # Remove all content which follows a % except if % is preceded by \
    return re.sub(r'(?<!\\)%.*', '', content)
