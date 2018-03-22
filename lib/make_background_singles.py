#:Example from Marc with how to build a ROOT file in pyROOT
#We'll want to take these ideas and build them into a program
#That will effectively build up our simulated FV and PMT backgrounds.
import copy as cp
import math
import time
from array import *
import numpy as np
from numpy import *

import utils.playDarts as pd
import utils.EventUtils as eu
import utils.RootReader as rr
import utils.summary_tree as st

import ROOT as ROOT
from ROOT import TChain, TFile, gROOT
from sys import stdout
import glob

import os
from sys import argv

from decimal import *


def __loadNewEvent(Bkg_rates_validfits,Bkg_entrynums,Bkg_files):
    '''
    From the available background files, shoot what the next event type 
    loaded into the singles fill will be.  Increment this file's entries used.
    '''
    shot =np.random.rand()
    for i in xrange(len(Bkg_rates_validfits)):
        frac_thisfile = sum(Bkg_rates_validfits[0:i+1]) / np.sum(Bkg_rates_validfits)
        if shot < frac_thisfile:
            Bkg_entrynums[i]+=1
            thisentry = (int(Bkg_entrynums[i]))
            thisfile = Bkg_files[i]
            break
    return thisentry, thisfile
        
def getBackgroundSingles(cutdict=None,rootfiles=[],outfile="signal_output.root",datatree='data',max_entries=9E15):
    Bkg_files = []
    #For a list of given files, 
    for f in rootfiles:
        rfile = ROOT.TFile(f, "read")
        Bkg_files.append(rfile)
    
    #Calculate the raw rate and valid rate of backgrounds in given files.
    #Uses metadata from WATCHMAKERS ProcSummary to do this.
    Bkg_rates_validfits = rr.GetRates_Valids(Bkg_files)
    Bkg_rates_raw = rr.GetRates_Raw(Bkg_files)
    Bkg_entrynums = np.zeros(len(Bkg_files))
    
    RAWRATE = np.sum(Bkg_rates_raw)
    VALIDRATE = np.sum(Bkg_rates_validfits)
    print("RAW RATE: " + str(RAWRATE))
    print("VALID SINGLE CANDIDATE RATE: " + str(VALIDRATE))

    '''Set up variables for root tree'''
    n9_rf        = np.zeros(1,dtype=float64)
    nhit_rf      = np.zeros(1,dtype=float64)
    pe_rf     = np.zeros(1,dtype=float64)
    mc_energy_rf = np.zeros(1,dtype=float64)
    event_number_rf        = np.zeros(1,dtype=float64)
    good_pos_rf   = np.zeros(1,dtype=float64)
    u_rf   = np.zeros(1,dtype=float64)
    v_rf   = np.zeros(1,dtype=float64)
    w_rf   = np.zeros(1,dtype=float64)
    x_rf   = np.zeros(1,dtype=float64)
    y_rf   = np.zeros(1,dtype=float64)
    r_rf   = np.zeros(1,dtype=float64)
    z_rf   = np.zeros(1,dtype=float64)
    good_dir_rf     = np.zeros(1,dtype=float64)
    closestPMT_rf    = np.zeros(1,dtype=float64)

    '''Open a root file with name of dataType'''

    f_root = ROOT.TFile(outfile,"recreate")
    
    '''Set up the tree and branch of variables one wishes to save'''
    sum_tree = ROOT.TTree("Summary","Fiducial volume and time cut parameters used")
    raw_rate = np.zeros(1,dtype=float64)
    pvalid_rate = np.zeros(1,dtype=float64)
    additional_cut_acc = np.zeros(1,dtype=float64)

    total_time = np.zeros(1,dtype=float64)
    sum_tree.Branch('raw_rate', raw_rate, 'raw_rate/D')
    sum_tree.Branch('pvalid_rate', pvalid_rate, 'pvalid_rate/D')
    sum_tree.Branch('additional_cut_acc', additional_cut_acc, 'additional_cut_acc\D')

    sum_tree.Branch('total_time', total_time, 'total_time/D')
   
    raw_rate[0] = RAWRATE
    pvalid_rate[0] = VALIDRATE
    sum_tree = st.fillSumWithCuts(sum_tree,cutdict)


    t_root = ROOT.TTree("Output","Singles File Composed of all backgrounds")
    t_root.Branch('pe',       pe_rf,    'pe/D')
    t_root.Branch('nhit',       nhit_rf,    'nhit/D')
    t_root.Branch('n9',      n9_rf,   'n9/D')

    t_root.Branch("mc_energy", mc_energy_rf, 'mc_energy/D')
    t_root.Branch('event_number',        event_number_rf,     'event_number/D')
    t_root.Branch('good_pos',        good_pos_rf ,      'good_pos/D')
    t_root.Branch('u',     u_rf,'u/D')
    t_root.Branch('v',     v_rf,'v/D')
    t_root.Branch('w',     w_rf,'w/D')
    t_root.Branch('x',     x_rf,'x/D')
    t_root.Branch('y',     y_rf,'y/D')
    t_root.Branch('r',     r_rf,'r/D')
    t_root.Branch('z',     z_rf,'z/D')
    t_root.Branch('good_dir', good_dir_rf, 'good_dir/D')
    t_root.Branch('closestPMT', closestPMT_rf, 'closestPMT/D')


    #Begin finding
    entrynum = 0
    entries_viewed = 0
    totaltime = 0.0

    while (entrynum < max_entries):
        if float(entrynum) / 20000.0 == int(entrynum / 20000.0):
            print("ENTRYNUM: " + str(entrynum))
        entries_viewed+=1
        
        #Shoot for the next background file and it's next unused entry
        thisentry, thisevent_bkgfile = __loadNewEvent(Bkg_rates_validfits,\
                Bkg_entrynums,Bkg_files)
        totaltime = totaltime + eu.shootTimeDiff(VALIDRATE)
        thisevent_bkgfile.cd()
        bkgtree = thisevent_bkgfile.Get(datatree)

        #Check if the file is depleted
        if thisentry >= bkgtree.GetEntries():
            print("BACKGROUND FILE %s DEPLETED.  FINISHING UP." % thisevent_bkgfile.GetName())
            break

        bkgtree.GetEntry(thisentry)
        #Check if this passes the input cuts
        if "singles" in cutdict:
            for cut in cutdict["singles"]:
                if cutdict[cut] is not None and \
                        cutdict[cut] > getattr(dtree,cut):
                    continue
        
        #It passed cuts; fill entry into output file
        pe_rf[0] = bkgtree.pe 
        n9_rf[0] = bkgtree.n9

        nhit_rf[0] = bkgtree.nhit
        mc_energy_rf[0] = bkgtree.mc_energy
        good_pos_rf[0] = bkgtree.good_pos
        u_rf[0] = bkgtree.u
        v_rf[0] = bkgtree.v
        w_rf[0] = bkgtree.w
        x_rf[0] = bkgtree.x
        y_rf[0] = bkgtree.y
        r_rf[0] = eu.radius(bkgtree.x, bkgtree.y)
        z_rf[0] = bkgtree.z
        good_dir_rf[0] = bkgtree.good_dir
        closestPMT_rf[0] = bkgtree.closestPMT
        t_root.Fill()
        entrynum+=1
    #/while(entrynum < max_entries)
    total_time[0] = float(totaltime)
    additional_cut_acc[0] = float(entrynum)/float(entries_viewed)
    f_root.cd()
    t_root.Write()
    sum_tree.Fill()
    sum_tree.Write()
    f_root.Close()
