#Example from Marc with how to build a ROOT file in pyROOT
#We'll want to take these ideas and build them into a program
#That will effectively build up our simulated FV and PMT backgrounds.

import math
import time
from array import *
import numpy as np
from numpy import *

import ROOT as ROOT
from ROOT import TChain, TFile, gROOT
from sys import stdout
import random

from sys import argv

from decimal import *
getcontext().prec = 18
import struct

def drange(start, stop, step):
	rii= start
	while rii<stop:
		yield rii
		rii+=step

def openFile(name):
    print name

f2 = TChain('wbRunSummary')
if len(argv) >=2:
    fileName = "silverFiles/silver_%s-%s*" % (argv[1],argv[2])
else:
    fileName = "silverFiles/silver_*"
f2.Add(fileName)

wbRunSummary	= gROOT. FindObject('wbRunSummary')
wbRunSummary.Show(0)

time_tot        = 0.0

t_tsa_1         = 0.0
t_tsa_2         = 0.0
t_tsa_3         = 0.0
t_tsa_c         = 0.0
t_tsa_12        = 0.0
t_tsa_23        = 0.0

#################

t_tsa_tw        = 1e5
t_muon          = 1e6

tsa_flag        = 0
tsa_target_1    = 0.0
tsa_qBal_1      = 0.0
tsa_target_2    = 0.0
tsa_qBal_2      = 0.0
tsa_target_3    = 0.0
tsa_qBal_3      = 0.0
tsa_mu_1        = 0.0
tsa_mu_2        = 0.0
tsa_mu_3        = 0.0
tsa_targmu_1	= 0.0
tsa_targmu_2    = 0.0
tsa_targmu_3    = 0.0
tsa_timestamp   = 0.0
b_shower        = 1111111111111111111111111111110.0

'''Set up variables for root tree'''
stamp_rf        = np.zeros(1,dtype=float64)
time2Mu_rf      = np.zeros(1,dtype=float64)
nAfterMu_rf     = np.zeros(1,dtype=int)
tsa_flag_rf     = np.zeros(1,dtype=int)
tsa_burst_rf    = np.zeros(1,dtype=int)
dT_12_rf       	= np.zeros(1,dtype=float64)
dT_23_rf        = np.zeros(1,dtype=float64)
tsa_target_1_rf = np.zeros(1,dtype=float64)
tsa_qBal_1_rf   = np.zeros(1,dtype=float64)
tsa_target_2_rf = np.zeros(1,dtype=float64)
tsa_qBal_2_rf   = np.zeros(1,dtype=float64)
tsa_target_3_rf = np.zeros(1,dtype=float64)
tsa_qBal_3_rf   = np.zeros(1,dtype=float64)
tsa_mu_1_rf     = np.zeros(1,dtype=float64)
tsa_mu_2_rf     = np.zeros(1,dtype=float64)
tsa_mu_3_rf     = np.zeros(1,dtype=float64)
tsa_targmu_1_rf = np.zeros(1,dtype=float64)
tsa_targmu_2_rf = np.zeros(1,dtype=float64)
tsa_targmu_3_rf = np.zeros(1,dtype=float64)
b_shower_rf		= np.zeros(1,dtype=float64)
b_targ_rf		= np.zeros(1,dtype=float64)
b_veto_rf		= np.zeros(1,dtype=float64)
b_targSpec_rf	= np.zeros(1,dtype=float64)
burstTime_rf	= np.zeros(1,dtype=float64)
showerMuCnt_rf  = np.zeros(1,dtype=int)
firstShowerDetected_rf  = np.zeros(1,dtype=int)
burstTime_ref   = 0.00000
burstTime_diff  = 0.00000
firstShowerDetected_rf[0] = 0

'''Open a root file with name of dataType'''


if len(argv) >=2:
    fileN = "tsa_%s-%s.root" % (argv[1],argv[2])
else:
    fileN = "tsa.root"

f_root = ROOT.TFile(fileN,"recreate")

'''Set up the tree and branch of variables one wishes to save'''

t_root = ROOT.TTree("tsa","tsa processed data")
t_root.Branch('nAfterMu',       nAfterMu_rf,    'nAfterMu/I')
t_root.Branch('tsa_flag',       tsa_flag_rf,    'tsa_flag/I')
t_root.Branch('tsa_burst',      tsa_burst_rf,   'tsa_burst/I')

t_root.Branch('timeStamp',      stamp_rf,       'timeStamp/D')
t_root.Branch('time2Mu',        time2Mu_rf,     'time2Mu/D')
t_root.Branch('dT_Prev',        dT_12_rf ,      'dT_Prev/D')
t_root.Branch('dT_Next',        dT_23_rf ,      'dT_Next/D')
t_root.Branch('charge',         tsa_target_2_rf,'charge/D')
t_root.Branch('prevCharge',     tsa_target_1_rf,'prevCharge/D')
t_root.Branch('nextCharge',     tsa_target_3_rf,'nextCharge/D')
t_root.Branch('qBal',     tsa_qBal_2_rf,  'qBal/D')
t_root.Branch('prevqBal', tsa_qBal_1_rf,  'prevqBal/D')
t_root.Branch('nextqBal', tsa_qBal_3_rf,  'nextqBal/D')
t_root.Branch('burstTime',      burstTime_rf,   'burstTime/D')
t_root.Branch('firstShowerDetected', firstShowerDetected_rf,   'firstShowerDetected/I')

'''Add a special time for when there is a multiplicity TBD that occurs'''

'''Start reading in the files. First get the summary tree and reset the global variables,
Show the raw trigger rate for the run, then load in data tree for processing '''
corr_muon_burst = 0
corr_muon_stamp = 111111111111111111.0
old_time        = -111111111111111111.0
corr_muon_veto  = 0.0
corr_muon_targ  = 0.0
b_veto          = 0.0
b_targ          = 0.0
b_time_stamp	= 0.0
s_time_stamp	= 0.0
rand_tag        = 0
shower_cnt      = 0

c_nm            = 0
c_nm_tag        = 0
targetUpper     = 100.0
targetLower     = 15.0
targetUpperN    = 100.0
targetLowerN    = 15.0
t_burst         = 0

cnt1            = 0
cnt2            = 0
cnt3            = 0
cnt4            = 0
cnt5m           = 0


saveEvents = zeros((20,12), dtype=float64)
t_tsa_c = 0
t_tsa_evts = 0
firstShowerMuon = -1

deadmap = np.zeros(54,dtype=int)
for entry in f2:
    voltages = entry.voltages
    c = 0
    for volt in voltages:
        deadmap[c] = volt >200
        c+=1
#    print deadmap
    fdata 	= TFile(entry.GetFile().GetName())
    wbData 	= gROOT.FindObject('wbData')

    time_tot+= entry.totalTime/3600./24

    t_tsa_1 = 0.0
    t_tsa_2 = 0.0
    t_tsa_3 = 0.0

    t_burst = 0
    t_tsa_c = 0
    
    unix_time = entry.unix_time
    
    print "Processing run %s: days %8.7e"  %(entry.GetFile().GetName(),time_tot)

    if(entry.totalTime==0):
        print "Run %s needs to be reprocessed" %(entry.GetFile().GetName())

    for data in wbData:
        nPMT = struct.unpack('B',wbData.nPMT)[0]
        speVeto = wbData.speVeto
        speTarget = wbData.speTarget
        qBalTarget = wbData.qBalTarget
        
        pID = wbData.pID
        time = wbData.time
        spePMT = wbData.spePMT
#        print spePMT[0],spePMT[1]

        '''isMuon or isBadBaseline?'''
        if(speVeto > entry.qMuon or speTarget > targetUpper or pID ==2):
            b_time_stamp        = time
            if c_nm > 1:
                s_time_stamp    = old_time
                c_nm_tag        = c_nm
                if firstShowerMuon == -1:
                    print 'Found first shower'
                    firstShowerMuon = 1
                    firstShowerDetected_rf[0] = 1
                else:
                    firstShowerDetected_rf[0] += 1
        
            c_nm = 0
            old_time            = b_time_stamp/1e9 + unix_time
        
        '''isRightAfterMuon'''
        if(speVeto < entry.qMuon and speTarget < targetUpperN and \
           speTarget > targetLowerN and pID !=2 and\
           (time-b_time_stamp) < t_muon and nPMT>2):
           c_nm                 += 1

        '''isLongAfterMuon?'''
        if((time-b_time_stamp) > t_muon and \
           speVeto < entry.qMuon and speTarget < targetUpper and\
            speTarget > targetLowerN and pID !=2 and nPMT>2):
                t_tsa_evts      += 1
                t_tsa_c         += 1
                t_tsa_1         = t_tsa_2
                t_tsa_2         = t_tsa_3
                t_tsa_3         = time
                time2Mu_rf[0]   = t_tsa_2/1e9 + unix_time - s_time_stamp
                nAfterMu_rf[0]  = c_nm_tag
                tsa_target_1    = tsa_target_2
                tsa_target_2    = tsa_target_3
                tsa_target_3    = speTarget
                tsa_qBal_1      = tsa_qBal_2
                tsa_qBal_2      = tsa_qBal_3
                tsa_qBal_3      = qBalTarget
                t_tsa_23        = t_tsa_3 - t_tsa_2
                t_tsa_12        = t_tsa_2 - t_tsa_1

                '''long long'''
                if (t_tsa_c >2 and t_tsa_12 > t_tsa_tw and t_tsa_23 > t_tsa_tw):
                    tsa_flag                    = 1000
                    t_burst                     = 0
                    stamp_rf[0]                 = t_tsa_2/1e9 + entry.unix_time
                    dT_12_rf[0]                 = t_tsa_12
                    dT_23_rf[0]                 = t_tsa_23
                    tsa_flag_rf[0]              = tsa_flag
                    tsa_burst_rf[0]             = tsa_flag
                    tsa_target_1_rf[0]          = tsa_target_1
                    tsa_qBal_1_rf[0]            = tsa_qBal_1
                    tsa_target_2_rf[0]          = tsa_target_2
                    tsa_qBal_2_rf[0]            = tsa_qBal_2
                    tsa_target_3_rf[0]          = tsa_target_3
                    tsa_qBal_3_rf[0]            = tsa_qBal_3
                    burstTime_rf[0]             = -0.05
                    t_root.Fill()
                '''long short'''
                if (t_tsa_c >2 and t_tsa_12 > t_tsa_tw and t_tsa_23 < t_tsa_tw):
                    tsa_flag                    = 100
                    burstTime_ref               = t_tsa_2
                    t_burst                     = 0
                    saveEvents[t_burst,0]       = float(tsa_flag)
                    saveEvents[0:t_burst+1,1]   = float(tsa_flag)
                    saveEvents[t_burst,2]       = t_tsa_2/1e9 + entry.unix_time
                    saveEvents[t_burst,3]       = t_tsa_12
                    saveEvents[t_burst,4]       = t_tsa_23
                    saveEvents[t_burst,5]       = tsa_target_1
                    saveEvents[t_burst,6]       = tsa_qBal_1
                    saveEvents[t_burst,7]       = tsa_target_2
                    saveEvents[t_burst,8]       = tsa_qBal_2
                    saveEvents[t_burst,9]       = tsa_target_3
                    saveEvents[t_burst,10]      = tsa_qBal_3

                '''Short short'''
                if (t_tsa_c >2 and t_tsa_12 < t_tsa_tw and t_tsa_23 < t_tsa_tw):
                    t_burst                     +=1
                    tsa_flag                    = 100+t_burst*10
                    saveEvents[t_burst,0]       = float(tsa_flag)
                    saveEvents[0:t_burst+1,1]   = float(tsa_flag)
                    saveEvents[t_burst,2]       = t_tsa_2/1e9 + entry.unix_time
                    saveEvents[t_burst,3]       = t_tsa_12
                    saveEvents[t_burst,4]       = t_tsa_23
                    saveEvents[t_burst,5]       = tsa_target_1
                    saveEvents[t_burst,6]       = tsa_qBal_1
                    saveEvents[t_burst,7]       = tsa_target_2
                    saveEvents[t_burst,8]       = tsa_qBal_2
                    saveEvents[t_burst,9]       = tsa_target_3
                    saveEvents[t_burst,10]      = tsa_qBal_3
                
                '''Short long'''
                if (t_tsa_c >2 and t_tsa_12 < t_tsa_tw and t_tsa_23 > t_tsa_tw):
                    tsa_flag                    = 100+ t_burst*10 + 1
                    t_burst                     += 1
                    burstTime_diff              = t_tsa_2 - burstTime_ref
                    saveEvents[t_burst,0]       = float(tsa_flag)
                    saveEvents[0:t_burst+1,1]   = float(tsa_flag)
                    saveEvents[t_burst,2]       = t_tsa_2/1e9 + entry.unix_time
                    saveEvents[t_burst,3]       = t_tsa_12
                    saveEvents[t_burst,4]       = t_tsa_23
                    saveEvents[t_burst,5]       = tsa_target_1
                    saveEvents[t_burst,6]       = tsa_qBal_1
                    saveEvents[t_burst,7]       = tsa_target_2
                    saveEvents[t_burst,8]       = tsa_qBal_2
                    saveEvents[t_burst,9]       = tsa_target_3
                    saveEvents[t_burst,10]      = tsa_qBal_3
                    if t_burst == 1:
                        cnt1            += 1
                    if t_burst == 2:
                        cnt2            += 1
                    if t_burst >2 :
                        cnt3            += 1

                    print 'burst ',t_burst,tsa_flag,cnt1,cnt2,cnt3
                    
                    for i in range(t_burst+1):
#                        print 'Filling ',i,' / ', t_burst
                        tsa_flag_rf[0]          = int(saveEvents[i,0])
                        tsa_burst_rf[0]         = int(saveEvents[i,1])
                        stamp_rf[0]             = (saveEvents[i,2])
                        dT_12_rf[0]             = (saveEvents[i,3])
                        dT_23_rf[0]             = (saveEvents[i,4])
                        tsa_target_1_rf[0]      = (saveEvents[i,5])
                        tsa_qBal_1_rf[0]        = (saveEvents[i,6])
                        tsa_target_2_rf[0]      = (saveEvents[i,7])
                        tsa_qBal_2_rf[0]        = (saveEvents[i,8])
                        tsa_target_3_rf[0]      = (saveEvents[i,9])
                        tsa_qBal_3_rf[0]        = (saveEvents[i,10])
                        burstTime_rf[0]         = burstTime_diff
                        t_root.Fill()

                    t_burst = 0
                if(t_tsa_evts%50000==0):
                    print t_tsa_evts,t_tsa_evts/50000.
                
                if(t_tsa_evts%50000==0):
                    f_root.cd()
                    t_root.Write("", ROOT.TObject.kOverwrite)

    fdata.Close()

f_root.cd()
t_root.Write("", ROOT.TObject.kOverwrite)
f_root.Close()
