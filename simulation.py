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


numofcars=5
tiv=generateSampleFromSample(numofcars)
h=list(itertools.accumulate(tiv))
delta_t=1
t_simul=30

voie_verticale=dict()

intervals=[None]*numofcars
for k in range(0,numofcars):
    intervals[k]=[h[k]]
    a=intervals[k]

    for t in range(1,t_simul):
        intervals[k].append(a[t-1]+1)

def s_etoile(v,delta_v,T):
    ''' a : acceleration
        b : deceleration confortable
        T : time headway
        s0 : gap minimum'''
    return s0+max(0,v*T+v*delta_v/(2*sqrt(a*b)))

def acc(v,delta_v,T,v0,a):
    '''a : acceleration maximale
       v0: vitesse desiree
       v : vitesse
       delta : exposant pour controler la reduction d'acceleration
       '''
    return a*(1-(v/v0)**delta-(s_etoile(v,delta_v,T)/s))

def positionV(v,y,a):
    # k1=v_1
    # k3=v_1+0.25*(v-v_1)
    # k4=v_1+0.5*(v-v_1)
    # k5=v_1+0.75*(v-v_1)
    # k6=v
    return moving.Point(2000,y+v*delta_t+0.5*a*(delta_t**2))

def gap(x_l,L,x_t):
    return x_l-x-L

    # return moving.Point(2000,y+1/90*(7*k1+32*k3+12*k4+32*k5+7*k6))

def vitesse(v,a):
    return v+a*delta_t

# def vitesse(a_n,v_n,x_n,V_n,v_n1,x_n1,s_n1):
#     b_n=-2*a_n
#     b_barre=min(-3,(b_n-3)/2)
#     tau=2/3
#
#     a=v_n+2.5*a_n*tau*(1-v_n/V_n)*math.sqrt(0.025+v_n/V_n)
#     # print(a)
#     # c=((b_n*tau)**2)-b_n*(2*(x_n1-s_n1-x_n)-v_n*tau-(v_n1**2)/b_barre)
#     # print(c)
#     # return 1
#     b=b_n*tau+math.sqrt(((b_n*tau)**2)-b_n*(2*(x_n1-s_n1-x_n)-v_n*tau-(v_n1**2)/b_barre))
#     return min(a,b)


# def acceleration(x0,x1,v0,v1,v):
#     return 0.78*v*(v0-v1)/(x0-x1)

"initialiser le premier vehicule : MovingObject"

l=random.normalvariate(6.5,0.3)
posV=[moving.Point(2000,15)]
v=17
speed=[v]
S=[]
S.append(l)
for k in range(1,t_simul):
    # posV.append(positionV(v,posV[k-1].y,speed[k-1]))
    posV.append(positionV(v,posV[k-1].y,0))
    speed.append(v)

voie_verticale[0]=moving.MovingObject(None,moving.TimeInterval(0,300),posV,speed,shapely.geometry.Polygon([(0,0),(0,1.8),(l,1.8),(l,0)]),2,None)

"autres véhicules"

y=[None]*numofcars
y[0]=[]

x=[None]*numofcars
x[0]=[]

for t in range(0,len(voie_verticale[0].positions)):
    y[0].append(voie_verticale[0].positions[t].y)


for k in range(1,numofcars):

    a_n=random.normalvariate(1.7,0.3) #m.s-2
    b_n=-2*a_n #m.s-2
    s_n=random.normalvariate(6.5,0.3) #m
    V_n=random.normalvariate(20,3.2) #m/s

    y[k]=[15]
    x[k]=[2000]

    S.append(s_n)

    voie_verticale[k]=moving.MovingObject()
    voie_verticale[k].timeInterval=moving.TimeInterval(intervals[k][0],300+intervals[k][0])
    voie_verticale[k].positions=[moving.Point(2000,15)]
    voie_verticale[k].velocities=[random.normalvariate(14,2)]
    l=random.uniform(6,8)
    voie_verticale[k].geometry=shapely.geometry.Polygon([(0,0),(0,1.8),(l,1.8),(l,0)])
    voie_verticale[k].userType=1 # 1 pour les voitures 2 pour les piétons
    for t in range(1,t_simul):
        acceleration=acc(v,delta_v,T,v0,a)
        voie_verticale[k].velocities.append(vitesse("vitesse,acceleration"))
        # voie_verticale[k].positions.append(positionV(moving.MovingObject.getVelocities(voie_verticale[k])[t-1],moving.MovingObject.getPositions(voie_verticale[k])[t-1].y,voie_verticale[k].velocities[t-1]))
        voie_verticale[k].positions.append(positionV("vitesse,position,acceleration"))

        # acc.append(acceleration(voie_verticale[k-1].positions[t].y,voie_verticale[k].positions[t].y,voie_verticale[k-1].velocities[t],voie_verticale[k].velocities[t],voie_verticale[k].velocities[t]))
        # posV.append(position(speed[t-1],pos[t-1]))
        # acc.append(acceleration(voie_verticale[k].positions[t-1],voie_verticale[k].positions[t],voie_verticale[k].velocities[t-1],voie_verticale[k].velocities[t]))
        y[k].append(voie_verticale[k].positions[t].y)
        x[k].append(2000)

    plt.plot(intervals[k],y[k])
    plt.plot(x[k],y[k])

create_yaml('traffic_voie_verticale.yml',voie_verticale)

#
plt.show()
plt.draw()
plt.close()
