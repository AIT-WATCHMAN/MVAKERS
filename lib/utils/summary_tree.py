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
                    if cutdict[cuttype][cut] is not None:
                        newcut = np.zeros(1, dtype=float64)
                        cut_tree.Branch(cut, newcut, '%s/D'%(cut))
                        newcut[0] = float(cutdict[cuttype][cut])
                        cut_tree.Fill()
    return cut_tree
