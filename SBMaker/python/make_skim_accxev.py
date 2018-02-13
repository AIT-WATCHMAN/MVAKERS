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
import lib.EventUtils as eu
import lib.RootReader as rr

import ROOT as ROOT
from ROOT import TChain, TFile, gROOT
from sys import stdout
import glob

import os
from sys import argv

from decimal import *


#--------------- PARAMETERS THE USER SHOULD ADJUST--------------------#
PHOTOCOVERAGE = "25pct" #specify which PC directory you want to analyze from

#######DIRECTORY OF FILES#############
basepath = os.path.dirname(__file__)
MAINDIR = "pass2_root_files_tankRadius_10000.000000_halfHeight_10000.000000_shieldThickness_1500.000000_U238_PPM_0.341000_Th232_PPM_1.330000_Rn222_0.001400"
ANALYZEDIR = os.path.abspath(os.path.join(basepath, "..", "..","data", "teal2500", \
        MAINDIR, "25pct"))

#######NAME OF OUTPUT FILE##########
fileN = 'tester.root'

#####FV parameters used to accept/reject IBD pairs#####
FV_RADIUS = 10.84/2.  #in m
FV_HEIGHT = 10.84/2.  #in m. Defined as height from center

TIMETHRESH = 1.5E5  #Time window, in nanoseconds, where IBD pairs are accepted

#------------- END TUNABLE PARAMETERS --------------#

Bkg_types = ["WV", "PMT"]  #watchmakers output has these in accidental names
Bkg_filelocs = []
Bkg_files = []
for bkgtype in Bkg_types:
    Bkg_filelocs = Bkg_filelocs + glob.glob(ANALYZEDIR + "/*" + bkgtype + ".root")
for loc in Bkg_filelocs:
    rfile = ROOT.TFile(loc, "read")
    Bkg_files.append(rfile)


#Want to shoot the rates of events that could be a prompt candidate.  Only want
#To shoot using this rate since only valid events are filled into the ntuple
Bkg_rates_validfits = rr.GetRates_Valids(Bkg_files)
Bkg_rates_raw = rr.GetRates_Raw(Bkg_files)
Bkg_entrynums = np.zeros(len(Bkg_files))

RAW_RATE = np.sum(Bkg_rates_raw)
VALID_RATE = np.sum(Bkg_rates_validfits)
print("RAW RATE: " + str(RAW_RATE))
print("VALID SINGLE CANDIDATE RATE: " + str(VALID_RATE))

def loadNewEvent(bufffile, entries, timediffs):
    '''
    Using the loaded-in background files, shoot the next event's information,
    including file it's in, it's entry number, and the time since last event
    '''
    shot =np.random.rand()
    #Assuming Bkg_rates is a numpy array
    for i in xrange(len(Bkg_rates_validfits)):
        if i > 0:
            if shot < (sum(Bkg_rates_validfits[0:i]) / \
                    sum(Bkg_rates_validfits[0:len(Bkg_rates_validfits)])):
                Bkg_entrynums[i]+=1
                entries.append(int(Bkg_entrynums[i]))
                bufffile.append(Bkg_files[i])
                timediffs.append(eu.shootTimeDiff(VALID_RATE))
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
    r_rf   = np.zeros(1,dtype=float64)
    z_rf   = np.zeros(1,dtype=float64)
    reco_z_rf = np.zeros(1,dtype=float64)
    good_dir_rf     = np.zeros(1,dtype=float64)
    closestPMT_rf    = np.zeros(1,dtype=float64)

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
    r_prev_rf   = np.zeros(1,dtype=float64)
    z_prev_rf   = np.zeros(1,dtype=float64)
    good_dir_prev_rf     = np.zeros(1,dtype=float64)
    closestPMT_prev_rf    = np.zeros(1,dtype=float64)

    interevent_time_rf  = np.zeros(1,dtype=float64)
    interevent_dist_fv_rf  = np.zeros(1,dtype=float64)

    '''Open a root file with name of dataType'''

    f_root = ROOT.TFile(fileN,"recreate")
    
    '''Set up the tree and branch of variables one wishes to save'''
    fiducial_r = np.zeros(1,dtype=float64)
    fiducial_z = np.zeros(1,dtype=float64)
    timecut = np.zeros(1,dtype=float64)
    m_root = ROOT.TTree("Summary","Fiducial volume and time cut parameters used")
    m_root.Branch('fiducial_z', fiducial_z, 'fiducial_z/D')
    m_root.Branch('fiducial_r', fiducial_r, 'fiducial_r/D')
    m_root.Branch('timecut', timecut, 'timecut/D')
    fiducial_r[0] = FV_RADIUS
    fiducial_z[0] = FV_HEIGHT
    timecut[0] = TIMETHRESH
    m_root.Fill()

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
    t_root.Branch('r',     r_rf,'r/D')
    t_root.Branch('z',     z_rf,'z/D')
    t_root.Branch('good_dir', good_dir_rf, 'good_dir/D')
    t_root.Branch('closestPMT', closestPMT_rf, 'closestPMT/D')

    t_root.Branch('interevent_time', interevent_time_rf,  'interevent_time/D')
    t_root.Branch('interevent_dist_fv', interevent_dist_fv_rf,  'interevent_dist_fv/D')

    t_root.Branch('pe_prev',       pe_prev_rf,    'pe_prev/D')
    t_root.Branch('nhit_prev',       nhit_prev_rf,    'nhit_prev/D')
    t_root.Branch('n9_prev',      n9_prev_rf,   'n9_prev/D')
    
    t_root.Branch('good_pos_prev',        good_pos_prev_rf ,      'good_pos_prev/D')
    t_root.Branch('u_prev',     u_prev_rf,'u_prev/D')
    t_root.Branch('v_prev',     v_prev_rf,'v_prev/D')
    t_root.Branch('w_prev',     w_prev_rf,'w_prev/D')
    t_root.Branch('x_prev',     x_prev_rf,'x_prev/D')
    t_root.Branch('y_prev',     y_prev_rf,'y_prev/D')
    t_root.Branch('r_prev',     r_prev_rf,'r_prev/D')
    t_root.Branch('z_prev',     z_prev_rf,'z_prev/D')
    t_root.Branch('good_dir_prev', good_dir_prev_rf, 'good_dir_prev/D')
    t_root.Branch('closestPMT_prev', closestPMT_prev_rf, 'closestPMT_prev/D')

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
            print("ENTRYNUM: " + str(entrynum))

        #load a new event into our buffer
        Buffer_files, Buffer_entries, Buffer_timediffs = \
                loadNewEvent(Buffer_files, 
                Buffer_entries, Buffer_timediffs)
        
        #Remove events at start of buffer outside the time width range
        Buffer_files, Buffer_entries, Buffer_timediffs = \
                deleteOld(Buffer_files, Buffer_entries, 
                Buffer_timediffs)
        if len(Buffer_timediffs) <= 1:
            continue
        #The newest event is our delayed candidate.
        delfile_index = len(Buffer_timediffs) - 1
        delayedfile = Buffer_files[delfile_index]
        for i in xrange(delfile_index):
            delayedfile.cd()
            deltree = delayedfile.Get("data")
            if Buffer_entries[delfile_index] >= deltree.GetEntries():
                FileDepleted = True
                break
            deltree.GetEntry(Buffer_entries[delfile_index])
            #Some bad reconstruction checks; don't want a ton of crazy nums,
            #just -1
            if eu.isFiducial(FV_RADIUS, FV_HEIGHT, deltree.x, deltree.y, 
                    deltree.z) is False:
                print("THIS AINT FIDUCIAL")
                #continue
            if deltree.nhit < 0 or deltree.nhit > 10000:
                continue
            if deltree.pe < 0 or abs(deltree.pe) > 1.E6:
                pe_rf[0] = -1.0
            else:
                pe_rf[0] = deltree.pe 
            if deltree.n9 < 0 or deltree.n9 > 10000:
                n9_rf[0] = -1.0
            else:
                n9_rf[0] = deltree.n9

            nhit_rf[0] = deltree.nhit
            good_pos_rf[0] = deltree.good_pos
            u_rf[0] = deltree.u
            v_rf[0] = deltree.v
            w_rf[0] = deltree.w
            x_rf[0] = deltree.x
            y_rf[0] = deltree.y
            r_rf[0] = np.sqrt(deltree.x**2 + deltree.y**2)
            z_rf[0] = deltree.z
            good_dir_rf[0] = deltree.good_dir
            closestPMT_rf[0] = deltree.closestPMT

            promptfile = Buffer_files[i]
            prompttree = promptfile.Get("data")
            if Buffer_entries[i] >= prompttree.GetEntries():
                FileDepleted = True
                break
            #Now, fill in the next tree entry with this entrys info as previous
            prompttree.GetEntry(Buffer_entries[i])
            if eu.isFiducial(FV_RADIUS, FV_HEIGHT, prompttree.x, prompttree.y, 
                    prompttree.z) is False:
                print("THIS ALSO AINT FIDUCIAL")
                #continue
            if prompttree.nhit < 0 or prompttree.nhit > 10000:
                continue
            if prompttree.pe < 0 or abs(prompttree.pe) > 1.E6:
                pe_prev_rf[0] = -1.0
            else:
                pe_prev_rf[0] = prompttree.pe 
            if prompttree.n9 < 0 or prompttree.n9 > 10000:
                n9_prev_rf[0] = -1.0
            else:
                n9_prev_rf[0] = prompttree.n9

            nhit_prev_rf[0] = prompttree.nhit #nhit_prev_rf #nextevent.nhit
            good_pos_prev_rf[0] = prompttree.good_pos #good_pos_prev_sf[0]
            u_prev_rf[0] = prompttree.u
            v_prev_rf[0] = prompttree.v
            w_prev_rf[0] = prompttree.w
            x_prev_rf[0] = prompttree.x
            y_prev_rf[0] = prompttree.y
            r_prev_rf[0] = np.sqrt(prompttree.x**2 + prompttree.y**2)
            z_prev_rf[0] = prompttree.z
            good_dir_prev_rf[0] = deltree.good_dir
            closestPMT_prev_rf[0] = deltree.closestPMT
            
            #interevent time between this pair is the sum of timediffs between them
            interevent_time_rf[0] = sum(Buffer_timediffs[i+1:delfile_index+1])

            interevent_dist_fv_rf[0] = eu.innerDist(x_prev_rf[0],
                    y_prev_rf[0],z_prev_rf[0], x_rf[0], y_rf[0], z_rf[0])
            event_number_rf[0] = entrynum
            t_root.Fill()
            entrynum+=1
    f_root.cd()
    t_root.Write()
    m_root.Write()
    f_root.Close()
    print("UISO MAX ENTRY: " + str(np.max(Bkg_entrynums)))
