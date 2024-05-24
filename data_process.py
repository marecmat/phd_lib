import numpy as np 

def find_nearest(array, value, getValue=False):
    idx = (np.abs(array - value)).argmin()
    if getValue:
        return array[idx]
    else: return idx

def closest_argmin(A, B):
    """ 
    stolen from https://stackoverflow.com/questions/45349561/find-nearest-indices-for-one-array-against-all-values-in-another-array-python
    """
    sidx_B = B.argsort()
    sorted_B = B[sidx_B]
    sorted_idx = np.searchsorted(sorted_B, A)
    sorted_idx[sorted_idx == B.size] = B.size - 1
    mask = (sorted_idx > 0) & ((np.abs(A - sorted_B[sorted_idx - 1]) < np.abs(A - sorted_B[sorted_idx])) )
    return sidx_B[sorted_idx-mask]


def get_regex_find_digits():
    return '([-+]?[0-9]+[.]?[0-9]*([eE][-+]?[0-9]+)?)'

def reduceComplexArrayBounds(array, realLimits, imagLimits):
    slc = np.logical_and.reduce(
        (
            np.real(array) < realLimits[1], 
            np.real(array) > realLimits[0], 
            np.imag(array) < imagLimits[1],
            np.imag(array) > imagLimits[0]
        )
    )
    return array[slc], slc

