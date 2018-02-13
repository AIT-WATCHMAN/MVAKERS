#### GenerateCorrMC.py ######
# Function: This program will take in Monte Carlo data and #
# Fire more data based on the correlations of the data     #
# sample given.                                            #
# NOTE: The method used here will only work if the         #
# Variables calculated are normal, correlated, random      #
# Variables.  This is generally not the case for the       #
# Fitting parameters output from RAT-PAC.                  #

import copy as cp
import math
import time
from array import *
import numpy as np
from numpy import *
import copy

import lib.playDarts as pd
import lib.EventUtils as eu
import lib.RootReader as rr
import lib.CorrelationTools as ct
import lib.CovPlots as cp


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
fileN = 'datoutput.root'
variables = ['closestPMT','good_pos','nhit','n9','pe','x','y','z','u','v','w','good_dir']

######NUMBER OF EVENTS TO GENERATE########
GenerateNumber = 100000  #WIll generate this number per background file
#------------- END TUNABLE PARAMETERS --------------#

Bkg_types = ["208Tl_PMT"]#["WV", "PMT"]  #watchmakers output has these in accidental names
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

    '''Open a root file with name of dataType'''

    f_root = ROOT.TFile(fileN,"recreate")
    
    '''Set up the tree and branch of variables one wishes to save'''
    
    s_root = ROOT.TTree("runSummary","Run summary information of original dataset")

    t_root = ROOT.TTree("AccidentalMC","MC Accidentals w/ Correlations")
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
    t_root.Branch('closestPMT', closestPMT_rf, 'closestPMT/D')

    #The following continues as long as the selected file still has entrys left

    for i in xrange(len(Bkg_files)):
        bkgfile = Bkg_files[i]
        bkgfile.cd()
        summarytree = bkgfile.Get("runSummary")
        s_root = summarytree
        datatree = bkgfile.Get("data")
        CorrelationFinder = ct.CorrelationFinder(rootfiles=Bkg_filelocs[i],\
                variables=variables,tree="data")
        CovarianceMatrix = CorrelationFinder.makeCovarianceMatrix()
        yvariables = copy.deepcopy(variables)
        #yvariables.reverse()
        cp.pCovarianceMatrix(CovarianceMatrix.cov_matrix,variables,yvariables)
        CovarianceMatrix.choleskydecompose()
        cp.pCovarianceMatrix(CovarianceMatrix.correlation_shooter_matrix,variables,yvariables)
        #We have our covariance matrix.  Go through the background file and
        #Adjust the variables based on the correlated monte carlo shots.
        GeneratedAmountMet = False
        entrynum = 0
        while (not GeneratedAmountMet):
            if entrynum > GenerateNumber:
                GeneratedAmountMet = True
                break
            if datatree.GetEntries() < 10000:
                print("You have less than 10k data points. Your statistics " + \
                        "are bad and you should feel bad.")
            for j in xrange(datatree.GetEntries()):
                if float(entrynum) / 20000.0 == int(entrynum / 20000.0):
                    print("ENTRYNUM: " + str(entrynum))
                datatree.GetEntry(j)
                variable_shots = CovarianceMatrix.shoot_corrvars()
                if datatree.nhit < 0 or datatree.nhit > 10000:
                    continue
                if datatree.pe < 0 or abs(datatree.pe) > 1.E6:
                    pe_rf[0] = -1.0
                else:
                    pe_rf[0] = getattr(datatree,"pe") + variable_shots["pe"] 
                if datatree.n9 < 0 or datatree.n9 > 10000:
                    n9_rf[0] = -1.0
                else:
                    n9_rf[0] = getattr(datatree,"n9") + variable_shots["n9"]
    
                nhit_rf[0] = getattr(datatree,"nhit") + variable_shots["nhit"]
                good_pos_rf[0] = getattr(datatree,"good_pos") + variable_shots["good_pos"]
                u_rf[0] = getattr(datatree,"u") + variable_shots["u"]
                v_rf[0] = getattr(datatree,"v") + variable_shots["v"]
                w_rf[0] = getattr(datatree,"w") + variable_shots["w"]
                x_rf[0] = getattr(datatree,"x") + variable_shots["x"]
                y_rf[0] = getattr(datatree,"y") + variable_shots["y"]
                z_rf[0] = getattr(datatree,"z") + variable_shots["z"]
                good_dir_rf[0] = getattr(datatree,"good_dir") + variable_shots["good_dir"]
                closestPMT_rf[0] = getattr(datatree,"closestPMT") + variable_shots["closestPMT"]
                event_number_rf[0] = entrynum
                t_root.Fill()
                entrynum+=1
    f_root.cd()
    t_root.Write()
    s_root.Write()
    f_root.Close()
    print("UISO MAX ENTRY: " + str(np.max(Bkg_entrynums)))
