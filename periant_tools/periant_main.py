import periant_tools.utils.periant_time as periant_time
import os
import pandas as pd
import xarray as xr
import netCDF4 as nc4
from typing import List, Tuple

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


class BP12DataLoader():

    def __init__(self, suffix_endwith: str = "diadT.nc", year_start: int = 2008,
                 year_end: int = 2008, time_step: str = "1-daily", flag: bool = True) -> None:
        """_summary_

        Args:
            suffix_endwith (str, optional): _description_. Defaults to "diadT.nc".
            year_start (int, optional): _description_. Defaults to 2008.
            year_end (int, optional): _description_. Defaults to 2008.
            time_step (str, optional): _description_. Defaults to "1-daily".
            flag (bool, optional): _description_. Defaults to True.

        Raises:
            TypeError: _description_
        """
        logger.info(" BIOPERIANT12 data loader instantiation")
        self.suffix_endwith = suffix_endwith
        self.year_start = year_start
        self.year_end = year_end
        self.time_step = time_step
        if time_step in ["1-daily"]:
            self.input_dir: str = "/mnt/nrestore/users/ERTH0834/BIOPERIANT12/BIOPERIANT12-CNCRUN05A-S"
            self.prefix: str = "BIOPERIANT12-CNCRUN05A"
        elif time_step in ["5-daily"]:
            self.input_dir: str = "/mnt/nrestore/users/ERTH0834/BIOPERIANT12/BIOPERIANT12-CNCLNG01-S"
            self.prefix: str = "BIOPERIANT12-CNCLNG01"
        else:
            error = f"Sorry! So far, BIOPERIANT12 only has 1-daily and 5-daily outputs."
            raise TypeError(error)
        self.flag = flag
    
    def __repr__(self):
        return f"<BP12DataLoader for {self.time_step} outputs from {self.year_start} to {self.year_end}>"

    def find_files(self) -> Tuple[list, list]:
        """
        This function find the files to be read from the input directory.
        
        Returns:
            tuple[list, list]: a list of correct files found and a list of missing ones.
        """
        logger.info(
            " Find the file names to be read from the input directory\n")
        # Get filenames
        filenames = []
        for year in range(self.year_start, self.year_end + 1):
            bp12_dates = periant_time.make_year_month_day_string(
                year=year, time_step=self.time_step)
            for day in bp12_dates:
                filename = self.input_dir + \
                    f"/{str(year)}/{self.prefix}_{day}_{self.suffix_endwith}"
                filenames.append(filename)

        # Remove missing file names from filenames
        missingfiles = []
        for _ in range(3):
            for filename in filenames:
                if not os.path.isfile(filename):
                    filenames.remove(filename)
                    missingfiles.append(filename)

        if self.flag:
            logger.info(
                f" {len(filenames)} files found and {len(missingfiles)} file(s) missing!")

        return filenames, missingfiles
    
    def load(self, in_parallel: bool = False) -> Tuple[xr.Dataset, list, list]:
        """
        Load at once all the datasets corresponding to the provided features and directory.

        Args:
            in_parallel (bool, optional): If True, the open and preprocess steps will be performed in parallel using ``dask.delayed``. Defaults to False.

        Returns:
            Tuple[xr.Dataset, list, list]: _description_
        """
        # Get the data datestamp and clean up for missing files
        logger.info(" Load all the datasets at once")
        filenames, missingfiles = self.find_files()  # Get the file names

        # Get the date stamp data or time axis
        time_axis = periant_time.make_time_axis(year_start=self.year_start,
                                         year_end=self.year_end,
                                         time_step=self.time_step)

        if len(missingfiles) != 0:
            logger.warn(" The following file names could not be opened:\n")
            for file in missingfiles:
                print(f" {file.split(self.input_dir)[-1]}")

        # Load all the datasets at once
        if in_parallel:
            xds = xr.open_mfdataset(paths=filenames, decode_times=False,
                                    concat_dim="time_counter",
                                    parallel=in_parallel)
        else:
            xds = xr.open_mfdataset(paths=filenames, decode_times=False,
                                    concat_dim="time_counter",
                                    chunks={"y": 500, "x": 1000})

        return xds, missingfiles, time_axis


class BP12DataProcessor():
    mpath = "/mnt/lustre/groups/erth0834/lustre3p/MODELS/BIOPERIANT12/BIOPERIANT12-I/PERIANT12_mask.nc"

    def __init__(self, path_to_ocean_mask: str = mpath) -> None:
        """
        This is the BIOPERIANT12 data processor module.
        Args:
            path_to_ocean_mask (str): the path to the ocean mask of BIOPERIANT12 data.
        """
        self.path_to_ocean_mask = path_to_ocean_mask
        logger.info(" BIOPERIANT12 data processor instantiation")
        if os.path.isfile(self.path_to_ocean_mask):
            with nc4.Dataset(self.path_to_ocean_mask) as nc_data:
                self.lon2d = nc_data.variables['nav_lon'][:].copy()
                self.lat2d = nc_data.variables['nav_lat'][:].copy()
                self.tmask = nc_data.variables['tmask'][0, :].copy()
        else:
            error = f"The ocean mask file doesn't exist. Maybe also check whether the following path you provided exist.\n\n{self.path_to_ocean_mask}"
            raise TypeError(error)
            
    def __repr__(self):
        return f"<BP12DataProcessor is using ocean mask from \n {self.path_to_ocean_mask}>"

    def refine_coords(self, xdata_array: xr.DataArray) -> xr.DataArray:
        """
        Apply the ocean mask to the provided BIOPERIANT12 model data variable,
        update the dimenssions & coordinates.

        Args:
            xdata_array (xr.DataArray): _description_

        Returns:
            xr.DataArray: _description_
        """
        logger.info(" Coordinates conversion")
        if len(xdata_array.shape) >= 4:
            # ocean mask at zlevel > 0
            xda = xdata_array[:].where(self.tmask[:] == 1)
            xda = xda.rename({"deptht": "depth"})
        else:
            # ocean mask at zlevel = 0
            xda = xdata_array[:].where(self.tmask[0, :] == 1)

        # Update the values of x/lon and y/lat coordinates
        xda.assign_coords(x=self.lon2d[0, :], y=self.lat2d[:, 0])
        xda["x"] = self.lon2d[0, :]
        xda["y"] = self.lat2d[:, 0]

        # Rename the dimensions and sort the data according to their coordinates
        if len(xda.shape) >= 3:
            xda = xda.rename({"time_counter": "time", "y": "lat", "x": "lon"})
            xda = xda.isel(time=xda.indexes["time"].argsort(),
                           lat=xda.indexes["lat"].argsort(),
                           lon=xda.indexes["lon"].argsort())
        else:
            xda = xda.rename({"y": "lat", "x": "lon"})
            xda = xda.isel(lat=xda.indexes["lat"].argsort(),
                           lon=xda.indexes["lon"].argsort())
        return xda

    def process(self, xds_params: Tuple[xr.Dataset, list, list], var_names: List[str]) -> xr.Dataset:
        """
        Extract the variables of interest of BIOPERIANT12 model data and apply the ocean mask;
        update the dimenssions & coordinates, and rescale the data of extracted variables.
        Args:
            xds_params (Tuple[xr.Dataset, list, list]): _description_
            var_names (List[str]): _description_

        Returns:
            xr.Dataset: _description_
        """
        logger.info(" Data processing")
        xds = xds_params[0]
        missing_files = xds_params[1]
        time_axis = xds_params[2]
        list_processed_xdas = []
        for var_name in var_names:
            xda_processed = self.refine_coords(xds[var_name])
            # Append to the list of processed data
            list_processed_xdas.append(xda_processed)

        # Merge the list of processed data
        processed_xds = xr.merge(list_processed_xdas)

        # Clean up for missing files
        for filename in missing_files:
            date_string = filename[filename.find("_y")+1:filename.find("_y")+12]
            date_stamp = pd.Timestamp(ts_input=int(date_string[1:5]),
                                      freq=int(date_string[6:8]),
                                      tz=int(date_string[9:11]), unit=12)
            time_axis.remove(date_stamp)

        # Update the values of the time coordinate
        processed_xds["time"] = time_axis

        # Rescale the data of the variables
        processed_xds = periant_time.rescale_vars_data(processed_xds)
        processed_xds = processed_xds.chunk({"time": 100, "lat": 500, "lon": 1000})
        processed_xds.attrs = {"Conventions": "GDT 1.3",
                               "production": "NEMO",
                               "output_frequency": "5d",
                               "CONFIG": "BIOPERIANT12",
                               "CASE": "CNCLNG01"}

        return processed_xds
