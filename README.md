MULTIVARAITE ANALYSIS TOOLS FOR WATCHMAN

======================================================

This repository contains tools for turning data from ROOT files into a
TMVA-friendly ROOT file format.  Currently, the TMVA files in use are 
heavily based on examples provided with the TMVA package installed with ROOT.

SBMaker/ contains a ROOT script that provides an example for converting data
from an ntuple into a TMVA-friendly histogram file.

SBMaker/python/ mostly contains tools for changing a WATCHMAN signal or
background file into an ntuple file where each event contains both the prompt
and delayed parameters for an IBD candidate.  This is preferable for optimizing
an MVA that will pick an IBD candidate based on both prompt and delayed info.
