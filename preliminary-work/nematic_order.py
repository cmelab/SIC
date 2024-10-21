import flowermd
import hoomd
import gsd
import numpy as np
import freud
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import time


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
    with gsd.hoomd.open(gsd_file) as traj: # Opening gsd file as traj
        for snap in traj[start:stop:stride]: # Looping through each frame
            bond_vectors = []
            nematic = freud.order.Nematic()
            for bond in snap.bonds.group: # Looping through each bond in frame
                pos2 = snap.particles.position[bond[1]]
                pos1 = snap.particles.position[bond[0]]
                vec = pos2 - pos1
                bond_vectors.append(vec)      
            nematic.compute(np.array(bond_vectors))# Computing nematic order for each frame
            nm_orders.append(nematic.order)
            directors.append(nematic.director)
    return(nm_orders,directors)

def get_frames(gsd_file, start=0, stop=None, stride=1):
    """
    Returns the orientations and positions of bonds for a GSD coarse-grained system.
    
    Parameters
    ----------
    gsdfile : str
        Filename for gsd file
    frame_num : int, default 0
        The frame of a gsd trajectory that you want to access.
    start : int, default 0
        Where to start reading the gsd trajectory the system was created
        with.
    stop : int, default None
        Where to stop reading the gsd trajectory the system was created
        with. If None, will stop at the last frame.
    stride : int, default 1
        The step size to use when iterating through start:stop
    """
    frames = []
    with gsd.hoomd.open(gsd_file) as traj: # Opening gsd file as traj
        for snap in traj[start:stop:stride]: # Looping through each frame
            bonds = snap.bonds.group
            pos = snap.particles.position
            positions = np.zeros((len(snap.bonds.group), 3))  # Assigning array size depending on bond size
            vecs = np.zeros((len(snap.bonds.group), 3))
            for i, bond in enumerate(bonds): # Looping through each bond in frame
                positions[i] = pos[bond[0]]  # Assign position directly to avoid appending to a list
                vecs[i] = pos[bond[1]] - pos[bond[0]]
            frame = np.column_stack((positions, vecs)) # Stacking positions and vectors into an array for one frame
            frames.append(frame) # Appending each frame to a list of frames
    return frames

def color_map(directors, frames, frame_num=0):
    """
    Colors the orientations of bond vectors for a GSD coarse-grained system depending on alignment with nematic director.
    
    Parameters
    ----------
    directors : list
        A list of director vectors as returned by the nematic_order function.
    frames : list
        A list of frames as returned by the get_frames function.
    frame_num : int, default 0
        The frame of the list of frames that you want to access.
    """
    frame = frames[frame_num]
    director = directors[frame_num]
    positions = frame[:, 0:3]
    vectors = frame[:, 3:]
    temp_vecs = np.copy(vectors)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    misalignments = []
    for i in range(len(frame)): # Calculating the difference between the bond vector and the nematic director for the frame
        if np.dot(vectors[i], director) < 0:
            temp_vecs[i] = -vectors[i]
        misalignment = (np.arccos(np.clip(np.dot(temp_vecs[i], director) /
        (np.linalg.norm(temp_vecs[i]) * np.linalg.norm(director)), -1.0, 1.0)))
        misalignments.append(misalignment)
    if len(misalignments) != 0: # Checking to see if there are any misalignments as perfectly crystalline systems won't have misalignments
        norm_misalignments = (np.array(misalignments) - np.min(misalignments)) / (np.max(misalignments) - np.min(misalignments)) # Normalizing
        colors = cm.magma_r(norm_misalignments) # Setting the colormap
        for i in range(len(frame)):
            ax.quiver(*positions[i], *vectors[i], color=colors[i], length=1) # Unpacking and plotting positions and vectors for each bond
    else:
        print("All of the bonds in this frame are aligned with the nematic director. The nematic order is 1.")
    
    
