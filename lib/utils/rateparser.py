
def ParseRateFile(rate_file):
    '''Takes the file output from running findRate() in the
    watchmakers code (see watchmakers.sensitivity).  Returns a
    dictionary with the values associated with proper keys'''
    ratelines = rate_file.readlines()
    if len(ratelines) > 1:
        print("WARNING: Rate file is longer than typical output of WATCHMAKERS.")
    dataline = ratelines[0]
    data = dataline.split(" ")
    ratedict = {"IBD_rate":float(data[0]), "WaterVolume": {"222Rn": float(data[1])}, "PMT": {"238U":float(data[2]),\
            "232Th": float(data[3]), "40K":float(data[4])}}
    return ratedict
	
