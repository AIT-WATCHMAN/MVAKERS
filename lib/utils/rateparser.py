
def ParseRateFile(rate_file):
    '''Takes the file output from running findRate() in the
    watchmakers code (see watchmakers.sensitivity).  Returns a
    dictionary with the values associated with proper keys'''
    ratelines = rate_file.readlines()
    if len(ratelines) > 1:
        print("WARNING: Rate file is longer than typical output of WATCHMAKERS.")
    dataline = ratelines[0]
    data = dataline.split(" ")
    ratedict = {"IBD_rate":data[0], "WV": {"Rn222": data[1]}, "PMT": {"U238":data[2],\
            "Th232": data[3], "K40":data[4]}}
    return ratedict
	
