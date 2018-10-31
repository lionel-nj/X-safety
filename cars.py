from trafficintelligence import *
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
from carsvsped import *
# import position from toolkit
# import gap from toolkit

parameters = load_yml('config.yml')

t_simul = parameters['simulation']['t_simulation']
delta_t = parameters['simulation']['delta_t']
number_of_cars = parameters['simulation']['number_of_cars']

class vehicles():

    def __init__(self,nom_fichier_sortie):
        self.nom_fichier_sortie = nom_fichier_sortie
        self.number_of_cars = number_of_cars


    def gap(s_leader,s_following,length_leader):
        "fonction de mise a jour des gaps"
        distance = s_leader-s_following-length_leader
        return distance

    #fonction de génération des trajectoires
    def generateTrajectories(self,alignment):
        '''alignment est un objet de la classe Alignment'''

        #définition des instants de création des véhicules

        tiv = generateSampleFromSample(number_of_cars,generateDistribution('data.csv')) #a revoir ! !on doit prendre en compte le debit de la voie
        h = list(itertools.accumulate(tiv))

        intervals = [None]*number_of_cars

        moving.prepareAlignments(alignment.points)

        for k in range(0,number_of_cars):
            intervals[k] = [h[k]]

            for t in range(1,t_simul):
                intervals[k].append(intervals[k][t-1]+1)

        ##########################################################
                # Initialisation du premier véhicule
        ##########################################################

        data_vehicles = dict()
        data_vehicles[0] = moving.MovingObject()

        vehicle_length = random.normalvariate(6.5,0.3)
        vehicle_width = random.normalvariate(2.5,0.2)

        L = []
        L.append(vehicle_length)
        # x0_alignment = alignment.points[0][0].x
        # y0_alignment = alignment.points[0][0].y

        v0 = random.normalvariate(25,3)

        curvilinearpositions = moving.CurvilinearTrajectory()
        curvilinearpositions = curvilinearpositions.generate(0,v0,1,alignment.id)

        speed = []
        for t in range(0,t_simul):
            speed.append(v0)

        for t in range(1,t_simul):
            v = speed[t]
            temp_s = curvilinearpositions.addPositionSYL(curvilinearpositions[-1][0]+v0,0,alignment.id)
            # temp_s = vehicles.position(posV[t-1].x,v.x,1)
            #
            # posV.positions[0].append(temp_x)
            # posV.positions[1].append(temp_y)

        # data_vehicles[0].timeInterval = [0,300]
        data_vehicles[0].timeInterval = moving.TimeInterval(0,300)
        data_vehicles[0].curvilinearPositions = curvilinearpositions
        data_vehicles[0].velocities = speed
        # data_vehicles[0].geometry = shapely.geometry.Polygon([(0,0),(0,1.8),(vehicle_length,1.8),(vehicle_length,0)])
        data_vehicles[0].userType = 1


        ##########################################################
                # Initialisation des autres véhicules
        ##########################################################


        for k in range(1,number_of_cars):

            data_vehicles[k] = moving.MovingObject()

            vehicle_length = random.uniform(6,8)
            vehicle_width = random.normalvariate(2.5,0.2)
            L.append(vehicle_length)

            # x0_alignment = alignment.points[0][0].x
            # y0_alignment = alignment.points[0][0].y

            # u = moving.Point(x0_alignment,y0_alignment).__mul__(1/(moving.Point.norm2(moving.Point(x0_alignment,y0_alignment))))
            v0 = random.normalvariate(25,3)

            data_vehicles[k].timeInterval = moving.TimeInterval(intervals[k][0],300+intervals[k][0])
            data_vehicles[k].velocities = [0]
            # data_vehicles[k].geometry = shapely.geometry.Polygon([(0,0),(0,1.8),(vehicle_length,1.8),(vehicle_length,0)])
            data_vehicles[k].userType = 1

            curvilinearpositions = moving.CurvilinearTrajectory()
            curvilinearpositions = curvilinearpositions.generate(0,v0,1,alignment.id)
            data_vehicles[k].curvilinearPositions = curvilinearpositions

            for t in range(1,t_simul):
                velocite = v0
                # temp_x = vehicles.position(data_vehicles[k].positions[t-1].x,velocite.x,1)
                # temp_y = vehicles.position(data_vehicles[k].positions[t-1].y,velocite.y,1)
                # temp_s =

                leader = data_vehicles[k-1].curvilinearPositions[t][0]
                following = data_vehicles[k].curvilinearPositions[t-1][0]
                s = vehicles.gap(leader,following,L[k-1])
                smin = 25

                if s < smin:
                    v = data_vehicles[k-1].velocities[t]
                    velocite = (v*t-L[k-1]-smin)/t

                if velocite < 0:
                    velocite = 0

                curvilinearpositions.addPositionSYL(curvilinearpositions[-1][0],velocite,alignment.id)
                # temp_s = vehicles.position(data_vehicles[k].positions[t-1].x,velocite.x,1)
                # temp_y = vehicles.position(data_vehicles[k].positions[t-1].y,velocite.y,1)
                data_vehicles[k].velocities.append(velocite)
                data_vehicles[k].curvilinearPositions = curvilinearpositions
                # data_vehicles[k].positions.addPosition(moving.Point(temp_x,temp_y))


        # for k in range(len(data_vehicles)):
        #     moving.MovingObject.projectCurvilinear(data_vehicles[k], alignment.points)


        create_yaml(self.nom_fichier_sortie,data_vehicles)
        create_yaml('intervals.yml',intervals)

        return data_vehicles, intervals


def trace(list_of_vehicles):
    temps = toolkit.load_yml('intervals.yml')
    x = []
    y = []
    v = []

    for k in range (0,len(veh)):
        x.append([])
        y.append([])
        v.append([])

        for time in range(0,len(list_of_vehicles[0].positions)):
            v[k].append(moving.Point.norm2(list_of_vehicles[k].velocities[time]))
            x[k].append(list_of_vehicles[k].positions[time].x)
            y[k].append(list_of_vehicles[k].positions[time].y)
            ylabel = "position selon l'axe x"

        plt.plot(temps[k],x[k])

    plt.xlabel('x')
    plt.ylabel('y')
    plt.show()
    plt.close()
