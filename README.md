# **BIOPERIANT12**

A library of Python modules for processing and analysing outputs from various simulations of the BIOPERIANT ocean model developed by Dr. Nicolette Chang from SOCCO. BIOPERIANT12 is a mesoscale-resolving ocean model whose simulations results in a series of experiments to address science questions formulated by the Southern Ocean Carbon – Climate Observatory (SOCCO), a research program within the Holistic Climate Change division, Smart Places, of the Council for Scientific and Industrial Research (CSIR)."

***Important:*** *This Python project is still at its early development stage and is being populated as new processing and analysis tools are developed.*

The package is currently loaded internally for preprocessing the BIOPERIANT12 model outputs from SOCCO data server hosted by `lengau` cluster, at the Centre for High-Performance Computing (CHPC).

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
