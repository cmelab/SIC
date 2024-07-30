#!/usr/bin/env python
"""Initialize the project's data space.

Iterates over all defined state points and initializes
the associated job workspace directories.
The result of running this file is the creation of a signac workspace:
    - signac.rc file containing the project name
    - signac_statepoints.json summary for the entire workspace
    - workspace/ directory that contains a sub-directory of every individual statepoint
    - signac_statepoints.json within each individual statepoint sub-directory.

"""

import signac
import flow
import logging
from collections import OrderedDict
from itertools import product


def get_parameters():
    ''''''
    parameters = OrderedDict()
    # Define some simulation related parameters:
    parameters["ensemble"] = ["NVT", "NVE"]
    parameters["kT"] = [3.0]
    parameters["n_steps"] = [1e7]
    parameters["n_osc"] = [1000]
    parameters["period"] = [1e4]
    parameters["shear_length"] = [2.0] # TODO Figure out interface size
    parameters["fix_particle_ratio"] = [0.05]
    parameters["gsd_write_freq"] = [1e4]
    parameters["log_write_freq"] = [1e3]
    parameters["interfac_file"] = ["interface.gsd"]
    parameters["forces_file"] = ["forcefield.pickle"]
    return list(parameters.keys()), list(product(*parameters.values()))


def main():
    project = signac.init_project() # Set the signac project name
    param_names, param_combinations = get_parameters()
    # Create the generate jobs
    for params in param_combinations:
        statepoint = dict(zip(param_names, params))
        job = project.open_job(statepoint)
        job.init()
        job.doc.setdefault("nvt_done", False)
        job.doc.setdefault("sample_done", False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
