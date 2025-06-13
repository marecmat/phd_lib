import os 
import sys
import numpy as np 
import matplotlib as mpl 
import matplotlib.pyplot as plt 

PATH = os.path.dirname(__file__)
sys.path.append(PATH+"/../")
from phd_lib.colormaps import nice_colors

def matplot_header(fontsize=12, tex=True, transparent_background=True, use_gui=True, colors='palette2', tex_packages=[]):

    plt.rc('font', **{
        'family': 'sans-serif',
        'weight': 'regular',
        'size': fontsize
    })
    if not use_gui: mpl.use('Agg')
    
    if tex:
        plt.rc('text', usetex=True)
        plt.rc('mathtext', fontset='cm')
        plt.rc('text.latex', preamble=''.join([fr"\usepackage{{{i}}}" for i in tex_packages]))
    
    match colors:
        case 'palette':  cycle = ["#332288", "#88CCEE", "#44AA99", "#117733", "#999933", "#DDCC77", "#CC6677", "#882255", "#AA4499"]
        case 'paultol':  cycle = ["#0077BB", '#33BBEE', '#009988', '#EE7733', '#CC3311', '#EE3377', '#BBBBBB']
        case 'custom':   cycle = list(nice_colors().values())
        case 'ibm':      cycle = ["#ffb000", '#dc267f','#785ef0', '#fe6100', '#648fff',]
        case 'palette2': cycle = ["#332288", '#dc267f', '#8fd687', "#ffb000", "#88CCEE", "#117733", '#785ef0', '#fe6100', '#648fff',]
        case _:          cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']

    plt.rcParams.update({"axes.prop_cycle" : mpl.cycler(color=cycle)})

    if transparent_background:
        plt.rcParams.update({
            "xtick.direction": "in",
            "ytick.direction": "in",
            "axes.edgecolor":    "black",
            "legend.framealpha": None,
            "figure.facecolor":  (0, 0, 0, 0),
            "axes.facecolor":    (0, 0, 0, 0),
            "savefig.facecolor": (0, 0, 0, 0),
            "legend.facecolor":  (1, 1, 1, 1),
            "legend.edgecolor":  (0, 0, 0, 1)
        })
    
    return cycle

def remove_get_axis_formatters(axes, which='x', sci_lim_low=-2, sci_lim_up=2, useOffset=False):
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

    if isinstance(axes, mpl.axes.Axes): 
        axes = np.array([axes])
        orig_shape = (1, 1)
    else: 
        axes = axes.flatten()
        orig_shape = axes.shape

    offset = []
    for ax in axes:
        if   which == 'x' :     
            axis = [ax.xaxis]
            reshape = orig_shape
        elif which == 'y' :     
            axis = [ax.yaxis]
            reshape = orig_shape
        elif which == 'z':
            axis = [ax.zaxis]
            reshape = orig_shape
        elif which == 'all':
            axis = [ax.xaxis, ax.yaxis, ax.zaxis]
            reshape = orig_shape

        elif which == 'both':   
            axis = [ax.xaxis, ax.yaxis]
            reshape = (*orig_shape, 2)

                
        ax.ticklabel_format(style='sci', axis=which, scilimits=(sci_lim_low, sci_lim_up), useOffset=useOffset)
        # Need to draw the canvas or `get_major_formatter()` returns an empty string    
        ax.figure.canvas.draw()
        # Get these offsets to call them in the figure formatting
        # The structure of the array is the same as the original ax array
        for a in axis:
            offset.append(a.get_major_formatter().get_offset().replace(r'\times', ''))
            a.offsetText.set_visible(False)
    return np.array(offset).reshape(reshape)


def fancy_legend(ax, leg=None, axes=None, merge=True, square_box=False, border_lw=.7, **kwargs):
    """
    Merge the legend of several plots into 1, change the border linewidth, 
    and passes the usual legend argument to the legend as kwargs
    """
    if axes is not None and merge:
        handles, labels = [], []
        for a in axes.flatten():
            h, l = a.get_legend_handles_labels()
            handles += h; labels += l
        leg = ax.legend(handles, labels, **kwargs)
    elif leg is not None:
        leg = leg
    else: 
        leg = ax.legend(**kwargs)

    leg.get_frame().set_linewidth(border_lw)

    if square_box: 
        leg.get_frame().set_boxstyle('Square', pad=0.2)

    return leg

def plot3d_format(ax, labelpad=[-5, -4, 0], grid=False, transparent=True, view=(30, 30)):
    ax.grid(grid)
    for axis, pad in zip([ax.xaxis, ax.yaxis, ax.zaxis], labelpad):
        axis.labelpad = pad
        axis.pane.fill = False
        if not grid: axis.pane.set_edgecolor('black')
        if transparent:
            # make the panes transparent
            axis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            axis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            axis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            # make the grid lines transparent
            axis._axinfo["grid"]['color'] =  (1,1,1,0)
            axis._axinfo["grid"]['color'] =  (1,1,1,0)
            axis._axinfo["grid"]['color'] =  (1,1,1,0)
    
    if type(view) == tuple:
        ax.view_init(*view)
    elif type(view) == type(ax):
        ax.shareview(view)
    else: print('issue setting view for ax')

def pcol_put_inner_labels(ax, xlabcoord=(0.15,0.8), ylabcoord=(0.85,0.15), xcolor='white', ycolor='white'):
    ax.yaxis.set_label_coords(*ylabcoord)
    ax.yaxis.label.set_color(ycolor)
    ax.xaxis.set_label_coords(*xlabcoord)
    ax.xaxis.label.set_color(xcolor)
    return None 

def fancy_plot(axes, side_spines=True):
    for ax in axes:
        ax.spines[['right', 'top']].set_visible(~side_spines)
    return None 

def subplots_annotations(axes, xys, labels, fontsize='16', kwargs={}):
    annotation = dict(xycoords='axes fraction', xytext=(-20, 20), textcoords='offset pixels',
            horizontalalignment='right', verticalalignment='bottom', fontsize=fontsize, **kwargs)
    for ax, xy, l in zip(axes, xys, labels):
        annotation['xy'] = xy
        ax.annotate(l, **annotation)

    return None


def axis3D_to_gif(fig, ax, filename='rotation.gif', frames=60, interval=100, dpi=300, elevation=None, use_animation=False, beamer_output=False):
    
    # fig.patch.set_facecolor('white')
    init_azim = ax.azim
    init_elev = ax.elev if elevation is None else elevation
    savefig_kwargs = {'transparent': False, 'facecolor': 'white'} #, 'dpi':dpi}
    
    if beamer_output:
        filename = filename.split('.')[0]
        if not os.path.exists(filename): 
            os.makedirs(filename)

        for i in range(frames):
            azim = (init_azim + 360 * i / frames) % 360
            ax.view_init(elev=init_elev, azim=azim)

            img_name = os.path.join(filename, f"img_{i:03d}.png")
            fig.savefig(img_name, **savefig_kwargs)

    elif use_animation:
        from matplotlib.animation import FuncAnimation, PillowWriter
        from mpl_toolkits.mplot3d import Axes3D

        def update(frame):
            azim = (init_azim + 360*frame/frames)%360
            ax.view_init(elev=init_elev, azim=azim)
            return fig,

        ani = FuncAnimation(fig, update, frames=frames, interval=interval, blit=False)

        ani.save(filename, writer=PillowWriter(fps=1000//interval), dpi=dpi, savefig_kwargs=savefig_kwargs)

    else: 
        import io
        from PIL import Image

        images = []
        for i in range(frames):
            azim = (init_azim + 360*i/frames)%360
            ax.view_init(elev=init_elev, azim=azim)
            buf = io.BytesIO()
            fig.savefig(buf, format='png', **savefig_kwargs)
            buf.seek(0)
            images.append(Image.open(buf))

        images[0].save(filename, save_all=True, append_images=images[1:], duration=interval, loop=0)


def add_arrow(line, arr=0, position=None, direction=None, size=15, color=None):
    """
    stolen and rewritten from https://stackoverflow.com/questions/34017866/arrow-on-a-line-plot
    add an arrow to a line.

    line:       Line2D object
    position:   x-position of the arrow. If None, mean of xdata is taken
    direction:  'left' or 'right'
    size:       size of the arrow in fontsize points
    color:      if None, line color is taken.
    """
    
    if color is None:   color = line.get_color()

    xdata = line.get_xdata()
    ydata = line.get_ydata()

    if position is None:    
        position = xdata.mean()

    # find closest index
    if type(arr) != int:
        start_ind = np.argmin(np.abs(arr - position))
    else:
        start_ind = np.argmin(np.abs(xdata - position))

    if direction == 'right':
        end_ind = start_ind + 1
    elif direction == 'left':
        end_ind = start_ind - 1
    else:
        end_ind = np.argmin(np.abs(xdata - xdata[start_ind-1]))

    line.axes.annotate('',
        xytext=(xdata[start_ind], ydata[start_ind]),
        xy=(xdata[end_ind], ydata[end_ind]),
        arrowprops=dict(arrowstyle="-|>", color=color),
        size=size
    )