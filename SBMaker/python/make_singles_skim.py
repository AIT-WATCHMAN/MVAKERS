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
#MAINDIR = "pass2_root_files_tankRadius_10000.000000_halfHeight_10000.000000_shieldThickness_1500.000000_U238_PPM_0.341000_Th232_PPM_1.330000_Rn222_0.001400"
MAINDIR = "1500"
ANALYZEDIR = os.path.abspath(os.path.join(basepath, "..", "..","data", "PMTActivityAnalysis", MAINDIR, PHOTOCOVERAGE))

#######NAME OF OUTPUT FILE##########
fileN = '1500_25pct_accidentals.root'

#####FV parameters used to accept/reject IBD pairs#####
FV_RADIUS = 10.84/2.  #in m
FV_HEIGHT = 10.84/2.  #in m. Defined as height from center
#------------- END TUNABLE PARAMETERS --------------#

Bkg_types = ["WV", "PMT"]  #watchmakers output has these in accidental names
Bkg_filelocs = []
Bkg_files = []
for bkgtype in Bkg_types:
    Bkg_filelocs = Bkg_filelocs + glob.glob(ANALYZEDIR + "/*" + bkgtype + ".root")
for loc in Bkg_filelocs:
    rfile = ROOT.TFile(loc, "read")
    Bkg_files.append(rfile)
print("BKGFILE LOCS: " + str(Bkg_filelocs))

#Want to shoot the rates of events that could be a prompt candidate.  Only want
#To shoot using this rate since only valid events are filled into the ntuple
Bkg_rates_validfits = rr.GetRates_Valids(Bkg_files)
Bkg_rates_raw = rr.GetRates_Raw(Bkg_files)
Bkg_entrynums = np.zeros(len(Bkg_files))

RAW_RATE = np.sum(Bkg_rates_raw)
VALID_RATE = np.sum(Bkg_rates_validfits)
print("RAW RATE: " + str(RAW_RATE))
print("VALID SINGLE CANDIDATE RATE: " + str(VALID_RATE))

def loadNewEvent():
    '''
    Using the loaded-in background files, shoot what the next event type 
    loaded into the skim fill will be.  Also return the next entrynum.
    '''
    shot =np.random.rand()
    #Assuming Bkg_rates is a numpy array
    for i in xrange(len(Bkg_rates_validfits)):
        frac_thisfile = sum(Bkg_rates_validfits[0:i+1]) / np.sum(Bkg_rates_validfits)
        if shot < frac_thisfile:
            Bkg_entrynums[i]+=1
            thisentry = (int(Bkg_entrynums[i]))
            thisfile = Bkg_files[i]
            break
    return thisentry, thisfile
        
if __name__ == '__main__':

    '''Set up variables for root tree'''
    n9_rf        = np.zeros(1,dtype=float64)
    nhit_rf      = np.zeros(1,dtype=float64)
    pe_rf     = np.zeros(1,dtype=float64)
    event_number_rf        = np.zeros(1,dtype=float64)
    is_fiducial_rf = np.zeros(1,dtype=bool)
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

    '''Open a root file with name of dataType'''

    f_root = ROOT.TFile(fileN,"recreate")
    
    '''Set up the tree and branch of variables one wishes to save'''
    fiducial_r = np.zeros(1,dtype=float64)
    fiducial_z = np.zeros(1,dtype=float64)
    raw_rate = np.zeros(1,dtype=float64)
    pvalid_rate = np.zeros(1,dtype=float64)
    m_root = ROOT.TTree("Summary","Fiducial volume and time cut parameters used")
    m_root.Branch('fiducial_z', fiducial_z, 'fiducial_z/D')
    m_root.Branch('fiducial_r', fiducial_r, 'fiducial_r/D')
    m_root.Branch('raw_rate', raw_rate, 'raw_rate/D')
    m_root.Branch('pvalid_rate', pvalid_rate, 'pvalid_rate/D')
    fiducial_r[0] = FV_RADIUS
    fiducial_z[0] = FV_HEIGHT
    raw_rate = RAW_RATE
    pvalid_rate = VALID_RATE
    m_root.Fill()

    t_root = ROOT.TTree("CombSingles","Combined Singles File")
    t_root.Branch('pe',       pe_rf,    'pe/D')
    t_root.Branch('nhit',       nhit_rf,    'nhit/D')
    t_root.Branch('n9',      n9_rf,   'n9/D')

    t_root.Branch('is_fiducial', is_fiducial_rf, 'is_fiducial/O')    
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


    #The following continues as long as the selected file still has entrys left
    FileDepleted = False
    entrynum = 0
    events_viewed = 0
    while (not FileDepleted) and (entrynum < 10000000):
        if float(entrynum) / 20000.0 == int(entrynum / 20000.0):
            print("ENTRYNUM: " + str(entrynum))
        events_viewed+=1
        #Shoot for the next file (and entrynumber) to pull fromr
        entrynumber, thisevent_bkgfile = loadNewEvent()
        thisevent_bkgfile.cd()
        bkgtree = thisevent_bkgfile.Get("data")
        if entrynumber >= bkgtree.GetEntries():
            print("FILE WAS DEPLETED...")
            FileDepleted = True
            break
        bkgtree.GetEntry(entrynumber)
        #Some bad reconstruction checks; don't want a ton of crazy nums,
        #just -1
        is_fiducial_rf[0] = eu.isFiducial(FV_RADIUS, FV_HEIGHT, bkgtree.x, bkgtree.y, 
                bkgtree.z)
        pe_rf[0] = bkgtree.pe 
        n9_rf[0] = bkgtree.n9

        nhit_rf[0] = bkgtree.nhit
        good_pos_rf[0] = bkgtree.good_pos
        u_rf[0] = bkgtree.u
        v_rf[0] = bkgtree.v
        w_rf[0] = bkgtree.w
        x_rf[0] = bkgtree.x
        y_rf[0] = bkgtree.y
        r_rf[0] = np.sqrt(bkgtree.x**2 + bkgtree.y**2)
        z_rf[0] = bkgtree.z
        good_dir_rf[0] = bkgtree.good_dir
        closestPMT_rf[0] = bkgtree.closestPMT
        t_root.Fill()
        entrynum+=1
    f_root.cd()
    t_root.Write()
    m_root.Write()
    f_root.Close()
    print("TOTAL EVENTS WENT OVER: " + str(events_viewed))
    print("BKGFILE MAX ENTRY: " + str(np.max(Bkg_entrynums)))
    print("BKGFILE MIN ENTRY: " + str(np.min(Bkg_entrynums)))
