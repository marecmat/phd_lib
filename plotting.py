import os 
import sys
import numpy as np 
import matplotlib as mpl 
import matplotlib.pyplot as plt 

PATH = os.path.dirname(__file__)
sys.path.append(PATH+"/../")
from phd_lib.colormaps import nice_colors
def matplot_header(fontsize=15, tex=True, transparent_background=True, use_gui=True, colors=False, tex_packages=''):

    plt.rc('font', **{
        'family': 'sans-serif',
        'weight': 'regular',
        'size': fontsize
    })
    if not use_gui: mpl.use('Agg')
    
    if tex:
        plt.rc('text', usetex=True)
        plt.rc('mathtext', fontset='cm')
        plt.rc('text.latex', preamble=tex_packages)

    match colors:
        case 'palette': cycle = ["#332288", "#88CCEE", "#44AA99", "#117733", "#999933", "#DDCC77", "#CC6677", "#882255", "#AA4499"]
        case 'paultol': cycle = ["#0077BB", '#33BBEE', '#009988', '#EE7733', '#CC3311', '#EE3377', '#BBBBBB']
        case 'custom':  cycle = list(nice_colors().values())
        case _:         cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']

    plt.rcParams.update({"axes.prop_cycle" : mpl.cycler(color=cycle)})

    if transparent_background:
        plt.rcParams.update({
            "axes.edgecolor":    "black",
            "legend.framealpha": None,
            "figure.facecolor":  (0, 0, 0, 0),
            "axes.facecolor":    (0, 0, 0, 0),
            "savefig.facecolor": (0, 0, 0, 0),
            "legend.facecolor":  (0, 0, 0, 0),
            "legend.edgecolor":  (0, 0, 0, 0)
        })
    
    return None 

def remove_get_axis_formatters(axes, which='x', sci_lim_low=-2, sci_lim_up=2):
    """
    Removes and returns the major axis formatter when scientific notation 
    is used to draw the axis of a plot. Can be used later to put it as a label, 
    for tidier figures (imo)

    # INPUT
        axes: axes type or array 
            the axes of which the formatters will be removed and returned
        which: str
            either 'x', 'y' or 'both' depending on the axis to 
            apply the function on
        sci_lim_low: int
            The power below which scientific notation will be applied on the axis.
            Matplotlib default is 1e-5, here 1e-2 is taken as default
        sci_lim_low: int
            The power above which scientific notation will be applied on the axis.
            Matplotlib default is 1e6, here 1e2 is taken as default

    # OUTPUT
        offset: array 
            the formatters generated after the canvas drawing with shape(axes) 
            or (shape(axes), 2) if the method is to be applied on both axes

    """
    orig_shape, offset = axes.shape, []

    if isinstance(axes, mpl.axes.Axes): 
        axes = np.array([axes])
    else: 
        axes = axes.flatten()

    for ax in axes:
        if   which == 'x' :     
            axis = [ax.xaxis]
            reshape = orig_shape
        elif which == 'y' :     
            axis = [ax.yaxis]
            reshape = orig_shape
        elif which == 'both':   
            axis = [ax.xaxis, ax.yaxis]
            reshape = (*orig_shape, 2)
                
        ax.ticklabel_format(style='sci', axis=which, scilimits=(sci_lim_low, sci_lim_up))
        # Need to draw the canvas or `get_major_formatter()` returns an empty string    
        ax.figure.canvas.draw()
        # Get these offsets to call them in the figure formatting
        # The structure of the array is the same as the original ax array
        for a in axis:
            offset.append(a.get_major_formatter().get_offset().replace(r'\times', ''))
            a.offsetText.set_visible(False)
    return np.array(offset).reshape(reshape)


def fancy_legend(ax, axes, merge=True, border_lw=.7, **kwargs):
    """
    Merge the legend of several plots into 1, change the border linewidth, 
    and passes the usual legend argument to the legend as kwargs
    """
    if merge:
        handles, labels = [], []
        for a in axes.flatten():
            h, l = a.get_legend_handles_labels()
            handles += h; labels += l
        leg = ax.legend(handles, labels, **kwargs)
    
    else: leg = ax.legend(**kwargs)

    leg.get_frame().set_linewidth(border_lw)
    return leg




if __name__ == '__main__':
    x       = np.arange(200)
    fig, ax = plt.subplots(5, 3)
    plots = []
    for ii, a in enumerate(ax.flatten()):
        a.plot(x, 3*x**(ii/2), label=f'{ii}')
        a.plot(x, 3*x**(ii/2), label=f'{ii}')

    fancy_legend(ax[-1, -1], axes=ax, border_lw=5, 
        draggable=True, loc='lower right', bbox_to_anchor=(1.6, -1))
    out = remove_get_axis_formatters(ax, which='both')
    for ii in range(ax.shape[0]):
        for jj in range(ax.shape[1]):
            ax[ii, jj].set_ylabel(out[ii, jj])
            ax[ii, jj].set_ylabel(out[ii, jj, 1])

    plt.show()