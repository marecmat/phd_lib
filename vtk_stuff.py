import numpy as np
import matplotlib.pyplot as plt
import pyvtk

from vtk import vtkUnstructuredGridReader, vtkXMLUnstructuredGridReader
from matplotlib.tri import Triangulation
from matplotlib.ticker import FormatStrFormatter


def export(filename, points, faces, scalar, scalar_name):
    grid = pyvtk.UnstructuredGrid(points, triangle=(faces))
    data = pyvtk.PointData(pyvtk.Scalars(scalar, name=scalar_name))
    pyvtk.VtkData(grid, data).tofile(filename)
    return None


def read_unstructured_grid(vtk_file: str):
    """
    Imports a vtk file and outputs points, faces and scalars
    
    input:
        vtk_file: str
        The name of the file to load

    output: 
        points: array
        faces: array
        scalars: dict
    """
    
    if vtk_file.endswith('.vtu'):
        reader = vtkXMLUnstructuredGridReader()
        reader.SetFileName(vtk_file)

    elif vtk_file.endswith('.vtk'):
        reader = vtkUnstructuredGridReader()
        reader.SetFileName(vtk_file)
        reader.ReadAllScalarsOn()
    else: raise NameError(f"Unsupported file extension .{vtk_file.split('.')[-1]}")

    reader.Update()
    grid = reader.GetOutput()
    points = np.array([grid.GetPoint(i) for i in range(grid.GetNumberOfPoints())])

    faces = []
    for i in range(grid.GetNumberOfCells()):
        cell = grid.GetCell(i)
        if cell.GetNumberOfPoints() == 3:
            faces.append([cell.GetPointId(j) for j in range(3)])
    faces = np.array(faces)

    scalars = {}
    point_data = grid.GetPointData()
    for i in range(point_data.GetNumberOfArrays()):
        scalar_name = point_data.GetArrayName(i)
        scalars[scalar_name] = np.array(point_data.GetArray(i))

    return points, faces, scalars


def plot(filename_data=None, figax=None, kx=None, norm=None, scalar='Pressure', scalar_func=abs, draw_mesh=False, contour_plot=None):

    if type(filename_data) == str: # read vtk file
        points, faces, scalars = read_unstructured_grid(filename_data)
    elif type(filename_data) == tuple: # use data if directly provided 
        points, faces, scalars = filename_data
    else: raise TypeError('Provide suitable data for plotting!')

    points = np.array(points)
    d, h = np.round(np.max(points[:, 0]), 15), np.round(np.max(points[:, 1]), 15)

    try:
        if scalar.endswith('_'):
            # Comsol exports a different scalar for the real and imag part
            # Specify the scalar to plot w/o the real or imag at the end
            field = np.array(scalars[scalar+'real'] + 1j*scalars[scalar+'imag'])
        else: 
            field = np.array(scalars[scalar])
            if not kx == None:
                field *= np.exp(1j*kx*points[:, 0])
            else: 
                print('no kx was provided')

    except KeyError:
        print(f'Invalid scalar {scalar} available is {scalars.keys()}')
        exit()

    if norm == None:
        corner_loc = np.where((points[:, 0] == 0) & (points[:, 1] == h))[0]
        norm_field = field/field[corner_loc]
    else: 
        norm_field = field/norm
    

    if figax == None:
        fig, ax = plt.subplots(1, 1)
    else: 
        fig, ax = figax

    if contour_plot is None: 
        min_val = np.min(scalar_func(norm_field)[scalar_func(norm_field) != 0])
        max_val = np.max(scalar_func(norm_field))
        contour_plot = {
            'cmap':'viridis',
            'levels': np.linspace(min_val, max_val, 50),
            'extend': 'max'
        }
    tri = Triangulation(points[:, 0], points[:, 1], faces)
    contour = ax.tricontourf(tri, scalar_func(norm_field), **contour_plot)
    for c in contour.collections: 
        c.set_rasterized(True)

    cbar = fig.colorbar(contour, ax=ax, shrink=.65, pad=0.05, 
        format=FormatStrFormatter('%.2g'), 
        ticks=[contour_plot['levels'][0], contour_plot['levels'][-1]])

    if draw_mesh:
        ax.triplot(tri, 'k-', linewidth=0.1)

    ax.set(xticks=[0, d/2, d], yticks=[0, h/2, h])
    ax.set_aspect('equal')
    return fig, ax, cbar, tri, scalar_func(norm_field)