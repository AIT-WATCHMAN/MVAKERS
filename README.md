MULTIVARAITE ANALYSIS TOOLS FOR WATCHMAN

======================================================

This repository contains tools for turning data from ROOT files into a
TMVA-friendly ROOT file format, running the TMVA packages using the python
wrapper, and then outputting the data using TMVA's graphic visualizer.

TMVA is a root-based library that can train different classifiers to
recognize and separate signal & background events.  

usage description:

python main.py --help

#####-----------_Tour of the current directories---------#####

./bash/: Some example bash scripts for running MVAKERS on a cluster using
the MOAB cluster suite for job subscription. Can also give you an idea of
how to use the flags specified when running main.py. 

./db/: Various hard-defined information used to generate plots and 
inform on what variables are available from RAT-PAC/BONSAI output.
WATCHMAKERS_variables.json: variables output from WATCHMAKERS ntuples
that can be defined in ./config/variables.json for TMVA classifier training.

./config/: Here are most of the toggles used by the user to decide what
variables to use in the TMVA software.

variables.json: for either a "pairs" or "singles" analysis run, variables
specified in the "variables" section will be used in the TMVA classifier
training process.  variables in "spectators" will be carried along for the
ride and plotted, but not used.

cuts.json: Cuts will define what events for a variable are used.
Variables that are compatible with definition in cuts.json:
  - interevent_time, interevent_dist,closestPMT: events with values 
less than defined cuts are accepted
  - pe, nhit, n9, good_pos, good_dir: events with values greater than the
defined cuts are accepted.

setup.json: Parameters that control the data preparation/partitioning in TMVA.
MAXBKGEV/MAXSIGNALEV: ntuples built that feed into TMVA will not have more than
the number of events specified here
BKGTYPES: Specify what background types will be used to construct the 
detector background file training the TMVA.
Currently implemented:
  - PMT_RADON: Takes files from a WATCHMAKERS data output's PMT & WaterVolume
 directories and uses these (with rate weighting) to construct the background file
Future implementation plans: MUON_RADIONUCLIDE, MUON_FASTNEUTRONS

methods.json: Here are defined the methods/classifiers used by the TMVA.
Each method's dictionary key can be named anything by the user.  A comments
section is also available for convenience.  The type and specs must be
defined according to the TMVA standards for each classifier.  See here:

tmva.sourceforge.net/optionRef.html

Or google for "TMVA Options Reference" for more references.

./doc/: Directory for any documentation I think is valuable.
The availablemethods.txt is a list of the default classifiers you can run
with TMVA's example script TMVAClassificationExample.C .  Take a look at
how these are defined for inspiration in your methods.json!

main.py: the main script you want to run to begin everything.  Mostly, this
is a controller of everything going on under the hood in the ./lib/ directory.

./lib/: Where most of the machinery is. make_background and make_signal files
are used to construct the signal/background ntuples fed to the TMVA.  The
argparser parses all of the flags fed to main.py.  ./lib/utils/ has some
lower level methods shared by scripts in ./lib/.  ./lib/TMVAGui/ has the
ROOT TMVA macro, which main.py calls/runs if --GUI is given to main.py

main.py: the main script you want to run to begin everything.  Mostly, this
is a controller of everything going on under the hood in the ./lib/ directory.

./lib/: Where most of the machinery is. make_background and make_signal files
are used to construct the signal/background ntuples fed to the TMVA.  The
argparser parses all of the flags fed to main.py.  ./lib/utils/ has some
lower level methods shared by scripts in ./lib/.  ./lib/TMVAGui/ has the
ROOT TMVA macro, which main.py calls/runs if --GUI is given to main.py

./output/: Default location for results output after generating signal/background
ntuples or TMVA results.  Files output have the name format
results_{JOBNUM}, where JOBNUM is an integer specified with the -j flag.

./tomb/: A place for old code that you don't quite have the heart to get rid
of or may want to reference in the future.  Here there be monsters.
