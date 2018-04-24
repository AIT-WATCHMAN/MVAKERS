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

def GetEfficiency_SingleFile(rootfile):
    '''
    Returns the fraction of events generated that passed the preliminary
    cuts for the prompt event.  The specs on the cuts defined can be found
    in the runSummary tree of these files.
    '''
    #initialize memory for branch data
    rootfile.cd()
    frunSummary = rootfile.Get('runSummary')
    totprompts = 0
    totevents = 0
    for i in xrange(frunSummary.GetEntries()):
        frunSummary.GetEntry(i)
        totprompts += float(frunSummary.potential_prompts)
        totevents += float(frunSummary.nEvents)
    valid_efficiency = (float(totprompts)/float(totevents))
    return valid_efficiency

#Make a function that grabs a particular entry from a root file given to it.
def GetEfficiency(rootfile_list):
    '''Returns the number of events that passed the preliminary cuts
    used when generating/keeping data'''
    totprompts = 0.0
    totevents = 0.0
    for f in rootfile_list:
        f.cd()
        frunSummary = f.Get('runSummary')
        tot_rateHz = 0.0
        for i in xrange(frunSummary.GetEntries()):
            frunSummary.GetEntry(i)
            totprompts += float(frunSummary.potential_prompts)
            totevents += float(frunSummary.nEvents)
    efficiency = totprompts/totevents
    return efficiency

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
            try:
            	tot_rateHz += float(frunSummary.rateHz)
            	totprompts += float(frunSummary.potential_prompts)
            	totevents += float(frunSummary.nEvents)
        	valid_rate = (tot_rateHz/float(frunSummary.GetEntries())) * \
                        ((totprompts)/ \
            	        (totevents))
                ValidCandidate_rates.append(valid_rate)
            except AttributeError:
                print("FILE %s HAS NO RATE INFORMATION. CONTINUING"%(str(f)))
    if len(ValidCandidate_rates) == 0:
        ValidCandidate_rates.append(0.0)	
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
            try:
                tot_rateHz += float(frunSummary.rateHz)
            except:
                print("FILE %s HAS NO RATEHZ IN RUNSUMMARY. CONTINUING"%str(f))
         rateHz = tot_rateHz/float(frunSummary.GetEntries())
        Raw_rates.append(rateHz)
    return np.array(Raw_rates)

