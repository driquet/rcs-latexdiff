rcs-latexdiff
#############

rcs-latexdiff is a simple tool to generate a diff of a LaTeX file contained in a Revision Control System (like Git, Mercurial, etc.).
The result is a LaTeX file with the differences between two revisions of a file.

Dependencies:
    * `latexdiff <http://www.ctan.org/tex-archive/support/latexdiff>`_ tool
    * `Python <http://www.python.org/>`_

Features:
    * Support of Git
    * Diff of a LaTeX File for different versions
    * Recursive search of files included

Install 
-------
First, grab sources::

    $ git clone https://github.com/driquet/rcs-latexdiff.git
    $ cd rcs-latexdiff

You may want to install rcs-latexdiff in a virtualenv ; following steps explain how to do it::

    $ virtualenv --prompt==rcs-latexdiff venv
    $ source venv/bin/activate
    $ python setup.py install

If you want to install rcs-latexdiff system wide, just skip the first two steps.

Usage 
-----
Basic usage is::
    
    $ rcs-latexdiff [OPTIONS] filename old_commit new_commit

The complete usage can be displayed with option `-h`.


Examples
--------
For example, if the file `paper.tex` is in a Git repository, you could do::

    $ rcs-latexdiff paper.tex HEAD~1 HEAD

to get a diff between the second to last and the last commit.

Licence
-------

Contributors
------------
