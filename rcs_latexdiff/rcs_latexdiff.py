import re
import argparse
import logging
import os
import glob

from rcs import get_rcs_class
from utils import run_command, write_file


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

def exec_pdflatex(tex_filename, src_path):
    
    tex_path = os.path.dirname(tex_filename)    
    
    aux_filename = os.path.splitext(tex_filename)[0] + ".aux"
    pdf_filename = os.path.splitext(tex_filename)[0] + ".pdf"
    
    # We enter the folder of the source to get proper relative paths to 
    # figures
    starting_dir = os.getcwd()
    os.chdir(src_path)
    
    def single_run():
        run_command("pdflatex -interaction nonstopmode -output-directory {} {}".format(tex_path, tex_filename))
    
    # Run pdflatex and bibtex a bunch of times
    try:
        single_run()
        single_run()
        
        if os.path.isfile(aux_filename):
            run_command("bibtex %s" % tex_filename)
            run_command("bibtex %s" % aux_filename)
            
        single_run()
        single_run()
        
        logger.info("Ran pdflatex and bibtex.")
    except:
        logger.debug("Problem building pdf file.")
    
    # Return to orig directory
    os.chdir(starting_dir)    
    
    return pdf_filename
    
def open_pdf(pdf_filename):
    pass

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

    # Write files (in same folder as dst_filename)
    dst_path = os.path.dirname(os.path.abspath(dst_filename))
    old_filename = os.path.join(dst_path, os.path.basename(dst_filename) + ".old")
    new_filename = os.path.join(dst_path, os.path.basename(dst_filename) + ".new")

    write_file(old_content, old_filename)
    write_file(new_content, new_filename)

    # Exec diff
    logger.info("Execute latexdiff")
    exec_diff(old_filename, new_filename, dst_filename)

    return dst_filename, old_filename, new_filename


def parse_arguments():
    parser = argparse.ArgumentParser(description='A tool to generate LaTeX Diff between two Revision Control System commits of a file.')

    parser.add_argument('--clean', action='store_true',
        dest='clean',
        help='Clean all files except the generated diff file.')
        
    parser.add_argument('--no-pdf', action='store_false',
        dest='makepdf',
        help='Don\'t try to run pdflatex on the diff file.')
        
    parser.add_argument('--no-open', action='store_false',
        dest='openpdf',
        help='Don\'t try to open the created pdf file.')

    parser.add_argument('-o', '--output', dest='output',
        help='Name of the generated diff file. If not specified, '
             'default output will be "diff.tex" in the path of '
             'the file you are comparing.')

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
        try:
            os.remove(filename)
            logger.debug("Removed file: %s" % filename)
        except OSError:
            logger.debug("Could not remove file: %s" % filename)

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
            
    # Populate the default output file
    if args.output is None:
        dst_filename = os.path.join(root_path, relative_path, 'diff.tex')
    else:
        dst_filename = args.output

    # Make the diff
    make_diff(rcs, args.OLD, args.NEW, root_path, relative_path, filename, dst_filename)

    # Make the pdf
    if args.makepdf:
        pdf_filename = exec_pdflatex(dst_filename, os.path.join(root_path, relative_path))
        
    # Open the pdf
    if args.openpdf:
        open_pdf(pdf_filename)

    # Clean output files
    if args.clean:
        # Clean everything except diff.pdf or diff.tex depending on makepdf
        clean_glob = glob.glob(os.path.splitext(dst_filename)[0] + '.*')
        keep_ext = 'pdf' if args.makepdf else 'tex'
        clean_glob = [f for f in clean_glob if f[-3:] != keep_ext]
        
        clean_output_files(clean_glob)


if __name__ == '__main__':
    main()
