import ROOT
import numpy as np


def MakeTimeHist(rootfiles,timethresh):
    #Takes in an IBD root file, and returns a TH1F object that has the 
    #interevent_time distribution with the required parameter values per event.
    #We have to do this since interevent_times were only generated for events
    #with the parameters below.
    RESOLUTION = int(timethresh/20.0)
    timevals = ROOT.TH1F("times","times", RESOLUTION, 0, int(timethresh))
    datchain = ROOT.TChain("data")
    for rf in rootfiles:
        datchain.Add(rf)
    FileDepleted = False
    entrynum=0
    while (not FileDepleted) and (entrynum < 10000000):
        datchain.GetEntry(entrynum)
        if datchain.good_pos > 0.1 and datchain.good_dir > 0.1 and \
                datchain.n9 > 5 and datchain.pe > 5.5 and \
                datchain.nhit>3:
            timevals.Fill(datchain.dt)
        if entrynum >= datchain.GetEntries():
            FileDepleted = True
            print("FILE DEPLETED.")
            break
    return timevals

def wald(x, p):
    if x[0]== 0:
        print("Cannot use x == 0.  Setting it close...")
        x[0] += 0.00000001
    return  p[2] * np.sqrt(p[0] / (2.* np.pi *(x[0]**p[3]))) * np.exp(-(p[0]*((x[0]-p[1])**2))/(2.*(p[1]**2)*x[0]))
    #return p[0] * np.exp(-p[1] * x[0]) * (1.0 - sps.erf(((p[2]**2 / p[1])-x[0])/(np.sqrt(2)*p[2])))

def risefall(x, p):
    if x[0]== 0:
        print("Cannot use x == 0.  Setting it close...")
        x[0] += 0.00000001
    return  p[0] * (np.exp(-x[0]/p[1]) - np.exp(-x[0]/p[2]))
    #return p[0] * np.exp(-p[1] * x[0]) * (1.0 - sps.erf(((p[2]**2 / p[1])-x[0])/(np.sqrt(2)*p[2])))

def MakeTimeFit_Landau(timehist):
    #Function takes in a time histogram and fits a polynomial to it. Returns
    #The polynomial function for random firing of values from
    TimeFit = ROOT.TF1('TimeFit', landau, 1,
            float(TIMETHRESH), 3)
    TimeFit.SetParameter(0, 100000.0)
    #TimeFit.SetParLimits(0, 0, )
    TimeFit.SetParameter(1, 100000.0)
    #TimeFit.SetParLimits(1, 0, 1E7)
    TimeFit.SetParameter(2, 1000)
    #TimeFit.SetParameter(3,1.5)
    TimeFit.SetParNames('A','t1','t2')
    TimeFit.SetLineColor(2)
    TimeFit.SetLineWidth(4)
    TimeFit.SetLineStyle(2)
    ROOT.gStyle.SetOptFit(0157)
    timehist.Fit('TimeFit','Lq')
    return TimeFit

def MakeTimeFit_wald(timehist):
    #Function takes in a time histogram and fits a polynomial to it. Returns
    #The polynomial function for random firing of values from
    TimeFit = ROOT.TF1('TimeFit', wald, 1,
            float(TIMETHRESH), 4)
    TimeFit.SetParameter(0, 100000.0)
    TimeFit.SetParLimits(0, 0, 1E7)
    TimeFit.SetParameter(1, 100000.0)
    TimeFit.SetParLimits(1, 0, 1E7)
    TimeFit.SetParameter(2, 1000)
    TimeFit.SetParameter(3,1.5)
    TimeFit.SetParNames('lambda','mu','C')
    TimeFit.SetLineColor(2)
    TimeFit.SetLineWidth(4)
    TimeFit.SetLineStyle(2)
    ROOT.gStyle.SetOptFit(0157)
    timehist.Fit('TimeFit','Lq')
    return TimeFit

if __name__ == '__main__':
    print("NOTHING HERE TO RUN AS MAIN")
    #timehistogram = MakeTimeHist(IBDDIR+"/"+IBD_FILE_TITLE)
    #timefit = MakeTimeFit_wald(timehistogram)
    #IBD_file = ROOT.TFile(IBDDIR+"/"+IBD_FILE_TITLE,"read")
    #IBD_entrynum = 0

