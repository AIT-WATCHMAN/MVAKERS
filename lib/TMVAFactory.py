import ROOT
from ROOT import gROOT
import os,sys
import numpy as np
import utils.dbutils as du

#Let's make ourselves a simple TMVA factory in python.
#FIXME: We should make a class with the main calls, but a subclass where
#The pair cases have the prompt and delayed "_p" and "_d" attached to the
#variables.

class TMVARunner(object):
    def __init__(self, signalfiles=[], backgroundfiles=[], mdict=None, 
            varspedict=None):
        '''
        This class takes in a signal file, background file, method
        dictionary, and variable dictionary and runs ROOT's TMVA classifiers.
        '''
        self.sfiles = signalfiles
        self.bfiles = backgroundfiles
        self.mdict = mdict
        self.vsdict = varspedict

        #weights for signal and background
        self.sweights = np.ones(len(signalfiles))
        self.bweights = np.ones(len(backgroundfiles))

        #Define a string of cuts, ROOT Style
        self.cuts = ""

    def setWeightForBackgroundFile(self,f,weight):
        '''for the given filename, set the weight in the weights array that
        corresponds to that file'''
        findex = None
        for j,fname in enumerate(self.bfiles):
            if fname == f:
                findex = j
        if findex is not None:
            self.bweights[findex] = weight
        else:
            print("Background file not found.  Weight not changed")
        return

    def setWeightForSignalFile(self,f,weight):
        '''for the given filename, set the weight in the weights array that
        corresponds to that file'''
        findex = None
        for j,fname in enumerate(self.sfiles):
            if fname == f:
                findex = j
        if findex is not None:
            self.sweights[findex] = weight
        else:
            print("Signal file not found.  Weight not changed")
        return

    def loadSignalFile(self,sf):
        '''Add a new signal file to TMVA signal file list'''
        self.sfiles.append(sf)
        self.sweights = np.append(self.sweights,1.0)
    
    def loadBackgroundFile(self,bf):
        '''Add a new background file to TMVA signal file list'''
        self.bfiles.append(bf)
        self.bweights = np.append(self.bweights,1.0)

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
        if len(self.sfiles)==0 or len(self.bfiles)==0:
            print("THERE ARE EITHER NO SIGNAL FILES OR BACKGROUND FILES.")
            print("PLEASE LOAD AT LEAST ONE OF EACH TYPE FOR THE MVA")
            return

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
        for j,sfile in enumerate(self.sfiles):
            sigfile = ROOT.TFile(sfile,"READ")
            signal = sigfile.Get("Output")
            factory.AddSignalTree(signal, self.sweights[j])
        for j,bfile in enumerate(self.bfiles):
            print("ADDING FILE " + str(bfile) + " TO BKGTREE\n")
            bkgfile = ROOT.TFile(bfile,"READ")
            background = bkgfile.Get("Output")
            factory.AddBackgroundTree(background, self.bweights[j])

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
