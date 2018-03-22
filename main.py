import lib.argparser as ap
import lib.make_signal_singles as ss
import lib.make_signal_pairs as sp
import lib.make_background_singles as bs
import lib.make_background_pairs as bp
import time
import json

args = ap.args

DEBUG = args.DEBUG
TIMETHRESH=args.TIMETHRESH
INTERDIST=args.INTERDIST
RADIUSCUT=args.RADIUSCUT
ZCUT=args.ZCUT
PAIRS=args.PAIRS
SINGLES=args.SINGLES
DATADIR=args.DATADIR
PC=args.PHOTOCOVERAGE
JNUM=args.JNUM
OUTDIR=args.OUTDIR+'/results_'+JNUM

#TODO:
#  - Need to make the OUTDIR that everything will be saved to.
#  - Load the cuts configuration json.  Any modifications done on
#  - command line should be added into the dictionary.
#  - Add the OUTDIR component onto the outputfile names given to each make
#    signal/background function.
#  - Want an option to only run the TMVA on the OUTDIR, no making the files
#  -

if __name__ == '__main__':
    print("WELCOME TO THE WATCHMVAKERS ANNEX.")

    if BUILD is True:
        print("------BUILDING SIGNAL AND BACKGROUND FILES------")
        time.sleep(2)

        print("GETTING ALL AVAILABLE BACKGROUND FILES FROM DATADIR")
        Bkg_types = ["WV","PMT"]
        bkgrootfiles=[]
        for btype in Bkg_types:
            bkgrootfiles += glob.glob("%s/%s/*%s.root" % (DATADIR,PC,btype))
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
        if len(bkgrootfiles) == 0:
            print("NO SIGNAL FILES FOUND.  EXITING")
        print("SIGNAL FILES ACQUIRED.")

        files_used = {"SIGNAL": sigrootfiles, "BACKGROUND": bkgrootfiles}
        with open(OUTDIR+"/SB_files_used.json","w") as f:
            json.dump(files_used,f,sort_keys=True,indent=4)

        print("PREPARING SIGNAL AND BACKGROUND NTUPLE FILES NOW...")
        sout = "%s/signal.root" % (OUTDIR)
        bout = "%s/background.root" % (OUTDIR)
        if SINGLES is not None:
            sfile = ss.getSignalSingles(rootfiles=sigrootfiles,outfile=sout)
            bfile = bs.getBackgroundSingles(rootfiles=bkgrootfiles,outfile=bout)
        if PAIRS is True:
            sfile = sp.getSignalPairs(rootfiles=sigrootfiles,outfile=sout)
            bfile = bp.getBackgroundPairs(rootfiles=bkgrootfiles,outfile=bout)
        print("SIGNAL AND OUTPUT FILES SAVED TO %s" % OUTDIR)
    if RUNTMVA is True:
        print("RUNNING TMVA ON SIGNAL AND BACKGROUND FILES NOW...")
