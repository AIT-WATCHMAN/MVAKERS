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

#Make a function that grabs a particular entry from a root file given to it.
def GetRates_Valids(rootfile_list):
    #initialize memory for branch data
    ValidCandidate_rates = []
    for f in rootfile_list:
        f.cd()
        frunSummary = f.Get('runSummary')
        totprompts = 0
        totevents = 0
        tot_rateHz = 0.0
        for i in xrange(frunSummary.GetEntries()):
            frunSummary.GetEntry(i)
            tot_rateHz += float(frunSummary.rateHz)
            totprompts += float(frunSummary.potential_prompts)
            totevents += float(frunSummary.nEvents)
        valid_rate = (tot_rateHz/float(frunSummary.GetEntries())) * \
                ((totprompts)/ \
            (totevents))
        ValidCandidate_rates.append(valid_rate)
    return np.array(ValidCandidate_rates)

def GetRates_Raw(rootfile_list):
    #initialize memory for branch data
    Raw_rates = []
    for f in rootfile_list:
        f.cd()
        tot_rateHz = 0.0
        frunSummary = f.Get('runSummary')
        for i in xrange(frunSummary.GetEntries()):
            frunSummary.GetEntry(i)
            tot_rateHz += float(frunSummary.rateHz)
        rateHz = tot_rateHz/float(frunSummary.GetEntries())
        Raw_rates.append(rateHz)
    return np.array(Raw_rates)

