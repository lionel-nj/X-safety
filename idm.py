from trafficintelligence import moving
from trafficintelligence import utils

import random
import numpy as np
import matplotlib.pyplot as plt
import math
import collections
from toolkit import *
import itertools
import shapely.geometry
from math import sqrt

number_of_cars=7

"définition des instants de création des véhicules"

tiv=generateSampleFromSample(number_of_cars)
h=list(itertools.accumulate(tiv))

delta_t=1
t_simul=300
intervals=[None]*t_simul

for k in range(0,number_of_cars):
    intervals[k]=[h[k]]

    for t in range(1,t_simul):
        intervals[k].append(intervals[k][t-1]+1)

##########################################################
#définition des fonctions utiles au modèle IDM"
##########################################################

"fonction de mise a jour des gaps"

def gap(x_leader,x_following,L_leader):
    return x_leader-x_following-L_leader

"fonction de maj des positions"

def position(y,t,v,DV,a):
    return moving.Point(2000,0.5*a*(t**2)+v*t+y)  #1/2*a*t^2+x0

"fonction de maj des vitesses"

def vitesse(v,a):
    return a*delta_t+v

"fonction pour la distance desirée : s_etoile"

def s_etoile(a,v,DV,T):
    b=1.5
    s0=2
    return s0+max(0,v*1+(v*DV)/(2*sqrt(a*b)))

"fonction de maj de l'acceleration"

def acceleration(a,v,v0,DV,s,T):
    delta=4
    # return a*(1-(v/v0)**delta-(s_etoile(a,v,DV,T)/s)**2)
    return a*(1-math.pow((v/v0),delta)-math.pow((s_etoile(a,v,DV,T)/s),2))

##########################################################
# Initialisation du premier véhicule : gap=1000m
##########################################################
voie_verticale=dict()
voie_verticale[0]=moving.MovingObject()

l=random.normalvariate(6.5,0.3)
posV=[moving.Point(2000,0)]
speed=[15]
L=[]
L.append(l)
# a=random.normalvariate(1.7,0.3)
a=1
v0=random.normalvariate(30,3.2)

for t in range(1,t_simul):
    acc=0
    speed.append(vitesse(speed[t-1],acc))
    posV.append(position(posV[t-1].y,k,15,50,acc))

voie_verticale[0].timeInterval=[0,300]
voie_verticale[0].positions=posV
voie_verticale[0].velocities=speed
voie_verticale[0].geometry=shapely.geometry.Polygon([(0,0),(0,1.8),(l,1.8),(l,0)])
voie_verticale[0].userType=1

##########################################################
# Initialisation des autres véhicules
##########################################################
v0=15#m/s
a=1
for k in range(1,number_of_cars):

    # a=random.normalvariate(1.7,0.3) #m.s-2 acceleration maximale
    # s=0 #m

    voie_verticale[k]=moving.MovingObject()
    voie_verticale[k].timeInterval=moving.TimeInterval(intervals[k][0],300+intervals[k][0])
    voie_verticale[k].positions=[moving.Point(2000,0)]
    voie_verticale[k].velocities=[0]
    l=random.uniform(6,8)
    L.append(l)
    voie_verticale[k].geometry=shapely.geometry.Polygon([(0,0),(0,1.8),(l,1.8),(l,0)])
    voie_verticale[k].userType=1

    for t in range(1,t_simul):
        a=1
        p=moving.MovingObject.getPositions(voie_verticale[k])[t-1].y
        v=moving.MovingObject.getVelocities(voie_verticale[k])[t-1]
        DV=moving.MovingObject.getVelocities(voie_verticale[k-1])[t-1]-moving.MovingObject.getVelocities(voie_verticale[k])[t-1]
        s=gap(moving.MovingObject.getPositions(voie_verticale[k-1])[t-1].y,moving.MovingObject.getPositions(voie_verticale[k])[t-1].y,L[k-1])
        T=h[k]
        acc=acceleration(a,v,v0,DV,s,h[k]-h[k-1])

        voie_verticale[k].velocities.append(vitesse(v,acc))
        voie_verticale[k].positions.append(position(p,v,1,DV,acc))


create_yaml('traffic_voie_verticale.yml',voie_verticale)

t=[]
p=[]
v=[]
plt.figure()

for k in range (0,len(voie_verticale)):
    p.append([])
    t.append(intervals[k])
    v.append(voie_verticale[k].velocities)
    for time in range(0,t_simul):
        p[k].append(voie_verticale[k].positions[time].y)


    plt.plot(t[k],v[k])
# plt.figure()
# plt.plot(t,p)

plt.show()
