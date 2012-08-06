import os

from rcs_latexdiff.utils import run_command


class RCS(object):
    """ Revision Control System class """

    def show_file(self, path, commit, filename):
        """ Return the content of a file for a commit

            :param path: path of the repository
            :param commit: Commit name
            :param filename: Name of the file
            :return: the content of the file (may be empty if the file does not exist) 

        """
        pass

    def is_valid_directory(self, path):
        """ Return wheter or not the directory is a valid RCS repository

            :param path: Path of the dir
            :return: True/False
        
        """
        pass

    def is_commit(self, path, commit):
        """ Return wheter or not the commit is a valid commit

            :param path: path of the repository
            :param commit: Commit name
            :return: True/False 

        """
        pass

    def get_relative_paths(self, filename):
        """ Return the root path of the repository

            :param path: path of the file containing the path
            :return: the root path, the relative path and the filename
        
        """
        pass



class Git(RCS):
    """ Git Revision Control System class """

    def show_file(self, path, commit, filename):
        # Execute 'git show' command and return content or empty string   
        git_show_command = "(cd %s && git show %s:%s)" % (path, commit, filename)
        ret, file_content = run_command(git_show_command)

        # Does the file exist ?
        if ret:
            # Return code != 0, file not found for this commit
            file_content = ""

        return file_content.strip()

    def is_valid_directory(self, path):
        # Verify that path is a valid repository
        # Following command do :
        #   - jump to path
        #   - git status
        #   - jump back to the current dir
        git_status_command = "(cd %s && git status)" % path
        ret, output = run_command(git_status_command)

        # Does the repository is a valid RCS dir
        return ret == 0

    def is_commit(self, path, commit):
        # Execute 'git show' command and return True of False according to ret code
        git_show_command = "(cd %s && git show %s)" % (path, commit)
        ret, output = run_command(git_show_command)

        # Valid commit ?
        return ret == 0


    def get_relative_paths(self, filename):
        path = os.path.dirname(filename)
        path = '.' if path == '' else path

        # Get the root path of the repository 
        git_path_command= "(cd %s && git rev-parse --show-toplevel)" % (path)
        ret, root_path = run_command(git_path_command)

        root_path = os.path.abspath(root_path.strip())

        # Get the relative path of the file
        relative_path = os.path.dirname(os.path.abspath(filename)[len(root_path)+1:])

        filename = os.path.basename(filename)

        return root_path, relative_path, filename

class SVN(RCS):
    """ SVN Revision Control System class """

    def show_file(self, path, commit, filename):
        # Execute 'svn cat' command and return content or empty string   
        svn_cat_command = "(cd %s && svn cat -r %s %s)" % (path, commit, filename)
        ret, file_content = run_command(svn_cat_command)

        # Does the file exist ?
        if ret:
            # Return code != 0, file not found for this commit
            file_content = ""

        return file_content.strip()

    def is_valid_directory(self, path):
        # Verify that path is a valid repository
        # Following command do :
        #   - jump to path
        #   - svn info
        #   - jump back to the current dir
        svn_status_command = "(cd %s && svn info)" % path
        ret, output = run_command(svn_status_command)

        # Does the repository is a valid RCS dir
        return ret == 0

    def is_commit(self, path, commit):
        # Execute 'svn show' command and return True of False according to ret code
        svn_info_command = "(cd %s && svn info -r %s)" % (path, commit)
        ret, output = run_command(svn_info_command)

        # Valid commit ?
        return ret == 0

    def get_relative_paths(self, filename):
        # In the case of SVN, we can consider use SVN commands whatever the path is
        # So we don't differentiate root and relative paths


        # Get the root path of the repository 
        root_path = os.path.dirname(filename)

        relative_path = ""
        filename = os.path.basename(filename)

        return root_path, relative_path, filename



# Contains all classes
_RCS = []

for cls in RCS.__subclasses__():
    _RCS.append(cls())


def get_rcs_class(path):
    """ Get the RCS class
        
        :param path: path of the file
        :return: the rcs instance or None if no class is valid
    """
    for cls in _RCS:
        if cls.is_valid_directory(path):
            return cls

    return None
