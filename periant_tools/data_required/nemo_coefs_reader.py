# Import required packages
import csv

class NemoCoefsReader():
    """
    Get dictionary of 2d plotting coefficients and ranges for NEMO variables
    """
    def dict_reader(self):
        """
         Read as dictionary the coefficients and ranges for NEMO variables
        Returns:
            _type_: list of dictionaries of coefficients and ranges of NEMO variables
        """
        return csv.DictReader(open("nemo_output_coeffs_periant.csv", mode="r"))
