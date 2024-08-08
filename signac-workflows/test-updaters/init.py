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
    parameters["ensemble"] = [
        "NVT",
        #"NVE"
    ]
    parameters["kT"] = [4.0]
    parameters["tau_kT"] = [100]
    parameters["n_steps"] = [5e6]
    parameters["n_osc"] = [10]
    parameters["period"] = [1000]
    parameters["dt"] = [0.0001]
    parameters["displacement"] = [
        4.0,
        #5.0,
        #6.0,
        #7.0,
        #8.0,
        #9.0,
        #10.0,
        #12.0,
        #14.0,
    ]
    parameters["shear_axis"] = [[(0,1,0)]]
    parameters["fix_particle_ratio"] = [0.05]
    parameters["gsd_write_freq"] = [5e3]
    parameters["log_write_freq"] = [1e3]
    parameters["interface_file"] = ["interface.gsd"]
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
        job.doc.setdefault("tensile_done", False)
        job.doc.setdefault("shear_done", False)
        job.doc.setdefault("sample_done", False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
