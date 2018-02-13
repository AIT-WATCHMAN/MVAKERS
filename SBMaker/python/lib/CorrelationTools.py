#This library contains functions relevant to producing the correlation matrix
#Based on the phi coefficient.  The phi coefficient gives you a measure
#of how correlated two binary values are.
import playDarts as pd

import ROOT
from ROOT import TChain, gDirectory, gROOT

import copy
import numpy as np
import scipy
import scipy.linalg
import numpy.linalg

    #TODO: So we need a couple things...
    #1: Feed the CovarianceMatrix class a list of ntuple title strings
    #2: Based on the string list, make the covariance matrix
    #   (The string map should also be how variables are fed into the
    #   self.variables function

#Class takes in root files of like structure and can output a 
#Covariance matrix associated with the variables.
class CorrelationFinder(object):
    def __init__(self, variables=None, rootfiles=None, tree=None):
        self.files = rootfiles
        self.treename = None
        self.setDataTree(tree)
        self.rchain = self.createTChain(self.files)
        self.variables = variables

    def setDataTree(self,datatree_string):
        self.treename=datatree_string

    def addRootFiles(self,rootfiles):
        if isinstance(rootfiles,list) is True:
            for rf in rootfiles:
                if isinstance(rf,TFile) is True:
                    self.files.append(rf)
                else:
                    print("warning: skipping array elements not of TFile type")
        if isinstance(rootfiles,TFile) is True:
            self.files.append(rootfiles)

    def clearRootFiles(self):
        self.files = None

    def createTChain(self,filelist):
        if filelist is None:
            print("Please add root files to your file list to create" + \
                    "a new TChain.  Returning None")
            return None
        chain = TChain(self.treename)
        if isinstance(filelist,list) is True:
            for rf in filelist:
                chain.Add(rf)
        else:
            chain.Add(filelist)
        return chain

    def makeCovarianceMatrix(self):
        matrix = []
        columns = copy.deepcopy(self.variables)
        #columns.reverse()
        for var in self.variables:
            matrix_row = self.getCovarianceRow(var, columns)
            matrix.append(matrix_row)
        return CovarianceMatrix(cov_matrix = matrix, variables = self.variables)

    def getCovarianceRow(self, rvar, colvars):
        #first, get the onevar's average value from the TChain
        covariance_row = []
        for cvar in colvars:
            covariance_element = self.getCovarianceElement(rvar, cvar)
            covariance_row.append(covariance_element)
        return covariance_row

    def getCovarianceElement(self, var1, var2):
        celement = 0.0
        #Don't want to output the draws
        gROOT.SetBatch(True)
        self.rchain.Draw(var1+">>var1mean")
        v1h = gDirectory.Get("var1mean")
        var1mean = v1h.GetMean()
        self.rchain.Draw(var2+">>var2mean")
        v2h = gDirectory.Get("var2mean")
        var2mean = v2h.GetMean()
        for i in xrange(self.rchain.GetEntries()):
            self.rchain.GetEntry(i)
            v1 = float(getattr(self.rchain,var1))
            v2 = float(getattr(self.rchain,var2))
            celement = celement + ((v1 - var1mean)*(v2-var2mean))
        Normalization = 1.0/(float(self.rchain.GetEntries())-1.0)
        return Normalization*celement

class CovarianceMatrix(object):
    def __init__(self, cov_matrix=None, variables=None):
        '''
        Class takes in a covariance matrix and the variables used to generate
        it (listed from row 0 to row N, and col 0 to col N).
        Tools included for Cholesky decomposition or SVD decomposition, then random
        shooting pass/fails with correlations included.
        '''

        self.cov_matrix = cov_matrix
        self.correlation_shooter_matrix = None #Cholesky decomposed or SVD
        self.variables = variables

    def choleskydecompose(self):
        dimension = len(np.diagonal(self.cov_matrix))
        ain = scipy.array(self.cov_matrix)
        #icorr = (0.4 * np.identity(dimension))
        #print(icorr)
        #ain = ain + icorr
        eigenvals = scipy.linalg.eigvalsh(ain)
        print("EIGENVALUES: " + str(eigenvals))
        for val in eigenvals:
            if val < 0:
                print("matrix must be positive definite to cholesky" +\
                        "decompose.  returning none")
                return none
        c = scipy.linalg.cholesky(ain, lower=True)
        #u = scipy.linalg.cholesky(ain, lower=false)
        self.correlation_shooter_matrix = c

    def svddecompose(self):
        dimension = len(np.diagonal(self.cov_matrix))
        ain = scipy.array(self.cov_matrix)
        U, V, S = numpy.linalg.svd(ain)
        self.correlation_shooter_matrix = U   #TODO: Do we only need U to random shoot probabilities?

    def shoot_corrvars(self):
        fired_variables = None
        if self.variables is None:
            print("Need to give the variable list to associate shots with\n" + \
                    "variables in the output dictionary.")
            return
        #First, shoot random numbers from a normal distribution
        fired_norms = pd.RandShoot(0,1,len(self.variables))
        #now, multiply your cholesky decomposition to add correlations
        corr_vector = self.correlation_shooter_matrix.dot(fired_norms)
        #Adjust your input variables by the correlated shot amount
        variable_dict = {}
        for j,entry in enumerate(self.variables):
            variable_dict[entry] = corr_vector[j]
        return variable_dict

