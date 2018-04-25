import numpy as np
import ROOT as ROOT
from ROOT import TChain, TFile, gROOT
from sys import stdout

def shootTimeDiff(rate):
    if rate< 0:
        return -9999  
    else:
        #Given an average rate in Hz, shoot from an exponential distribution for the
        #Time to next event.  Return time in nanoseconds.
        return np.random.exponential(1./float(rate))*1.0E9

def shootTimeDiff_Slow(raw_freq):
    #Assume your process is poisson with an occurence of raw_freq/msec
    #on average.  We get the time diff by shooting that many events in
    #a one second timespan, sort, then get the average time difference.
    #Returns event time difference in nanoseconds
    fired_event = False
    timediff = 0.
    while not fired_event:
        if raw_freq < 20:
            num_events = pd.RandShoot_p(raw_freq,1)
        else:
            num_events = pd.RandShoot_g0(raw_freq, np.sqrt(raw_freq),1)
        event_times = np.random.rand(num_events)
        event_times.sort()
        if len(event_times) > 2:
            the_event_index = np.random.randint(1,len(event_times)-1)
            timediff += (event_times[the_event_index] - event_times[the_event_index -1])
            fired_event = True
        elif len(event_times) >0:
            timediff += 1. - event_times[0]
            fire_event = True
        else:
            timediff+=1
    return timediff * 1.0E6 * scaler

def radius(x,y):
    return np.sqrt(x**2 + y**2)

def innerDist(prev_x, prev_y, prev_z, x, y, z):
    return np.sqrt((prev_x - x)**2 + (prev_y - y)**2 + (prev_z - z)**2)


