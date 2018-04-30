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
        thissource = "None"
        thisiso = "None"
        for sourcetype in ratedict:
            if sourcetype in str(f):
                for isotope in ratedict[sourcetype]:
                    if isotope in str(f):
                        raw_rateHz = ratedict[sourcetype][isotope]
                        thissource = sourcetype
                        thisiso = isotope
                        break
        if raw_rateHz is None:
            print("RATE NOT FOUND FOR BACKGROUND FILE %s.  SETTING RATE TO -1")
            trigrates_perfile.append(-1)
            continue

        #Now, we scale the raw rate by the fraction of events that
        #had one tube hit
        f.cd()
        tot_generated = 0.0
        frunSummary = None
        try:
            frunSummary = f.Get('runSummary')
        except AttributeError:
            print("FILE %s HAS NO RUN SUMMARY. RATE SET TO -1"%(str(f)))
            trigrates_perfile.append(-1)
            continue
        for i in xrange(frunSummary.GetEntries()):
            frunSummary.GetEntry(i)
            tot_generated+= float(frunSummary.nEvents) 
        fdata = f.Get("data")
        tot_trigged = float(fdata.GetEntries())
        fraction_trigged = tot_trigged/tot_generated
        print("FRACTION_TRIGGERED in %s %s: %s" %(thisiso,thissource, str(fraction_trigged)))
        trigrates_perfile.append(raw_rateHz * fraction_trigged)
    print("FINAL TRIG RATES: " + str(trigrates_perfile))
    return np.array(trigrates_perfile)
