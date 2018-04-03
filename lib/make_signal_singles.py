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

   
def getSignalSingles(cutdict=None,rootfiles=[],outfile="signal_output.root",datatree='data',max_entries=9E15):
    rfiles = []
    for f in rootfiles:
        rfiles.append(ROOT.TFile(f,"read"))
    
    '''Set up variables for root tree'''
    n9_rf        = np.zeros(1,dtype=float64)
    nhit_rf      = np.zeros(1,dtype=float64)
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
    wm_signal_acc = np.zeros(1,dtype=float64)
    additional_cut_acc = np.zeros(1,dtype=float64)
    sum_tree.Branch('wm_signal_acc',wm_signal_acc, 'wm_signal_acc/D')
    sum_tree.Branch('additional_cut_acc', additional_cut_acc, 'additional_cut_acc\D')
    cut_tree = ROOT.TTree("AppliedCuts","Cuts applied")
    cut_tree = st.fillSumWithCuts(cut_tree,cutdict)

    wm_signal_acc[0] = rr.GetEfficiency(rfiles)

    #Prep our data tree that will hold event candidate information
    t_root = ROOT.TTree("Output","Singles File Composed of all backgrounds")
    t_root.Branch('pe',       pe_rf,    'pe/D')
    t_root.Branch('nhit',       nhit_rf,    'nhit/D')
    t_root.Branch('n9',      n9_rf,   'n9/D')

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
        for rfile in rfiles:
            thisfile_entrynum = 0
            sigtree = rfile.Get(datatree)
            if float(entrynum) / 20000.0 == int(entrynum / 20000.0):
                print("ENTRYNUM: " + str(entrynum))
            entries_viewed+=1
            thisfile_entrynum+=1
            
            #Check if the file is depleted
            if thisfile_entrynum >= sigtree.GetEntries():
                print("SIGNAL FILE %s DEPLETED.  MOVING TO NEXT, IF ANY MORE" % thisevent_bkgfile.GetName())
                break
    
            sigtree.GetEntry(thisfile_entrynum)
            #Check if this passes the input cuts
            if "singles" in cutdict:
                for cut in cutdict["singles"]:
                    if cutdict["singles"][cut] is not None and \
                            cutdict["singles"][cut] > getattr(dtree,cut):
                        continue
            
            #It passed cuts; fill entry into output file
            pe_rf[0] = sigtree.pe 
            n9_rf[0] = sigtree.n9
    
            nhit_rf[0] = sigtree.nhit
            mc_energy_rf[0] = sigtree.mc_energy
            good_pos_rf[0] = sigtree.good_pos
            u_rf[0] = sigtree.u
            v_rf[0] = sigtree.v
            w_rf[0] = sigtree.w
            x_rf[0] = sigtree.x
            y_rf[0] = sigtree.y
            r_rf[0] = np.sqrt(sigtree.x**2 + sigtree.y**2)
            z_rf[0] = sigtree.z
            good_dir_rf[0] = sigtree.good_dir
            closestPMT_rf[0] = sigtree.closestPMT
            t_root.Fill()
            entrynum+=1
    #/while(entrynum < max_entries)

    additional_cut_acc[0] = float(entrynum)/float(entries_viewed)
    f_root.cd()
    t_root.Write()
    sum_tree.Fill()
    sum_tree.Write()
    cut_tree.Write()
    f_root.Close()
