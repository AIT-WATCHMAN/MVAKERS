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
MAINDIR = "pass2_root_files_tankRadius_10000.000000_halfHeight_10000.000000_shieldThickness_1500.000000_U238_PPM_0.341000_Th232_PPM_1.330000_Rn222_0.001400"
ANALYZEDIR = os.path.abspath(os.path.join(basepath, "..", "..","data", MAINDIR, "25pct"))

#Name of file that will be output
fileN = 'tester.root'

#These are all the isotopes available in the UTh and FV directories
Bkg_types = ["WV", "PMT"]  #watchmakers output has these in accidental names
Bkg_filelocs = []
Bkg_files = []
for bkgtype in Bkg_types:
    Bkg_filelocs = Bkg_filelocs + glob.glob(ANALYZEDIR + "/" + bkgtype)
for loc in Bkg_filelocs:
    rfile = ROOT.TFile(loc, "read")
    Bkg_files.append(rfile)
   

#FIXME: have to program this function to read from runSummary trees
#See ./lib/root_reader.py for notes on how to do dis
Bkg_rates = rr.GetRates_Valids(Bkg_files)
Bkg_entrynums = np.zeros(len(Bkg_files))

#Parameters used to define loaded values in ntuple
FV_radius = 10.84/2.  #in m
FV_height = 10.84  #in m
TIMETHRESH = 1.5E5  #Time window, in nanoseconds, where IBD pairs are searched

ACC_RATE = np.sum(Bkg_rates)
print("RAW RATE: " + str(ACC_RATE)) 

#FIXME: Let's do time-to-next event like watchmakers. FIND IT

def loadNewEvent(bufffile, entries, timediffs):
    '''
    Using the loaded-in background files, shoot the next event's information,
    including file it's in, it's entry number, and the time since last event
    '''
    shot =np.random.rand()
    #Assuming Bkg_rates is a numpy array
    for i in xrange(len(Bkg_rates)):
        if i > 0:
            if shot < (Bkg_rates[0:i] / Bkg_rates[0:len(Bkg_rates)]):
            Bkg_entrynums[i]+=1
            entries.append(int(Bkg_entrynums[i]))
            bufffile.append(Bkg_files[i])
    #FIXME: Need to write timetonextevent function
    timediffs.append(timetonextevent(ACC_RATE))
    return bufffile, entries, timediffs

def deleteOld(bufffiles, entries, timediffs):
    '''
    Delete entries at the start of each array until the total time difference
    is less than TIMETHRESH defined at the top of the file.
    '''
    below_threshold = False
    while not below_threshold:
        totaltime = sum(timediffs[1:len(timediffs)])
        if totaltime <= TIMETHRESH:
            below_threshold = True
            continue
        else:
            del bufffiles[0]
            del entries[0]
            del timediffs[0]
            continue     
    return bufffiles, entries, timediffs
       
        
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
    good_pos_sf   = np.zeros(1,dtype=float64)
    u_sf   = np.zeros(1,dtype=float64)
    v_sf   = np.zeros(1,dtype=float64)
    w_sf   = np.zeros(1,dtype=float64)
    x_sf   = np.zeros(1,dtype=float64)
    y_sf   = np.zeros(1,dtype=float64)
    z_sf   = np.zeros(1,dtype=float64)
    reco_z_sf = np.zeros(1,dtype=float64)
    good_dir_sf     = np.zeros(1,dtype=float64)

    n9_prev_sf        = np.zeros(1,dtype=float64)
    nhit_prev_sf      = np.zeros(1,dtype=float64)
    pe_prev_sf     = np.zeros(1,dtype=float64)
    event_number_prev_sf        = np.zeros(1,dtype=float64)
    good_pos_prev_sf   = np.zeros(1,dtype=float64)
    u_prev_sf   = np.zeros(1,dtype=float64)
    v_prev_sf   = np.zeros(1,dtype=float64)
    w_prev_sf   = np.zeros(1,dtype=float64)
    x_prev_sf   = np.zeros(1,dtype=float64)
    y_prev_sf   = np.zeros(1,dtype=float64)
    z_prev_sf   = np.zeros(1,dtype=float64)
    reco_z_prev_sf = np.zeros(1,dtype=float64)
    good_dir_prev_sf     = np.zeros(1,dtype=float64)
 
        '''VARIABLES ASSOCIATED WITH SKIM FILE'''

    '''Set up variables for root tree'''
    n9_rf        = np.zeros(1,dtype=float64)
    nhit_rf      = np.zeros(1,dtype=float64)
    pe_rf     = np.zeros(1,dtype=float64)
    event_number_rf        = np.zeros(1,dtype=float64)
    good_pos_rf   = np.zeros(1,dtype=float64)
    u_rf   = np.zeros(1,dtype=float64)
    v_rf   = np.zeros(1,dtype=float64)
    w_rf   = np.zeros(1,dtype=float64)
    x_rf   = np.zeros(1,dtype=float64)
    y_rf   = np.zeros(1,dtype=float64)
    z_rf   = np.zeros(1,dtype=float64)
    reco_z_rf = np.zeros(1,dtype=float64)
    good_dir_rf     = np.zeros(1,dtype=float64)

    n9_prev_rf        = np.zeros(1,dtype=float64)
    nhit_prev_rf      = np.zeros(1,dtype=float64)
    pe_prev_rf     = np.zeros(1,dtype=float64)
    event_number_prev_rf        = np.zeros(1,dtype=float64)
    good_pos_prev_rf   = np.zeros(1,dtype=float64)
    u_prev_rf   = np.zeros(1,dtype=float64)
    v_prev_rf   = np.zeros(1,dtype=float64)
    w_prev_rf   = np.zeros(1,dtype=float64)
    x_prev_rf   = np.zeros(1,dtype=float64)
    y_prev_rf   = np.zeros(1,dtype=float64)
    z_prev_rf   = np.zeros(1,dtype=float64)
    reco_z_prev_rf = np.zeros(1,dtype=float64)
    good_dir_prev_rf     = np.zeros(1,dtype=float64)
 
    '''Open a root file with name of dataType'''

    f_root = ROOT.TFile(fileN,"recreate")
    
    '''Set up the tree and branch of variables one wishes to save'''
    
    t_root = ROOT.TTree("CombAcc","Combined Accidentals File")
    t_root.Branch('pe',       pe_rf,    'pe/D')
    t_root.Branch('nhit',       nhit_rf,    'nhit/D')
    t_root.Branch('n9',      n9_rf,   'n9/D')
    
    t_root.Branch('event_number',        event_number_rf,     'event_number/D')
    t_root.Branch('good_pos',        good_pos_rf ,      'good_pos/D')
    t_root.Branch('u',     u_rf,'u/D')
    t_root.Branch('v',     v_rf,'v/D')
    t_root.Branch('w',     w_rf,'w/D')
    t_root.Branch('x',     x_rf,'x/D')
    t_root.Branch('y',     y_rf,'y/D')
    t_root.Branch('z',     z_rf,'z/D')
    t_root.Branch('good_dir', good_dir_rf, 'good_dir/D')

    t_root.Branch('interevent_time', interevent_time_rf,  'interevent_time/D')
    t_root.Branch('interevent_dist_fv', interevent_dist_fv_rf,  'interevent_dist_fv/D')

    t_root.Branch('pe_prev',       pe_prev_rf,    'pe_prev/D')
    t_root.Branch('nhit_prev',       nhit_prev_rf,    'nhit_prev/D')
    t_root.Branch('n9_prev',      n9_prev_rf,   'n9_prev/D')
    
    t_root.Branch('event_number_prev',        event_number_prev_rf,     'event_number_prev/D')
    t_root.Branch('good_pos_prev',        good_pos_prev_rf ,      'good_pos_prev/D')
    t_root.Branch('u_prev',     u_prev_rf,'u_prev/D')
    t_root.Branch('v_prev',     v_prev_rf,'v_prev/D')
    t_root.Branch('w_prev',     w_prev_rf,'w_prev/D')
    t_root.Branch('x_prev',     x_prev_rf,'x_prev/D')
    t_root.Branch('y_prev',     y_prev_rf,'y_prev/D')
    t_root.Branch('z_prev',     z_prev_rf,'z_prev/D')
    t_root.Branch('good_dir_prev', good_dir_prev_rf, 'good_dir_prev/D')


    #To properly pair all events with a time separation < TIMETHRESH, we have a
    #running buffer of event information within our time window.
    Buffer_files = []
    Buffer_entries = []
    Buffer_timediffs = []

    #The following continues as long as the selected file still has entrys left
    FileDepleted = False
    entrynum = 0
    while (not FileDepleted) and (entrynum < 100000000):
        if float(entrynum) / 20000.0 == int(entrynum / 20000.0):
            print("ENTRYNUM " + str(entrynum))
        Buffer_files, Buffer_entries, Buffer_timediffs = \
                loadNewEvent(Buffer_files, 
                Buffer_entries, Buffer_timediffs)
        #Remove events at start of entry outside the range of the newly added
        #event info
        Buffer_files, Buffer_entries, Buffer_timediffs = \
                deleteOld(Buffer_files, Buffer_entries, 
                Buffer_timediffs)
        if len(Buffer_timediffs) <= 1:
            continue
        #Now, build the pairs for the newest event with each event within the
        #time window
        delfile_index = len(Buffer_timediffs) - 1
        delayedfile = Buffer_files[delfile_index]
        for i in xrange(delfile_index):
            delayedfile.cd()
            deltree = delayedfile.Get("data")
            deltree.SetBranchAddress('pe',      pe_sf)
            deltree.SetBranchAddress('nhit',       nhit_sf)
            deltree.SetBranchAddress('n9',      n9_sf)
            
            deltree.SetBranchAddress('event_number',        event_number_sf)
            deltree.SetBranchAddress('good_pos',        good_pos_sf)
            deltree.SetBranchAddress('posReco',    posReco_sf)
            deltree.SetBranchAddress('u',     u_sf)
            deltree.SetBranchAddress('reco_z',     reco_z_sf)
            #deltree.SetBranchAddress('posTruth',     posTruth_sf)
            deltree.SetBranchAddress('true_r', true_r_sf)
            deltree.SetBranchAddress('true_z', true_z_sf)
            deltree.SetBranchAddress('good_dir', good_dir_sf)
            #deltree.SetBranchAddress('dirReco',     dirReco_sf)
            if Buffer_entries[delfile_index] >= deltree.GetEntries():
                FileDepleted = True
                break
            deltree.GetEntry(Buffer_entries[delfile_index])
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

            nhit_rf[0] = nhit_sf[0] #nextevent.nhit
            mc_prim_energy_rf[0] = mc_prim_energy_sf[0] #nextevent.mc_prim_energy
            FV_rf[0] = FV_sf[0]  #nextevent.good_pos
            good_pos_rf[0] = good_pos_sf[0]  #nextevent.good_pos
            posReco_rf = posReco_sf
            u_rf[0] = u_sf[0]  #nextevent.u
            reco_z_rf[0] = reco_z_sf[0]  #nextevent.reco_z
            #posTruth_rf = posTruth_sf
            true_r_rf[0] = true_r_sf[0]  #nextevent.true_r
            true_z_rf[0] = true_z_sf[0]  #nextevent.true_z
            good_dir_rf[0] = good_dir_sf[0] #nextevent.good_dir
            #dirReco_rf = dirReco_sf
    
            promptfile = Buffer_files[i]
            prompttree = promptfile.Get("data")
            prompttree.SetBranchAddress('pe',      pe_prev_sf)
            prompttree.SetBranchAddress('nhit',       nhit_prev_sf)
            prompttree.SetBranchAddress('n9',      n9_prev_sf)
            
            prompttree.SetBranchAddress('event_number',        event_number_prev_sf)
            prompttree.SetBranchAddress('mc_prim_energy',        mc_prim_energy_prev_sf)
            prompttree.SetBranchAddress('FV',        FV_prev_sf)
            prompttree.SetBranchAddress('good_pos',        good_pos_prev_sf)
            prompttree.SetBranchAddress('posReco',    posReco_prev_sf)
            prompttree.SetBranchAddress('u',     u_prev_sf)
            prompttree.SetBranchAddress('reco_z',     reco_z_prev_sf)
            #prompttree.SetBranchAddress('posTruth',     posTruth_prev_sf)
            prompttree.SetBranchAddress('true_r', true_r_prev_sf)
            prompttree.SetBranchAddress('true_z', true_z_prev_sf)
            prompttree.SetBranchAddress('good_dir', good_dir_prev_sf)
            #prompttree.SetBranchAddress('dirReco',     dirReco_prev_sf)
            if Buffer_entries[i] >= prompttree.GetEntries():
                FileDepleted = True
                break
           #Now, fill in the next tree entry with this entrys info as previous
            prompttree.GetEntry(Buffer_entries[i])
            if nhit_prev_sf[0] < 0 or nhit_prev_sf[0] > 4000:
                continue
            if pe_prev_sf[0] < 0 or abs(pe_prev_sf[0]) > 1.E6:
                pe_prev_rf[0] = -1.0
            else:
                pe_prev_rf[0] = pe_prev_sf[0] 
            if n9_prev_sf[0] < 0 or n9_prev_sf[0] > 4000:
                n9_prev_rf[0] = -1.0
            else:
                n9_prev_rf[0] = n9_prev_sf[0]  #nextevent.n9

            nhit_prev_rf[0] = nhit_prev_sf[0] #nextevent.nhit
            mc_prim_energy_prev_rf[0] = mc_prim_energy_prev_sf[0] #nextevent.mc_prim_energy
            FV_prev_rf[0] = FV_prev_sf[0]
            good_pos_prev_rf[0] = good_pos_prev_sf[0]  #nextevent.good_pos
            posReco_prev_rf = cp.deepcopy(posReco_prev_sf) #nextevent.posReco
            u_prev_rf[0] = u_prev_sf[0]  #nextevent.u
            reco_z_prev_rf[0] = reco_z_prev_sf[0]  #nextevent.reco_z
            #posTruth_prev_rf = posTruth_prev_sf #cp.deepcopy(posTruth_prev_sf)
            true_r_prev_rf[0] = true_r_prev_sf[0]  #nextevent.true_r
            true_z_prev_rf[0] = true_z_prev_sf[0]  #nextevent.true_z
            good_dir_prev_rf[0] = good_dir_prev_sf[0] #nextevent.good_dir
            #dirReco_prev_rf = dirReco_prev_sf #cp.deepcopy(dirReco_prev_sf)
            interevent_time_rf[0] = sum(Buffer_timediffs[i+1:delfile_index+1])
            interevent_dist_fv_rf[0] = innerDist(u_prev_rf[0],
                        reco_z_prev_rf[0], u_rf[0], reco_z_rf[0],
                        posReco_rf, posReco_prev_rf)

            event_number_rf[0] = entrynum
            t_root.Fill()
            entrynum+=1
    f_root.cd()
    t_root.Write()
    f_root.Close()
    print("UISO MAX ENTRY: " + str(np.max(U_entry)))
    print("THISO MAX ENTRY: " + str(np.max(Th_entry)))
