import numpy as np

def dagger(A):
    return np.transpose(np.conjugate(A))

def coth(x):
    """
    cotangente hyperbolique: 
        coth(x) = cosh(x)/sinh(x)
    """

    return np.cosh(x)/np.sinh(x)
    
def extrema(array, return_id=False, mini=False):
    """
    Performs a double differentiation of an array to locate local extrema

    Parameters
    --------
    array:  array
        The data on which to search for extrema
    return_id: boolean, optional
        If True, return the indices of the array where extrema 
        where found, and else, returns the values of the extrema
    mini: boolean, optional
        If True, searches for local minimas (diff), and else 
        looks for maximas
        TODO: add condition to return both
    
    Returns
    -------
    indices: array
        The indices where the local extrema were located, or the 
        extrema values
    """

    diffdiff = np.diff(np.sign(np.diff(array)))

    if mini: indices = np.where(diffdiff > 0 )[0] + 1
    else:    indices = np.where(diffdiff < 0 )[0] + 1

    if not return_id:
        return array[indices]
    else: 
        return indices
