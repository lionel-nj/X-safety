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

parameters = load_yml('config.yml')

t_simul = parameters['simulation']['t_simulation']
delta_t = parameters['simulation']['delta_t']
number_of_cars = parameters['simulation']['number_of_cars']

class vehicles():

    def __init__(self,nom_fichier_sortie):
        self.nom_fichier_sortie = nom_fichier_sortie
        self.number_of_cars = number_of_cars


    def gap(position_leader,position_following,L_leader):
        "fonction de mise a jour des gaps"
        distance = moving.distanceNorm2(position_leader,position_following)
        return distance-L_leader

    def position(y,v,t):
        "fonctions de maj des positions"
        return v*t+y

    #fonction de génération des trajectoires
    def generateTrajectories(self,alignment):

        "définition des instants de création des véhicules"

        tiv = generateSampleFromSample(number_of_cars,generateDistribution('data.csv')) #a revoir ! !on doit prendre en compte le debit de la voie
        h = list(itertools.accumulate(tiv))

        intervals = [None]*t_simul

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
        x_alignment = alignment.points[0].x
        y_alignment = alignment.points[0].y

        posV = moving.Trajectory(positions = [[x_alignment],[y_alignment]])

        u = moving.Point(x_alignment,y_alignment)/(moving.norm2(moving.Point(x_alignment,y_alignment)))
        v0 = u.__mul__(random.normalvariate(25,3))
        speed = []

        for t in range(0,t_simul):
            speed.append(v0)

        for t in range(1,t_simul):
            v = speed[t]
            temp_x = vehicles.positionV(posV[t-1].x,v.x,1)
            temp_y = vehicles.positionV(posV[t-1].y,v.y,1)

            posV.positions[0].append(temp_x)
            posV.positions[1].append(temp_y)

        # data_vehicles[0].timeInterval = [0,300]
        data_vehicles[0].timeInterval = moving.TimeInterval(0,300)
        data_vehicles[0].positions = posV
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

            x_alignment = alignment.points[0].x
            y_alignment = alignment.points[0].y

            u = moving.Point((x_alignment,y_alignment)/(moving.norm2(moving.Point(x_alignment,y_alignment))))
            v0 = u.__mul__(random.normalvariate(25,3))

            data_vehicles[k].timeInterval = moving.TimeInterval(intervals[k][0],300+intervals[k][0])
            data_vehicles[k].positions = moving.Trajectory(positions = [[x_alignment],[y_alignment]])
            data_vehicles[k].velocities = [v0]
            # data_vehicles[k].geometry = shapely.geometry.Polygon([(0,0),(0,1.8),(vehicle_length,1.8),(vehicle_length,0)])
            data_vehicles[k].userType = 1


            for t in range(1,t_simul):
                velocite = v0
                temp_x = vehicles.positionV(data_vehicles[k].positions[t-1].x,velocite.x,1)
                temp_y = vehicles.positionV(data_vehicles[k].positions[t-1].y,velocite.y,1)

                leader = data_vehicles[k-1].positions[t]
                following = moving.Point(temp_x,temp_y)
                s = vehicles.gap(leader,following,L[k-1])
                smin = 25

                if s < smin:
                    v = data_vehicles[k-1].velocities[t]
                    velocite = u.__mul__((v*t-L[k-1]-smin)/t)

                if velocite.x < 0 or velocite.y < 0:
                    velocite = moving.Point(0,0)

                temp_x = vehicles.position(data_vehicles[k].positions[t-1].x,velocite.x,1)
                temp_y = vehicles.position(data_vehicles[k].positions[t-1].y,velocite.y,1)
                data_vehicles[k].velocities.append(velocite)
                data_vehicles[k].positions.addPosition(moving.Point(temp_x,temp_y))

        #porttion de sauvegarde à séparer du reste
        create_yaml(self.nom_fichier_sortie,data_vehicles)
        create_yaml('intervals.yml',intervals)

        return data_vehicles, intervals
