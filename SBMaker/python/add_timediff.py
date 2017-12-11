# This script serves a distinct purpose of filling in the expected
# Time difference between events that would occur for a particular background
# in WATCHMAN.  There's three main tasks done here given a set of ntuples
# representing physics events in WATCHMAN:
#   1) The efficiency for the # events that construct within 2 meters of
#      each other is calculated from the "inner_dist_fv" ntuple entry.
#   2) The expected IBD candidates/day for the background source is grabbed
#      from the event rate JSON provided by Marc that corresponds to this MC.
#   3) The expected raw rate of events is calculated from this.  
#   4) Given this expected event rate, the Skellam distribution produced 
#      assuming two poissons with this raw rate average.  This is sampled and
#      filled into the "inner_time" ntuple for the .ntuple.root.

import numpy as np
import scipy.stats as scs #will use scs.skellam
import ROOT
import glob
import json
import os.path
import lib.playDarts as pd

basepath = os.path.dirname(__file__)
DBDIR = os.path.abspath(os.path.join(basepath, "..","DB"))

FILENAME = "BoulbySignals_PC.json"
distcut = 2.  # in m. Cut is associated with values generated in DB
timecut = 1E5 #in nanoseconds.
PMT_RATE = 3805 #Number of PMT radioactive decays expected per second
FV_RATE = 7  #Actually 6.4, but we'll round up to be conservative
bkgfiles = glob.glob("../../data/UTh/*228Ac_25pct_PMT_tester.root")
NTUPLENAME = "interevent_time"

class TimeDiffGen(object):
    def __init__(self,bkg_IBDrate,bkgfile_names):
        self.bkg_IBDrate = bkg_IBDrate  #candidates/day
        self.bkgfiles = bkgfile_names
        #FIME: Once we're actually generating times, let's start as None here
        self.disteff = None
        self.detectioneff = None
        self.fiteff = None  #FIXME: Do we need this?  Did Marc use it?
        self.bkg_rawrate = PMT_RATE

    def setRateAverage(self, timecut):
        #FIXME: Times aren't quite making sense... like an event every second
        #on average.  Seems too low.
        #given the time cut used, distance cut efficiency, and expected IBD rate
        #/day, shoot a value from the skrellam distribution (i.e. a distance
        #between the result of two shots from poissons of average mu1 and mu2
        if self.disteff is None or self.detectioneff is None:
            print("You must first calculate the distance cut  and detection "+\
                    "efficiency from the background files before "+\
                    "shooting this value")
        #Get IBD candidates per microsecond
        bkgrate_sec = self.bkg_IBDrate/(24.* 60.* 60.)
        raw_freq = np.sqrt(bkgrate_sec/(timecut*self.disteff)) / \
                self.detectioneff
        print("RAW RATE (Hz): " + str(raw_freq))
        self.bkg_rawrate = raw_freq #Returned in Hertz

    def evalIBDRate(self):
        if self.disteff is None or self.detectioneff is None:
            print("You must first calculate the distance cut  and detection "+\
                    "efficiency from the background files before "+\
                    "shooting this value")
        #Get IBD candidates per microsecond
        IBD_eff = ((self.bkg_rawrate*self.detectioneff*self.fiteff)**2)*self.disteff*timecut*1E-9
        IBD_perday = IBD_eff*24*60*60  #From per second to per day
        print("IBDs PER DAY: " + str(IBD_perday))
         

    def shootTimeDiff(self, raw_freq):
        #Assume your process is poisson with an occurence of raw_freq/sec
        #on average.  We get the time diff by shooting that many events in
        #a one second timespan, sort, then get the average time difference.
        #Returns event time difference in nanoseconds

        if raw_freq < 20:
            num_events = pd.RandShoot_p(raw_freq,1)
        else:
            num_events = pd.RandShoot_g0(raw_freq, np.sqrt(raw_freq),1)
        event_times = np.random.rand(num_events)
        event_times.sort()
        the_event_index = np.random.randint(1,len(event_times)-1)
        timediff = (event_times[the_event_index] - event_times[the_event_index -1])
        return timediff * 1.0E9

    def addTimeDiffNtuple(self, ntname):
        '''
        Uses self.shootTimeDiff to fill a new value in all rootfiles
        found in self.bkgfiles.
        '''
        if self.bkg_rawrate is None:
            print("NEED TO SET YOUR RAW RATE BASED ON YOUR TIME CUT FIRST")
            return
        #This is dangerous because you are messing with the file itself.
        #It's better to make a copy of the file with the entry in it. See
        #Here for how to do it:
        #https://root.cern.ch/root/roottalk/roottalk01/0363.html
        for bkgfile in self.bkgfiles:
            print(bkgfile)
            _file0 = ROOT.TFile.Open(bkgfile,"UPDATE")
            tvar = np.zeros(1, dtype=float)
            dattree = _file0.Get("data")
            dattree.Branch(ntname,tvar,ntname+"/D")
            #ROOT needs the for loop; one way trip to slow town
            indexer = 0
            for event in np.arange(dattree.GetEntries()):
                if float(indexer)/float(100000) == int(indexer/100000):
                    print("ADDING NTUPLE TO EVENT " + str(indexer))
                indexer+=1
                tvar[0] = self.shootTimeDiff(self.bkg_rawrate)
                dattree.Fill()
            dattree.Write()
            _file0.Close()


    def setEfficiencies(self, distcut):
        total_events = 0
        total_fitvalids = 0
        total_detected = 0
        dist_valid = 0
        for bkgfile in self.bkgfiles:
            _file0 = ROOT.TFile.Open(bkgfile,"READ")
            dattree = _file0.Get("data")
            dattree.Show()
            #ROOT needs the for loop; one way trip to slow town
            for event in dattree:
                total_events+=1
                if event.detected_ev ==1 :
                    total_detected += 1
                    if event.pos_goodness > 0:
                        total_fitvalids+=1
                if event.inner_dist_fv > 0:
                    if event.inner_dist_fv < distcut:
                        dist_valid+=1
        print("TOTAL EVENTS IN FILES: " + str(total_events))
        self.disteff = float(dist_valid) / (float(total_events)/2.)
        self.detectioneff = float(total_fitvalids) / float(total_events)
        self.fiteff = float(total_fitvalids) / float(total_detected)
        print("DISTANCE EFF: " + str(self.disteff))
        print("DETECTION FF: " + str(self.detectioneff))

if __name__ == '__main__':
    #Open the database entry used to calculate the interevent time difference
    with open(DBDIR + "/" + FILENAME,"r") as f:
        IBDrate_dict = json.load(f)
    PC_IBDrates = IBDrate_dict["Photocoverage_Cases"]
    for PC in PC_IBDrates:
        if PC["Photocoverage"] == 0.25:
            Acc_rate = PC["Signal_Contributions"]["Accidentals"]

    #Initialize your time difference generator and use it to add in
    #The ntuple to the bkgfiles fed to the class
    TDG = TimeDiffGen(Acc_rate,bkgfiles)
    TDG.setEfficiencies(distcut)
    #TDG.setRateAverage(timecut)
    TDG.evalIBDRate()
    #TDG.addTimeDiffNtuple(NTUPLENAME)
