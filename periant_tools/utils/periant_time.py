from periant_tools.utils import nemo_functions as nf
import pandas as pd
import xarray as xr
import numpy as np
from typing import Tuple, List

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def get_days_of_month(month: int, time_step: str = "1-daily") -> List[int]:
    """
    Get the BIOPERIANT12 out days of a given month according to the time step of the model outputs.
    Args:
        month (int): month number of interest (1, 2, ..., 12)
        time_step (str, optional): time step of the model outputs. Defaults to "1-daily".

    Raises:
        TypeError: if month number is out of range
        TypeError: if time step is not one of the known BIOPERIANT12 model output steps. 

    Returns:
        List[int]: list of the model output days of the given month.
    """
    # logger.info(" Get the output days corresponding to the provided month")
    if month not in range(1, 12+1):
        error = f"Ouuf, sorry! You provided {month=} which is out of month range [1, 2, ..., 12]"
        raise TypeError(error)

    if time_step == "1-daily":
        if month in [1, 3, 5, 7, 8, 10, 12]:
            days = range(1, 31+1)
        elif month in [2]:
            days = range(1, 28+1)
        elif month in [4, 6, 9, 11]:
            days = range(1, 30+1)
        return list(days)
    elif time_step == "5-daily":
        if month in [1, 4, 5]:
            days = [5, 10, 15, 20, 25, 30]
        elif month in [2]:
            days = [4, 9, 14, 19, 24]
        elif month in [3, 12]:
            days = [1, 6, 11, 16, 21, 26, 31]
        elif month in [6, 7]:
            days = [4, 9, 14, 19, 24, 29]
        elif month in [8]:
            days = [3, 8, 13, 18, 23, 28]
        elif month in [9, 10]:
            days = [2, 7, 12, 17, 22, 27]
        elif month in [11]:
            days = [1, 6, 11, 16, 21, 26]
        return days
    else:
        error = f"Sorry! So far, BIOPERIANT12 only has 1-daily and 5-daily outputs."
        raise TypeError(error)


def make_time_axis(year_start: int, year_end: int, time_step: str) -> List[pd.Timestamp]:
    """
    Making the time axis corresponding to the provided date range and model output time step.
    Args:
        year_start (int): starting year of interest.
        year_end (int): ending year of interest.
        time_step (str): time step of the model outputs.

    Returns:
        List[pd.Timestamp]: list of date stamps corresponding to the provided date range and
        model output time step.
    """
    logger.info(" Making the time axis corresponding to the provided date range")
    dates = []
    for year in range(year_start, year_end + 1):
        for month in range(1, 13):
            days = get_days_of_month(month, time_step)
            for day in days:
                dates.append(pd.Timestamp(
                    ts_input=year, freq=month, tz=day, unit=12))

    return dates


def make_year_month_day_string(year: int, time_step: str) -> List[str]:
    """
    Make a BIOPERIANT12 file date-like based on the year, month, day and model output time step
    of interest.
    Args:
        year (int): year of interest.
        time_step (str): time step of the model outputs.

    Returns:
        List[str]: list of BIOPERIANT12 file date string based on year, month and day.
    """
    dates_string = []
    for month in range(1, 12+1):
        mm = str(month).zfill(2)
        days = get_days_of_month(month, time_step)
        for day in days:
            dd = str(day).zfill(2)
            yr_mm_dd_str = "y" + str(year) + "m" + mm + "d" + dd
            dates_string.append(yr_mm_dd_str)

    return dates_string


def get_var_scaling_params(var_name: str, suff: int = 0) -> Tuple[float]:
    """
    Get the scaling coefficient and range of a BIOPERIANT12 output variable.
    Args:
        var_name (str): name of the variable of interest.
        suff (int, optional): suffix of the scaling coefficient. Defaults to 0. It can be 0, 50, 100

    Returns:
        Tuple[float]: scaling coefficient/factor, min, max and step.
    """
    suff = str(suff)

    if nf.get_varcoeffs_circ(var_name):
        # Coefficients
        coef = float(nf.get_varcoeffs_circ(var_name)["scale"])

        # Ranges
        cmin = float(nf.get_varcoeffs_circ(var_name)["min"+suff])
        cmax = float(nf.get_varcoeffs_circ(var_name)["max"+suff])
        cstp = float(nf.get_varcoeffs_circ(var_name)["step"+suff])

        return coef, cmin, cmax, cstp


def rescale_vars_data(xds: xr.Dataset) -> xr.Dataset:
    """
    Rescale the data of all the variables in the dataset
    Args:
        xds (xr.Dataset): an xarray dataset.

    Returns:
        xr.Dataset: the rescaled data as a xarray dataset
    """
    logger.info(" Rescale the data of the variables of interest:\n")
    for var_name in list(xds.data_vars):
        print(f" {var_name}: ", end=" ")
        if get_var_scaling_params(var_name):
            # Get the coefficient
            Coef, Cmin, Cmax, Cstep = get_var_scaling_params(var_name)
            # Rescale the data
            xda_adj = xds[var_name].copy()
            xda_adj.data = Coef*xda_adj.data
            mask_limit = (xda_adj>=Cmin) & (xda_adj<=Cmax)
            xds[var_name].data = xda_adj.where(mask_limit).data
            
            print(f"{Coef = }, {Cmin = }, {Cmax = }, and {Cstep = }", end="\n")

    return xds


def get_fronts_position(xda: xr.DataArray,
                        min_value: float,
                        max_value: float,
                        xlon2d: np.ndarray = None,
                        ylat2d: np.ndarray = None) -> xr.DataArray:
    # Set the criteria mask and apply to the data
    criteria_mask = (xda > min_value) & (xda < max_value)
    xda_mask  = xda.where(criteria_mask)
    
    # Get front positions by convert to mask where 1 fits the criteria domain
    front_positions = (xda_mask / xda_mask) * ylat2d
    
    
    
    
    
    np.meshgrid()