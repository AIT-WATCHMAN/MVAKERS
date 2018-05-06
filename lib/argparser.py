# Here we will put in the argparser commands for main that will be imported.
import argparse
import sys, os

basepath = os.path.dirname(__file__)
defaultout = os.path.abspath(os.path.join(basepath,"..","output"))

parser = argparse.ArgumentParser(description='Parser for WATCHMAKERS Multivariate Analysis Tools')

##---------------------MAIN RUN FLAGS---------------------##
parser.add_argument('--debug', dest='DEBUG',action='store_true',
        help='Run in debug mode and get some extra outputs and stuff')
parser.add_argument('--buildSB', dest='BUILD', action='store_true',
        help='take files from a WATCHMAKERS data directory (specified with the'+\
                "--datadir flag) and prepare signal/background root files for"+\
                "the TMVA")
parser.add_argument('--MVA', dest='RUNTMVA', action='store_true',
        help='Take the signal.root and background.root from the specified outdir and'+\
                "run the TMVA analysis.  Output root file is saved in outdir")
parser.add_argument('--GUI', dest='RUNGUI', action='store_true',
        help='If flag is activated, ROOT TMVA GUI is run on TMVA output in current'+\
                'research directory')
parser.add_argument('--datadir', dest='DATADIR', action='store', type=str,
        help="Points to data where WATCHMAKERS  files")
parser.add_argument('--jobnum', dest='JNUM', action='store', type=int,
        help='Specify the job number; will have results save in output/results_JNUM')
parser.add_argument('--outdir', dest='OUTDIR', action='store', type=str,
        help='Specify the output directory to save the results_JNUM directory'+\
                'into (will have SBbuild files and MVA results')
parser.add_argument('--pc', dest='PHOTOCOVERAGE', action='store', type=str,
        help="Specify the photocoverage directory you want to read from"+\
                "(FORMAT: 'Npct' for N percent photocoverage)")
parser.add_argument('--singles', dest='SINGLES', action='store', type=str,
        help='Build signal/background files with accidentals for background and'+\
                'either "neutron" or "positron" for signal (input is a '+\
                'string, either "neutron" or "positron")')
parser.add_argument('--ibd', dest='PAIRS', action='store_true',
        help='Build signal/background files by forming IBD pairs from '+\
                'PMT/WaterVolume radioactivity accidentals and the '+\
                'IBD Monte Carlo present in the input DATADIR flag')

##--------------------SPECIFICATIONS FOR BKG RATE CALCULATION----------##
parser.add_argument('--halfHeight', dest='HALFHEIGHT', action='store', type=float,
        help='Define the height of the WATCHMAN tank in mm')
parser.add_argument('--shieldThick', dest='SHIELDTHICK', action='store', type=float,
        help='Distance from tank to PMT frame in mm')
parser.add_argument('--tankRadius', dest='TANKRADIUS', action='store', type=float,
        help='Radius of tank in mm')
##--------------------ADDITIONAL CUTS TO USE PRE-MVA-------------------##
parser.add_argument('--addcuts', dest='ADDCUTS', action='append', nargs=2,
        metavar=('cutname','cutval'), help='Add a cut to implement '+\
                'when selecting events buildSB stage. '+\
                'Variable must be defined in DB directory. '+\
                '(overwrites any values defined in cuts.json)')

parser.set_defaults(DEBUG=False,JNUM=0, ADDCUTS=[], BUILD=False,
        SINGLES=None,PAIRS=False, DATADIR=None,PHOTOCOVERAGE='25pct',
        RUNTMVA=False,OUTDIR=defaultout, RUNGUI=False)


def checkParserInput(argin):
    if argin.BUILD is True:
        if argin.DATADIR is None:
            print("No WATCHMAKERS data directory input.  Exiting")
            sys.exit(1)
        if os.path.isdir(argin.DATADIR) is False:
            print("The Data directory input does not exist.  Exiting")
            sys.exit(1)
        if os.path.isdir("%s/%s/" % (argin.DATADIR, argin.PHOTOCOVERAGE)) is False:
            print("Photocoverage selected was not available in input data directory."+\
                "exiting")
            sys.exit(1)
        if argin.PAIRS is True and argin.SINGLES is not None:
            print("You are trying to build both IBD pair candidates and singles"+\
                "in the SB-Builder.  Please choose only one")
            sys.exit(1)
        if argin.SINGLES is not None and argin.SINGLES not in ["positron","neutron"]:
            print("Please select either the positron or neutron option for"+\
                "building your signal singles.")
            sys.exit(1)
#TODO: Have some check that makes sure all variables are > 0 that should be

args = parser.parse_args()
checkParserInput(args)

