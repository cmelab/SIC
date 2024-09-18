import flowermd
import hoomd
import gsd
import numpy as np
import freud


def nematic_order(gsd_file):
    # Starting timer to see how long this process takes
    start = time.process_time()
    s2_orders = []
    count = 0
    traj = gsd.hoomd.open(gsd_file)
    nematic = freud.order.Nematic()
    # Iterate through every frame in the trajectory
    for frame in traj:
        # Get the positional data of all atoms
        positions = frame.particles.position
        # Get the number of molecules
        molecule_ids = frame.bonds.group
        # Assigning the first atoms position to temp variable
        temp = positions[0]
        # Initialize list of vectors
        vectors = []
        # Loop through all atoms with counter i
        for i, pos in enumerate(positions):
            # Check to see if all atoms have been counted
            if i < len(molecule_ids):
                # Addding the vector difference between current and previous atom positions
                vectors.append(np.stack(pos) - np.stack(temp))
                # Updating temp variable for the next cycle
                temp = pos
                # Converting the list into an array, ignoring the first one
        vectors = np.array(vectors[1:])
        # Computing the S2 order parameter based off of the nop function of the frame
        nematic.compute(vectors)
        # Appending the order of the frame for plotting purposes
        s2_orders.append(nematic.order)
    return(s2_orders)
