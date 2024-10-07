import flowermd
import hoomd
import gsd
import numpy as np
import freud
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm


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

def graph_bonds(gsd_file, start=0, stop=None, stride=1):
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
    frames = [[]]
    with gsd.hoomd.open(gsd_file) as traj: # Opening gsd file as traj
        for snap in traj[start:stop:stride]: # Looping through each frame
            frame = []
            vectors = []
            positions = []
            nematic = freud.order.Nematic()
            for bond in snap.bonds.group: # Looping through each bond in frame
                pos2 = snap.particles.position[bond[1]]
                pos1 = snap.particles.position[bond[0]]
                vec = pos2 - pos1
                vectors.append(vec)
                positions.append(pos1)
                frame.append([[pos1,vec]]) # Appending the positions and vectors of each bond to the frame
            frames.append(frame) # Appending this frame to a list of frames
    return(frames)

def color_map(gsd_file, frame_num=0):
    """
    Colors the orientations of bond vectors for a GSD coarse-grained system depending on alignment with nematic director.
    
    Parameters
    ----------
    gsdfile : str
        Filename for gsd file
    frame_num : int, default 0
        The frame of a gsd trajectory that you want to access.
    """
    orders,directors = nematic_order(gsd_file) # Obtaining director vectors to compare against
    frames = graph_bonds(gsd_file)
    vectors = []
    positions = []
    frame = frames[frame_num]
    director = directors[frame_num]
    for i in range(len(frame)): # Getting the position and vectors of each bond in the specified frame
        vectors.append(frame[i][0][1])
        positions.append(frame[i][0][0])
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    misalignments = []
    for i in range(len(frame)): # Calculating the difference between the bond vector and the nematic director for the frame
        misalignment = np.arccos(np.clip(np.dot(vectors[i], director) / (np.linalg.norm(vectors[i]) * np.linalg.norm(director)), -1.0, 1.0))
        misalignments.append(misalignment)
    if len(misalignments) != 0:
        norm_misalignments = (np.array(misalignments) - np.min(misalignments)) / (np.max(misalignments) - np.min(misalignments)) # Normalizing
        colors = cm.magma(norm_misalignments) # Setting the colormap
        for i in range(len(frame)): # Plotting
            ax.quiver(positions[i][0],
                      positions[i][1],
                      positions[i][2],
                      vectors[i][0],
                      vectors[i][1],
                      vectors[i][2],
                      color=colors[i], length=1)
    else:
        print("All of the bonds in this frame are aligned with the nematic director. The nematic order is 1.")
    
    
