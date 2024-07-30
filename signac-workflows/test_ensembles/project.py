"""Define the project's workflow logic and operation functions.

Execute this script directly from the command line, to view your project's
status, execute operations and submit them to a cluster. See also:

    $ python src/project.py --help
"""
import signac
from flow import FlowProject, directives
from flow.environment import DefaultSlurmEnvironment
import os


class MyProject(FlowProject):
    pass


class Borah(DefaultSlurmEnvironment):
    hostname_pattern = "borah"
    template = "borah.sh"

    @classmethod
    def add_args(cls, parser):
        parser.add_argument(
            "--partition",
            default="shortgpu",
            help="Specify the partition to submit to."
        )


class Fry(DefaultSlurmEnvironment):
    hostname_pattern = "fry"
    template = "fry.sh"

    @classmethod
    def add_args(cls, parser):
        parser.add_argument(
            "--partition",
            default="v100," "batch",
            help="Specify the partition to submit to."
        )

# Definition of project-related labels (classification)
@MyProject.label
def done(job):
    return job.doc.done


@MyProject.label
def sample_done(job):
    return job.doc.sample_done


@MyProject.post(done)
@MyProject.operation(
        directives={"ngpu": 1, "executable": "python -u"}, name="run"
)
def run(job):
    import os
    import pickle

    import hoomd
    import unyt as u

    import flowermd
    from flowermd.library import Shear

    with job:
        print("JOB ID NUMBER:")
        print(job.id)
        print("------------------------------------")
    
        gsd_path = job.fn("trajectory.gsd")
        log_path = job.fn("log.txt")
        init_gsd = os.path.join(job.project.path, job.sp.interface_file)
        ff_file = os.path.join(job.project.path, job.sp.forces_file)
        with open(ff_file, "rb") as f:
            forces = pickle.load(f)
            for force in forces:
                if isinstance(force, hoomd.md.external.wall.LJ):
                    forces.remove(force)
        refs = {
                "length": 0.3438 * u.Unit("nm"),
                "mass": 32.06 * u.Unit("amu"),
                "energy": 1.7782 * u.Unit("kJ/mol")
        }

        sim = Shear(
                initial_state=init_gsd,
                forcefield=forces,
                reference_values=refs,
                shear_axis=job.sp.shear_axis,
                shear_axis_normal=(1,0,0),
                fix_ratio=job.sp.fix_particle_ratio,
                gsd_write_freq=job.sp.gsd_write_freq,
                gsd_file_name=gsd_path,
                log_write_freq=job.sp.log_write_freq,
                log_file_name=log_path,
        )
        # Save initial config and forces for each job
        sim.pickle_forcefield(job.fn("forcefield.pickle"))
        sim.save_restart_gsd(job.fn("init.gsd"))
        # Store unit information in job doc
        tau_kT = sim.dt * job.sp.tau_kT
        job.doc.tau_kT = tau_kT
        job.doc.ref_mass = sim.reference_mass.to("amu").value
        job.doc.ref_mass_units = "amu"
        job.doc.ref_energy = sim.reference_energy.to("kJ/mol").value
        job.doc.ref_energy_units = "kJ/mol"
        job.doc.ref_length = sim.reference_length.to("nm").value
        job.doc.ref_length_units = "nm"
        job.doc.real_time_step = sim.real_timestep.to("fs").value
        job.doc.real_time_units = "fs"
        # Set up frequency and steps
        steps_per_osc = job.sp.n_steps // job.sp.n_osc 
        steps_per_shear_sim = steps_per_osc // 4
        print("Running simulation.")
        for i in range(job.sp.n_osc):
                # Positive shear
                sim.run_shear(
                        n_steps=steps_per_shear_sim,
                        shear_length=job.sp.shear_length,
                        kT=job.sp.kT,
                        tau_kT=job.doc.tau_kT,
                        period=int(job.sp.period),
                        ensemble=job.sp.ensemble
                )
                # Negative
                sim.run_shear(
                        n_steps=steps_per_shear_sim,
                        shear_length=-job.sp.shear_length,
                        kT=job.sp.kT,
                        tau_kT=job.doc.tau_kT,
                        period=int(job.sp.period),
                        ensemble=job.sp.ensemble
                )
                # Negative 
                sim.run_shear(
                        n_steps=steps_per_shear_sim,
                        shear_length=-job.sp.shear_length,
                        kT=job.sp.kT,
                        tau_kT=job.doc.tau_kT,
                        period=int(job.sp.period),
                        ensemble=job.sp.ensemble
                )
                # Positive
                sim.run_shear(
                        n_steps=steps_per_shear_sim,
                        shear_length=job.sp.shear_length,
                        kT=job.sp.kT,
                        tau_kT=job.doc.tau_kT,
                        period=int(job.sp.period),
                        ensemble=job.sp.ensemble
                )
        # Save a restart GSD for resuming and running longer
        sim.save_restart_gsd(job.fn("restart.gsd"))
        job.doc.done = True
        print("Simulation finished.")


@MyProject.pre(done)
@MyProject.post(sample_done)
@MyProject.operation(
        directives={"ngpu": 0, "executable": "python -u"}, name="sample"
)
def sample(job):
    # Add package imports here
    with job:
        print("JOB ID NUMBER:")
        print(job.id)
        print("------------------------------------")
        # Add your script here
        job.doc.sample_done = True


if __name__ == "__main__":
    MyProject(environment=Fry).main()
