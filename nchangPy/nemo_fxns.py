# get dictionary of 2d plotting coeffs and ranges for nemo variables
def get_varcoeffs(varname):
	import csv

	fname = csv.DictReader(open(
		"/home/ldjeutchouang/CODE/pyscripts/base/nicoPy/nemo_output_coeffs.csv", "r"))
	# make list of dict
	for line in fname:
		if line["vname"] == varname:
			return line


def get_varcoeffs_circ(varname):
	import csv

	fname = csv.DictReader(open(
		"/home/ldjeutchouang/CODE/pyscripts/base/nicoPy/nemo_output_coeffs_bp12.csv", "r"))
	# make list of dict
	for line in fname:
		if line["vname"] == varname:
			return line

# find indice of closest grid coord to specified grid point


def find_ind(grid1d, coord):
	import numpy as np
	a = abs(grid1d-coord)
	return np.where(a == np.min(a))


def find_zind(zarray, zlev):
    import numpy as np
    if zarray.max() < -1:  # if array is negative
        zarray = -1*zarray
    a = abs(zarray-zlev)
    return np.where(a == np.min(a))
