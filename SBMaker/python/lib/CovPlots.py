#File contains plotting functions for use in main.  
import numpy as np
import matplotlib.pyplot as plt
import pylab as pl

def pCovarianceMatrix(rows, xtitles, ytitles):
    '''
    Takes in an array that contains arrays, each representing the
    Covariance matrix elements calculated from the results from a
    bifurcation analysis.  The titles label/identify each box.
    '''
    allrows=None
    for row in rows:
        if allrows==None:
            allrows=np.array([row])
            continue
        nextrow = np.array([row])
        allrows = np.concatenate((allrows,nextrow))
    #Plot the heatmap showing the covariance matrix elements
    im = plt.imshow(allrows,interpolation='none', aspect ='auto')
    plt.colorbar()
    plt.tick_params(axis='both', which='both', bottom='off', top='off', \
            labelbottom='off', labelleft='off')
    for i,row in enumerate(allrows):
        for j,column in enumerate(row):
            plt.text(j-0.35,i, str(np.around(column,4)), size = '18', \
                backgroundcolor='white')
    for k,ytitle in enumerate(ytitles):
        plt.text(-1.5,k, str(ytitle), size = '16')
    for k,xtitle in enumerate(xtitles):
        plt.text(float(k)-0.1,float(len(allrows))-0.32, str(xtitle), size = '16',rotation=-25)
   #FIXME: Need titles to be set at the right ticks
    plt.title("Covariance Matrix of Variables", size="20")
    plt.show()


