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
            varspedict=None):
        '''
        This class takes in a signal file, background file, method
        dictionary, and variable dictionary and runs ROOT's TMVA classifiers.
        '''
        self.sfile = signalfile
        self.bfile = backgroundfile
        self.mdict = mdict
        self.vsdict = varspedict

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

    def addPairVars(self, factory, vardict):
        for var in vardict["prompt"]:
            factory.AddVariable("%s_p"%str(var),"prompt %s"%(str(vardict["prompt"][var]["title"])),
                str(vardict["prompt"][var]["units"]))
        for var in vardict["delayed"]:
            factory.AddVariable("%s_d"%str(var),"delayed %s"%(str(vardict["delayed"][var]["title"])),
                str(vardict["delayed"][var]["units"]))
        for var in vardict["interevent"]:
            factory.AddVariable(str(var),str(vardict["interevent"][var]["title"]),
                    str(vardict["interevent"][var]["units"]))
        return factory

    def addPairSpecs(self, factory, vardict):
        for var in vardict["prompt"]:
            factory.AddSpectator("%s_p"%str(var),"prompt %s"%(str(vardict["prompt"][var]["title"])),
                str(vardict["prompt"][var]["units"]))
        for var in vardict["delayed"]:
            factory.AddSpectator("%s_d"%str(var),"delayed %s"%(str(vardict["delayed"][var]["title"])),
                str(vardict["delayed"][var]["units"]))
        for var in vardict["interevent"]:
            factory.AddSpectator(str(var),str(vardict["interevent"][var]["title"]),
                    str(vardict["interevent"][var]["units"]))
        return factory


    def RunTMVA(self,outfile='TMVA_output.root',pairs=True):
        '''Runs the TMVA with the given settings.'''

        ROOT.TMVA.Tools.Instance()


        #initialize the TMVA Factory
        ofile = ROOT.TFile.Open(outfile, "RECREATE")
        factory = ROOT.TMVA.Factory("TMVAClassification", ofile,\
                "!V:!Silent:Color:DrawProgressBar:Transformations"+\
                "=I;D;P;G;D:AnalysisType=Classification")

        if pairs is True:
            factory = self.addPairVars(factory, self.vsdict["variables"])
        else:
            for var in self.vsdict["variables"]:
                factory.AddVariable(str(var),str(self.vsdict["variables"][var]["title"]),
                    str(self.vsdict["variables"][var]["units"]))
        if pairs is True:
            factory = self.addPairSpecs(factory, self.vsdict["spectators"])
        else:
            for var in self.vsdict["spectators"]:
                factory.AddSpectator(str(var),str(self.vsdict["spectators"][var]["title"]),
                    str(self.vsdict["spectators"][var]["units"]))
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
                specs = "!H:!V:FitMethod=MC:EffSel:SampleSize=15000000:VarProp=FSmart"
                if method == "CutsD":
                    specs = specs + ":VarTransform=Decorrelate"
                if method == "CutsPCA":
                    specs = specs + ":VarTransform=PCA"
                if method == "CutsGA":
                    #TODO: Have defaults in dictionary in DB, put mods in mdict  
                    specs = self.mdict[method]["specs"]
                    print("SPECS: " + str(specs))
            else:
                specs = self.mdict[method]["specs"]
            print("BOOKING..." + str(self.mdict[method]["type"]))
            factory.BookMethod(getattr(ROOT.TMVA.Types,
                str(self.mdict[method]["type"])),str(method),str(specs))

        factory.TrainAllMethods() #Train MVAs with training events
        factory.TestAllMethods() #Evaluate all MVAS with set of test events
        factory.EvaluateAllMethods() #Evaluate and compare method performances

        ofile.Close()

        print("MVA Factory done.  Wrote output to %s." % (ofile.GetName()))
        del factory
