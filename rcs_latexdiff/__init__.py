import re
import argparse
import logging
import os

from rcs_latexdiff.rcs import get_rcs_class
from rcs_latexdiff.utils import run_command, write_file


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
    # Get files
    old_content = get_file(rcs, root_path, relative_path, old_commit, src_filename)
    new_content = get_file(rcs, root_path, relative_path, new_commit, src_filename)

    # Write files
    old_filename = dst_filename + ".old"
    new_filename = dst_filename + ".new"

    write_file(old_content, old_filename)
    write_file(new_content, new_filename)

    # Exec diff
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


def init_logging(verbosity):
    """ Initialization of logging module

        :param verbosity:

    """
    logger = logging.getLogger()
    FORMAT = '%(message)s'
    logging.basicConfig(format=FORMAT)

    if verbosity:
        logger.setLevel(verbosity)
    

def clean_output_files(files):
    """ Clean temporary files generated for the diff tool
        
        :param files: files to be removed

    """
    for filename in files:
        logging.debug("Removing file: %s" % filename)
        os.remove(filename)


def main():
    # Parse arguments, init logging and extract information
    args = parse_arguments()
    init_logging(args.verbosity)

    # Get the current rcs class
    rcs = get_rcs_class(os.path.dirname(args.FILE)) 
    if not rcs:
        logging.info("No RCS repository found: %s" % (path))
        exit(1)

    root_path, relative_path, filename = rcs.get_relative_paths(args.FILE)

    print 'root', root_path
    print 'relative', relative_path
    print 'filename', filename

    # Ensure that commits exist
    for commit in [args.OLD, args.NEW]:
        if not rcs.is_commit(root_path, commit):
            logging.info("Commit does not exist: %s" % (commit))
            exit(1)

    # Make the diff
    generated_files = make_diff(rcs, args.OLD, args.NEW, root_path, relative_path, filename, args.output)

    # Clean output files
    if args.clean:
        clean_output_files(generated_files[1:])


if __name__ == '__main__':
    main()
