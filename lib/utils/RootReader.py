import ROOT
import numpy as np

import os
from numpy import *

def GetEntryLengths(rootfile_list):
    EntryLengths = []
    for f in rootfile_list:
        f.cd()
        fdata = f.Get("data")
        entrylength = int(fdata.GetEntries())
        EntryLengths.append(entrylength)
    return np.array(EntryLengths)

def GetRates_Triggered(rootfile_list,ratedict):
    '''Takes in a list of root files and background/signal ratedict output from
    lib/RootReader.py.  Returns an array of the rates for events that caused at
    least 1 PMT to fire (these are the only events saved to WATCHMAKERS outputs)'''
    if ratedict is None:
        print("NO RATE INFORMATION AVAILABLE FOR ANY FILES.  RETURNING -1's")
        return -1 * np.ones(len(rootfile_list))
    
    ValidCandidate_rates = []
    for f in rootfile_list:
        trig_rateHz = None
        for sourcetype in ratedict:
            if sourcetype in str(f):
                for isotope in ratedict[source]:
                    if isotope in str(f):
                        #Found the right rate
                        trig_rateHz = ratedict[sourcetype][isotope] 
        
        if trig_rateHz is None:
            print("RATE NOT FOUND FOR BACKGROUND FILE %s.  SETTING RATE TO -1")
            ValidCandidate_rates.append(-1)
            continue
        ValidCandidate_rates.append(trig_rateHz)
        continue
        #FIXME: use the subEventTally here to correct events? I don't think so..
        #f.cd()
        #frunSummary = f.Get('runSummary')
        #tottriggered = 0
        #totevents = 0
        #for i in xrange(frunSummary.GetEntries()):
        #    frunSummary.GetEntry(i)
        #    try:
        #    	tottriggered += float(frunSummary.QUEES)
        #    	totevents += float(frunSummary.nEvents)
        # 	trig_rate = (trig_rateHz/float(frunSummary.GetEntries())) * \
        #                 ((tottriggered)/ \
        #     	          (totevents))
        #       Triggered_rates.append(trig_rate)
        #    except AttributeError:
        #        print("FILE %s HAS NO RATE INFORMATION. CONTINUING"%(str(f)))
    return np.array(ValidCandidate_rates)

