import re
import argparse
import logging
import os

from rcs_latexdiff.rcs import get_rcs_class
from rcs_latexdiff.utils import run_command, write_file


logger = logging.getLogger("rcs-latexdiff")

def get_file(rcs, root_path, relative_path, commit, filename):
    # TODO docs path root and relative
    """ Process a File that includes
        - Read a file
        - Look for recursively includes or inputs
        - Replace content

        :param rcs: Rcs instance
        :type rcs: RCS object
        :param path: path of the repository
        :param commit: Commit name
        :param filename: Name of the file
        :return: the content of the file

    """
    # Debug info
    logger.info("> Get file %s" % filename)

    # Read the file
    file_content = rcs.show_file(root_path, commit, os.path.join(relative_path, filename))

    # Look for external inputs
    external_inputs = re.findall("\\\(?:input|include)\{.*\}",file_content)

    for external_input in external_inputs:


        # For each external input, find the name of the file, read it and replace it in the original content
        input_name = re.search("\{(.*)\}", external_input).group(1)

        if not input_name.endswith(".tex"):
            input_name += ".tex"

        # Read the content of the input
        input_content = get_file(rcs, root_path, relative_path, commit, input_name)

        # Add delimiters
        begin_delimiter = "%% Input %s" % input_name
        end_delimeter = "%% End of Input %s" % input_name
        input_content = "%s\n%s\n%s" % (begin_delimiter, input_content, end_delimeter)

        # Replace
        file_content = file_content.replace(external_input, input_content)


    # Return the content
    return file_content


def exec_diff(old_filename, new_filename, diff_filename):
    """ Exec Latexdiff

        :param old_filename:
        :param new_filename:
        :param diff_filename:

    """
    run_command("latexdiff %s %s > %s" % (old_filename, new_filename, diff_filename))
        


def make_diff(rcs, old_commit, new_commit, root_path, relative_path, src_filename, dst_filename):
    # TODO docs path root and relative
    """ Make a diff for a name between two commits

        :param rcs: Rcs instance
        :type rcs: RCS object
        :param old_commit: old commit
        :param new_commit: new commit
        :param path: path of the repository
        :param src_filename: name of the file
        :param dst_filename: name of the output file
        :return: destination file and temporary files

    """

    # Debug info
    logger.info("Root path of the repository: %s" % root_path)
    if relative_path: logger.info("Relative path: %s" % relative_path)
    logger.info("Filename: %s" % src_filename)
    logger.info("Output: %s" % dst_filename)

    # Get files
    logger.info("Get old content (commit %s)..." % old_commit)
    old_content = get_file(rcs, root_path, relative_path, old_commit, src_filename)
    logger.info("Get new content (commit %s)..." % new_commit)
    new_content = get_file(rcs, root_path, relative_path, new_commit, src_filename)

    # Write files
    old_filename = dst_filename + ".old"
    new_filename = dst_filename + ".new"

    write_file(old_content, old_filename)
    write_file(new_content, new_filename)

    # Exec diff
    logger.info("Execute latexdiff")
    exec_diff(old_filename, new_filename, dst_filename)

    return dst_filename, old_filename, new_filename


def parse_arguments():
    parser = argparse.ArgumentParser(description='A tool to generate LaTeX Diff between two Revision Control System commits of a file.')

    parser.add_argument('--clean', action='store_const',
        const=True, dest='clean',
        help='Clean all files except the generated diff file.')

    parser.add_argument('-o', '--output', dest='output', default='diff.tex',
        help='Name of the generated diff file. If not specified, '
             'default output will be "diff.tex" in the current path.')

    parser.add_argument('-v', '--verbose', action='store_const',
        const=logging.INFO, dest='verbosity',
        help='Show all messages.')

    parser.add_argument('-D', '--debug', action='store_const',
        const=logging.DEBUG, dest='verbosity',
        help='Show all message, including debug messages.')    

    parser.add_argument('FILE', help='File to be compared.')

    parser.add_argument('OLD', help='Old commit (SHA1 or branche name).')

    parser.add_argument('NEW', help='New commit (SHA1 or branche name).')

    return parser.parse_args()


def init_logger(verbosity):
    """ Initialization of logger module

        :param verbosity:

    """
    FORMAT = '%(message)s'
    logging.basicConfig(format=FORMAT)

    if verbosity:
        logger.setLevel(verbosity)
    

def clean_output_files(files):
    """ Clean temporary files generated for the diff tool
        
        :param files: files to be removed

    """
    for filename in files:
        logger.debug("Removing file: %s" % filename)
        os.remove(filename)

def check_latexdiff():
    """ Check that latexdiff binary is in the PATH """
    check_latexdiff = "which latexdiff"
    ret, output = run_command(check_latexdiff)

    # latexdiff tool not available ?
    if ret:
        print """latexdiff tool not found in PATH
Install it or correct your PATH

You can install it as follows:
    Apt-based distribution:
        apt-get install latexdiff
    MacPorts (OS X):
        sudo port install latexdiff
"""
        exit(1)

    


def main():
    # Make sure that latexdiff is available
    check_latexdiff()

    # Parse arguments, init logger and extract information
    args = parse_arguments()
    init_logger(args.verbosity)

    # Get the current rcs class
    dirname = os.path.dirname(args.FILE)
    path = '.' if dirname == '' else dirname
    rcs = get_rcs_class(path)
    if not rcs:
        logger.info("No RCS repository found")
        exit(1)

    root_path, relative_path, filename = rcs.get_relative_paths(args.FILE)

    # Ensure that commits exist
    for commit in [args.OLD, args.NEW]:
        if not rcs.is_commit(root_path, commit):
            logger.info("Commit does not exist: %s" % (commit))
            exit(1)

    # Make the diff
    generated_files = make_diff(rcs, args.OLD, args.NEW, root_path, relative_path, filename, args.output)

    # Clean output files
    if args.clean:
        clean_output_files(generated_files[1:])


if __name__ == '__main__':
    main()
