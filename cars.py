from trafficintelligence import moving
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
import objectsofworld

class VehicleInput(object):
    def __init__(self, aligmentIdx, fileName):
        self.aligmentIdx = aligmentIdx
        self.fileName = fileName

    @staticmethod
    def gap(sLeader,sFollowing,lengthLeader):
        "calculates gaps between two vehicles"
        distance = sLeader-sFollowing-lengthLeader
        if distance < 0 :
            distance = 0
        return distance

    #fonction de génération des trajectoires
    def generateTrajectories(self, alignment, tSimul, sMin, averageVehicleLength, averageVehicleWidth, vehicleLengthSD, vehicleWidthSD):
        '''generates trajectories on an alignment class object
        tSimul : int
        sMin : float'''

        #définition des instants de création des véhicules
        sampleSize = round(alignment.volume*tSimul/3600)
        # tiv = toolkit.generateSample(sampleSize)
        # tiv = toolkit.generateSample(sampleSize)
        np.random.seed(123)
        tiv = toolkit.generateSample(sampleSize,1/alignment.volume)

        h = list(itertools.accumulate(tiv))

        intervals = [None]*sampleSize

        moving.prepareAlignments([alignment.points])

        for k in range(0,sampleSize):
            intervals[k] = [h[k]]

            for t in range(1,tSimul):
                intervals[k].append(intervals[k][t-1]+1)

        ##########################################################
                # Initialisation du premier véhicule
        ##########################################################

        dataVehicles = dict()
        dataVehicles[0] = moving.MovingObject()
        positions = moving.Trajectory()

        vehicleLength = random.normalvariate(averageVehicleLength,vehicleLengthSD)
        vehicleWidth = random.normalvariate(averageVehicleWidth,vehicleWidthSD)

        L = []
        L.append(vehicleLength)

        v0 = random.normalvariate(25,3)

        curvilinearpositions = moving.CurvilinearTrajectory()
        curvilinearpositions = curvilinearpositions.generate(0,v0,1,alignment.idx)
        positions.addPosition(moving.getXYfromSY(0,0,0,[alignment.points]))

        speed = []
        for t in range(0,tSimul):
            speed.append(v0)

        for t in range(1,tSimul):
            v = speed[t]
            curvilinearpositions.addPositionSYL(curvilinearpositions[-1][0]+v0,0,alignment.idx)
            positions.addPosition(moving.getXYfromSY(curvilinearpositions[t][0],curvilinearpositions[t][1],0,[alignment.points]))

        dataVehicles[0].timeInterval = moving.TimeInterval(0,300)
        dataVehicles[0].curvilinearPositions = curvilinearpositions
        dataVehicles[0].velocities = speed
        dataVehicles[0].userType = 1
        dataVehicles[0].positions = positions


        ##########################################################
                # Initialisation des autres véhicules
        ##########################################################


        for k in range(1,sampleSize):

            dataVehicles[k] = moving.MovingObject()
            positions = moving.Trajectory()

            vehicleLength = random.uniform(6,8)
            vehicleWidth = random.normalvariate(2.5,0.2)
            L.append(vehicleLength)

            dataVehicles[k].timeInterval = moving.TimeInterval(intervals[k][0],300+intervals[k][0])
            dataVehicles[k].velocities = [0]
            # dataVehicles[k].geometry = shapely.geometry.Polygon([(0,0),(0,1.8),(vehicleLength,1.8),(vehicleLength,0)])
            dataVehicles[k].userType = 1

            curvilinearpositions = moving.CurvilinearTrajectory()
            curvilinearpositions = curvilinearpositions.generate(0,v0,1,alignment.idx)

            dataVehicles[k].curvilinearPositions = curvilinearpositions
            positions.addPosition(moving.getXYfromSY(0,0,0,[alignment.points]))


            for t in range(1,tSimul):
                velocite = random.normalvariate(25,3)

                leader = dataVehicles[k-1].curvilinearPositions[t][0]
                following = dataVehicles[k].curvilinearPositions[t-1][0] + velocite
                s = VehicleInput.gap(leader,following,L[k-1])

                if s < sMin:
                    v = dataVehicles[k-1].velocities[t]
                    velocite = (v*t-L[k-1]-sMin)/t

                if velocite < 0:
                    velocite = 0

                curvilinearpositions.addPositionSYL(curvilinearpositions[t-1][0]+velocite,0,alignment.idx)
                positions.addPosition(moving.getXYfromSY(curvilinearpositions[t][0],curvilinearpositions[t][1],0,[alignment.points]))

                dataVehicles[k].velocities.append(velocite)
                dataVehicles[k].curvilinearPositions = curvilinearpositions
                dataVehicles[k].positions = positions

        toolkit.save_yaml(self.fileName,dataVehicles)
        toolkit.save_yaml('intervals.yml',intervals)

        return dataVehicles, intervals

    @staticmethod
    def generateGhostVehicle(t_simul, alignment):
        ghost = moving.MovingObject()
        ghost.positions = moving.Trajectory.generate(alignment.points[0], moving.Point(0,0), t_simul)
        ghost.velocities = [0]*t_simul
        ghost.curvilinearPositions = moving.CurvilinearTrajectory.generate(0, 0, t_simul, alignment.idx)
        ghost.isGhost = True
        return ghost
