import numpy as np 

def require_directory_input(parser=None, suffix=''):
    import argparse
    
    # print(type(parser))
    if not isinstance(parser, argparse.ArgumentParser):
        parser = argparse.ArgumentParser()
    
    parser.add_argument("-d", "--directory")
    args = parser.parse_args()
    directory = args.directory
    
    if type(directory) != str:
        raise Exception('chemin invalide')

    if directory[-1] != '/': directory += '/'
    if suffix != '': directory += suffix

    return directory

def add_arguments(arguments):
    """
    Pass a list in the form of 
        [
            ...
            (- <short_flag>, -- <long_flag>, dict(args)),
            ...
        ]
    
    Returns a dict of the parsed args
    """
    import argparse
    parser = argparse.ArgumentParser()

    for arg in arguments:
        parser.add_argument(arg[0], arg[1], **arg[2])

    return vars(parser.parse_args()), parser



def interactWithFortran(fortran_binary, args):
    from subprocess import Popen, PIPE

    """
    Allows to return the input of a compiled fortran program 
    given some arguments to the binary

    Parameters
    --------
    fortran_binary: str
        The name of the compiled fortran program
    args: list, length I
        The list of the provided arguments in the fortran program
        INTEGER args(I)
        DO ii = 1,I
        CALL getarg( ii, argv )
        READ (ARGV,*) argarg
        args(ii) = argarg
        ENDDO
    
    Returns
    -------
    The output stdout and stderr of the process
    """
    proc = Popen(
        [
            f'./{fortran_binary}', 
            *args
        ], 
        stdout=PIPE, 
        stderr=PIPE
    )
    stdout, stderr = proc.communicate()
    return stdout, stderr

def loadComsolComplexData(filename, sep=',', header=4, skipfooter=0):
    """
    INPUT
    -----
        filename: str
            The name of the file to load with the path
        sep: str
            The character used as a separator for the data, a column by default
        header: int
            The number of line taken as header, to be skipped. 
            The first line with the column name should not be counted. 
        skipfooter: int
            The number of lines to skip at the end of the file
    OUTPUT
    ______
        pandas dataframe with the data
    """
    import pandas as pd
    # The file needs to be in csv
    def TOcomplex(s):
        # Function that takes a string s and formats it properly as a 
        # complex interpretable object for Python
        if 'i' in str(s) and not('n' in str(s)):
            return complex(str(s).replace('i', 'j'))

        else :
            return complex(str(s))

    return pd.read_csv(
        f'{filename}', engine='python', sep=sep, 
        header=header, skipfooter=skipfooter).map(TOcomplex).values 


def writeSimulation(dirName, infoDict, files, overwrite=False):    
    import json
    import os

    if os.path.exists(dirName) and not overwrite:
        try:
            dirName += infoDict['date']
        except KeyError:
            dirName += getDate()
        os.makedirs(dirName, exist_ok=True)
    elif not os.path.exists(dirName):
        os.makedirs(dirName, exist_ok=True)

    dirName += '/' 
    with open(dirName+'infos.json', 'w') as jsonFile:
        json.dump(infoDict, jsonFile, indent=4)

    for name, data in files.items():
        if type(data) == dict:
            np.savez(dirName+name, **data)
        elif len(data.shape) < 3: 
            np.savetxt(dirName+name, data, delimiter=',')
        elif len(data.shape) >= 3:
            np.save(dirName+name, data, allow_pickle=False)
        
            # dir3Darrayname = dirName+name
            # if not os.path.exists(dir3Darrayname): 
            #     os.mkdir(dir3Darrayname)
            # for i in range(data.shape[2]):
            #     np.savetxt(dir3Darrayname+f'/{i}.csv', data[..., i], delimiter=',')
        # else: print(f"Can't write array with shape {data.shape} into file")
    print(f'Finished writing data in {dirName} !')

def load_data(directory, type):
    import json
    csv_load = {'delimiter':',', 'dtype':complex}

    if type == 'spectral':
        # Load SCM data 
        data = {
            'k1_array': np.loadtxt(directory+'wavenumber_k1.csv', **csv_load),       
            'k2_array': np.loadtxt(directory+'wavenumber_k2.csv', **csv_load),       
            'eigvals':  np.loadtxt(directory+'eigvals.csv', **csv_load)      ,
            'eigvecs':  np.load(directory+'eigvecs.npy')      ,
        }

    if type == 'spectral_direct':
        # Load SCM data 
        data = {
            'k1_array': np.loadtxt(directory+'wavenumber_k1.csv', **csv_load),       
            'k2_array': np.loadtxt(directory+'wavenumber_k2.csv', **csv_load),       
            'eigvals':  np.loadtxt(directory+'eigvals.csv', **csv_load)      ,
            'eigvecs':  np.load(directory+'eigvecs.npy')      ,
            'refl':  np.loadtxt(directory+'refl.csv', **csv_load)      ,
        }


        with open(directory+'infos.json') as jsonFile:
            data['simuInfos'] = json.load(jsonFile)    
    
    else:
    
        data = { }
        raise NameError('Not a valid type of data to load !')

    return data


def getDate():
    from datetime import datetime
    return datetime.now().strftime('%Y%m%d_%H%M%S')



def load_yaml_as_my_dicts(material):
    import yaml
    # Import the yaml, parse it as a dict object
    with open(f'materials/{material}.yaml', 'r') as file:
        dic = yaml.safe_load(file)

    # The yaml library sucks and does not read values 
    # w/o a dot as floats it means that e.g 400e-6 is 
    # cast as a float, try to match the values when possible
    for key, val in dic.items():
        try:
            dic[key] = float(val) 
        except: pass

    # The labels used in pyPlanes differ from my routines, 
    # match those as: 
    dic['tort'] = dic['alpha']
    dic['ld']   = dic['Lambda']
    dic['ldp']  = dic['Lambda_prime']

    return dic
