#Here are our fitter tools
import ROOT
import numpy as np

class FitEngine(object):
    __dlib = {"Exp":[3.0,1.0,3.0], "Gauss":[1.0,1.0,1.0], "Wald":[10,0, 10.0, 10.0,1.0],  "Landau": [1000.0, 100.0, 100.0]}

    def __init__(self, TH1=None, distribution=None,fit_range=[0.0,100.0]):
        self.histogram = TH1
        self.distribution = distribution
        if distribution is not None:
            self.initial_parameters = self.__dlib[distribution]
        else:
            self.initial_parameters = None
        self.current_fit = None
        self.fit_range = fit_range

    def DrawHistogram(self):
        if self.histogram is None:
            print("No histogram available to draw right now.")
        else:
            self.histogram.Draw()

    def DrawFit(self):
        if self.current_fit is None:
            print("No fit available to draw.  Run MakeFit() first.")
        else:
            self.histogram.Draw()
            self.current_fit.Draw("same")

    def setHistogramToFit(self,TH1):
        self.histogram = TH1

    def setFitRange(self,fitrange):
        if len(fitrange) is not 2:
            print("Please give an array with two elements [min,max]")
        if fitrange[0] >= fitrange[1]:
            print("Please choose a min less than the max value")
        self.fit_range = fitrange

    def setDistribution(self, distribution):
        if distribution not in self.__dlib:
            print("Function to fit not supported.  Please select from: ")
            print(self.__dlib)
            return
        else:
            self.distribution = distribution
            self.initial_parameters = self.__dlib[distribution] #Default

    def setParameters(self, parameters):
        if self.initial_parameters is None:
            print("There are no parameters right now.  Did you set your")
            print("Distribution type?")
        if len(parameters) is not len(self.initial_parameters):
            print("Selected distribution does not have this many parameters.")
            print("Please feed in an array of "+len(self.initial_parameters)+\
                    " parameters.")

    def gauss(self, x, p):
        return (p[0]/np.sqrt(2.*np.pi*(p[2]**2)))*np.exp(-((x[0]-p[1])**2)/(2.*p[2]**2))

    def exp(self, x, p):
        return p[0] * np.exp(-p[1]*(x[0] - p[2]))

    def wald(self, x, p):
        if x[0]== 0:
            print("Cannot use x == 0.  Setting it close...")
            x[0] += 0.00000001
        return  p[2] * np.sqrt(p[0] / (2.* np.pi *(x[0]**p[3]))) * np.exp(-(p[0]*((x[0]-p[1])**2))/(2.*(p[1]**2)*x[0]))
        #return p[0] * np.exp(-p[1] * x[0]) * (1.0 - sps.erf(((p[2]**2 / p[1])-x[0])/(np.sqrt(2)*p[2])))
    
    def landau(self, x, p):
        if x[0]== 0:
            print("Cannot use x == 0.  Setting it close...")
            x[0] += 0.00000001
        return  p[0] * (np.exp(-x[0]/p[1]) - np.exp(-x[0]/p[2]))
        #return p[0] * np.exp(-p[1] * x[0]) * (1.0 - sps.erf(((p[2]**2 / p[1])-x[0])/(np.sqrt(2)*p[2])))
    
    def MakeFit(self):
        #Function takes in a time histogram and fits a polynomial to it. Returns
        #The polynomial function for random firing of values from
        if self.distribution is None:
            print("Choose a distribution to fit your histogram to.")
            return
        if self.initial_parameters is None:
            print("No initial parameters for this distribution.")
        if self.distribution is "Gauss": 
            TimeFit = ROOT.TF1('TimeFit', self.gauss, self.fit_range[0],
                    self.fit_range[1], 3)
            for j,p in enumerate(self.initial_parameters):
                TimeFit.SetParameter(j+1,p)
                TimeFit.SetParNames('A','mu','sigma')
        if self.distribution is "Exp": 
            TimeFit = ROOT.TF1('TimeFit', self.exp, self.fit_range[0],
                    self.fit_range[1], 3)
            for j,p in enumerate(self.initial_parameters):
                TimeFit.SetParameter(j+1,p)
                TimeFit.SetParNames('A','lamb','x0')
        if self.distribution is "Landau": 
            TimeFit = ROOT.TF1('TimeFit', self.landau, self.fit_range[0],
                    self.fit_range[1], 3)
            for j,p in enumerate(self.initial_parameters):
                TimeFit.SetParameter(j+1,p)
                TimeFit.SetParNames('A','t1','t2')
        if self.distribution is "Wald": 
            TimeFit = ROOT.TF1('TimeFit', self.wald, self.fit_range[0],
                    self.fit_range[1], 4)
            for j,p in enumerate(self.initial_parameters):
                TimeFit.SetParameter(j+1,p)
                TimeFit.SetParNames('lambda','mu','C','xp')
        TimeFit.SetLineColor(2)
        TimeFit.SetLineWidth(4)
        TimeFit.SetLineStyle(2)
        print(TimeFit)
        ROOT.gStyle.SetOptFit(0157)
        self.histogram.Fit('TimeFit','Lq')
        self.current_fit = TimeFit
        return TimeFit
   
class ChainShooter(object):
    def __init__(self,datafiles=None,variable_list=None):
        print("NEED TO MAKE")

    def MakeTH1(tree,branch):
        #Return a TH1 histogram made of all data for a branch in the given
        #data files
        for f in datafiles:
            thefile = ROOT.TFile(f,"READ")
            t=thefile.Get(tree)
            for entry in xrange(t.GetEntries()):
                t.GetEntry(entry)
                #Fill hisgotram with GetProperty(t,branch)
