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

number_of_cars=6

"définition des instants de création des véhicules"

tiv=generateSampleFromSample(number_of_cars)
h=list(itertools.accumulate(tiv))

delta_t=1
t_simul=30
intervals=[None]*number_of_cars

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

def position(y,v,DV,a):
    return moving.Point(2000,y+v*delta_t+0.5*a*(delta_t**2))

"fonction de maj des vitesses"

def vitesse(v,a):
    return v+a*delta_t

"fonction pour la distance desirée : s_etoile"

def s_etoile(a,v,DV):
    b=2.5
    s0=2
    return s0+max(0,v*1.2+(v*DV)/(2*sqrt(a*b)))

"fonction de mise a jour de l'acceleration"

def acceleration(a,v,v0,DV,s):
    delta=4
    return a*(1-math.pow(v/v0,delta)-math.pow(s_etoile(a,v,DV)/s,2))

##########################################################
# Initialisation du premier véhicule : gap=1000m
##########################################################
voie_verticale=dict()
voie_verticale[0]=moving.MovingObject()

l=random.normalvariate(6.5,0.3)
posV=[moving.Point(2000,0)]
v=17
speed=[v]
L=[]
L.append(l)
t_simul=30
a=random.normalvariate(1.7,0.3)
v0=random.normalvariate(20,3.2)

for k in range(1,t_simul):
    acc=a/30
    speed.append(vitesse(speed[k-1],acc))
    posV.append(position(posV[k-1].y,v,50,acc))

voie_verticale[0].timeInterval=[0,300]
voie_verticale[0].positions=posV
voie_verticale[0].velocities=speed
voie_verticale[0].geometry=shapely.geometry.Polygon([(0,0),(0,1.8),(l,1.8),(l,0)])
voie_verticale[0].userType=1

##########################################################
# Initialisation des autres véhicules
##########################################################

y=[None]*number_of_cars
y[0]=[]

x=[None]*number_of_cars
x[0]=[]


for t in range(0,len(voie_verticale[0].positions)):
    y[0].append(voie_verticale[0].positions[t].y)

for k in range(1,number_of_cars):

    a=random.normalvariate(1.7,0.3) #m.s-2 acceleration maximale
    s=random.normalvariate(6.5,0.3) #m
    v0=random.normalvariate(20,3.2) #m/s

    voie_verticale[k]=moving.MovingObject()
    voie_verticale[k].timeInterval=moving.TimeInterval(intervals[k][0],300+intervals[k][0])
    voie_verticale[k].positions=[moving.Point(2000,0)]
    voie_verticale[k].velocities=[random.normalvariate(14,2)]
    l=random.uniform(6,8)
    L.append(l)
    voie_verticale[k].geometry=shapely.geometry.Polygon([(0,0),(0,1.8),(l,1.8),(l,0)])
    voie_verticale[k].userType=1

    for t in range(1,t_simul):
        a=random.normalvariate(1.7,0.3)
        v=moving.MovingObject.getVelocities(voie_verticale[k])[t-1]
        DV=moving.MovingObject.getVelocities(voie_verticale[k-1])[t-1]-moving.MovingObject.getVelocities(voie_verticale[k])[t-1]
        s=gap(moving.MovingObject.getPositions(voie_verticale[k-1])[t].y,moving.MovingObject.getPositions(voie_verticale[k])[t-1].y,L[k-1])

        acc=acceleration(a,v,v0,DV,s)
        voie_verticale[k].velocities.append(vitesse(moving.MovingObject.getVelocities(voie_verticale[k])[t-1],acc))
        voie_verticale[k].positions.append(position(moving.MovingObject.getPositions(voie_verticale[k])[t-1].y,moving.MovingObject.getVelocities(voie_verticale[k])[t-1],DV,acc))


create_yaml('traffic_voie_verticale.yml',voie_verticale)
# 
# t=[]
# v=[]
# for k in range(0,6):
#     t.append(intervals[k])
#     v.append(voie_verticale[k].velocities)
#     plt.plot(t,v)
# plt.show()
# plt.close()
