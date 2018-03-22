import lib.argparser as ap

args = ap.args

DEBUG = args.DEBUG
TIMETHRESH=args.TIMETHRESH
INTERDIST=args.INTERDIST
RADIUSCUT=args.RADIUSCUT
ZCUT=args.ZCUT
DATADIR=args.DATADIR
PHOTOCOVERAGE=args.PHOTOCOVERAGE

if __name__ == '__main__':
    print("WELCOME TO THE WATCHMVAKERS ANNEX.")

    print("GETTING ALL AVAILABLE BACKGROUND FILES FROM DATADIR")
    Bkg_types = ["WV","PMT"]
    for btype in Bkg_types:
        bkgrootfiles = glob.glob("%s/%s/*%s.root" % (DATADIR,PHOTOCOVERAGE,btype))
    if len(bkgrootfiles) == 0:
        print("NO BACKGROUND FILES FOUND.  EXITING")
        sys.exit(1)



