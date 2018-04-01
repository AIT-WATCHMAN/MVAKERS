#Function that takes events in a Bonsai output ntuple and pairs them into
#Prompt and delayed candidates.

#NOTE: This program assumes there is only TWO events to every mcid.  If this
#is not the case, I need to go and re-write the logic.

import copy as cp
import math
import time
import numpy as np
from numpy import *

import sys

import os
from decimal import *

import ROOT
from ROOT import TChain, TFile, gROOT
import utils.playDarts as pd
import utils.EventUtils as eu
import utils.RootReader as rr
import utils.summary_tree as st



def getSignalPairs(cutdict=None, rootfiles=[], outfile='signalout.root',datatree="data",max_entries=9E15):
    '''
    Given a cut dictionary and list of rootfiles, this function
    returns a single root file ready for passing to the TMVA Factory in
    the TMVARunner class.
    '''

    #Set up variables for output root tree
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
    n9_p       = np.zeros(1,dtype=float64)

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
    n9_d       = np.zeros(1,dtype=float64)

    interevent_dist = np.zeros(1,dtype=float64)
    interevent_time = np.zeros(1,dtype=float64)

    pair_number = np.zeros(1,dtype=int)

    #Variables for filling ProcSummary
    allpairnum = np.zeros(1,dtype=int)
    validpairnum = np.zeros(1,dtype=int)
    timecut = np.zeros(1,dtype=float64)

    #Open the root file that will be filled with signal IBDs
    f_root = ROOT.TFile(outfile,"recreate")

    sum_tree = ROOT.TTree("ProcSummary","Cuts applied and some meta information")
    sum_tree.Branch('allpairnum', allpairnum, 'allpairnum/I')
    sum_tree.Branch('validpairnum', validpairnum, 'validpairnum/I')

    sum_tree = st.fillSumWithCuts(sum_tree,cutdict)


    #Initialize the output root's branches
    t_root = ROOT.TTree("Output","Combined reactor positron and neutrons from MC")
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
    t_root.Branch("n9_p", n9_p, "n9_p/D")

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
    t_root.Branch("n9_d", n9_d, "n9_d/D")

    t_root.Branch('interevent_time', interevent_time,  'interevent_time/D')
    t_root.Branch('interevent_dist', interevent_dist,  'interevent_dist/D')
    t_root.Branch('pair_number', pair_number, 'pair_number/I')

#Keep track of meta information for calculating efficiencies pre-MVA entry
    pairnum = 0
    valpairnum = 0

    #Loop through input rootfiles and find IBD pairs
    print("LOOPING THROUGH INPUT SIGNAL ROOTFILES TO FIND IBDS")
    for rf in rootfiles:
        rootfile = ROOT.TFile(rf, "READ")
        dtree = rootfile.Get(datatree)

        delayedinvalid = False
        promptinvalid = False
        promptmcid = None
        entrynum = 0
   
        while True and valpairnum < max_entries:
            if float(entrynum) / 20000.0 == int(entrynum / 20000.0):
                print("ENTRYNUM: " + str(pairnum))
            #loop through and match this delayed event with all previous prompts
            if entrynum == dtree.GetEntries():
                print("BONSAI FILE WAS DEPLETED")
                break
            dtree.GetEntry(entrynum)
            #Check if this passes prompt cutdict
            if cutdict is not None and "singles" in cutdict:
                scuts = cutdict["singles"]
                for cut in scuts:
                    if scuts[cut] is not None and scuts[cut] > getattr(dtree,cut):
                        if promptmcid is None:
                            promptinvalid = True
                            break
                        else:
                            #delayed was invalid.
                            delayedinvalid = True
                            break
    
            #Fill the prompt if it's a prompt entry
            if promptmcid is None and promptinvalid is False:
                promptmcid = dtree.mcid
                nhit_p[0]     = dtree.nhit 
                x_p[0]       = dtree.x
                y_p[0]        = dtree.y
                z_p[0]      = dtree.z
                r_p[0]        = eu.radius(x_p[0],y_p[0])
                u_p[0]      = dtree.u
                v_p[0]      = dtree.v 
                w_p[0]      = dtree.w 
                mc_energy_p[0]    = dtree.mc_energy 
                good_pos_p[0] = dtree.good_pos 
                good_dir_p[0] = dtree.good_dir 
                pe_p[0]     = dtree.pe 
                closestPMT_p[0]  = dtree.closestPMT
                n9_p[0]  = dtree.n9
                entrynum+=1
                continue
            
            #If true, failed prompt event.  Keep MCID, but don't save values
            elif promptmcid is None and promptinvalid is True:
                #This entry is a failed prompt event.
                promptmcid = dtree.mcid
                entrynum+=1
                continue
  
            #Have a prompt, either passed or failed.
            pairnum+=1
            #if the prompt and delayed we have are valid, we form an IBD pair
            if promptmcid is not None and promptinvalid is False and \
                    delayedinvalid is False and promptmcid == dtree.mcid:
                nhit_d[0]     = dtree.nhit 
                x_d[0]       = dtree.x
                y_d[0]        = dtree.y
                z_d[0]      = dtree.z
                r_d[0]        = eu.radius(x_d[0],y_d[0])
                u_d[0]      = dtree.u
                v_d[0]      = dtree.v 
                w_d[0]      = dtree.w 
                mc_energy_d[0]    = dtree.mc_energy 
                good_pos_d[0] = dtree.good_pos 
                good_dir_d[0] = dtree.good_dir 
                pe_d[0]     = dtree.pe 
                closestPMT_d[0]  = dtree.closestPMT
                n9_d[0]  = dtree.n9
                entrynum+=1

            else:
                #Prompt and/or delayed failed cuts.
                entrynum+=1
                promptmcid = None
                promptinvalid = False
                delayedinvalid = False
                continue
            
            #We've formed a pair.  Re-initialize pairvalid checks for next pair
            promptmcid = None
            promptinvalid = False
            delayedinvalid = False
 
            #Check for valid interevent_dist/time, save the pair if valid.
            interevent_dist[0] = eu.innerDist(x_p[0], y_p[0], z_p[0], x_d[0],\
                    y_d[0], z_d[0])
            interevent_time[0] = dtree.dt 

            itid_dict = {"interevent_dist": interevent_dist[0], \
                    "interevent_time": interevent_time[0]}
            if cutdict is not None and "pairs" in cutdict:
                pcuts = cutdict["pairs"]
                for cut in pcuts:
                    if pcuts[cut] is not None and \
                            pcuts[cut] > itid_dict[cut]:
                        continue

            pair_number[0] = cp.deepcopy(valpairnum)
            t_root.Fill()
            valpairnum+=1
        #/while True
    allpairnum[0] = pairnum
    validpairnum[0] = valpairnum
    
    sum_tree.Fill()
    f_root.cd()
    t_root.Write()
    sum_tree.Write()
    f_root.Close()
