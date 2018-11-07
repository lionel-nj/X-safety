#from trafficintelligence import *
from trafficintelligence import utils
import decimal
import random
import numpy as np
import matplotlib.pyplot as plt
import math
import collections

import toolkit
import itertools
import shapely.geometry
from math import sqrt
from carsvsped import *

# def getXYfromSY2(s, y, alignmentNum, alignments):
#     ''' Find X,Y coordinate from S,Y data.
#     if mode = 0 : return Snapped X,Y
#     if mode !=0 : return Real X,Y
#     '''
#     alignment = alignments
#     i = 1
#     while s > alignment.points[0].getCumulativeDistance(i) and i < len(alignment.points[0]):
#         i += 1
#     if i < len(alignment.points[0]):
#         d = s - alignment.points[0].getCumulativeDistance(i-1) # distance on subsegment
#         #Get difference vector and then snap
#         dv = alignment.points[0][i] - alignment.points[0][i-1]
#         magnitude  = dv.norm2()
#         normalizedV = dv.divide(magnitude)
#         #snapped = alignment[i-1] + normalizedV*d # snapped point coordinate along alignment
#         # add offset finally
#         orthoNormalizedV = normalizedV.orthogonal()
#         return alignment.points[0][i-1] + normalizedV*d + orthoNormalizedV*y
#     else:
#         print('Curvilinear point {} is past the end of the alignement'.format((s, y, alignmentNum)))
#         return None


class VehicleInput(object):
    def __init__(self, aligmentIdx, nom_fichier_sortie):
        self.aligmentIdx = aligmentIdx
        self.nom_fichier_sortie = nom_fichier_sortie

    @staticmethod
    def gap(s_leader,s_following,length_leader):
        "fonction de mise a jour des gaps"
        distance = s_leader-s_following-length_leader
        if distance < 0 :
            distance = 0
        return distance

    #fonction de génération des trajectoires
    def generateTrajectories(self, alignment, t_simul, s_min):
        '''alignment est un objet de la classe Alignment'''

        #définition des instants de création des véhicules
        number_of_cars = 100#round(t_simul*alignment.flow/3600)
        tiv = toolkit.generateSampleFromSample(number_of_cars,toolkit.generateDistribution('data.csv')) #a revoir ! !on doit prendre en compte le debit de la voie
        h = list(itertools.accumulate(tiv))

        intervals = [None]*number_of_cars

        moving.prepareAlignments([alignment.points])

        for k in range(0,number_of_cars):
            intervals[k] = [h[k]]

            for t in range(1,t_simul):
                intervals[k].append(intervals[k][t-1]+1)

        ##########################################################
                # Initialisation du premier véhicule
        ##########################################################

        data_vehicles = dict()
        data_vehicles[0] = moving.MovingObject()
        positions = moving.Trajectory()

        vehicle_length = random.normalvariate(6.5,0.3)
        vehicle_width = random.normalvariate(2.5,0.2)

        L = []
        L.append(vehicle_length)

        v0 = random.normalvariate(25,3)

        curvilinearpositions = moving.CurvilinearTrajectory()
        curvilinearpositions = curvilinearpositions.generate(0,v0,1,alignment.idx)
        positions.addPosition(moving.getXYfromSY(0,0,0,[alignment.points]))

        speed = []
        for t in range(0,t_simul):
            speed.append(v0)

        for t in range(1,t_simul):
            v = speed[t]
            curvilinearpositions.addPositionSYL(curvilinearpositions[-1][0]+v0,0,alignment.idx)
            positions.addPosition(moving.getXYfromSY(curvilinearpositions[t][0],curvilinearpositions[t][1],0,[alignment.points]))

        data_vehicles[0].timeInterval = moving.TimeInterval(0,300)
        data_vehicles[0].curvilinearPositions = curvilinearpositions
        data_vehicles[0].velocities = speed
        # data_vehicles[0].geometry = shapely.geometry.Polygon([(0,0),(0,1.8),(vehicle_length,1.8),(vehicle_length,0)])
        data_vehicles[0].userType = 1
        data_vehicles[0].positions = positions


        ##########################################################
                # Initialisation des autres véhicules
        ##########################################################


        for k in range(1,number_of_cars):

            data_vehicles[k] = moving.MovingObject()
            positions = moving.Trajectory()

            vehicle_length = random.uniform(6,8)
            vehicle_width = random.normalvariate(2.5,0.2)
            L.append(vehicle_length)

            data_vehicles[k].timeInterval = moving.TimeInterval(intervals[k][0],300+intervals[k][0])
            data_vehicles[k].velocities = [0]
            # data_vehicles[k].geometry = shapely.geometry.Polygon([(0,0),(0,1.8),(vehicle_length,1.8),(vehicle_length,0)])
            data_vehicles[k].userType = 1

            curvilinearpositions = moving.CurvilinearTrajectory()
            curvilinearpositions = curvilinearpositions.generate(0,v0,1,alignment.idx)

            data_vehicles[k].curvilinearPositions = curvilinearpositions
            positions.addPosition(moving.getXYfromSY(0,0,0,[alignment.points]))

            for t in range(1,t_simul):
                velocite = random.normalvariate(25,3)

                leader = data_vehicles[k-1].curvilinearPositions[t][0]
                following = data_vehicles[k].curvilinearPositions[t-1][0] + velocite
                s = VehicleInput.gap(leader,following,L[k-1])

                if s < s_min:
                    v = data_vehicles[k-1].velocities[t]
                    velocite = (v*t-L[k-1]-s_min)/t

                if velocite < 0:
                    velocite = 0

                curvilinearpositions.addPositionSYL(curvilinearpositions[t-1][0]+velocite,0,alignment.idx)
                positions.addPosition(moving.getXYfromSY(curvilinearpositions[t][0],curvilinearpositions[t][1],0,[alignment.points]))

                data_vehicles[k].velocities.append(velocite)
                data_vehicles[k].curvilinearPositions = curvilinearpositions
                data_vehicles[k].positions = positions

        toolkit.save_yaml(self.nom_fichier_sortie,data_vehicles)
        toolkit.save_yaml('intervals.yml',intervals)

        return data_vehicles, intervals
