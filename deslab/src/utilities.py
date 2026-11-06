"""Common utilities."""
#    Copyright (C) 2011-2012 by
#    Leonardo Bermeo <lbermeoc@unal.edu.co>
#    Joao Carlos Basilio <basilio@poli.ufrj.br>
#    GNU license.

from deslab.src.def_const import *
from itertools import chain
from shutil import which as _find_executable

## we should improve this definition by defining a class for languages and sequences
   
def syms(namelst):
    import sys
    """
    syms takes a string of symbol names separated by
    blanks and converts them to string variable whose 
    name is the same that the string contained in such
    variable
    """
    namelst = str.split(namelst)
    for name in namelst:
        sys._getframe(1).f_locals[name] = name
    return namelst



def which(program):
    """
    Determines if the current program is an executable file
    """    

    return _find_executable(program)
