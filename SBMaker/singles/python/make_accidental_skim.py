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
UTHDIR = os.path.abspath(os.path.join(basepath, "..", "..", "data", "UTh"))
FVDIR = os.path.abspath(os.path.join(basepath, "..", "..", "data", "UTh", "FV"))

#Name of file that will be output
fileN = 'Accidentals_lowbkgPMTs_Combined.root'

#These are all the isotopes available in the UTh and FV directories
U_isos = ["234Pa","214Pb","214Bi","210Tl","210Bi"]
Th_isos = ["228Ac","212Pb","212Bi","208Tl"]
FV_isos = ["210Bi","210Tl","214Bi","214Pb","222Rn"]

U_files = []
Th_files = []
FV_files = []

U_entry = np.zeros(len(U_isos))
Th_entry = np.zeros(len(Th_isos))
FV_entry = np.zeros(len(FV_isos))

#The below assume secular equilibrium with U238 for all isotopes
U_rate = 2598.0 * float(len(U_isos))    #in Hz, assumes 0.43 PPM U in 3500 PMTs
                                        #PMT mass 1.4 kg
Th_rate = 2645.0* float(len(Th_isos))   #in Hz, same assumptions as U
FV_rate = 5.6   * float(len(FV_isos))   #in Hz, given by Marc Bergevin
scaler = 1.0
#U_rate = 20685.0 * float(len(U_isos))
#Th_rate = 26445.0 * float(len(Th_isos))
#scaler = 0.1

#Parameters used to define loaded values in ntuple
FV_radius = 10.82/2.  #in m
FV_height = 10.82  #in m

ACC_RATE = (U_rate + Th_rate + FV_rate)
ACC_RATE_TD = ACC_RATE / (1000./scaler) #In 1/10 of a milliseconds

print("ACC_RATE: " + str(ACC_RATE))

def shootTimeDiff(raw_freq):
    #Assume your process is poisson with an occurence of raw_freq/msec
    #on average.  We get the time diff by shooting that many events in
    #a one second timespan, sort, then get the average time difference.
    #Returns event time difference in nanoseconds
    fired_event = False
    timediff = 0.
    while not fired_event:
        if raw_freq < 20:
            num_events = pd.RandShoot_p(raw_freq,1)
        else:
            num_events = pd.RandShoot_g0(raw_freq, np.sqrt(raw_freq),1)
        event_times = np.random.rand(num_events)
        event_times.sort()
        if len(event_times) > 2:
            the_event_index = np.random.randint(1,len(event_times)-1)
            timediff += (event_times[the_event_index] - event_times[the_event_index -1])
            fired_event = True
        elif len(event_times) >0:
            timediff += 1. - event_times[0]
            fire_event = True
        else:
            timediff+=1
    return timediff * 1.0E6 * scaler

def innerDistFV(FV, FV_prev, posReco, posReco_prev):
    #First checks that the current and previous event reconstruct in the
    #FV.  If they do, returns the inner_dist_fv
    if FV==1 and FV_prev==1:
        return np.sqrt((posReco_prev.x() - posReco.x())**2 + 
                (posReco_prev.y() - posReco.y())**2 + 
                (posReco_prev.z() - posReco.z())**2)
    else:
        return -1

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

def loadBkgFiles():
    for iso in U_isos:
        filename = glob.glob(UTHDIR + "/*" + iso +"*")[0]
        rfile = ROOT.TFile(filename, "read")
        U_files.append(rfile)
    for iso in Th_isos:
        filename = glob.glob(UTHDIR + "/*" + iso +"*")[0]
        rfile = ROOT.TFile(filename, "read")
        Th_files.append(rfile)
    for iso in FV_isos:
        filename = glob.glob(FVDIR + "/*" + iso +"*")[0]
        rfile = ROOT.TFile(filename, "read")
        FV_files.append(rfile)
    print("UFILES: " + str(U_files))

def getRootFile():
    '''
    Using the defined constants above, random shoot a ROOT file to be opened.
    Also updates the entry number for the entry arrays above by 1 each time
    the filename is shot.
    '''
    shot =np.random.rand()
    if shot < (FV_rate / ACC_RATE):
        #Stuff for FV file
        index = int(np.random.rand() * len(FV_isos))
        FV_entry[index]+=1
        rfile = FV_files[index]
        evindex = int(FV_entry[index])
    elif shot < ((Th_rate + FV_rate)/ACC_RATE):
        #Stuff for Th file
        index = int(np.random.rand() * len(Th_isos))
        Th_entry[index]+=1
        rfile = Th_files[index]
        evindex = int(Th_entry[index])
    else:
        #Stuff for U file
        index = int(np.random.rand() * len(U_isos))
        U_entry[index]+=1
        rfile = U_files[index]
        evindex = int(U_entry[index])
    return rfile, evindex

if __name__ == '__main__':
    loadBkgFiles()

    #f2 = TChain('SkimFile')
    #if len(argv) >=2:
    #    fileName = "silverFiles/silver_%s-%s*" % (argv[1],argv[2])
    #else:
    #    fileName = "silverFiles/silver_*"
    #f2.Add(fileName)
    
    '''VARIABLES ASSOCIATED WITH OPENED RANDOM FILE'''
    n9_sf        = np.zeros(1,dtype=float64)
    nhit_sf      = np.zeros(1,dtype=float64)
    pe_sf     = np.zeros(1,dtype=float64)
    event_number_sf        = np.zeros(1,dtype=float64)
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
    
    t_root = ROOT.TTree("CombAcc","Combined Accidentals File")
    t_root.Branch('pe',       pe_rf,    'pe/D')
    t_root.Branch('nhit',       nhit_rf,    'nhit/D')
    t_root.Branch('n9',      n9_rf,   'n9/D')
    
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
    while (not FileDepleted) and (entrynum < 1000000):
        shotfile, evindex = getRootFile()
        shotfile.cd()
        dattree = shotfile.Get("data")
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
        #dattree.SetBranchAddress('dirReco',     dirReco_sf)
        if evindex >= dattree.GetEntries():
            FileDepleted = True
            break
        dattree.GetEntry(evindex)
        #Some bad reconstruction checks; don't want a ton of crazy nums,
        #just -1
        if nhit_sf[0] < 0 or nhit_sf[0] > 4000:
            continue
        if pe_sf[0] < 0 or abs(pe_sf[0]) > 1.E6:
            pe_rf[0] = -1.0
        else:
            pe_rf[0] = pe_sf[0] 
        if n9_sf[0] < 0 or n9_sf[0] > 4000:
            n9_rf[0] = -1.0
        else:
            n9_rf[0] = n9_sf[0]  #nextevent.n9

        entrynum += 1
        nhit_rf[0] = nhit_sf[0] #nextevent.nhit
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

        if entrynum > 0:
            interevent_time_rf[0] = shootTimeDiff(ACC_RATE_TD)
            interevent_dist_fv_rf[0] = innerDist(reco_r_prev_rf[0],
                    reco_z_prev_rf[0], reco_r_rf[0], reco_z_rf[0],
                    posReco_rf, posReco_prev_rf)


        t_root.Fill()

        if entrynum == 0:
            continue
        #Now, fill in the next tree entry with this entrys info as previous
        pe_prev_rf[0] = pe_sf[0] #nextevent.pe
        nhit_prev_rf[0] = nhit_sf[0] #nextevent.nhit
        n9_prev_rf[0] = n9_sf[0]  #nextevent.n9
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
    f_root.cd()
    t_root.Write()
    f_root.Close()
