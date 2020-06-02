import btrack

import numpy as np

from matplotlib.cm import get_cmap
from matplotlib.colors import ListedColormap




# state colors are grey, blue, green, magenta, red
STATE_COLORMAP = np.array([[0.5,0.5,0.5,1.0],
                           [0.0,0.0,1.0,1.0],
                           [0.0,1.0,0.0,1.0],
                           [1.0,0.0,1.0,1.0],
                           [1.0,0.0,0.0,1.0]])
state_cmap = ListedColormap(STATE_COLORMAP)



# def displacement(track):
#     displacements = [0.]
#
#     for i in range(1,len(track)):
#         d = np.sqrt((track.x[i]-track.x[i-1])**2 + (track.y[i]-track.y[i-1])**2)
#         displacements.append(d)
#
#     hi = np.ptp(displacements)
#     lo = np.min(displacements)
#     norm_displacements = ((displacements - lo) / hi)
#     return 31 * np.clip(norm_displacements, 0., 1.)


def survivor(tracks, track):
    """ eye of the tiger """
    root = [t for t in tracks if t.ID == track.root]
    if root:
        return 16 if root[0].t[0] <= 30 else 0
    return 0



class TrackManager:
    """ TrackManager

    Deals with the track data and appropriate slicing for display

    """
    def __init__(self, tracks):
        self.tracks = tracks

        # build trees from the tracks
        self._trees = btrack.utils.build_trees(tracks)

    @property
    def trees(self): return self._trees

    @property
    def data(self):
        return [np.stack([t.t, t.y, t.x], axis=-1) for t in self.tracks]

    @property
    def properties(self):
        return [{'ID': t.ID,
                 'root': t.root,
                 'parent': t.parent,
                 'states':t.state,
                 'fate':t.fate.value,
                 'survivor': survivor(self.tracks, t)} for t in self.tracks]