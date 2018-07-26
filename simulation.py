from trafficintelligence import moving
import random
import numpy as np
import matplotlib.pyplot as plt
import math
import collections
from sfroms import generateSampleFromSample
import itertools
import shapely.geometry
from math import sqrt

numofcars=7
tiv=generateSampleFromSample(numofcars)
h=list(itertools.accumulate(tiv))
delta_t=1
t_simul=30

voie1=dict()

intervals=[None]*numofcars
for k in range(0,numofcars):
    intervals[k]=[h[k]]
    a=intervals[k]

    for t in range(1,t_simul):
        intervals[k].append(a[t-1]+1)

def positionV(v,y):
    return moving.Point(2000,y+v*delta_t)

# def vitesse(v,a):
#     return v+a*delta_t

def vitesse(a_n,v_n,x_n,s_n,V_n,v_n1,x_n1,s_n1):
    b_n=-2*a_n
    b_barre=min(-3,(b_n-3)/2)
    tau=2/3
    a=v_n+tau*2.5*a_n*(1-v_n/V_n)*((((0.025+v_n)/V_n))**0.5)
    # print(a)
    # c=((b_n*tau)**2)-b_n*(2*(x_n1-s_n1-x_n)-v_n*tau-(v_n1**2)/b_barre)
    # print(c)
    # return 1
    b=b_n+math.sqrt(((b_n*tau)**2)-b_n*(2*(x_n1-s_n1-x_n)-v_n*tau-(v_n1**2)/b_barre))
    return min(a,b)


# def acceleration(x0,x1,v0,v1,v):
#     return 0.78*v*(v0-v1)/(x0-x1)

#initialiser le premier vehicule : MovingObject

l=random.normalvariate(6.5,0.3)
posV=[moving.Point(2000,0)]
v=15
speed=[v]
S=[]
S.append(l)
for k in range(1,t_simul):
    posV.append(positionV(v,posV[k-1].y))
    speed.append(v)

voie1[0]=moving.MovingObject(None,moving.TimeInterval(0,300),posV,speed,shapely.geometry.Polygon([(0,0),(0,1.8),(l,1.8),(l,0)]),2,None)

#autres véhicules

y=[None]*numofcars
y[0]=[]

x=[None]*numofcars
x[0]=[]

for t in range(0,len(voie1[0].positions)):
    y[0].append(voie1[0].positions[t].y)



for k in range(1,numofcars):

    a_n=random.normalvariate(1.7,0.3) #m.s-2
    b_n=-2*a_n #m.s-2
    s_n=random.normalvariate(6.5,0.3) #m
    V_n=random.normalvariate(20,3.2) #m/s

    y[k]=[0]
    x[k]=[2000]

    S.append(s_n)

    voie1[k]=moving.MovingObject()
    voie1[k].timeInterval=moving.TimeInterval(intervals[k][0],300+intervals[k][0])
    voie1[k].positions=[moving.Point(2000,0)]
    voie1[k].velocities=[random.normalvariate(14,2)]
    l=random.uniform(6,8)
    voie1[k].geometry=shapely.geometry.Polygon([(0,0),(0,1.8),(l,1.8),(l,0)])
    voie1[k].userType=2

    for t in range(1,t_simul):
        voie1[k].velocities.append(vitesse(a_n,voie1[k].velocities[t-1],voie1[k].positions[t-1].y,S[k],V_n,voie1[k-1].velocities[t-1],voie1[k-1].positions[t-1].y,S[k-1]))
        voie1[k].positions.append(positionV(voie1[k].velocities[t-1],voie1[k].positions[t-1].y))
        # acc.append(acceleration(voie1[k-1].positions[t].y,voie1[k].positions[t].y,voie1[k-1].velocities[t],voie1[k].velocities[t],voie1[k].velocities[t]))
        # posV.append(position(speed[t-1],pos[t-1]))
        # acc.append(acceleration(voie1[k].positions[t-1],voie1[k].positions[t],voie1[k].velocities[t-1],voie1[k].velocities[t]))
        y[k].append(voie1[k].positions[t].y)
        x[k].append(2000)
    plt.plot(intervals[k],y[k])
    plt.plot(x[k],y[k])

plt.show()
plt.draw()
plt.close()
