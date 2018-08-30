from trafficintelligence import moving
from trafficintelligence import utils
import decimal
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

"fonction de mise a jour des gaps"

def gap(x_leader,x_following,L_leader):
    return x_leader-x_following-L_leader

"fonction de maj des positions"

def position(y,v,t):
    return moving.Point(2000,v*t+y)

"définition des instants de création des véhicules"

tiv=generateSampleFromSample(number_of_cars)
h=list(itertools.accumulate(tiv))

delta_t=1
t_stop=30
t_marche1=30
t_marche2=30
t_simul=t_marche1+t_marche2+t_stop

intervals=[None]*t_simul

for k in range(0,number_of_cars):
    intervals[k]=[h[k]]

    for t in range(1,t_simul):
        intervals[k].append(intervals[k][t-1]+1)

##########################################################
        # Initialisation du premier véhicule
##########################################################

voie_verticale=dict()
voie_verticale[0]=moving.MovingObject()

l=random.normalvariate(6.5,0.3)
# l=7
posV=[moving.Point(2000,0)]
L=[]
L.append(l)

v0=random.normalvariate(30,3.2)
speed=[0]

for t in range(1,t_marche1):
    speed.append(v0)
    # posV.append(position(posV[t-1].y,v0,1))

for t in range(0,t_stop):
    speed.append(0)
    # posV.append(position(posV[t-1].y,v0,1))

for t in range(0,t_marche2):
    speed.append(v0)
    # posV.append(position(posV[t-1].y,v0,1))

for t in range(1,t_simul):
    posV.append(position(posV[t-1].y,speed[t],1))

voie_verticale[0].timeInterval=[0,300]
voie_verticale[0].positions=posV
voie_verticale[0].velocities=speed
voie_verticale[0].geometry=shapely.geometry.Polygon([(0,0),(0,1.8),(l,1.8),(l,0)])
voie_verticale[0].userType=1


##########################################################
        # Initialisation des autres véhicules
##########################################################


for k in range(1,number_of_cars):
    v0=random.normalvariate(30,3.2)
    l=random.uniform(6,8)
    L.append(l)

    voie_verticale[k]=moving.MovingObject()
    voie_verticale[k].timeInterval=moving.TimeInterval(intervals[k][0],300+intervals[k][0])
    voie_verticale[k].positions=[moving.Point(2000,0)]
    voie_verticale[k].velocities=[0]
    voie_verticale[k].geometry=shapely.geometry.Polygon([(0,0),(0,1.8),(l,1.8),(l,0)])
    voie_verticale[k].userType=1

    for t in range(1,t_simul):
        p=moving.MovingObject.getPositions(voie_verticale[k])[t-1].y
        v=moving.MovingObject.getVelocities(voie_verticale[k-1])[t]
        # DV=moving.MovingObject.getVelocities(voie_verticale[k])[t-1]-moving.MovingObject.getVelocities(voie_verticale[k-1])[t-1]
        velocite=v0
        new_position=position(p,velocite,t)
        # voie_verticale[k].positions.append(new_position)

        s=gap(moving.MovingObject.getPositions(voie_verticale[k-1])[t].y,new_position.y,L[k-1])
        smin=7

        # if velocite>v0:
        #     velocite=v0

        if s<smin:
            velocite=(v*t-L[k-1]-smin)/(t)

        if velocite<0:
            velocite=0


        voie_verticale[k].velocities.append(velocite)
        voie_verticale[k].positions.append(position(p,velocite,1))



#         # if new_position.y<moving.MovingObject.getPositions(voie_verticale[k])[t-1].y:
#         #     new_position=moving.MovingObject.getPositions(voie_verticale[k])[t-1]
#         #
#         # if velocite==0:
#         #     voie_verticale[k].positions.append(moving.MovingObject.getPositions(voie_verticale[k])[t-1])
#         # else:


t=[]
p=[]
v=[]
plt.figure()

for k in range (0,5):
    p.append([])
    t.append(intervals[k])
    v.append(voie_verticale[k].velocities)
    for time in range(0,t_simul):
        p[k].append(voie_verticale[k].positions[time].y)

    plt.plot(t[k],v[k])
    # plt.plot(t[k],p[k])
# plt.plot(t,p)
#
plt.show()
