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
    return moving.Point(v*t+y,2000)

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

voie_horizontale=dict()
voie_horizontale[0]=moving.MovingObject()

l=random.normalvariate(6.5,0.3)
# l=7
posH=[moving.Point(0,2000)]
L=[]
L.append(l)

v0=random.normalvariate(30,3.2)
speed=[0]

for t in range(1,t_marche1):
    speed.append(v0)
    # posH.append(position(posH[t-1].x,v0,1))

for t in range(0,t_stop):
    speed.append(0)
    # posH.append(position(posH[t-1].x,v0,1))

for t in range(0,t_marche2):
    speed.append(v0)
    # posH.append(position(posH[t-1].x,v0,1))

for t in range(1,t_simul):
    posH.append(position(posH[t-1].x,speed[t],1))

voie_horizontale[0].timeInterval=[0,300]
voie_horizontale[0].positions=posH
voie_horizontale[0].velocities=speed
voie_horizontale[0].geometry=shapely.geometry.Polygon([(0,0),(0,1.8),(l,1.8),(l,0)])
voie_horizontale[0].userType=1


##########################################################
        # Initialisation des autres véhicules
##########################################################


for k in range(1,number_of_cars):
    v0=random.normalvariate(30,3.2)
    l=random.uniform(6,8)
    L.append(l)

    voie_horizontale[k]=moving.MovingObject()
    voie_horizontale[k].timeInterval=moving.TimeInterval(intervals[k][0],300+intervals[k][0])
    voie_horizontale[k].positions=[moving.Point(0,2000)]
    voie_horizontale[k].velocities=[0]
    voie_horizontale[k].geometry=shapely.geometry.Polygon([(0,0),(0,1.8),(l,1.8),(l,0)])
    voie_horizontale[k].userType=1

    for t in range(1,t_simul):
        p=moving.MovingObject.getPositions(voie_horizontale[k])[t-1].x
        v=moving.MovingObject.getVelocities(voie_horizontale[k-1])[t]
        velocite=v0
        new_position=position(p,velocite,t)

        s=gap(moving.MovingObject.getPositions(voie_horizontale[k-1])[t].x,new_position.x,L[k-1])
        smin=7

        if s<smin:
            velocite=(v*t-L[k-1]-smin)/(t)

        if velocite<0:
            velocite=0


        voie_horizontale[k].velocities.append(velocite)
        voie_horizontale[k].positions.append(position(p,velocite,1))

create_yaml('voie_horizontale.yml',voie_horizontale)


t=[]
p=[]
v=[]
plt.figure()

for k in range (0,5):
    p.append([])
    t.append(intervals[k])
    v.append(voie_horizontale[k].velocities)
    for time in range(0,t_simul):
        p[k].append(voie_horizontale[k].positions[time].x)

    plt.plot(t[k],v[k])
    # plt.plot(t[k],p[k])
# plt.plot(t,p)
#
plt.show()
