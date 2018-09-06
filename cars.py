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
# import position from toolkit
# import gap from toolkit

"fonction de mise a jour des gaps"

def gap(x_leader,x_following,L_leader):
    return x_leader-x_following-L_leader

"fonction de maj des positions"

def position_v(y,v,t):
    return moving.Point(2000,v*t+y)

def position_h(y,v,t):
    return moving.Point(v*t+y,2000)

number_of_cars=7

class vehicules():

    def __init__(self,direction,nom_fichier_sortie): #direction est un vecteur de la forme moving.Point(x,y)
        self.direction=direction
        self.nom_fichier_sortie=nom_fichier_sortie

    #fonction de génération des trajectoires
    def generate_trajectories(self):

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

        voie=dict()
        voie[0]=moving.MovingObject()

        l=random.normalvariate(6.5,0.3)
        L=[]
        L.append(l)
        # l=7
        if self.direction==moving.Point(0,1):
            posV=moving.Trajectory(positions=[[2000],[0]])
        else:
            posV=moving.Trajectory(positions=[[0],[2000]])

        v0=self.direction.__mul__(random.normalvariate(30,3.2))
        speed=[moving.Point(0,0)]


        for t in range(0,t_simul):
            speed.append(self.direction.__mul__(moving.Point.norm2(v0)))

        if self.direction==moving.Point(0,1):
            for t in range(1,t_simul):
                temp=position_v(posV[t-1].y,moving.Point.norm2(speed[t]),1)
                posV.positions[0].append(temp.x)
                posV.positions[1].append(temp.y)

        else:
            for t in range(1,t_simul):
                temp=position_h(posV[t-1].x,moving.Point.norm2(speed[t]),1)

                posV.positions[0].append(temp.x)
                posV.positions[1].append(temp.y)

        voie[0].timeInterval=moving.Interval(0,300)
        voie[0].positions=posV
        voie[0].velocities=speed
        voie[0].geometry=shapely.geometry.Polygon([(0,0),(0,1.8),(l,1.8),(l,0)])
        voie[0].userType=1


        ##########################################################
                # Initialisation des autres véhicules
        ##########################################################


        for k in range(1,number_of_cars):
            v0=self.direction.__mul__(random.normalvariate(30,3.2))
            l=random.uniform(6,8)
            L.append(l)

            voie[k]=moving.MovingObject()
            voie[k].timeInterval=moving.Interval(intervals[k][0],300+intervals[k][0])

            if self.direction==moving.Point(0,1):
                voie[k].positions=moving.Trajectory(positions=[[2000],[0]])
            else:
                voie[k].positions=moving.Trajectory(positions=[[0],[2000]])

            voie[k].velocities=[moving.Point(0,0)]
            voie[k].geometry=shapely.geometry.Polygon([(0,0),(0,1.8),(l,1.8),(l,0)])
            voie[k].userType=1
            for t in range(1,t_simul):
                # p=moving.MovingObject.getPositions(voie[k])[t-1].y
                if self.direction==moving.Point(0,1):
                    p=voie[k].positions[t-1].y
                else:
                    p=voie[k].positions[t-1].x

                v=moving.Point.norm2(moving.MovingObject.getVelocities(voie[k-1])[t])
                velocite=self.direction.__mul__(moving.Point.norm2(v0))
                new_position=position_v(p,moving.Point.norm2(velocite),t)
                # s=gap(moving.MovingObject.getPositions(voie[k-1])[t].y,new_position.y,L[k-1])
                if self.direction==moving.Point(0,1):
                    s=gap(voie[k-1].positions[t].y,new_position.y,L[k-1])
                else:
                    s=gap(voie[k-1].positions[t].x,new_position.x,L[k-1])

                smin=7

                if s<smin:
                    velocite=self.direction.__mul__((v*t-L[k-1]-smin)/t)

                if self.direction==moving.Point(0,1):
                    if velocite.y<0:
                        velocite=moving.Point(0,0)
                    voie[k].velocities.append(velocite)
                    voie[k].positions.addPosition(position_v(p,moving.Point.norm2(velocite),1))
                else:
                    if velocite.x<0:
                        velocite=moving.Point(0,0)
                    voie[k].velocities.append(velocite)
                    voie[k].positions.addPosition(position_h(p,moving.Point.norm2(velocite),1))


                # voie[k].positions.append(position(p,moving.Point.norm2(velocite),1))

        create_yaml(self.nom_fichier_sortie,voie)

        t=[]
        p=[]
        v=[]
        plt.figure()

        for k in range (0,number_of_cars):
            p.append([])
            v.append([])
            t.append(intervals[k])

            for time in range(0,t_simul):
                if self.direction==moving.Point(0,1):
                    p[k].append(voie[k].positions[time].y)
                else:
                    p[k].append(voie[k].positions[time].x)
                v[k].append(moving.Point.norm2(voie[k].velocities[time]))

            plt.plot(t[k],p[k])
            # plt.plot(t[k],p[k])
        plt.show()
