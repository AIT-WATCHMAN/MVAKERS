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
import json


parser = argparse.ArgumentParser(description='Parser to decide what analysis to do')
parser.add_argument('--debug', dest='DEBUG',action='store_true',
        help='Run in debug mode and get some extra outputs and stuff')
parser.add_argument('--zcut', dest='ZCUT', action='store',
        help='Only consider IBD candidates within abs(z) coordinate of'+\
                'detector center')
parser.add_argument('--timecut', dest='TIMETHRESH', action='store',
        help='Only consider IBD candidates with an interevent time <= input')
parser.add_argument('--distcut', dest='INTERDIST', action='store',
        help='Only consider IBD candidates with an interevent_dist <= input.')
parser.add_argument('--pc', dest='PHOTOCOVERAGE', action='store',
        help="Specify the photocoverage directory you want to read from"+\
                "(FORMAT: 'Npct' for N percent photocoverage)")
parser.add_argument('--posrcut', dest='RADIUSCUT', action='store',
        help='Only consider IBD candidates with an interevent distance <= input.')
parser.add_argument('--datadir', dest='DATADIR', action='store',
        help="Points to data directory with positron and neutron files")
parser.add_argument('--ITID', dest='USEITID', action='store',
        help="Will use data in directory string given to shoot interevent times")
parser.add_argument('--output','-o', dest='OUTFILE', action='store',
        help="Provide the name desired for the output root file")

dd='/p/lscratche/adg/Watchboy/simplifiedData/rp_sim/dec2017/pass2_root_files_tankRadius_10000.000000_halfHeight_10000.000000_shieldThickness_1500.000000_U238_PPM_0.341000_Th232_PPM_1.330000_Rn222_0.001400'
ditid='../../../data/ITID'
parser.set_defaults(DEBUG=False, TIMETHRESH=1.5E5, 
        INTERDIST=None, RADIUSCUT=None,ZCUT=None,DATADIR=dd,
        PHOTOCOVERAGE='25pct',OUTFILE='output.root',USEITID=ditid)
args = parser.parse_args()

DEBUG = args.DEBUG
TIMETHRESH=args.TIMETHRESH
INTERDIST=args.INTERDIST
RADIUSCUT=args.RADIUSCUT
ZCUT=args.ZCUT
DATADIR=args.DATADIR
OUTFILE=args.OUTFILE
PHOTOCOVERAGE=args.PHOTOCOVERAGE
USEITID=args.USEITID

if DATADIR is None:
    print("No data directory specified for pairing IBDs. exiting.")
    sys.exit(0)

#have to import ROOT here, or it steals --help's output
import ROOT
from ROOT import TChain, TFile, gROOT
import lib.playDarts as pd
import lib.EventUtils as eu
import lib.RootReader as rr
import lib.ITIDShooter as itd

#---------- FORMAT-SPECIFIC PARAMETERS ------------#
dattree = "data"
event_types = {"prompt":"IBD", "delayed":"neutron"}  #watchmakers output has these in accidental names
MAXPAIRS = 10000000 #Just in case you don't want a crazy amount of candidates
#------------- END TUNABLE PARAMETERS --------------#

#First, load all the water volume and PMT accidental MC
ANALYZEDIR = DATADIR+"/"+PHOTOCOVERAGE

#We'll shoot interevent distances and times here
ITID_filenames = glob.glob(USEITID+"/*.root")

if DEBUG is True:
    print("ITID FILES: " + str(ITID_filenames))
 
if __name__ == '__main__':
    with open("cutdict.json","r") as f:
        cuts = json.load(f)

    if DEBUG is True:
        print("SETTING UP VARIABLES FOR ROOT TREE TO BE SAVED...")
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
    posr_p      = np.zeros(1,dtype=float64)
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
    posr_d      = np.zeros(1,dtype=float64)
    closestPMT_d    = np.zeros(1,dtype=float64)
    n9_d       = np.zeros(1,dtype=float64)

    interevent_dist = np.zeros(1,dtype=float64)
    interevent_time = np.zeros(1,dtype=float64)

    pair_number = np.zeros(1,dtype=int)

    #Variables for filling ProcSummary
    allpairnum = np.zeros(1,dtype=int)
    validpairnum = np.zeros(1,dtype=int)
    timecut = np.zeros(1,dtype=float64)

    if INTERDIST is not None:
        interdistcut = np.zeros(1,dtype=float64)
    if RADIUSCUT is not None:
        posrcut = np.zeros(1,dtype=float64)
    if ZCUT is not None:
        posrcut = np.zeros(1,dtype=float64)

    '''Open a root file with name of dataType'''

    f_root = ROOT.TFile(OUTFILE,"recreate")
    
    m_root = ROOT.TTree("ProcSummary","Cuts applied and some meta information")
    m_root.Branch('allpairnum', allpairnum, 'allpairnum/I')
    m_root.Branch('validpairnum', validpairnum, 'validpairnum/I')
    m_root.Branch('timecut', timecut, 'timecut/D')
    timecut[0] = TIMETHRESH

    if INTERDIST is not None:
        m_root.Branch('interdistcut', interdistcut, 'interdistcut/D')
        interdistcut[0] = INTERDIST
    if RADIUSCUT is not None:
        m_root.Branch('posrcut', posrcut, 'posrcut/D')
        posrcut[0] = RADIUSCUT
    if ZCUT is not None:
        m_root.Branch('zcut',zcut, 'zcut/D')
        zcut[0] = ZCUT


    t_root = ROOT.TTree("CombinedOutput","Combined reactor positron and neutrons from MC")
    t_root.Branch('z_p',      z_p,   'z_p/D')
    t_root.Branch('y_p',      y_p,   'y_p/D')
    t_root.Branch('x_p',      x_p,   'x_p/D')
    t_root.Branch('posr_p',      posr_p,   'posr_p/D')
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
    t_root.Branch('posr_d',      posr_d,   'posr_d/D')
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

    for rf in ITID_filenames:
        rootfile = ROOT.TFile(rf, "READ")
        dtree = rootfile.Get("data")

        delayedinvalid = False
        promptinvalid = False
        promptmcid = None
        entrynum = 0
   
        while (pairnum < MAXPAIRS):
            if float(entrynum) / 20000.0 == int(entrynum / 20000.0):
                print("ENTRYNUM: " + str(pairnum))
            #loop through and match this delayed event with all previous prompts
            if entrynum == dtree.GetEntries():
                print("BONSAI FILE WAS DEPLETED")
                break
            dtree.GetEntry(entrynum)
            #Check if this passes prompt cuts
            for cut in cuts:
                if cuts[cut] > getattr(dtree,cut):
                    if promptmcid is None:
                        promptinvalid = True
                        break
                    else:
                        #delayed was invalid.
                        delayedinvalid = True
                        break
    
            #Passed cuts; fill the prompt if it's a prompt entry
            if promptmcid is None and promptinvalid is False:
                promptmcid = dtree.mcid
                nhit_p[0]     = dtree.nhit 
                x_p[0]       = dtree.x
                y_p[0]        = dtree.y
                z_p[0]      = dtree.z
                posr_p[0]        = eu.radius(x_p[0],y_p[0],z_p[0])
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
                print("VALID PROMPT")
                continue
            elif promptmcid is None and promptinvalid is True:
                #This entry is a failed prompt event.
                print("FAILED PROMPT")
                promptmcid = dtree.mcid
                entrynum+=1
                continue
    
            pairnum+=1
            #Have a prompt, either passed or failed.
            if promptmcid is not None and promptinvalid is False and \
                    delayedinvalid is False:
                #See if the next event is our prompt's delayed candidate
                print("CURRENTID: " + str(promptmcid))
                print("THIS NEUTRONS MCID: " + str(dtree.mcid))
                if promptmcid == dtree.mcid:
                    nhit_d[0]     = dtree.nhit 
                    x_d[0]       = dtree.x
                    y_d[0]        = dtree.y
                    z_d[0]      = dtree.z
                    posr_d[0]        = eu.radius(x_d[0],y_d[0],z_d[0])
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

            promptmcid = None
            promptinvalid = False
            delayedinvalid = False
   
            interevent_dist[0] = eu.innerDist(x_p[0], y_p[0], z_p[0], x_d[0],\
                    y_d[0], z_d[0])
            #Check for intereventdist cut and fill in interevent dist
            if INTERDIST is not None:
                if float(interevent_dist[0]) > float(INTERDIST):
                    continue
            interevent_time[0] = dtree.dt * 1.0E9
            if TIMETHRESH is not None:
                if float(interevent_time[0]) > float(TIMETHRESH):
                    continue
            pair_number[0] = cp.deepcopy(valpairnum)
            t_root.Fill()
            valpairnum+=1
    allpairnum[0] = pairnum
    print(valpairnum)
    validpairnum[0] = valpairnum
    m_root.Fill()
    f_root.cd()
    t_root.Write()
    m_root.Write()
    f_root.Close()
