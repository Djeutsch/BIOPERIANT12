import utils
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
            bp12_dates = utils.make_year_month_day_string(
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

    def load(self) -> Tuple[xr.Dataset, list, list]:
        """
        Load at once all the datasets corresponding to the provided features and directory.
        Returns:
            Tuple[xr.Dataset, list, list]: _description_
        """
        # Get the data datestamp and clean up for missing files
        logger.info(" Load all the datasets at once")
        filenames, missingfiles = self.find_files()  # Get the file names

        # Get the date stamp data or time axis
        time_axis = utils.make_time_axis(year_start=self.year_start,
                                         year_end=self.year_end,
                                         time_step=self.time_step)

        if len(missingfiles) != 0:
            logger.warn(" The following file names could not be opened:\n")
            for file in missingfiles:
                print(f" {file.split(self.input_dir)[-1]}")

        # Load all the datasets at once
        xds = xr.open_mfdataset(paths=filenames, decode_times=False,
                                concat_dim="time_counter",
                                chunks={"y": 500, "x": 1000})

        return xds, missingfiles, time_axis


class BP12DataProcessor():
    def __init__(self, bp12_ocean_mask_path: str) -> None:
        """
        This is the BIOPERIANT12 data processor module.
        Args:
            bp12_ocean_mask_path (str): the path to the ocean mask of BIOPERIANT12 data.
        """
        self.bp12_ocean_mask_path = bp12_ocean_mask_path
        logger.info(" BIOPERIANT12 data processor instantiation")
        with nc4.Dataset(self.bp12_ocean_mask_path) as nc_data:
            self.lon2d = nc_data.variables['nav_lon'][:, 2:].copy()
            self.lat2d = nc_data.variables['nav_lat'][:, 2:].copy()
            self.tmask = nc_data.variables['tmask'][0, :, :, 2:].copy()
            
    def __repr__(self):
        return f"<BP12DataProcessor using the ocean mask @\n {self.bp12_ocean_mask_path}>"

    def process(self, xds_params: Tuple[xr.Dataset, list, list], var_names: List[str],
                var_names_with_profile: List[str] = [None]) -> xr.Dataset:
        """
        Extract the variables of interest of BIOPERIANT12 model data and apply the ocean mask;
        update the dimenssions & coordinates, and rescale the data of extracted variables.
        Args:
            xds_params (Tuple[xr.Dataset, list, list]): _description_
            var_names (List[str]): _description_
            var_names_with_profile (List[str], optional): _description_. Defaults to [None].

        Returns:
            xr.Dataset: _description_
        """
        logger.info(" Data processing")
        xds = xds_params[0]
        missing_files = xds_params[1]
        time_axis = xds_params[2]
        list_processed_xdas = []
        for var_name in var_names:
            if var_name in var_names_with_profile:
                xda_processed = xds[var_name][:, 0, :, 2:].where(self.tmask[0, :] == 1)
                xda_processed = xda_processed.drop(["deptht"])
            else:
                xda_processed = xds[var_name][:, :, 2:].where(self.tmask[0, :] == 1)

            # Update the values of x/lon and y/lat coordinates
            xda_processed.assign_coords(x=self.lon2d[0, :], y=self.lat2d[:, 0])
            xda_processed["x"] = self.lon2d[0, :]
            xda_processed["y"] = self.lat2d[:, 0]

            # Rename the dimensions and sort the data according to their coordinates
            xda_processed = xda_processed.rename({"time_counter": "time", "y": "lat", "x": "lon"})
            xda_processed = xda_processed.isel(time=xda_processed.indexes["time"].argsort(),
                                               lat=xda_processed.indexes["lat"].argsort(),
                                               lon=xda_processed.indexes["lon"].argsort())

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
        processed_xds = utils.rescale_vars_data(processed_xds)
        processed_xds = processed_xds.chunk({"time": 100, "lat": 500, "lon": 1000})
        processed_xds.attrs = {"Conventions": "GDT 1.3",
                               "production": "NEMO",
                               "output_frequency": "5d",
                               "CONFIG": "BIOPERIANT12",
                               "CASE": "CNCLNG01"}

        return processed_xds
