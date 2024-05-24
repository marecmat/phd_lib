import os
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, Normalize

def nice_colors(i=False):
    cycle = {'b':'#3593CC', 'y':'#D49902', 'p':'#B34BBE',  'g':'#26C485', 'r':'#DB5461'}
    if not i:
        return cycle 
    else: return cycle[i]

def TrRi(N=256):
    cm_data = np.array([
        [0.961, 0.663, 0.722],
        [1, 1, 1],
        [0.357, 0.808, 0.98]
    ])
    return LinearSegmentedColormap.from_list('TrRi', cm_data, N=N)


def BlKPk(N=256):
    # import struct
    # colors = ["ff0e5c", "ff6aad", "999999", "80c9e6", "8bdcff"]
    colors = ["8bdcff", "80c9e6", "999999", "e0777e", "e01d4e"]
    cm_data = np.array([[int(i, 16)/255 for i in list(map(''.join, zip(*[iter(c)]*2)))] for c in colors])
    return LinearSegmentedColormap.from_list('BlKPk', cm_data, N=N)

def PiKYG(N=256):
    # import struct
    colors = ["940557", "eca9d2", "ffe4af", "99cd5f", "2a6219"]
    cm_data = np.array([[int(i, 16)/255 for i in list(map(''.join, zip(*[iter(c)]*2)))] for c in colors])
    return LinearSegmentedColormap.from_list('PiKYG', cm_data, N=N)

def OrKGr(N=256):
    # import struct
    colors = ["ff8d00", "ffae7b", "fff983", "80ffad", "129300"]
    cm_data = np.array([[int(i, 16)/255 for i in list(map(''.join, zip(*[iter(c)]*2)))] for c in colors])
    return LinearSegmentedColormap.from_list('OrKGr', cm_data, N=N)

def parula(N=256):
    cm_data = np.loadtxt(os.path.dirname(__file__)+'/data/parula_data.csv', delimiter=',')
    return LinearSegmentedColormap.from_list('parula', cm_data, N=N)

def rgb_white2alpha(rgb, ensure_increasing=False):
    # https://stackoverflow.com/questions/37327308/add-alpha-to-an-existing-matplotlib-colormap
    """
    Convert a set of RGB colors to RGBA with maximum transparency.
    
    The transparency is maximised for each color individually, assuming
    that the background is white.
    
    Parameters
    ----------
    rgb : array_like shaped (N, 3)
        Original colors.
    ensure_increasing : bool, default=False
        Ensure that alpha values are strictly increasing.
    
    Returns
    -------
    rgba : numpy.ndarray shaped (N, 4)
        Colors with maximum possible transparency, assuming a white
        background.
    """
    # The most transparent alpha we can use is given by the min of RGB
    # Convert it from saturation to opacity
    alpha = 1. - np.min(rgb, axis=1)
    if ensure_increasing:
        # Let's also ensure the alpha value is monotonically increasing
        a_max = alpha[0]
        for i, a in enumerate(alpha):
            alpha[i] = a_max = np.maximum(a, a_max)
    alpha = np.expand_dims(alpha, -1)
    # Rescale colors to discount the white that will show through from transparency
    rgb = (rgb + alpha - 1) / alpha
    # Concatenate our alpha channel
    return np.concatenate((rgb, alpha), axis=1)
    

def cmap_white2alpha(name, ensure_increasing=False, register=True):
    # https://stackoverflow.com/questions/37327308/add-alpha-to-an-existing-matplotlib-colormap
    """
    Convert colormap to have the most transparency possible, assuming white background.
    
    Parameters
    ----------
    name : str
        Name of builtin (or registered) colormap.
    ensure_increasing : bool, default=False
        Ensure that alpha values are strictly increasing.
    register : bool, default=True
        Whether to register the new colormap.

    Returns
    -------
    cmap : matplotlib.colors.ListedColormap
        Colormap with alpha set as low as possible.
    """
    import matplotlib
    import matplotlib.pyplot as plt 
    # Fetch the cmap callable
    cmap = plt.get_cmap(name)
    # Get the colors out from the colormap LUT
    rgb = cmap(np.arange(cmap.N))[:, :3]  # N-by-3
    # Convert white to alpha
    rgba = rgb_white2alpha(rgb, ensure_increasing=ensure_increasing)
    # Create a new Colormap object
    cmap_alpha = matplotlib.colors.ListedColormap(rgba, name=name + "_alpha")
    if register:
        matplotlib.cm.register_cmap(name=name + "_alpha", cmap=cmap_alpha)
    return cmap_alpha


def mappable_colorbar(values, cmap):
    from matplotlib.cm import ScalarMappable
    sm = ScalarMappable(
        cmap=cmap, 
        norm=Normalize(vmin=np.min(values), vmax=np.max(values)))
    
    return sm
