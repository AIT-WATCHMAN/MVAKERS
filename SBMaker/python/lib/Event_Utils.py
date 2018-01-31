def shootTimeDiff(raw_freq):
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

#FIXME: need a version that takes in x, y, and z, and does this
def innerDist(prev_r, prev_z, r, z, posReco, posReco_prev):
    #First checks that the current and previous event reconstruct in the
    #FV.  If they do, returns the inner_dist_fv
    if (0< abs(prev_r) < FV_radius) and (0 < abs(r) < FV_radius):
        if (0 < abs(prev_z) < (FV_height/2.)) and (0 < abs(z) < (FV_height / 2.)):
            return np.sqrt((posReco_prev.x() - posReco.x())**2 + 
                    (posReco_prev.y() - posReco.y())**2 + 
                    (posReco_prev.z() - posReco.z())**2)
        else:
            return -1
    else:
        return -1

