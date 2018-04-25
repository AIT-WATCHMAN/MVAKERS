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
    trigrates_perfile = []
    for f in rootfile_list:
        raw_rateHz = None
        for sourcetype in ratedict:
            if sourcetype in str(f):
                for isotope in ratedict[sourcetype]:
                    if isotope in str(f):
                        raw_rateHz = ratedict[sourcetype][isotope] 
        if raw_rateHz is None:
            print("RATE NOT FOUND FOR BACKGROUND FILE %s.  SETTING RATE TO -1")
            trigrates_perfile.append(-1)
            continue

        #Now, we scale the raw rate by the fraction of events that
        #had one tube hit
        f.cd()
        frunSummary = f.Get('runSummary')
        frunSummary.GetEntry(0)
        tot_generated = 0.0
        fdata = f.Get("data")
        tot_trigged = 0.0
        try:
            tot_generated = float(frunSummary.nEvents)
            tot_trigged = float(fdata.GetEntries())
        except AttributeError:
            print("FILE %s HAS NO RUN SUMMARY. RATE SET TO -1"%(str(f)))
            trigrates_perfile.append(-1)
            continue
        fraction_trigged = tot_trigged/tot_generated
        trigrates_perfile.append(raw_rateHz * fraction_trigged)
    print("FINAL TRIG RATES: " + str(trigrates_perfile))
    return np.array(trigrates_perfile)
