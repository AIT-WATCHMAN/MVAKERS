#   :Example from Marc with how to build a ROOT file in pyROOT
#We'll want to take these ideas and build them into a program
#That will effectively build up our simulated FV and PMT backgrounds.
import copy as cp
import math
import time
from array import *
import numpy as np
from numpy import *
import lib.playDarts as pd

import scipy.special as sps
import ROOT
from ROOT import TChain, TFile, TMath, gROOT
from sys import stdout
import glob

import os
from sys import argv

from decimal import *

basepath = os.path.dirname(__file__)
IBDDIR = os.path.abspath(os.path.join(basepath, "..", "..", "data","16m_size"))

IBD_FILE_TITLE = "merged_ntuple_watchman_IBD_25pct_I.root"

#Parameters used to define loaded values in ntuple
FV_radius = 10.84/2.  #in m
FV_height = 10.84  #in m
TIMESFROMHIST = True #if True, the event times are all shot from a histogram
                     #parameterization based on interevent times for events
                     #w pos_goodness > 0.65, dir_goodness > 0.1, and n9 > 18.
                     #Had to add because WATCHAMKERS only adds times to these
FVONLY = True #Defines if you only take events that truly happened in the FV
TIMETHRESH = 2.50E5#We will reshoot times for IBD pairs greater than this
                   #Time or with interevent_time == 0.  There was a bug in
                   #the inner_time variable production

#Name of file that will be output
fileN = 'IBD_Signal_Skimfile.root'

def innerDist(prev_r, prev_z, r, z, posReco, posReco_prev):
    #First checks that the current and previous event reconstruct in the
    #FV.  If they do, returns the inner_dist_fv
    if (0< abs(prev_r) < FV_radius) and (0 < abs(r) < FV_radius):
        if (0 < abs(prev_z) < (FV_height/2.)) and (0 < abs(z) < (FV_height / 2.)):
            return np.sqrt((posReco_prev.x() - posReco.x())**2 + 
                    (posReco_prev.y() - posReco.y())**2 + 
                    (posReco_prev.z() - posReco.z())**2)
        else:
            return -1
    else:
        return -1

def MakeTimeHist(filepath):
    #Takes in an IBD root file, and returns a TH1F object that has the 
    #interevent_time distribution with the required parameter values per event.
    #We have to do this since interevent_times were only generated for events
    #with the parameters below.
    RESOLUTION = int(TIMETHRESH/20.0)
    timevals = ROOT.TH1F("times","times", RESOLUTION, 0, int(TIMETHRESH))
    IBD_file = ROOT.TFile(filepath,"read")
    n9_sf        = np.zeros(1,dtype=float64)
    true_r_sf = np.zeros(1,dtype=float64)
    true_z_sf = np.zeros(1,dtype=float64)
    pos_goodness_sf   = np.zeros(1,dtype=float64)
    dir_goodness_sf     = np.zeros(1,dtype=float64)
    all_ev_sf = np.zeros(1, dtype=int)
    all_ev_tot_sf = np.zeros(1, dtype=int)
    interevent_time_sf = np.zeros(1, dtype=float64)
    FileDepleted = False
    entrynum=0
    while (not FileDepleted) and (entrynum < 10000000):
        IBD_file.cd()
        dattree = IBD_file.Get("data")
        dattree.SetBranchAddress('n9',      n9_sf)
        dattree.SetBranchAddress('pos_goodness',        pos_goodness_sf)
        dattree.SetBranchAddress('dir_goodness', dir_goodness_sf)
        dattree.SetBranchAddress('true_r',        true_r_sf)
        dattree.SetBranchAddress('true_z', true_z_sf)
        dattree.SetBranchAddress('all_ev', all_ev_sf)
        dattree.SetBranchAddress('all_ev_tot', all_ev_tot_sf)
        dattree.SetBranchAddress('inner_time', interevent_time_sf)
        if entrynum >= dattree.GetEntries():
            FileDepleted = True
            print("FILE DEPLETED.")
            break
        dattree.GetEntry(entrynum)
        entrynum+=1
        #If we have a delayed entry that has the correct parameters for a 
        #Valid time, fill it in
        #if FVONLY, then skip events that are not in the FV defined
        if FVONLY is True:
            if true_r_sf[0] > FV_radius or abs(true_z_sf[0]) > FV_height/2.:
                haveprompt = False
                continue
        if pos_goodness_sf[0] > 0.65 and dir_goodness_sf[0] > 0.1 and \
                n9_sf[0] > 10:
            if all_ev_sf[0] == 2 and all_ev_tot_sf[0] == 2:
                timevals.Fill(interevent_time_sf[0])
    print("ENTRYNUM MET")
    return timevals

def wald(x, p):
    if x[0]== 0:
        print("Cannot use x == 0.  Setting it close...")
        x[0] += 0.00000001
    return  p[2] * np.sqrt(p[0] / (2.* np.pi *(x[0]**p[3]))) * np.exp(-(p[0]*((x[0]-p[1])**2))/(2.*(p[1]**2)*x[0]))
    #return p[0] * np.exp(-p[1] * x[0]) * (1.0 - sps.erf(((p[2]**2 / p[1])-x[0])/(np.sqrt(2)*p[2])))

def risefall(x, p):
    if x[0]== 0:
        print("Cannot use x == 0.  Setting it close...")
        x[0] += 0.00000001
    return  p[0] * (np.exp(-x[0]/p[1]) - np.exp(-x[0]/p[2]))
    #return p[0] * np.exp(-p[1] * x[0]) * (1.0 - sps.erf(((p[2]**2 / p[1])-x[0])/(np.sqrt(2)*p[2])))

def MakeTimeFit_risefall(timehist):
    #Function takes in a time histogram and fits a polynomial to it. Returns
    #The polynomial function for random firing of values from
    TimeFit = ROOT.TF1('TimeFit', risefall, 1,
            float(TIMETHRESH), 3)
    TimeFit.SetParameter(0, 100000.0)
    #TimeFit.SetParLimits(0, 0, )
    TimeFit.SetParameter(1, 100000.0)
    #TimeFit.SetParLimits(1, 0, 1E7)
    TimeFit.SetParameter(2, 1000)
    #TimeFit.SetParameter(3,1.5)
    TimeFit.SetParNames('A','t1','t2')
    TimeFit.SetLineColor(2)
    TimeFit.SetLineWidth(4)
    TimeFit.SetLineStyle(2)
    ROOT.gStyle.SetOptFit(0157)
    timehist.Fit('TimeFit','Lq')
    return TimeFit

def MakeTimeFit_wald(timehist):
    #Function takes in a time histogram and fits a polynomial to it. Returns
    #The polynomial function for random firing of values from
    TimeFit = ROOT.TF1('TimeFit', wald, 1,
            float(TIMETHRESH), 4)
    TimeFit.SetParameter(0, 100000.0)
    TimeFit.SetParLimits(0, 0, 1E7)
    TimeFit.SetParameter(1, 100000.0)
    TimeFit.SetParLimits(1, 0, 1E7)
    TimeFit.SetParameter(2, 1000)
    TimeFit.SetParameter(3,1.5)
    TimeFit.SetParNames('lambda','mu','C')
    TimeFit.SetLineColor(2)
    TimeFit.SetLineWidth(4)
    TimeFit.SetLineStyle(2)
    ROOT.gStyle.SetOptFit(0157)
    timehist.Fit('TimeFit','Lq')
    return TimeFit

if __name__ == '__main__':
    timehistogram = MakeTimeHist(IBDDIR+"/"+IBD_FILE_TITLE)
    timefit = MakeTimeFit_wald(timehistogram)
    IBD_file = ROOT.TFile(IBDDIR+"/"+IBD_FILE_TITLE,"read")
    IBD_entrynum = 0


    '''VARIABLES ASSOCIATED WITH OPENED RANDOM FILE'''
    n9_sf        = np.zeros(1,dtype=float64)
    nhit_sf      = np.zeros(1,dtype=float64)
    pe_sf     = np.zeros(1,dtype=float64)
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
    
    t_root = ROOT.TTree("data","Combined IBD prompt/delayed files")
    t_root.Branch('pe',       pe_rf,    'pe/D')
    t_root.Branch('nhit',       nhit_rf,    'nhit/D')
    t_root.Branch('n9',      n9_rf,   'n9/D')
    
    t_root.Branch('event_number',        event_number_rf,     'event_number/D')
    t_root.Branch('mc_prim_energy',        mc_prim_energy_rf ,      'mc_prim_energy/D')
    t_root.Branch('FV',        FV_rf ,      'FV/I')
    t_root.Branch('pos_goodness',        pos_goodness_rf ,      'pos_goodness/D')
    t_root.Branch('posReco',         posReco_rf, 'posReco')
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
    
    t_root.Branch('mc_prim_energy_prev',        mc_prim_energy_prev_rf ,      'mc_prim_energy_prev/D')
    t_root.Branch('FV_prev',        FV_prev_rf ,      'FV_prev/I')
    t_root.Branch('pos_goodness_prev',        pos_goodness_prev_rf ,      'pos_goodness_prev/D')
    t_root.Branch('posReco_prev',     posReco_prev_rf,'TVector3')
    t_root.Branch('reco_r_prev',     reco_r_prev_rf,'reco_r_prev/D')
    t_root.Branch('reco_z_prev',     reco_z_prev_rf,'reco_z_prev/D')
    #t_root.Branch('posTruth_prev','TVector3',     posTruth_rf)
    t_root.Branch('true_r_prev', true_r_prev_rf,  'true_r_prev/D')
    t_root.Branch('true_z_prev', true_z_prev_rf,  'true_z_prev/D')
    t_root.Branch('dir_goodness_prev', dir_goodness_prev_rf, 'dir_goodness_prev/D')
    #t_root.Branch('dirReco_prev','TVector3', dirReco_rf)



    #The following continues as long as the selected file still has entrys left
    FileDepleted = False
    entrynum = 0
    IBD_num = 0
    prompt_evnum = 0
    have_prompt = False
    while (not FileDepleted) and (entrynum < 10000000):
        IBD_file.cd()
        dattree = IBD_file.Get("data")
        dattree.SetBranchAddress('pe',      pe_sf)
        dattree.SetBranchAddress('nhit',       nhit_sf)
        dattree.SetBranchAddress('n9',      n9_sf)
        
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
        dattree.SetBranchAddress('inner_time', interevent_time_sf)

        #dattree.SetBranchAddress('dirReco',     dirReco_sf)
        if entrynum >= dattree.GetEntries():
            FileDepleted = True
            break
        dattree.GetEntry(entrynum)
        entrynum+=1
        #if FVONLY, then skip events that are not in the FV defined
        if FVONLY is True:
            if true_r_sf[0] > FV_radius or abs(true_z_sf[0]) > FV_height/2.:
                haveprompt = False
                continue
        #Some bad reconstruction checks; don't want a ton of crazy nums,
        #just -1
        if nhit_sf[0] < 0 or nhit_sf[0] > 4000:
            haveprompt = False
            continue
        current_event_num = cp.deepcopy(event_number_sf[0])
        current_all_ev_tot = cp.deepcopy(all_ev_tot_sf[0])
        current_all_ev = cp.deepcopy(all_ev_sf[0])
        if current_all_ev == 1 and current_all_ev_tot == 2 and have_prompt is False:
            #We fill our prev values, then continue
            if pe_sf[0] < 0 or abs(pe_sf[0]) > 1.E6:
                pe_prev_rf[0] = -1.0
            else:
                pe_prev_rf[0] = pe_sf[0] 
            if n9_sf[0] < 0 or n9_sf[0] > 4000:
                n9_prev_rf[0] = -1.0
            else:
                n9_prev_rf[0] = n9_sf[0]  #nextevent.n9

            nhit_prev_rf[0] = nhit_sf[0] #nextevent.nhit
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
            #if interevent_time_sf[0] > TIMETHRESH:
            #    have_prompt = False
            #    continue
            IBD_num += 1
            if pe_sf[0] < 0 or abs(pe_sf[0]) > 1.0E6:
                pe_rf[0] = -1.0
            else:
                pe_rf[0] = pe_sf[0] 
            if n9_sf[0] < 0 or n9_sf[0] > 4000:
                n9_rf[0] = -1.0
            else:
                n9_rf[0] = n9_sf[0]  #nextevent.n9

            nhit_rf[0] = nhit_sf[0] #nextevent.nhit
            event_number_rf[0] = entrynum
            mc_prim_energy_rf[0] = mc_prim_energy_sf[0] #nextevent.mc_prim_energy
            FV_rf[0] = FV_sf[0]  #nextevent.pos_goodness
            pos_goodness_rf[0] = pos_goodness_sf[0]  #nextevent.pos_goodness
            posReco_rf = cp.deepcopy(posReco_sf)
            reco_r_rf[0] = reco_r_sf[0]  #nextevent.reco_r
            reco_z_rf[0] = reco_z_sf[0]  #nextevent.reco_z
            #posTruth_rf = posTruth_sf
            true_r_rf[0] = true_r_sf[0]  #nextevent.true_r
            true_z_rf[0] = true_z_sf[0]  #nextevent.true_z
            dir_goodness_rf[0] = dir_goodness_sf[0] #nextevent.dir_goodness
            #dirReco_rf = dirReco_sf
            if TIMESFROMHIST is True:
                interevent_time_rf[0] = float(timefit.GetRandom())
            else:
                interevent_time_rf[0] = interevent_time_sf[0]
            interevent_dist_fv_rf[0] = innerDist(reco_r_prev_rf[0], \
                    reco_z_prev_rf[0], reco_r_rf[0], reco_z_rf[0], \
                    posReco_rf, posReco_prev_rf)
            #done getting an IBD
            t_root.Fill()
            have_prompt = False
            continue
        else:
            #The interevent distance was madness. skip forward
            have_prompt = False
            continue
    print("FINAL ENTRY NUM: " + str(entrynum))
    print("IBD NUM: " + str(IBD_num))
    f_root.cd()
    t_root.Write()
    f_root.Close()
