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
    rateHz_rf = np.zeros(1,dtype=float64)
    potential_prompts_rf = np.zeros(1,dtype=int)
    nEvents_rf = np.zeros(1,dtype=int)
    #Initialize the array that will hold the rates of valid events according to
    #the prompt cuts specified
    ValidCandidate_rates = []
    for f in rootfile_list:
        f.cd()
        frunSummary = f.Get('runSummary')
        frunSummary.SetBranchAddress('rateHz', rateHz_rf)
        frunSummary.SetBranchAddress('potential_prompts', potential_prompts_rf)
        frunSummary.SetBranchAddress('nEvents', nEvents_rf)
        frunSummary.GetEntry(0)
        print("RATEHZ: " + str(rateHz_rf[0]))
        valid_rate = rateHz_rf[0] * (float(potential_prompts_rf[0])/ \
                float(nEvents_rf[0]))
        ValidCandidate_rates.append(valid_rate)
    return np.array(ValidCandidate_rates)

