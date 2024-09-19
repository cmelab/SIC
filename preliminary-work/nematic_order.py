import flowermd
import hoomd
import gsd
import numpy as np
import freud


def nematic_order(gsd_file, start=0, stop=None, stride=1):
    """
    Calculate nematic order for a coarse-grained system by calculating bond vectors for each bond between two beads.
    
    Parameters
    ----------
    gsdfile : str
        Filename for gsd file
    start : int, default 0
        Where to start reading the gsd trajectory the system was created
        with.
    stop : int, default None
        Where to stop reading the gsd trajectory the system was created
        with. If None, will stop at the last frame.
    stride : int, default 1
        The step size to use when iterating through start:stop
    """
    nm_orders = []
    directors = []
    with gsd.hoomd.open(gsd_file) as traj: #opening gsd file as traj
        for snap in traj[start:stop:stride]: #looping through each frame
            bond_vectors = []
            nematic = freud.order.Nematic()
            for bond in snap.bonds.group: #looping through each bond in frame
                pos2 = snap.particles.position[bond[1]]
                pos1 = snap.particles.position[bond[0]]
                vec = pos2 - pos1
                bond_vectors.append(vec)
            nematic.compute(np.array(bond_vectors))#computing nematic order for each frame
            nm_orders.append(nematic.order)
            directors.append(nematic.director)
    
    return(nm_orders,directors)

