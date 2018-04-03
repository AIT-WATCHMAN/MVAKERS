#Function takes in a summary tree and fills in what additional cuts were
#Applied to event selection, if any.
import numpy as np
from numpy import *

def fillSumWithCuts(cut_tree,cutdict):
    if cutdict is None:
        return cut_tree

    if len(cutdict)>0:
        for cuttype in cutdict:
            if len(cuttype) > 0:
                for cut in cutdict[cuttype]:
                    if cut=="interevent_dist" and \
                            cutdict[cuttype][cut] is not None:
                        interdistcut = np.zeros(1,dtype=float64)
                        cut_tree.Branch('interdistcut', interdistcut, 'interdistcut/D')
                        interdistcut[0] = float(cutdict[cuttype][cut])
                    if cut=="interevent_time" and \
                            cutdict[cuttype][cut] is not None:
                        intertimecut = np.zeros(1,dtype=float64)
                        cut_tree.Branch('intertimecut', intertimecut, 'intertimecut/D')
                        intertimecut[0] = float(cutdict[cuttype][cut])
                    if cut=="r" and cutdict[cuttype][cut] is not None:
                        rcut = np.zeros(1,dtype=float64)
                        cut_tree.Branch('rcut', rcut, 'rcut/D')
                        rcut[0] = float(cutdict[cuttype][cut])
                    if cut=="z" and cutdict[cuttype][cut] is not None:
                        zcut = np.zeros(1,dtype=float64)
                        cut_tree.Branch('zcut',zcut, 'zcut/D')
                        zcut[0] = float(cutdict[cuttype][cut])
    cut_tree.Fill()
    return cut_tree
