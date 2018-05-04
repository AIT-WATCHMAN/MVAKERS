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

   
def getSignalSingles(ratedict=None,cutdict=None,rootfiles=[],outfile="signal_output.root",datatree='data',max_entries=9E15):
    print("ROOTFILES BEING FED IN: " + str(rootfiles)) 
    sigchain = ROOT.TChain(datatree)
    for f in rootfiles:
       sigchain.Add(f)
         
    '''Set up variables for root tree'''
    n9_rf        = np.zeros(1,dtype=int)
    nhit_rf      = np.zeros(1,dtype=int)
    pe_rf     = np.zeros(1,dtype=float64)
    event_number_rf        = np.zeros(1,dtype=float64)
    mc_energy_rf    = np.zeros(1,dtype=float64)
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
    sum_tree = ROOT.TTree("ProcSummary","Summary of metadata")
    IBDrate = np.zeros(1,dtype=float64)
    allsinglesnum = np.zeros(1,dtype=int)
    validsinglesnum = np.zeros(1,dtype=int)
    sum_tree.Branch('IBDrate', IBDrate, 'IBDrate/D')
    sum_tree.Branch('allsinglesnum', allsinglesnum, 'allsinglesnum/I')
    sum_tree.Branch('validsinglesnum', validsinglesnum, 'validsinglesnum/I')
    IBDrate[0] = ratedict["IBD_rate"]

    cut_tree = ROOT.TTree("AppliedCuts","Cuts applied")
    cut_tree = st.fillSumWithCuts(cut_tree,cutdict)


    #Prep our data tree that will hold event candidate information
    t_root = ROOT.TTree("Output","Singles File Composed of all backgrounds")
    t_root.Branch('pe',       pe_rf,    'pe/D')
    t_root.Branch('nhit',       nhit_rf,    'nhit/I')
    t_root.Branch('n9',      n9_rf,   'n9/I')

    t_root.Branch('event_number',        event_number_rf,     'event_number/D')
    t_root.Branch('mc_energy',        mc_energy_rf ,      'mc_energy/D')
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

    while (entrynum < max_entries):
        if float(entrynum) / 20000.0 == int(entrynum / 20000.0):
            print("ENTRYNUM: " + str(entrynum))
        entries_viewed+=1
        
        #Check if the chain is depleted
        if entries_viewed >= sigchain.GetEntries():
            print("SIGNAL CHAIN DEPLETED.  DONE")
            break
        
        eventvalid=True
        sigchain.GetEntry(entries_viewed)
        #Check if this passes the input cuts
        if cutdict is not None and "singles" in cutdict:
            for cut in cutdict["singles"]:
                if cutdict["singles"][cut] is not None and \
                        cutdict["singles"][cut] > getattr(sigchain,cut):
                    eventvalid=False
                    break
        if eventvalid is False:
            continue
        
        #It passed cuts; fill entry into output file
        pe_rf[0] = sigchain.pe 
        n9_rf[0] = sigchain.n9

        nhit_rf[0] = sigchain.nhit
        mc_energy_rf[0] = sigchain.mc_energy
        good_pos_rf[0] = sigchain.good_pos
        u_rf[0] = sigchain.u
        v_rf[0] = sigchain.v
        w_rf[0] = sigchain.w
        x_rf[0] = sigchain.x
        y_rf[0] = sigchain.y
        r_rf[0] = np.sqrt(sigchain.x**2 + sigchain.y**2)
        z_rf[0] = sigchain.z
        good_dir_rf[0] = sigchain.good_dir
        closestPMT_rf[0] = sigchain.closestPMT
        t_root.Fill()
        entrynum+=1
    #/while(entrynum < max_entries)

    allsinglesnum[0] = entries_viewed
    validsinglesnum[0] = entrynum
    f_root.cd()
    t_root.Write()
    sum_tree.Fill()
    sum_tree.Write()
    cut_tree.Write()
    f_root.Close()
