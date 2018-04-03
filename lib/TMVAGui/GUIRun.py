import subprocess

def loadResultsInGui(GUIdir,resultfile):
    '''Load the resultfile with the TMVA Gui'''
    print(resultfile)
    subprocess.call(["root",".L",'%s/TMVAGui.C+(\"%s\")'%(GUIdir,resultfile)])

