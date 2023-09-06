# **BIOPERIANT12**
A module to load internally and preprocess the BIOPERIANT12 mesoscale-resolving ocean model outputs from SOCCO data server hosted by the CHPC `lengau` cluster.

***Important:*** *This module is still at its early development stage.*


## **Quickstart**
We have a series of tutorials on Jupyter notebooks in the notebooks folder. We recommend reading them in the following order to see a typical workflow. First install the main required packages as follows: `pip install -r requirements.txt`.

### Data loading
1. Import the BIOPERIANT12 module:
```python
import bioperiant_main as mbp
```
2. Assign the data loader attributes and call it:
```python
suffix_endwith = "diadT.nc"
year_start = 1991
year_end = 2010
time_step = "5-daily"

bp12_diadT = mbp.BP12DataLoader(suffix_endwith=suffix_endwith,
                                 year_start=year_start,
                                 year_end=year_end,
                                 time_step=time_step)
```
3. Load the data corresponding to the assigned attrbutes:
```python
xds_diadT = bp12_diadT.load()
```

### Data pre-processing
4. Assign the data loader attributes and call it:
```python
ocean_mask_path = "../ocean_mask.nc" # A netCDF file (.nc format)
bp12_processor = mbp.BP12DataProcessor(path_to_ocean_mask=ocean_mask_path)
```
5. Pre-process the variables of interest:
```python
var_names = [var1, var2, ...] # Variables of interest
xds_diadT = bp12_processor.process(xds_params=xds_diadT,
                                   var_names=var_names)
```

### Data visualization
