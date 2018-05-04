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


def __loadNewEvent(Bkg_rates_validfits,Bkg_entrynums,Bkg_chains):
    '''
    From the available background files, shoot what the next event type 
    loaded into the singles fill will be.  Increment this file's entries used.
    '''
    shot =np.random.rand()
    for i in xrange(len(Bkg_rates_validfits)):
        frac_thischain = sum(Bkg_rates_validfits[0:i+1]) / np.sum(Bkg_rates_validfits)
        if shot < frac_thischain:
            Bkg_entrynums[i]+=1
            thisentry = (int(Bkg_entrynums[i]))
            thischain = Bkg_chains[i]
            break
    return thisentry, thischain
        
def getBackgroundSingles(ratedict=None,cutdict=None,rootfiles=[],outfile="signal_output.root",datatree='data',max_entries=9E15):
    #For a list of given files, 
    print("ROOTFILES BEING FED IN: " + str(rootfiles)) 
    Bkg_chains = []
    Bkg_files = []
    for f in rootfiles:
        rfile = ROOT.TFile(f, "READ")
        rchain = rfile.Get(datatree)
        Bkg_files.append(rfile)
        Bkg_chains.append(rchain)
    
    #Calculate the raw rate and valid rate of backgrounds in given files.
    #Uses metadata from WATCHMAKERS ProcSummary to do this.
    Bkg_rates_validfits = rr.GetRates_Triggered(Bkg_files,ratedict)
    Bkg_entrynums = np.zeros(len(Bkg_files))
    
    TRIGDRATE = np.sum(Bkg_rates_validfits)
    print("VALID SINGLE CANDIDATE RATE: " + str(TRIGDRATE))

    '''Set up variables for root tree'''
    n9_rf        = np.zeros(1,dtype=int)
    nhit_rf      = np.zeros(1,dtype=int)
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
    sum_tree = ROOT.TTree("Summary","Meta information")
    trigd_rate = np.zeros(1,dtype=float64)
    cut_acceptance = np.zeros(1,dtype=float64)
    allsinglesnum = np.zeros(1,dtype=int)
    validsinglesnum = np.zeros(1,dtype=int)
    total_time = np.zeros(1,dtype=float64)
    sum_tree.Branch('trigd_rate', trigd_rate, 'trigd_rate/D')
    sum_tree.Branch('cut_acceptance', cut_acceptance, 'cut_acceptance/D')
    sum_tree.Branch('allsinglesnum', allsinglesnum, 'allsinglesnum/I')
    sum_tree.Branch('validsinglesnum', validsinglesnum, 'validsinglesnum/I')
    sum_tree.Branch('total_time', total_time, 'total_time/D')
   
    trigd_rate[0] = TRIGDRATE
    cut_tree = ROOT.TTree("AppliedCuts","Cuts applied")
    cut_tree = st.fillSumWithCuts(cut_tree,cutdict)



    t_root = ROOT.TTree("Output","Singles File Composed of all backgrounds")
    t_root.Branch('pe',       pe_rf,    'pe/D')
    t_root.Branch('nhit',       nhit_rf,    'nhit/I')
    t_root.Branch('n9',      n9_rf,   'n9/I')

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


    #Begin finding valid singles
    entrynum = 0
    entries_viewed = 0
    totaltime = 0.0

    while (entrynum < max_entries):
        if float(entrynum) / 20000.0 == int(entrynum / 20000.0):
            print("ENTRYNUM: " + str(entrynum))
        entries_viewed+=1
        
        #Shoot for the next background file and it's next unused entry
        thisentry, bkgchain = __loadNewEvent(Bkg_rates_validfits,\
                Bkg_entrynums,Bkg_chains)
        totaltime = totaltime + eu.shootTimeDiff(TRIGDRATE)

        #Check if the file is depleted
        if thisentry >= bkgchain.GetEntries():
            print("A BACKGROUND FILE WAS DEPLETED.  FINISHING UP.")
            break

        
        eventvalid=True
        
        bkgchain.GetEntry(thisentry)
        #Check if this passes the input cuts
        if cutdict is not None and "singles" in cutdict:
            for cut in cutdict["singles"]:
                if cutdict["singles"][cut] is not None and \
                        cutdict["singles"][cut] > getattr(bkgchain,cut):
                    eventvalid=False
                    break
        if eventvalid is False:
            continue
        
        #It passed cuts; fill entry into output file
        pe_rf[0] = bkgchain.pe 
        n9_rf[0] = bkgchain.n9

        nhit_rf[0] = bkgchain.nhit
        mc_energy_rf[0] = bkgchain.mc_energy
        good_pos_rf[0] = bkgchain.good_pos
        u_rf[0] = bkgchain.u
        v_rf[0] = bkgchain.v
        w_rf[0] = bkgchain.w
        x_rf[0] = bkgchain.x
        y_rf[0] = bkgchain.y
        r_rf[0] = eu.radius(bkgchain.x, bkgchain.y)
        z_rf[0] = bkgchain.z
        good_dir_rf[0] = bkgchain.good_dir
        closestPMT_rf[0] = bkgchain.closestPMT
        t_root.Fill()
        entrynum+=1
    #/while(entrynum < max_entries)
    total_time[0] = float(totaltime)
    cut_acceptance[0] = float(entrynum)/float(entries_viewed)
    allsinglesnum[0] = entries_viewed
    validsinglesnum[0] = entrynum
    f_root.cd()
    t_root.Write()
    sum_tree.Fill()
    sum_tree.Write()
    cut_tree.Write()
    f_root.Close()
