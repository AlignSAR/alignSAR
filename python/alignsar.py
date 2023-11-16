# Collection of Python functions implemented for AlignSAR
from snap_rdrcode import *
import numpy as np

def RI2cpx(R, I, cpxfile, intype=np.float32):
    """Convert real and imaginary binary files to a complex number binary file.
    
    Args:
        R (string or np.ndarray): path to the binary file with real values, or directly loaded as numpy ndarray
        I (string or np.ndarray): path to the binary file with imaginary values, or directly loaded as numpy ndarray
        cpxfile (string or None): path to the binary file for complex output (the output will be as complex64). if None, it will only return the cpxarray
        intype (type): data type of the binary file. np.float32 or np.float64 if needed.
    
    Returns:
        np.array: this array must be reshaped if needed
    """
    # we may either load R, I from file:
    if type(R) == type('str'):
        r = np.fromfile(R, dtype=intype)
        i = np.fromfile(I, dtype=intype)
    else:
        r = R.astype(intype).ravel()
        i = I.astype(intype).ravel()
    if cpxfile:
        cpx = np.zeros(len(r)+len(i))
        cpx[0::2] = r
        cpx[1::2] = i
        cpx.astype(np.float32).tofile(cpxfile)
    return r + 1j*i
