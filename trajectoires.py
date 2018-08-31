import pandas as pd
import random
import matplotlib.pyplot  as plt
import numpy as np
from scipy.interpolate import interp1d

left_border=([0,0],[0,3900])
right_border=([3.6,3.6],[0,3900])
e=0.1

plt.plot(left_border[0],left_border[1])
plt.plot(right_border[0],right_border[1])


def xo():
    return random.normalvariate(1.8,0.2)

def in_bound(abscisse):
    if (0<abscisse and abscisse<3.6):
        return True
    else:
        return False

def deviation_x(x):
    erreur=random.uniform(-e,e)
    x1=x+erreur
    x2=x-erreur
    if not in_bound(x1):
        return x2
    else:
        return x1


def calcul_y(speed,t,fin):
    if speed*t>fin:
        return fin
    else:
        return speed*t


for i in range(0,20):
    x0=xo()
    x=[x0]
    y=[0]
    speed=13 #m/s
    for k in range(300):
        x=x+[deviation_x(x[0])]
        y=y+[calcul_y(speed,k,3900)]
    plt.plot(x,y)


####Fonction de lissage
def lissage(Lx,Ly,p):
    '''Fonction qui débruite une courbe par une moyenne glissante
    sur 2P+1 points'''
    Lxout=[]
    Lyout=[]
    Lxout = Lx[p: -p]
    for index in range(p, len(Ly)-p):
        average = np.mean(Ly[index-p : index+p+1])
        Lyout.append(average)
    return Lxout,Lyout



plt.show()
plt.close()
