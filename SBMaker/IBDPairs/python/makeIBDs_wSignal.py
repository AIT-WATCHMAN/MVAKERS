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

from sys import stdout
import glob

import os
from sys import argv

from decimal import *
import argparse

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
parser.add_argument('--output','-o', dest='OUTFILE', action='store',
        help="Provide the name desired for the output root file")

parser.set_defaults(DEBUG=False, TIMETHRESH=1.5E5, 
        INTERDIST=None, RADIUSCUT=None,ZCUT=None,DATADIR=None,
        PHOTOCOVERAGE='25pct',OUTFILE='output.root')
args = parser.parse_args()

DEBUG = args.DEBUG
TIMETHRESH=args.TIMETHRESH
INTERDIST=args.INTERDIST
RADIUSCUT=args.RADIUSCUT
ZCUT=args.ZCUT
DATADIR=args.DATADIR
OUTFILE=args.OUTFILE
PHOTOCOVERAGE=args.PHOTOCOVERAGE

#have to import ROOT here, or it steals --help's output
import ROOT
from ROOT import TChain, TFile, gROOT
import lib.playDarts as pd
import lib.EventUtils as eu
import lib.RootReader as rr

#---------- FORMAT-SPECIFIC PARAMETERS ------------#
dattree = "data"
event_types = {"prompt":"IBD", "delayed":"neutron"}  #watchmakers output has these in accidental names
MAXPAIRS = 10000000 #Just in case you don't want a crazy amount of candidates
#------------- END TUNABLE PARAMETERS --------------#

#First, load all the water volume and PMT accidental MC
ANALYZEDIR = DATADIR+"/"+PHOTOCOVERAGE
positron_filename = ANALYZEDIR+"/watchman_"+event_types["prompt"]+".root"
neutron_filename = ANALYZEDIR+"/watchman_"+event_types["delayed"]+".root"
positron_file = ROOT.TFile(positron_filename,"READ")
ptree = positron_file.Get("output")
neutron_file = ROOT.TFile(neutron_filename,"READ")
ntree = neutron_file.Get("output")

#Want to shoot the rates of events that could be a prompt candidate.  Only want
#To shoot using rates_validfits since only valid events are filled into the ntuple
positron_eff_validfits = rr.GetPromptEff(prompt_file)
neutron_eff_validfits = rr.GetPromptEff(del_file)
file_entrynums = np.zeros(len(event_types))

if DEBUG is True:
    print("PROMPT EFFICIENCY: " + str(prompt_eff_validfits))
    print("DELAYED EFFICIENCY: " + str(del_eff_validfits))

if __name__ == '__main__':

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
    timecut = np.zeros(1,dtype=float64)
    positron_valideff = np.zeros(1,dtype=float64)
    neutron_valideff = np.zeros(1,dtype=float64)

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
    m_root.Branch('timecut', timecut, 'timecut/D')
    m_root.Branch('positron_valideff', positron_valideff, 'positron_valideff/D')
    m_root.Branch('neutron_valideff', neutron_valideff, 'neutron_valideff/D')
    timecut[0] = TIMETHRESH
    positron_valideff[0] = positron_eff_validfits 
    neutron_valideff[0] = neutron_eff_validfits 

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
    while (pairnum < MAXPAIRS):
        if float(pairnum) / 20000.0 == int(pairnum / 20000.0):
            print("ENTRYNUM: " + str(pairnum))
        #loop through and match this delayed event with all previous prompts
        if pairnum == dtree.GetEntries() or pairnum == ptree.GetEntries():
            print("POSITRON OR NEUTRON FILE WAS DEPLETED")
            break
            
            ptree.GetEntry(pairnum)
            nhit_p[0]     = ptree.nhit 
            x_p[0]       = ptree.x
            y_p[0]        = ptree.y
            z_p[0]      = ptree.z
            posr_p[0]        = eu.radius(x_p[0],y_p[0],z_p[0])
            u_p[0]      = ptree.u
            v_p[0]      = ptree.v 
            w_p[0]      = ptree.w 
            mc_energy_p[0]    = ptree.mc_energy 
            good_pos_p[0] = ptree.good_pos 
            good_dir_p[0] = ptree.good_dir 
            pe_p[0]     = ptree.pe 
            closestPMT_p[0]  = ptree.closestPMT
            n9_p[0]  = ptree.n9

            dtree.GetEntry(pairnum)
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

            #TODO: NEED TO SHOOT FOR THE INTEREVENT_DIST AND TIME 
            interevent_dist[0] = -1
            #Check for intereventdist cut and fill in interevent dist
            if INTERDIST is not None:
                if float(interevent_dist[0]) > float(INTERDIST):
                    continue
            interevent_time[0] = -1
            pair_number[0] = pairnum
            t_root.Fill()
            pairnum+=1
    allpairnum[0] = pairnum
    m_root.Fill()
    f_root.cd()
    t_root.Write()
    m_root.Write()
    f_root.Close()
