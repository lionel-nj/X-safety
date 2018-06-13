import random
import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as  pd
import csv
from scipy.interpolate import interp1d
import scipy.integrate as integrate
import scipy.special as special
from scipy import stats

data=pd.read_csv('trajectories.csv',sep=';',header=0) #source sample

def generatesamplefromsample(numofcars):
    #get the info you need, here we need headway from the csv file, that's how we extract them
    lane=1
    voitlane=(data["lane"]==lane) & (data["origin"]!=108) & (data["origin"]!=109) & (data["origin"]!=110) & (data["origin"]!=111) & (data["dest"]==208)
    a=data[voitlane].vehid
    indices=a.drop_duplicates("last",False)
    tivbyvehid=[]
    for k in indices :
        a=data[data.vehid==k]
        tivbyvehid = tivbyvehid +[a[a.localy>=800].headway.iloc[0]]

#tivbyvehid : headways
    n, bins, patches = plt.hist(tivbyvehid, 12, normed=True) #histogram of observed sample
    y=[] #getting the height of bars
    for k in n:
        y=y+[k]
    y=y+[n[len(n)-1]]
    x=[] # getting the x position of the bars
    for k in range(0,len(bins)-1):
        x=x+[bins[k]]

    width=x[1]-x[0]
    x=x+[bins[len(bins)-1]+width]

#interpolating in order to get the density function of the sample
    f = interp1d(x, y, kind='cubic')
    xnew=np.linspace(min(x),max(x),100)
    plt.plot(xnew, f(xnew))

    F=[]
    for k in xnew:
        F = F+[integrate.quad(interp1d(x, y, kind='cubic'), min(xnew), k)]

    #F is a list of interpolated points

    #calculating the cdf : cumulative distribution function of the sample
    inte=[]
    for k in range(0,len(F)):
        inte=inte+[F[k][0]]

    #generation of a sample of values, based on the observed data

    def generate():
        indexx=0
        b=random.uniform(0,0.735)
        for k in range(0,len(inte)):
            if((abs(inte[k]-b))<=0.01):
                indexx=k
        return xnew[indexx]

    newsample=[]
<<<<<<< HEAD
    for k in range(0,numofcars):
        a=generate()
        if a<1.5:
            a=1.5
        newsample=newsample+[a]
=======
    for k in range(0,42):
        newsample=newsample+[generate()]
>>>>>>> 4a33fab79768a77f5ae21b01a5c3d4e840a21a29

    return newsample
