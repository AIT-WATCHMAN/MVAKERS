import ROOT
from ROOT import gROOT
import os,sys
import utils.dbutils as du

#Let's make ourselves a simple TMVA factory in python.
#FIXME: We should make a class with the main calls, but a subclass where
#The pair cases have the prompt and delayed "_p" and "_d" attached to the
#variables.

class TMVARunner(object):
    def __init__(self, signalfile=None, backgroundfile=None, mdict=None, 
            sdict=None,vdict=None):
        '''
        This class takes in a signal file, background file, method
        dictionary, and variable dictionary and runs ROOT's TMVA classifiers.
        '''
        self.sfile = signalfile
        self.bfile = backgroundfile
        self.mdict = mdict
        self.vdict = vdict
        self.sdict = sdict

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

    def loadBkgFile(self,bf):
        '''load a new signal file to run the TMVA with.'''
        self.bfile = bf

    def addPairVars(self, factory, var, vardict):
        factory.AddVariable("%s_p"%str(var),str(vardict[var]["title"]),
                str(vardict[var]["units"]))
        factory.AddVariable("%s_d"%str(var),str(vardict[var]["title"]),
                str(vardict[var]["units"]))
        return factory

    def addPairSpecs(self, factory, var, vardict):
        print("ADDIND SPECTATOR " + str(var))
        factory.AddSpectator("%s_p"%str(var),str(vardict[var]["title"]),
                str(vardict[var]["units"]))
        factory.AddSpectator("%s_d"%str(var),str(vardict[var]["title"]),
                str(vardict[var]["units"]))
        return factory

    def RunTMVA(self,outfile='TMVA_output.root',pairs=True):
        '''Runs the TMVA with the given settings.'''

        #TODO: Check if we actually need this...
        ROOT.TMVA.Tools.Instance()


        #initialize the TMVA Factory
        ofile = ROOT.TFile.Open(outfile, "RECREATE")
        factory = ROOT.TMVA.Factory("TMVAClassification", ofile,\
                "!V:!Silent:Color:DrawProgressBar:Transformations"+\
                "=I;D;P;G;D:AnalysisType=Classification")

        print(self.vdict)
        for var in self.vdict:
            if pairs is True and var not in ["interevent_time","interevent_dist"]:
                factory = self.addPairVars(factory, var,self.vdict)
            else:
                factory.AddVariable(str(var),str(self.vdict[var]["title"]),
                        str(self.vdict[var]["units"]))
        if self.sdict is not None:
            for spe in self.sdict:
                if pairs is True and spe not in ["interevent_time","interevent_dist"]:
                    factory = self.addPairSpecs(factory, spe, self.sdict)
                else:
                    factory.AddSpectator(str(spe),
                            str(self.sdict[spe]["title"]),str(self.sdict[spe]["units"]))
        #Add signal and background info. to factory
        sigfile = ROOT.TFile(self.sfile,"READ")
        bkgfile = ROOT.TFile(self.bfile,"READ")
        signal = sigfile.Get("Output")
        background = bkgfile.Get("Output")
        factory.AddSignalTree(signal, self.sw)
        factory.AddBackgroundTree(background, self.bw)

        #Now, we book our methods to use in the TMVA.
        print("BOOKING METHODS...")
        for method in self.mdict:
            #FIXME: Have a nice parser class for making these strings
            if self.mdict[method]["type"] == "kCuts":
                specs = "!H:!V:FitMethod=MC:EffSel:SampleSize=200000:VarProp=FSmart"
            elif self.mdict[method]["type"] == "kBDT":
                specs = "!H:!V:NTrees=1000:MinNodeSize=2.5%:MaxDepth=3:"+\
                        "BoostType=AdaBoost:AdaBoostBeta=0.5:UseBaggedBoost:"+\
                        "BaggedSampleFraction=0.5:SeparationType=GiniIndex:"+\
                        "ncuts=20"
            else:
                print("Method %s not supported in this class yet." % (self.mdict[method]["type"]))
                continue
            print("BOOKING..." + str(self.mdict[method]["type"]))
            print("METHOD IS " + str(method))
            factory.BookMethod(getattr(ROOT.TMVA.Types,
                str(self.mdict[method]["type"])),str(method),specs)

        factory.TrainAllMethods() #Train MVAs with training events
        factory.TestAllMethods() #Evaluate all MVAS with set of test events
        factory.EvaluateAllMethods() #Evaluate and compare method performances

        ofile.Close()

        print("MVA Factory done.  Wrote output to %s." % (ofile.GetName()))

        del factory
