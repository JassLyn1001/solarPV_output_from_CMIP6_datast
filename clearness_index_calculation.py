import xarray as xr
import cftime
import numpy as np
from scipy import stats
import os, sys
import seaborn as sns
import glob
import pandas as pd
from pathlib import Path
import fnmatch

# Read in data
# Define pathfile
datapath = "/root/master_thesis_proj/data/CMIP6/"
modelsname = ['MIROC6','MPI-ESM1-2-LR','MPI-ESM-1-2-HAM','AWI-ESM-1-1-LR',
              'MPI-ESM1-2-HR','CMCC-CM2-SR5','CMCC-CM2-HR4','CMCC-ESM2',
              'AWI-ESM-1-REcoM'] # list of CMIP6 models that available

# Create a function to read in netcdf files using xarray 
def read_mfiles(filespath):
    with xr.open_mfdataset(filespath, chunks={
        "lat": 1000, "lon": 2000, "time": 5000}) as ds:
        print(ds.keys())
    return ds # return xarray's dataset

# Define a function to get files in input directory
def search_files(dirpath, model): # varname might be both rsds and rsdt
    file_list = []
    for file_name in os.listdir(dirpath):
        if fnmatch.fnmatch(file_name, f'*_{model}_*.nc'): 
            file_list.append(file_name)
    return file_list
    

# Loop through all models directory
for model in modelsname:
    print(f'Working on model: {model}')
    # Get a list of all files from MIROC6 model
    rsds_list = search_files(datapath+'rsds/historical/',model)
    rsds_list.sort()
    
    rsdt_list = search_files(datapath+'rsdt/historical/',model)
    rsdt_list.sort()
    
    # Check if the files exist, if True than continue to calculate clearness index
    if len(rsds_list)!=0 and len(rsdt_list)!= 0:
        rsds_ds = read_mfiles(glob.glob(datapath+f'rsds/historical/*_{model}_*.nc'))
        rsdt_ds = read_mfiles(glob.glob(datapath+f'rsdt/historical/*_{model}_*.nc'))
        clearness_idx = rsds_ds.rsds / rsdt_ds.rsdt
        # To ignore error such as "divide by zero" or "divide by NaN", let's handle them using numpy.seterr()
        np.seterr(divide='ignore', invalid='ignore') #
        clearness_idx.compute()
        
        # Convert to xarray dataset
        clearness_idx_ds = clearness_idx.to_dataset(dim=None, name='clearness_index')
        
        # Create a new filename for output
        fname_list = rsdt_list[0].split('_')
        fname_list[0] = 'clearness_index'
        startdate = fname_list[-1].split('.')[0].split('-')[0]
        enddate = '20141231'
        fname_list[-1] = startdate+'-'+enddate
        fname = '_'.join(fname_list)
        
        # Save bias-corrected data into a new netcdf file
        out_dir = "/root/master_thesis_proj/data/CMIP6/clearness_index/historical/"
        clearness_idx_ds.to_netcdf(
            out_dir+fname+'.nc',
            format = "NETCDF4",
            engine ="netcdf4",
            encoding= {"clearness_index": {"dtype": "float32"}},
            unlimited_dims='time')
    else:
        print(f'Data for {model} is not available')
    
