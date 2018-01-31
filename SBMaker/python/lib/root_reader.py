#Make a function that grabs a particular entry from a root file given to it.
def GetRates_Valids(rootfile_list):
    for f in rootfile_list:
        #First, point to the runSummary tree
        #Then, get the first entry
        #Finally, Get the values and calculate the following
        #rateHz * (float(potential_prompts)/ float(nEvents))
        #Note that for our cuts, if an event is a candidate delayed event,
        #it automatically is also a prompt.  So the # prompts is actually also
        #The number of events with SOME valid fit where it wouldn't have been
        #Thrown out of the data.
