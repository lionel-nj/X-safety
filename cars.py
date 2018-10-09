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

t_stop = 30
t_marche1 = 30
t_marche2 = 30
t_simul = t_marche1+t_marche2+t_stop
number_of_cars = 7

class flow():

    def __init__(self,direction,nom_fichier_sortie): #direction est un vecteur de la forme moving.Point(x,y)
        self.direction = direction
        self.nom_fichier_sortie = nom_fichier_sortie


    def gap(x_leader,x_following,L_leader):
        "fonction de mise a jour des gaps"
        return x_leader-x_following-L_leader

    def positionV(y,v,t,p):
        "fonctions de maj des positions"
        return moving.Point(p,v*t+y)

    def positionH(y,v,t,p):
        "fonctions de maj des positions"
        return moving.Point(v*t+y,p)

    #fonction de génération des trajectoires
    def generateTrajectories(self):

        "définition des instants de création des véhicules"

        tiv = generateSampleFromSample(number_of_cars)
        h = list(itertools.accumulate(tiv))

        delta_t = 1
        t_stop = 30
        t_marche1 = 30
        t_marche2 = 30
        t_simul = t_marche1+t_marche2+t_stop

        intervals = [None]*t_simul

        for k in range(0,number_of_cars):
            intervals[k] = [h[k]]

            for t in range(1,t_simul):
                intervals[k].append(intervals[k][t-1]+1)

        ##########################################################
                # Initialisation du premier véhicule
        ##########################################################

        data_flow = dict()
        data_flow[0] = moving.MovingObject()

        l = random.normalvariate(6.5,0.3)
        L = []
        L.append(l)
        # l = 7
        if self.direction == moving.Point(0,1):
            posV = moving.Trajectory(positions = [[2000],[0]])
        else:
            posV = moving.Trajectory(positions = [[0],[2000]])

        v0 = self.direction.__mul__(random.normalvariate(30,3.2))
        speed = [moving.Point(0,0)]

        # if control_device.category == 3:
            #bla bla en cas d'absence de controlDevice
        for t in range(0,t_simul):
            speed.append(self.direction.__mul__(moving.Point.norm2(v0)))

        if self.direction == moving.Point(0,1):
            for t in range(1,t_simul):
                temp = flow.positionV(posV[t-1].y,moving.Point.norm2(speed[t]),1,2000)
                posV.positions[0].append(temp.x)
                posV.positions[1].append(temp.y)

        else:
            for t in range(1,t_simul):
                temp = flow.positionH(posV[t-1].x,moving.Point.norm2(speed[t]),1,2000)

                posV.positions[0].append(temp.x)
                posV.positions[1].append(temp.y)
        #
        # elif control_device.category == 0:
        #     #blabla en cas de stop
        #     while distance_to_stop > 2:
        #         for t in range(0,t_simul):
        #             speed.append(self.direction.__mul__(moving.Point.norm2(v0)))
        #
        #         if self.direction == moving.Point(0,1):
        #             for t in range(1,t_simul):
        #                 temp = flow.positionV(posV[t-1].y,moving.Point.norm2(speed[t]),1,2000)
        #                 posV.positions[0].append(temp.x)
        #                 posV.positions[1].append(temp.y)
        #
        #         else:
        #             for t in range(1,t_simul):
        #                 temp = flow.positionH(posV[t-1].x,moving.Point.norm2(speed[t]),1,2000)
        #
        #                 posV.positions[0].append(temp.x)
        #                 posV.positions[1].append(temp.y)
        #
        #     next_veh_to_exit=detect_next_vehicle_to_exit_crossing_zone()
        #
        #
        # 
        # elif control_device.category == 1:
        #     #blabla en cas de yield
        #
        # elif control_device.category == 2:
        #     #blabla redlight

        # data_flow[0].timeInterval = [0,300]
        data_flow[0].timeInterval = moving.TimeInterval(0,300)
        data_flow[0].positions = posV
        data_flow[0].velocities = speed
        data_flow[0].geometry = shapely.geometry.Polygon([(0,0),(0,1.8),(l,1.8),(l,0)])
        data_flow[0].userType = 1


        ##########################################################
                # Initialisation des autres véhicules
        ##########################################################


        for k in range(1,number_of_cars):
            v0 = self.direction.__mul__(random.normalvariate(30,3.2))
            l = random.uniform(6,8)
            L.append(l)

            data_flow[k] = moving.MovingObject()
            # data_flow[k].timeInterval = [intervals[k][0],300+intervals[k][0]]
            data_flow[k].timeInterval = moving.TimeInterval(intervals[k][0],300+intervals[k][0])

            if self.direction == moving.Point(0,1):
                data_flow[k].positions = moving.Trajectory(positions = [[2000],[0]])
            else:
                data_flow[k].positions = moving.Trajectory(positions = [[0],[2000]])

            data_flow[k].velocities = [moving.Point(0,0)]
            data_flow[k].geometry = shapely.geometry.Polygon([(0,0),(0,1.8),(l,1.8),(l,0)])
            data_flow[k].userType = 1


            for t in range(1,t_simul):
                # p = moving.MovingObject.getPositions(data_flow[k])[t-1].y
                if self.direction == moving.Point(0,1):
                    p = data_flow[k].positions[t-1].y
                else:
                    p = data_flow[k].positions[t-1].x

                v = moving.Point.norm2(moving.MovingObject.getVelocities(data_flow[k-1])[t])
                velocite = self.direction.__mul__(moving.Point.norm2(v0))
                new_position = flow.positionV(p,moving.Point.norm2(velocite),t,2000)
                # s = gap(moving.MovingObject.getPositions(data_flow[k-1])[t].y,new_position.y,L[k-1])
                if self.direction == moving.Point(0,1):
                    s = flow.gap(data_flow[k-1].positions[t].y,new_position.y,L[k-1])
                else:
                    s = flow.gap(data_flow[k-1].positions[t].x,new_position.x,L[k-1])

                smin = 25

                if s < smin:
                    velocite = self.direction.__mul__((v*t-L[k-1]-smin)/t)

                if self.direction == moving.Point(0,1):
                    if velocite.y < 0:
                        velocite = moving.Point(0,0)
                    data_flow[k].velocities.append(velocite)
                    data_flow[k].positions.addPosition(flow.positionV(p,moving.Point.norm2(velocite),1,2000))
                else:
                    if velocite.x < 0:
                        velocite = moving.Point(0,0)
                    data_flow[k].velocities.append(velocite)
                    data_flow[k].positions.addPosition(flow.positionH(p,moving.Point.norm2(velocite),1,2000))


                # data_flow[k].positions.append(position(p,moving.Point.norm2(velocite),1))

        #porttion de sauvegarde à séparer du reste
        create_yaml(self.nom_fichier_sortie,data_flow)
        return data_flow, intervals

    def trace(self,data_flow):
        t = []
        p = []
        v = []
        objet = data_flow.generateTrajectories()
        ylabel = ''

        for k in range (0,number_of_cars):
            p.append([])
            v.append([])
            t.append(objet[1][k])

            for time in range(0,t_simul):
                if self.direction == moving.Point(0,1):
                    p[k].append(objet[0][k].positions[time].y)
                    ylabel = "position selon l'axe x"
                else:
                    p[k].append(objet[0][k].positions[time].x)
                    ylabel = "position selon l'axe y"

                v[k].append(moving.Point.norm2(objet[0][k].velocities[time]))

            plt.plot(t[k],p[k])
            # plt.plot(t[k],p[k])
        plt.xlabel('temps')
        plt.ylabel(ylabel)

        plt.show()
