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
        frunSummary.GetEntry(0)
        rateHz = float(frunSummary.rateHz)
        potential_prompts = float(frunSummary.potential_prompts)
        nEvents = float(frunSummary.nEvents)
        valid_rate = rateHz * ((potential_prompts)/ \
               (nEvents))
        ValidCandidate_rates.append(valid_rate)
    return np.array(ValidCandidate_rates)

def GetRates_Raw(rootfile_list):
    #initialize memory for branch data
    Raw_rates = []
    for f in rootfile_list:
        f.cd()
        frunSummary = f.Get('runSummary')
        frunSummary.GetEntry(0)
        rateHz = float(frunSummary.rateHz)
        Raw_rates.append(rateHz)
    return np.array(Raw_rates)

