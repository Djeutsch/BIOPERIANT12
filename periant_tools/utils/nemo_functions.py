# Import required packages
import numpy as np
from periant_tools.data_required import nemo_coefs_reader as ncr 


# Get dictionary of 2d plotting coeffs and ranges for nemo variables
def get_varcoeffs_circ(varname):
	list_of_dicts = ncr.NemoCoefsReader().dict_reader()
	# Make list of dict
	for line in list_of_dicts:
		if line["vname"] == varname:
			return line

# Find indice of closest grid coord to specified grid point
def find_ind(grid1d, coord):
	a = abs(grid1d-coord)
	return np.where(a == np.min(a))


def find_zind(zarray, zlev):
    if zarray.max() < -1:  # If array is negative
        zarray = -1*zarray
    a = abs(zarray-zlev)
    return np.where(a == np.min(a))
