import ROOT
from ROOT import gROOT
import os,sys

#Let's make ourselves a simple TMVA factory in python.

class TMVARunner(object):
    def __init__(self, sfile=None, bfile=None, mdict=None):
        '''
        This class takes in a signal file, background file, and method
        dictionary and runs ROOT's TMVA classifiers.
        '''
        self.sfile = sfile
        self.bfile = bfile
        self.mdict = mdict

        #weights for signal and background
        self.sw = 1.0
        self.bw = 1.0

        #Define a string of cuts, ROOT Style
        self.cuts = ""

    def setWeights(self,signal=1.0,background=1.0):
        self.sw = signal
        self.bw = background

    def loadSignalFile(self,sf):
        '''Choose a new signal file to run the TMVA with'''
        self.sfile = sf

    def addCut(self,cut):
        '''
        Add a cut to the cuts to be used by the factory.  Cut must be 
        a variable written in the methods dictionary.
        Format: (cutmask&17)==17 && n9>3"
        '''
        if self.cuts == "":
            self.cuts = self.cuts + cut
        else:
            self.cuts = self.cuts + "&&" + cut

    def clearCuts(self):
        '''Delete all cuts to be fed to the TMVA factory'''
        self.cuts=""

    def loadBkgFile(self,sf):
        '''load a new signal file to run the TMVA with.'''
        self.sfile = sf

    def loadResultsInGui(self,resultfile):
        '''Load the resultfile with the TMVA Gui'''
        #gROOT.SetMacroPath(Use os.path to fill in where the macrow will be)
        #gROOT.ProcessLine(".L TMVAGui.C")

    def RunTMVA(self,outfile='TMVA_output.root'):
        '''Runs the TMVA with the given settings.'''

        #TODO: Check if we actually need this...
        ROOT.TMVA.Tools.Instance()


        #initialize the TMVA Factory
        ofile = ROOT.TFile.Open(outfile, "RECREATE")
        factory = ROOT.TMVA.Factory("TMVAClassification", ofile,\
                "!V:!Silent:Color:DrawProgressBar:Transformations"+\
                "=I;D;P;G;D:AnalysisType=Classification")

        for var in self.mdict["variables"]:
            factory.AddVariable(var["name"],var["title"],var["units"],var["type"])
        for spe in self.mdict["spectators"]:
            factory.AddSpectator(spe["name"],spe["title"],spe["units"],spe["type"])
        #Add signal and background info. to factory
        sigfile = ROOT.TFile(self.sfile,"READ")
        bkgfile = ROOT.TFile(self.bfile,"READ")
        signal = sigfile.Get("Output")
        background = bkgfile.Get("Output")
        factory.AddSignalTree(signal, self.sw)
        factory.AddBackgroundTree(background, self.bw)

        #Now, we book our methods to use in the TMVA.
        for method in self.mdict["methods"]:
            #FIXME: Have a nice parser class for making these strings
            if method["type"] == "kCuts":
                specs = "!H:!V:FitMethod=MC:EffSel:SampleSize=200000:VarProp=FSmart"
            elif method["type"] == "kBDT":
                specs = "!H:!V:NTrees=1000:MinNodeSize=2.5%:MaxDepth=3:"+\
                        "BoostType=AdaBoost:AdaBoostBeta=0.5:UseBaggedBoost:"+\
                        "BaggedSampleFraction=0.5:SeparationType=GiniIndex:"+\
                        "ncuts=20"
            else:
                print("Method %s not supported in this class yet." % (method["type"])
                continue
            factory.BookMethod(getattr(ROOT.TMVA.Types,method["type"]),\
                   specs)

        factory.TrainAllMethods() #Train MVAs with training events
        factory.TestAllMethods() #Evaluate all MVAS with set of test events
        factory.EvaluateAllMethods() #Evaluate and compare method performances

        ofile.Close()

        print("MVA Factory done.  Wrote output to %s." % (ofile.GetName()))

        del factory
