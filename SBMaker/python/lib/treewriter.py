#Single function that takes in a ROOT file, grabs the tree named
#data, and writes in a new ntuple into it.
import numpy as np
import ROOT

def addTimeDiffNtuple(rootfiles, ntname,timecut):
        '''
        Uses self.shootTimeDiff to fill a new value in all rootfiles
        found in self.bkgfiles.
        '''
        #This is dangerous because you are messing with the file itself.
        #It's better to make a copy of the file with the entry in it. See
        #Here for how to do it:
        #https://root.cern.ch/root/roottalk/roottalk01/0363.html
        for bkgfile in rootfiles:
            print(bkgfile)
            _file0 = ROOT.TFile.Open(bkgfile,"UPDATE")
            tvar = np.zeros(1, dtype=float)
            dattree = _file0.Get("data")
            dattree.Branch(ntname,tvar,ntname+"/D")
            #ROOT needs the for loop; one way trip to slow town
            for event in np.arange(dattree.GetEntries()):
                tvar[0] = np.random.rand() #self.shootTimeDiff(timecut, 1)
                dattree.Fill()
            dattree.Write()
            _file0.Close()

if __name__ == "__main__":
    #First, get the rootfile name
    rootfile = ["tester_copy.root"]
    ntname = "ntest"
    timecut = "whatever"
    addTimeDiffNtuple(rootfile, ntname, timecut)
