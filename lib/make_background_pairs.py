#One-shot script that reads all PMT and WV root files in a WATCHMAKERS
#output.  File format and directory structure are all assumed to be that
#of the default WATCHMAKERS output.
#The program will take all PMT and WV files for a coverage and pair events
#from all files into prompt and delayed IBD candidates.  The rates used to
#shoot interevent times are pulled from 'runSummary' trees of the root files
#for each background.


import copy as cp
import math
import time
import numpy as np
from numpy import *

import sys
from sys import stdout
import glob

import os
from sys import argv

from decimal import *
import argparse
#have to import ROOT here, or it steals --help's output
import ROOT
from ROOT import TChain, TFile, gROOT
import utils.playDarts as pd
import utils.EventUtils as eu
import utils.RootReader as rr
import utils.summary_tree as st


def __loadNewEvent(buff,Bkg_rates_validfits,Bkg_entrynums,Bkg_files,VALIDRATE,totaltime):
    '''
    Using the loaded-in background files, shoot the next event's information,
    including file it's in, it's entry number, and the time since last event
    '''
    shot =np.random.rand()
    #Assuming Bkg_rates is a numpy array
    for i in xrange(len(Bkg_rates_validfits)):
        if shot < (sum(Bkg_rates_validfits[0:i+1]) / \
                np.sum(Bkg_rates_validfits)):
            Bkg_entrynums[i]+=1
            buff["entrynums"].append(int(Bkg_entrynums[i]))
            buff["files"].append(Bkg_files[i])
            shottime = eu.shootTimeDiff(VALIDRATE)
            totaltime= totaltime + shottime
            buff["times"].append(shottime)
            break
    return buff,totaltime

def __deleteOutOfWindow(buff,TIMETHRESH):
    allinwindow = False
    while not allinwindow:
    	if sum(buff["times"][1:len(buff["times"])]) > TIMETHRESH:
            del buff["times"][0]
            del buff["files"][0]
            del buff["entrynums"][0]
        else:
            allinwindow=True
    return buff

def __deleteNewestEntry(buff):
    del buff["times"][len(buff["times"]) -1]
    del buff["files"][len(buff["files"]) -1]
    del buff["entrynums"][len(buff["files"]) -1]
    return buff


def getBackgroundPairs(cutdict=None,rootfiles=[],outfile="background_output.root",datatree='data',max_entries=9E15):
    #For a list of given files, append the ROOT file object to Bkg_files list 
    print("ROOTFILES BEING FED IN: " + str(rootfiles)) 
    Bkg_files = []
    for f in rootfiles:
        rfile = ROOT.TFile(f, "READ")
        Bkg_files.append(rfile)
    
    #Want to shoot the rates of events that could be a prompt candidate.  Only want
    #To shoot using rates_validfits since only valid events are filled into the ntuple
    Bkg_rates_validfits = rr.GetRates_Valids(Bkg_files)
    Bkg_rates_raw = rr.GetRates_Raw(Bkg_files)
    Bkg_entrynums = np.zeros(len(Bkg_files))
    
    RAW_RATE = np.sum(Bkg_rates_raw)
    VALIDRATE = np.sum(Bkg_rates_validfits)
    
    '''Set up variables for output root tree'''
    x_p       = np.zeros(1,dtype=float64)
    y_p        = np.zeros(1,dtype=float64)
    z_p      = np.zeros(1,dtype=float64)
    u_p      = np.zeros(1,dtype=float64)
    v_p      = np.zeros(1,dtype=float64)
    w_p      = np.zeros(1,dtype=float64)
    mc_energy_p    = np.zeros(1,dtype=float64)
    nhit_p     = np.zeros(1,dtype=int)
    good_pos_p = np.zeros(1,dtype=float64)
    good_dir_p = np.zeros(1,dtype=float64)
    pe_p     = np.zeros(1,dtype=int)
    r_p      = np.zeros(1,dtype=float64)
    closestPMT_p    = np.zeros(1,dtype=float64)
    n9_p       = np.zeros(1,dtype=int)

    x_d       = np.zeros(1,dtype=float64)
    y_d        = np.zeros(1,dtype=float64)
    z_d      = np.zeros(1,dtype=float64)
    u_d      = np.zeros(1,dtype=float64)
    v_d      = np.zeros(1,dtype=float64)
    w_d      = np.zeros(1,dtype=float64)
    mc_energy_d    = np.zeros(1,dtype=float64)
    nhit_d     = np.zeros(1,dtype=int)
    good_pos_d = np.zeros(1,dtype=float64)
    good_dir_d = np.zeros(1,dtype=float64)
    pe_d     = np.zeros(1,dtype=int)
    r_d      = np.zeros(1,dtype=float64)
    closestPMT_d    = np.zeros(1,dtype=float64)
    n9_d       = np.zeros(1,dtype=int)

    interevent_dist = np.zeros(1,dtype=float64)
    interevent_time = np.zeros(1,dtype=float64)
    pair_number = np.zeros(1,dtype=int)


    #Variables for filling ProcSummary
    allsinglesnum = np.zeros(1,dtype=int)
    raw_rate = np.zeros(1,dtype=float64)
    validsinglesnum = np.zeros(1,dtype=int)
    validpairnum = np.zeros(1,dtype=int) 
    pvalid_rate = np.zeros(1,dtype=float64)
    total_time = np.zeros(1,dtype=float64)

    '''Open a root file with name of dataType'''

    f_root = ROOT.TFile(outfile,"recreate")
    
    sum_tree = ROOT.TTree("ProcSummary","Some meta information")
    sum_tree.Branch('raw_rate', raw_rate, 'raw_rate/D')
    sum_tree.Branch('pvalid_rate', pvalid_rate, 'pvalid_rate/D')
    sum_tree.Branch('allsinglesnum', allsinglesnum, 'allsinglesnum/I')
    sum_tree.Branch('validpairnum', validpairnum, 'validpairnum/I')
    sum_tree.Branch('validsinglesnum', validsinglesnum, 'validsinglesnum/I')
    sum_tree.Branch('total_time', total_time, 'total_time/D')

    cut_tree = ROOT.TTree("AppliedCuts","Cuts applied and some meta information")
    cut_tree = st.fillSumWithCuts(cut_tree,cutdict)

    pvalid_rate[0] = VALIDRATE
    raw_rate[0] = RAW_RATE

    t_root = ROOT.TTree("Output","Combined Prompt & Delayed candidates from Background MC")
    t_root.Branch('z_p',      z_p,   'z_p/D')
    t_root.Branch('y_p',      y_p,   'y_p/D')
    t_root.Branch('x_p',      x_p,   'x_p/D')
    t_root.Branch('r_p',      r_p,   'r_p/D')
    t_root.Branch('w_p',      w_p,   'w_p/D')
    t_root.Branch('v_p',      v_p,   'v_p/D')
    t_root.Branch('u_p',      u_p,   'u_p/D')
    t_root.Branch("mc_energy_p",    mc_energy_p, 'mc_energy_p/D')
    t_root.Branch("nhit_p",     nhit_p,  'nhit_p/I')
    t_root.Branch("good_pos_p", good_pos_p,   'good_pos_p/D')
    t_root.Branch("good_dir_p", good_dir_p,   'good_dir_p/D')
    t_root.Branch("pe_p", pe_p,   'pe_p/I')
    t_root.Branch("closestPMT_p", closestPMT_p, "closestPMT_p/D")
    t_root.Branch("n9_p", n9_p, "n9_p/I")

    t_root.Branch('z_d',      z_d,   'z_d/D')
    t_root.Branch('y_d',      y_d,   'y_d/D')
    t_root.Branch('x_d',      x_d,   'x_d/D')
    t_root.Branch('r_d',      r_d,   'r_d/D')
    t_root.Branch('w_d',      w_d,   'w_d/D')
    t_root.Branch('v_d',      v_d,   'v_d/D')
    t_root.Branch('u_d',      u_d,   'u_d/D')
    t_root.Branch("mc_energy_d",    mc_energy_d, 'mc_energy_d/D')
    t_root.Branch("nhit_d",     nhit_d,  'nhit_d/I')
    t_root.Branch("good_pos_d", good_pos_d,   'good_pos_d/D')
    t_root.Branch("good_dir_d", good_dir_d,   'good_dir_d/D')
    t_root.Branch("pe_d", pe_d,   'pe_d/I')
    t_root.Branch("closestPMT_d", closestPMT_d, "closestPMT_d/D")
    t_root.Branch("n9_d", n9_d, "n9_d/I")

    t_root.Branch('interevent_time', interevent_time,  'interevent_time/D')
    t_root.Branch('interevent_dist', interevent_dist,  'interevent_dist/D')
    t_root.Branch('pair_number', pair_number, 'pair_number/I')

    #initialize a buffer dictionary that holds the information of files and
    #events to make pairs from
    Buffer = {}
    Buffer["files"] = []
    Buffer["entrynums"] = []
    Buffer["times"] = []
    
    
    #Keep track of meta information for calculating efficiencies pre-MVA entry
    pairnum = 0
    entrynum = 0
    vsnum = 0
    totaltime = 0.0
    while (pairnum < max_entries):
        if float(entrynum) / 20000.0 == int(entrynum / 20000.0):
            print("ENTRYNUM: " + str(entrynum))

        #load a new event into our buffer
        Buffer,totaltime = __loadNewEvent(Buffer,Bkg_rates_validfits,
                Bkg_entrynums,Bkg_files,VALIDRATE,totaltime)
        entrynum+=1

        #Remove events at start of buffer outside the time width range
        try:
            Buffer = __deleteOutOfWindow(Buffer,cutdict["pairs"]["interevent_time"])
        except KeyError:
            print("interevent_time separation not defined.  Means we have no pair")
            print("window.  Define and interevent_time and run again.")
            sys.exit(1)

        #loop through and match this delayed event with all previous prompts
        delayedindex = len(Buffer["entrynums"]) - 1
        Delayedfile = Buffer["files"][delayedindex]
        Delayedtree = Delayedfile.Get(datatree)
        Delayedtree.GetEntry(Buffer["entrynums"][delayedindex])
        eventvalid = True

	#Check if we've exhausted a MC file's data yet
        if Buffer["entrynums"][len(Buffer["entrynums"])-1] == \
                Delayedtree.GetEntries():
            print("A BACKGROUND FILE WAS DEPLETED")
            break

        #Check if this passes the input cuts
        if cutdict is not None and "singles" in cutdict:
            for cut in cutdict["singles"]:
                if cutdict["singles"][cut] is not None and \
                        cutdict["singles"][cut] > getattr(Delayedtree,cut):
                    eventvalid=False
                    break
        if eventvalid is False:
            __deleteNewestEntry(Buffer)
            continue
        #event is valid for given singles cuts
        vsnum+=1

        if len(Buffer["entrynums"]) <=1:
            continue

        for i in xrange(delayedindex):
            Promptfile = Buffer["files"][i]
            Prompttree = Promptfile.Get(datatree)
            Prompttree.GetEntry(Buffer["entrynums"][i])
            nhit_p[0]     = Prompttree.nhit 
            x_p[0]       = Prompttree.x
            y_p[0]        = Prompttree.y
            z_p[0]      = Prompttree.z
            r_p[0]        = eu.radius(x_p[0],y_p[0])
            u_p[0]      = Prompttree.u
            v_p[0]      = Prompttree.v 
            w_p[0]      = Prompttree.w 
            mc_energy_p[0]    = Prompttree.mc_energy 
            good_pos_p[0] = Prompttree.good_pos 
            good_dir_p[0] = Prompttree.good_dir 
            pe_p[0]     = Prompttree.pe 
            closestPMT_p[0]  = Prompttree.closestPMT
            n9_p[0]  = Prompttree.n9
            
            Delayedtree.GetEntry(Buffer["entrynums"][delayedindex])
            nhit_d[0]     = Delayedtree.nhit 
            x_d[0]       = Delayedtree.x
            y_d[0]        = Delayedtree.y
            z_d[0]      = Delayedtree.z
            r_d[0]        = eu.radius(x_d[0],y_d[0])
            u_d[0]      = Delayedtree.u
            v_d[0]      = Delayedtree.v 
            w_d[0]      = Delayedtree.w 
            mc_energy_d[0]    = Delayedtree.mc_energy 
            good_pos_d[0] = Delayedtree.good_pos 
            good_dir_d[0] = Delayedtree.good_dir 
            pe_d[0]     = Delayedtree.pe 
            closestPMT_d[0]  = Delayedtree.closestPMT
            n9_d[0]  = Delayedtree.n9
            
            #Check for intereventdist cut and fill in interevent dist
            interevent_dist[0] = eu.innerDist(x_p[0], y_p[0],
                    z_p[0],x_d[0],y_d[0],z_d[0])
          
            interevent_time[0] = sum(Buffer["times"][i+1:delayedindex+1])
            itid_dict = {"interevent_dist": interevent_dist[0], \
                    "interevent_time": interevent_time[0]}
            itid_valid = True
            if cutdict is not None and "pairs" in cutdict:
                pcuts = cutdict["pairs"]
                for cut in pcuts:
                    if pcuts[cut] is not None and \
                            pcuts[cut] < itid_dict[cut]:
                        itid_valid = False
            if itid_valid is False:
                continue
            pair_number[0] = pairnum
            t_root.Fill()
            pairnum+=1

    #Fill ProcSummary metadata on run
    allsinglesnum[0] = entrynum
    validsinglesnum[0] = vsnum
    validpairnum[0] = pairnum
    total_time[0] = totaltime

    sum_tree.Fill()
    f_root.cd()
    t_root.Write()
    sum_tree.Write()
    cut_tree.Write()
    f_root.Close()
