import flowermd
import hoomd
import gsd
import numpy as np
import freud


def nematic_order(gsd_file):

    nm_orders = []
    with gsd.hoomd.open(gsd_file) as traj: #opening gsd file as traj
        for snap in traj: #looping through each frame
            bond_vectors = []
            nematic = freud.order.Nematic() 
            for bond in snap.bonds.group: #looping through each bond in frame
                pos2 = snap.particles.position[bond[1]]
                pos1 = snap.particles.position[bond[0]]
                vec = pos2 - pos1
                bond_vectors.append(vec)
            nematic.compute(np.array(bond_vectors))#computing nematic order for each frame
            nm_orders.append(nematic.order)

    return(nm_orders)
