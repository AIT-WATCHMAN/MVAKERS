#This library contains functions relevant to producing the correlation matrix
#Based on the phi coefficient.  The phi coefficient gives you a measure
#of how correlated two binary values are.
import maskbuilder as mb
import resultgetter as rg
import leakestimator as le
import playDarts as pd

from collections import OrderedDict
import numpy as np
import scipy
import scipy.linalg
import numpy.linalg

#FIXME: Initial probabilities shouldn't be shot with covariance matrix; should
#Be the lower level variables themselves that will make the cov. matrix elements
class CovarianceMatrix(object):
    def __init__(self, cov_matrix=None):
        '''
        Class takes in a covariance matrix and probabilities of getting
        a "FAIL" for each cut in the bifurcation analysis.  Tools included
        for Cholesky decomposition or SVD decomposition, then random
        shooting pass/fails with correlations included.
        '''

        self.cov_matrix = cov_matrix
        self.variables = None
        self.correlation_shooter_matrix = None

    #TODO: So we need a couple things...
    #1: Feed the CovarianceMatrix class a list of ntuple title strings
    #2: Based on the string list, make the covariance matrix
    #   (The string map should also be how variables are fed into the
    #   self.variables function

    def fill_variables(self,variablearray):
        self.variables=np.array(variablearray)

    def choleskydecompose(self):
        dimension = len(np.diagonal(self.cov_matrix))
        ain = scipy.array(self.cov_matrix)
        #icorr = (0.4 * np.identity(dimension))
        #print(icorr)
        #ain = ain + icorr
        eigenvals = scipy.linalg.eigvalsh(ain)
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
            print("Need to give variables to randomly fire with cov. matrix")
            return
        variables_thisshot = []
        #First, shoot random numbers from a normal distribution
        fired_norms = pd.RandShoot(0,1,len(self.variables))
        #now, multiply your cholesky decomposition to add correlations
        corr_vector = self.correlation_shooter_matrix.dot(fired_norms)
        #Shoot the probabilities by multiplying by variance, adding mu
        corr_vector = corr_vector + self.variables
        #Finally, shoot random numbers and build the "pass_fail" vector
        fired_variables.append(variables_thisshot)
        return fired_variables

