#:Example from Marc with how to build a ROOT file in pyROOT
#We'll want to take these ideas and build them into a program
#That will effectively build up our simulated FV and PMT backgrounds.
import copy as cp
import math
import time
from array import *
import numpy as np
from numpy import *
import lib.playDarts as pd

import ROOT as ROOT
from ROOT import TChain, TFile, gROOT
from sys import stdout
import glob

import os
from sys import argv

from decimal import *

basepath = os.path.dirname(__file__)
IBDDIR = os.path.abspath(os.path.join(basepath, "..", "..", "data"))

IBD_FILE_TITLE = "merged_ntuple_watchman_IBD_25pct_I.root"

#Name of file that will be output
fileN = 'IBD_Signal_Skimfile.root'

if __name__ == '__main__':
    IBD_file = ROOT.TFile(IBDDIR+"/"+IBD_FILE_TITLE,"read")
    IBD_entrynum = 0


    '''VARIABLES ASSOCIATED WITH OPENED RANDOM FILE'''
    n9_sf        = np.zeros(1,dtype=float64)
    nhit_sf      = np.zeros(1,dtype=float64)
    pe_sf     = np.zeros(1,dtype=float64)
    detected_ev_sf       	= np.zeros(1,dtype=float64)
    event_number_sf        = np.zeros(1,dtype=int)
    mc_prim_energy_sf = np.zeros(1,dtype=float64)
    FV_sf = np.zeros(1, dtype=float64)
    pos_goodness_sf   = np.zeros(1,dtype=float64)
    posReco_sf = ROOT.TVector3()
    reco_r_sf   = np.zeros(1,dtype=float64)
    reco_z_sf = np.zeros(1,dtype=float64)
    #posTruth_sf   = ROOT.TVector3()
    true_r_sf     = np.zeros(1,dtype=float64)
    true_z_sf     = np.zeros(1,dtype=float64)
    dir_goodness_sf     = np.zeros(1,dtype=float64)
    all_ev_sf = np.zeros(1, dtype=int)
    all_ev_tot_sf = np.zeros(1, dtype=int)
    interevent_dist_fv_sf = np.zeros(1, dtype=float64)
    interevent_time_sf = np.zeros(1, dtype=float64)
    #dirReco_sf     = ROOT.TVector3()
 

    '''VARIABLES ASSOCIATED WITH SKIM FILE'''

    '''Set up variables for root tree'''
    n9_rf        = np.zeros(1,dtype=float64)
    nhit_rf      = np.zeros(1,dtype=float64)
    pe_rf     = np.zeros(1,dtype=float64)
    detected_ev_rf       	= np.zeros(1,dtype=float64)
    event_number_rf        = np.zeros(1,dtype=float64)
    mc_prim_energy_rf = np.zeros(1,dtype=float64)
    FV_rf = np.zeros(1, dtype=int)
    pos_goodness_rf   = np.zeros(1,dtype=float64)
    posReco_rf = ROOT.TVector3()
    reco_r_rf   = np.zeros(1,dtype=float64)
    reco_z_rf = np.zeros(1,dtype=float64)
    #posTruth_rf   = ROOT.TVector3()
    true_r_rf     = np.zeros(1,dtype=float64)
    true_z_rf     = np.zeros(1,dtype=float64)
    dir_goodness_rf     = np.zeros(1,dtype=float64)
    #dirReco_rf     = ROOT.TVector3()

    interevent_time_rf     = np.zeros(1,dtype=float64)
    interevent_dist_fv_rf     = np.zeros(1,dtype=float64)

    n9_prev_rf        = np.zeros(1,dtype=float64)
    nhit_prev_rf      = np.zeros(1,dtype=float64)
    pe_prev_rf     = np.zeros(1,dtype=float64)
    detected_ev_prev_rf       	= np.zeros(1,dtype=float64)
    mc_prim_energy_prev_rf = np.zeros(1,dtype=float64)
    FV_prev_rf   = np.zeros(1,dtype=int)
    pos_goodness_prev_rf   = np.zeros(1,dtype=float64)
    posReco_prev_rf = ROOT.TVector3() 
    reco_r_prev_rf   = np.zeros(1,dtype=float64)
    reco_z_prev_rf = np.zeros(1,dtype=float64)
    #posTruth_prev_rf   = ROOT.TVector3()
    true_r_prev_rf     = np.zeros(1,dtype=float64)
    true_z_prev_rf     = np.zeros(1,dtype=float64)
    dir_goodness_prev_rf     = np.zeros(1,dtype=float64)
    #dirReco_prev_rf     = ROOT.TVector3()
      
    '''Open a root file with name of dataType'''


    f_root = ROOT.TFile(fileN,"recreate")
    
    '''Set up the tree and branch of variables one wishes to save'''
    
    t_root = ROOT.TTree("CombAcc","Combined Accidentals File")
    t_root.Branch('pe',       pe_rf,    'pe/D')
    t_root.Branch('nhit',       nhit_rf,    'nhit/D')
    t_root.Branch('n9',      n9_rf,   'n9/D')
    
    t_root.Branch('detected_ev',      detected_ev_rf,       'detected_ev/I')
    t_root.Branch('event_number',        event_number_rf,     'event_number/D')
    t_root.Branch('mc_prim_energy',        mc_prim_energy_rf ,      'mc_prim_energy/D')
    t_root.Branch('FV',        FV_rf ,      'FV/I')
    t_root.Branch('pos_goodness',        pos_goodness_rf ,      'pos_goodness/D')
    t_root.Branch('posReco',         posReco_rf, 'TVector3')
    t_root.Branch('reco_r',     reco_r_rf,'reco_r/D')
    t_root.Branch('reco_z',     reco_z_rf,'reco_z/D')
    #t_root.Branch('posTruth','TVector3',     posTruth_rf)
    t_root.Branch('true_r', true_r_rf,  'true_r/D')
    t_root.Branch('true_z', true_z_rf,  'true_z/D')
    t_root.Branch('dir_goodness', dir_goodness_rf, 'dir_goodness/D')
    #t_root.Branch('dirReco','TVector3', dirReco_rf)

    t_root.Branch('interevent_time', interevent_time_rf,  'interevent_time/D')
    t_root.Branch('interevent_dist_fv', interevent_dist_fv_rf,  'interevent_dist_fv/D')

    t_root.Branch('pe_prev',       pe_prev_rf,    'pe_prev/D')
    t_root.Branch('nhit_prev',       nhit_prev_rf,    'nhit_prev/D')
    t_root.Branch('n9_prev',      n9_prev_rf,   'n9_prev/D')
    
    t_root.Branch('detected_ev_prev',      detected_ev_prev_rf,       'detected_ev_prev/I')
    t_root.Branch('mc_prim_energy_prev',        mc_prim_energy_prev_rf ,      'mc_prim_energy_prev/D')
    t_root.Branch('FV_prev',        FV_prev_rf ,      'FV_prev/I')
    t_root.Branch('pos_goodness_prev',        pos_goodness_prev_rf ,      'pos_goodness_prev/D')
    t_root.Branch('posReco_prev',     posReco_prev_rf,'TVector3')
    t_root.Branch('reco_r_prev',     reco_r_prev_rf,'reco_r_prev/D')
    t_root.Branch('reco_z_prev',     reco_z_prev_rf,'reco_z_prev/D')
    #t_root.Branch('posTruth_prev','TVector3',     posTruth_rf)
    t_root.Branch('true_r_prev', true_r_prev_rf,  'true_r_prev/D')
    t_root.Branch('true_z_prev', true_z_prev_rf,  'true_z_prev/D')
    t_root.Branch('dir_goodness_prev.g', dir_goodness_rf, 'dir_goodness/D')
    #t_root.Branch('dirReco_prev','TVector3', dirReco_rf)



    #The following continues as long as the selected file still has entrys left
    FileDepleted = False
    entrynum = 0
    IBD_num = 0
    prompt_evnum = 0
    have_prompt = False
    while (not FileDepleted) and (entrynum < 1000000):
        IBD_file.cd()
        dattree = IBD_file.Get("data")
        dattree.SetBranchAddress('pe',      pe_sf)
        dattree.SetBranchAddress('nhit',       nhit_sf)
        dattree.SetBranchAddress('n9',      n9_sf)
        
        dattree.SetBranchAddress('detected_ev',      detected_ev_sf)
        dattree.SetBranchAddress('event_number',        event_number_sf)
        dattree.SetBranchAddress('mc_prim_energy',        mc_prim_energy_sf)
        dattree.SetBranchAddress('FV',        FV_sf)
        dattree.SetBranchAddress('pos_goodness',        pos_goodness_sf)
        dattree.SetBranchAddress('posReco',    posReco_sf)
        dattree.SetBranchAddress('reco_r',     reco_r_sf)
        dattree.SetBranchAddress('reco_z',     reco_z_sf)
        #dattree.SetBranchAddress('posTruth',     posTruth_sf)
        dattree.SetBranchAddress('true_r', true_r_sf)
        dattree.SetBranchAddress('true_z', true_z_sf)
        dattree.SetBranchAddress('dir_goodness', dir_goodness_sf)
        dattree.SetBranchAddress('all_ev', all_ev_sf)
        dattree.SetBranchAddress('all_ev_tot', all_ev_tot_sf)
        dattree.SetBranchAddress('inner_dist_fv', interevent_dist_fv_sf)
        dattree.SetBranchAddress('inner_time', interevent_time_sf)

        #dattree.SetBranchAddress('dirReco',     dirReco_sf)
        if entrynum >= dattree.GetEntries():
            FileDepleted = True
            break
        dattree.GetEntry(entrynum)
        entrynum+=1
        if pe_sf[0] < 0 or abs(pe_sf[0]) > 1.E6:
            have_prompt = False
            continue
        if nhit_sf[0] < 0 or nhit_sf[0] > 4000:
            have_prompt = False
            continue
        if n9_sf[0] < 0 or n9_sf[0] > 4000:
            have_prompt = False
            continue
        current_event_num = cp.deepcopy(event_number_sf[0])
        current_all_ev_tot = cp.deepcopy(all_ev_tot_sf[0])
        current_all_ev = cp.deepcopy(all_ev_sf[0])
        if current_all_ev == 1 and current_all_ev_tot == 2 and have_prompt is False:
            #We fill our prev values, then continue
            pe_prev_rf[0] = pe_sf[0] #nextevent.pe
            nhit_prev_rf[0] = nhit_sf[0] #nextevent.nhit
            n9_prev_rf[0] = n9_sf[0]  #nextevent.n9
            detected_ev_prev_rf[0] = detected_ev_sf[0] #nextevent.detected_ev
            mc_prim_energy_prev_rf[0] = mc_prim_energy_sf[0] #nextevent.mc_prim_energy
            FV_prev_rf[0] = FV_sf[0]
            pos_goodness_prev_rf[0] = pos_goodness_sf[0]  #nextevent.pos_goodness
            posReco_prev_rf = cp.deepcopy(posReco_sf) #nextevent.posReco
            reco_r_prev_rf[0] = reco_r_sf[0]  #nextevent.reco_r
            reco_z_prev_rf[0] = reco_z_sf[0]  #nextevent.reco_z
            #posTruth_prev_rf = posTruth_sf #cp.deepcopy(posTruth_sf)
            true_r_prev_rf[0] = true_r_sf[0]  #nextevent.true_r
            true_z_prev_rf[0] = true_z_sf[0]  #nextevent.true_z
            dir_goodness_prev_rf[0] = dir_goodness_sf[0] #nextevent.dir_goodness
            #dirReco_prev_rf = dirReco_sf #cp.deepcopy(dirReco_sf)
            have_prompt = True
            prompt_evnum = current_event_num
            continue
        if current_all_ev == 2 and current_all_ev_tot == 2 and \
                have_prompt is True and current_event_num == prompt_evnum:
            IBD_num += 1
            pe_rf[0] = pe_sf[0] 
            nhit_rf[0] = nhit_sf[0] #nextevent.nhit
            n9_rf[0] = n9_sf[0]  #nextevent.n9
            detected_ev_rf[0] = detected_ev_sf[0] #nextevent.detected_ev
            event_number_rf[0] = entrynum
            mc_prim_energy_rf[0] = mc_prim_energy_sf[0] #nextevent.mc_prim_energy
            FV_rf[0] = FV_sf[0]  #nextevent.pos_goodness
            pos_goodness_rf[0] = pos_goodness_sf[0]  #nextevent.pos_goodness
            posReco_rf = posReco_sf
            reco_r_rf[0] = reco_r_sf[0]  #nextevent.reco_r
            reco_z_rf[0] = reco_z_sf[0]  #nextevent.reco_z
            #posTruth_rf = posTruth_sf
            true_r_rf[0] = true_r_sf[0]  #nextevent.true_r
            true_z_rf[0] = true_z_sf[0]  #nextevent.true_z
            dir_goodness_rf[0] = dir_goodness_sf[0] #nextevent.dir_goodness
            #dirReco_rf = dirReco_sf
    
            interevent_time_rf[0] = interevent_time_sf[0]
            interevent_dist_fv_rf[0] = interevent_dist_fv_sf[0]
            #done getting an IBD
            t_root.Fill()
            have_prompt = False
            continue
    print("FINAL ENTRY NUM: " + str(entrynum))
    print("IBD NUM: " + str(IBD_num))
    f_root.cd()
    t_root.Write()
    f_root.Close()
