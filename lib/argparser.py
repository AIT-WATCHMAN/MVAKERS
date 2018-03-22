# Here we will put in the argparser commands for main that will be imported.
import argparse

import os

#TODO: Have OUTDIR default to pointing at output/results_JOBNUM

parser = argparse.ArgumentParser(description='Parser for WATCHMAKERS Multivariate Analysis Tools')
parser.add_argument('--debug', dest='DEBUG',action='store_true', type=bool,
        help='Run in debug mode and get some extra outputs and stuff')
parser.add_argument('--jobnum', dest='JNUM', action='store', type=str,
        help='Specify the job number; will have results save in output/results_JNUM')
arser.add_argument('--outdir', dest='OUTDIR', action='store', type=str,
        help='Specify the output directory to save signal and background roots'+\
                'as well as the TMVA results')
parser.add_argument('--pc', dest='PHOTOCOVERAGE', action='store', type=str,
        help="Specify the photocoverage directory you want to read from"+\
                "(FORMAT: 'Npct' for N percent photocoverage)")
parser.add_argument('--buildSB', dest='BUILD', action='store_true', type=str,
        help='take files from a WATCHMAKERS data directory (specified with the'+\
                "--datadir flag) and prepare signal/background root files for"+\
                "the TMVA")
parser.add_argument('--datadir', dest='DATADIR', action='store', type=str,
        help="Points to data directory that will be used to build Sig/Bkg files")
parser.add_argument('--singles', dest='SINGLES', action='store', type=str,
        help='Build signal/background files with accidentals for background and'+\
                'either "neutron" or "positron" for signal (input is a '+\
                'string, either "neutron" or "positron")')
parser.add_argument('--ibd', dest='PAIRS', action='store_true', type=bool,
        help='Build signal/background files by forming IBD pairs from '+\
                'accidentals in given directory for'+\
                'background, and from Bonsai IBD Monte Carlo in DATADIR/ITID/')
parser.add_argument('--zcut', dest='ZCUT', action='store', type=float,
        help='Only consider events with abs(z) less than abs(input)'+\
                'relative to detector center')
parser.add_argument('--timecut', dest='TIMETHRESH', action='store', type=float,
        help='If IBD option set, only consider IBD candidates with an interevent time <= input')
parser.add_argument('--distcut', dest='INTERDIST', action='store', type=float,
        help='If IBD option set, only consider IBD candidates with an interevent_dist <= input.')
parser.add_argument('--rcut', dest='RADIUSCUT', action='store', type=float,
        help='Only consider events with reconstructed r <= input (in mm).')
parser.add_argument('--noMVA', dest='RUNTMVA', action='store_false', type=bool,
        help='Give this flag if you only want to build signal/background files'+\
                'and exit afterwards.')
parser.set_defaults(DEBUG=False,JNUM=0, TIMETHRESH=5.0E5, BUILD=False,
        INTERDIST=None, RADIUSCUT=None,ZCUT=None,DATADIR=None,
        PHOTOCOVERAGE='25pct',RUNTMVA=True)


def checkParserInput(argin):
    if argin.BUILD is True:
        if argin.DATADIR is None:
            print("No WATCHMAKERS data directory input.  Exiting")
            sys.exit(1)
        if os.path.isdir(argin.DATADIR) is False:
            print("The Data directory input does not exist.  Exiting")
            sys.exit(1)
        if os.path.isdir("%s/%s/" % (argin.DATADIR, argin.PHOTOCOVERAGE)):
            print("Photocoverage selected was not available in input data directory."+\
                "exiting")
            sys.exit(1)
        if argin.PAIRS is True and argin.SINGLES is not None:
            print("You are trying to build both IBD pair candidates and singles"+\
                "in the SB-Builder.  Please choose only one")
            sys.exit(1)
        if argin.SINGLES not in ["positron","neutron"]:
            print("Please select either the positron or neutron option for"+\
                "building your signal singles.")
        sys.exit(1)
    for val in [argin.TIMETHRESH, argin.ZCUT, argin.RADIUSCUT, argin.INTERDIST]:
        if val < 0:
            print("Negative value given for an input cut value.  Exiting")
            sys.exit(1)


args = parser.parse_args()
checkParserInput(args)

