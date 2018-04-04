import lib.argparser as ap
import lib.TMVAGui.GUIRun as tvag
import lib.utils.dbutils as du
import lib.TMVAFactory as tf
import lib.make_signal_singles as ss
import lib.make_signal_pairs as sp
import lib.make_background_singles as bs
import lib.make_background_pairs as bp
import lib.utils.splash as s
import glob
import os, sys, time
import json
import subprocess

basepath = os.path.dirname(__file__)
mainpath = os.path.abspath(basepath)
configpath = os.path.abspath(os.path.join(basepath,"config"))
dbpath = os.path.abspath(os.path.join(basepath,"db"))
guipath = os.path.abspath(os.path.join(basepath,"lib","TMVAGui"))

args = ap.args

#args defining what files are used to run what kind of MVA
BUILD = args.BUILD
RUNTMVA = args.RUNTMVA
RUNGUI = args.RUNGUI
DEBUG = args.DEBUG
PAIRS=args.PAIRS
SINGLES=args.SINGLES
DATADIR=args.DATADIR
PC=args.PHOTOCOVERAGE
JNUM=args.JNUM
OUTDIR=args.OUTDIR+'/results_%i' % (JNUM)

#Cuts applied if value is not None
TIMETHRESH=args.TIMETHRESH
INTERDIST=args.INTERDIST
RADIUSCUT=args.RADIUSCUT
ZCUT=args.ZCUT

if not os.path.exists(OUTDIR):
    os.makedirs(OUTDIR)
if BUILD is True and os.path.exists(OUTDIR) is True:
    print("WARNING: YOU ARE BUILDING SIGNAL/BKG FILES TO AN EXISTING DIRECTORY.")
    print("EXISTANT DATA IN THE DIRECTORY WILL BE DELETED IF YOU PROCEED")
    time.sleep(3)

#TODO:
#  - Need to make the OUTDIR that everything will be saved to.
#  - Load the cuts configuration json.  Any modifications done on
#  - command line should be added into the dictionary.
#  - Add the OUTDIR component onto the outputfile names given to each make
#    signal/background function.
#  - Want an option to only run the TMVA on the OUTDIR, no making the files
#  -

if __name__ == '__main__':
    s.splash()

    #FIXME: Have these as a toggle flag?  Or in config json? 
    MAXSIGNALEV = 1000
    MAXBKGEV = 1000
    sout = "%s/signal.root" % (OUTDIR)
    bout = "%s/background.root" % (OUTDIR)
    mvaout = "%s/TMVA_output.root" % (OUTDIR)
    if BUILD is True:
        print("------BUILDING SIGNAL AND BACKGROUND FILES------")
        time.sleep(2)

        print("LOADING CUTS TO USE AS DEFINED IN CONFIG DIR")
        with open("%s/%s" % (configpath,"cuts.json"),"r") as f:
            cutdict = json.load(f)
        
        print("GETTING ALL AVAILABLE BACKGROUND FILES FROM DATADIR")
        Bkg_types = ["WV","PMT"]
        #Bkg_types = ["neutron"]
        bkgrootfiles=[]
        for btype in Bkg_types:
            bkgrootfiles += glob.glob("%s/%s/*%s.root" % (DATADIR,PC,btype))
        if DEBUG is True:
            print("BKGFILES BEING USED: " + str(bkgrootfiles))
        if len(bkgrootfiles) == 0:
            print("NO BACKGROUND FILES FOUND.  EXITING")
            sys.exit(1)
        print("BACKGROUND FILES ACQUIRED.")
    
        sigrootfiles=[]
        if PAIRS is True:
            print("GETTING PAIR SIGNAL FILES FROM DATADIR/ITID")
            sigrootfiles += glob.glob("%s/%s/ITID/*.root" % (DATADIR,PC))
        if SINGLES is not None:
            print("GETTING SINGLES SIGNAL FILE OF TYPE %s" % (SINGLES))
            sigrootfiles += glob.glob("%s/%s/*%s.root" % (DATADIR,PC,SINGLES))

        if DEBUG is True:
            print("SIGNAL FILES BEING USED: " + str(sigrootfiles))
        if len(bkgrootfiles) == 0:
            print("NO SIGNAL FILES FOUND.  EXITING")
        print("SIGNAL FILES ACQUIRED.")

        #Save configuration files for user reference
        files_used = {"SIGNAL": sigrootfiles, "BACKGROUND": bkgrootfiles}
        with open(OUTDIR+"/SB_files_used.json","w") as f:
            json.dump(files_used,f,sort_keys=True,indent=4)
	with open(OUTDIR+"/cuts_applied.json","w") as f:
            json.dump(cut_dict,f,sort_keys=True,indent=4)

        if SINGLES is not None:
            print("PREPARING SINGLE SIGNAL NTUPLE FILES NOW...")
            ss.getSignalSingles(cutdict=cutdict,
                    rootfiles=sigrootfiles,outfile=sout)
            print("SIGNAL FILES COMPLETE.  PREPARING SINGLE BKG. NTUPLES...") 
            bs.getBackgroundSingles(cutdict=cutdict,
                    rootfiles=bkgrootfiles,outfile=bout)
        if PAIRS is True:
            print("PREPARING PAIRED SIGNAL NTUPLE FILES NOW...")
            sp.getSignalPairs(cutdict=cutdict, 
                    rootfiles=sigrootfiles,outfile=sout,max_entries=MAXSIGNALEV)
            print("SIGNAL FILES COMPLETE.  PREPAIRING PAIR BKG. NTUPLES...")
            bp.getBackgroundPairs(cutdict=cutdict,
                    rootfiles=bkgrootfiles,outfile=bout,max_entries=MAXBKGEV)
        print("SIGNAL AND OUTPUT FILES SAVED TO %s" % OUTDIR)

    if RUNTMVA is True:
        print("LOADING VARIABLES TO USE AS DEFINED IN CONFIG DIR")
        with open("%s/%s" % (configpath,"variables.json"),"r") as f:
            varstouse = json.load(f)
        with open("%s/%s" % (dbpath,"WATCHMAKERS_variables.json"),"r") as f:
            variable_db = json.load(f)
        vardict = du.loadVariableDescriptions(varstouse["variables"],
                        variable_db)
        spedict = du.loadVariableDescriptions(varstouse["spectators"],
                        variable_db)

        methoddict = {}
        print("LOADING METHODS TO USE AS DEFINED IN CONFIG DIR")
        with open("%s/%s" % (configpath,"methods.json"),"r") as f:
            methoddict = json.load(f)
        
        if DEBUG is True:
            print("VARIABLES BEING FED IN TO MVA: " + str(vardict))
            print("METHODS BEING FED IN TO MVA: " + str(methoddict))
        print("RUNNING TMVA ON SIGNAL AND BACKGROUND FILES NOW...")
        mvaker = tf.TMVARunner(signalfile=sout, backgroundfile=bout,
                mdict=methoddict, vdict=vardict,sdict=spedict)
        mvaker.RunTMVA(outfile=mvaout,pairs=PAIRS)
        subprocess.call(["mv","-f","%s/weights"%(mainpath),OUTDIR])
    if RUNGUI is True:
        tvag.loadResultsInGui(GUIdir=guipath, resultfile=mvaout)

