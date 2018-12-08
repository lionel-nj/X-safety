from trafficintelligence import moving
import decimal
import random as rd
import numpy as np
import matplotlib.pyplot as plt
import math
import collections

import toolkit
import itertools
import shapely.geometry
from math import sqrt
import objectsofworld
import random as rd

class VehicleInput(object):
    def __init__(self, alignmentIdx, fileName, volume):
        self.alignmentIdx = alignmentIdx
        self.fileName = fileName
        self.volume = volume

    def save(self):
        toolkit.save_yaml(self.fileName, self)

    @staticmethod
    def gap(sLeader,sFollowing,lengthLeader):
        "calculates gaps between two vehicles"
        distance = sLeader-sFollowing-lengthLeader
        return distance

    @staticmethod
    def generateHeadways(seed):
        return toolkit.generateSample(seed, sample_size, scale = None, tiv = None, tivprobcum = None)

    @staticmethod
    def generateDesiredSpeed(seed, mean, sd):
        rd.seed(seed)
        return rd.normalvariate(mean, sd)
    #fonction de génération des trajectoires
    def generateTrajectories(self, alignment, tSimul, TIVmin, averageVehicleLength, averageVehicleWidth,
                            vehicleLengthSD, vehicleWidthSD, seed):
        '''generates trajectories on an alignment class object
        tSimul : int
        sMin : float'''

        #définition des instants de création des véhicules
        sampleSize = round(self.volume*tSimul/3600)
        tiv = toolkit.generateSample(seed, sampleSize,3600/self.volume, tiv = None, tivprobcum = None)

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
        rd.seed(seed-1)
        vehicleLength = rd.normalvariate(averageVehicleLength,vehicleLengthSD)
        rd.seed(seed-2)
        vehicleWidth = rd.normalvariate(averageVehicleWidth,vehicleWidthSD)

        L = []
        L.append(vehicleLength)
        rd.seed(seed+1)
        v0 = rd.normalvariate(14,2)

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
        dataVehicles[0].vehicleLength = L[0]


        ##########################################################
                # Initialisation des autres véhicules
        ##########################################################


        for k in range(1,sampleSize):

            dataVehicles[k] = moving.MovingObject()
            positions = moving.Trajectory()
            rd.seed(seed-3*k)
            vehicleLength = rd.normalvariate(averageVehicleLength,vehicleLengthSD)
            rd.seed(seed-4*k)
            vehicleWidth = rd.normalvariate(averageVehicleWidth,vehicleWidthSD)
            L = []
            L.append(vehicleLength)

            dataVehicles[k].timeInterval = moving.TimeInterval(intervals[k][0],tSimul+intervals[k][0])
            rd.seed(seed+k)
            v0 = rd.normalvariate(14,2)
            dataVehicles[k].velocities = [v0]
            dataVehicles[k].userType = 1

            curvilinearpositions = moving.CurvilinearTrajectory()
            curvilinearpositions = curvilinearpositions.generate(0,v0,1,alignment.idx)

            dataVehicles[k].curvilinearPositions = curvilinearpositions
            positions.addPosition(moving.getXYfromSY(0,0,0,[alignment.points]))

            for t in range(1,tSimul):


                leader = dataVehicles[k-1]
                following = dataVehicles[k]
                d = leader.curvilinearPositions[t][0]-(following.curvilinearPositions[t-1][0]+v0) - leader.vehicleLength
                TIV = d/v0
                # s = VehicleInput.gap(leader.curvilinearPositions[t][0],following.curvilinearPositions[t-1][0] + velocite,dataVehicles[k-1].vehicleLength)

                if TIV < TIVmin:

                    velocite = d/TIVmin

                if velocite < 0:
                    velocite = 0

                curvilinearpositions.addPositionSYL(curvilinearpositions[t-1][0]+velocite,0,alignment.idx)
                positions.addPosition(moving.getXYfromSY(curvilinearpositions[t][0],curvilinearpositions[t][1],0,[alignment.points]))

                dataVehicles[k].velocities.append(velocite)
                dataVehicles[k].curvilinearPositions = curvilinearpositions
                dataVehicles[k].positions = positions
                dataVehicles[k].vehicleLength = L[0]


        # toolkit.save_yaml(self.fileName,dataVehicles)
        if alignment.idx == 0 :
            toolkit.save_yaml('intervalsHorizontal.yml',intervals)
        else :
            toolkit.save_yaml('intervalsVertical.yml',intervals)


        return dataVehicles, intervals

# TODO: completer les classes des modeles

class Models(object):
    def __init__(self, name, parameters):
        self.name = name
        self.parameters = parameters

    class Naive(object):
        def __init__(self, parameters):
            self.parameters = parameters

        def nextPosition(previousPosition, desiredSpeed):
            return None

        def nextSpeed(curvilinearPositionLeader, curvilinearPositionFollowing, desiredSpeed):
            return None


    class Newell(object):
        def __init__(self, parameters):
            self.parameters = parameters

        def nextPosition(previousPosition, desiredSpeed, acceleration):
            return None

        def nextSpeed(curvilinearPositionLeader, curvilinearPositionFollowing, desiredSpeed, acceleration):
            return None

def trace(alignment_idx,y_axis):
    import matplotlib.pyplot as plt

    if alignment_idx == 0:
        vehiclesFile = toolkit.load_yaml('horizontal.yml')
        timeFile  = toolkit.load_yaml('intervalsHorizontal.yml')
    else :
        vehiclesFile = toolkit.load_yaml('vertical.yml')
        timeFile = toolkit.load_yaml('intervalsVertical.yml')

    x = []
    # v = []

    for k in range (0,len(vehiclesFile)):
        x.append([])
        # v.append([])

        for time in range(len(vehiclesFile[0].curvilinearPositions)):
            # v[k].append(len(vehiclesFile[0][k].velocities[time]))
            x[k].append(vehiclesFile[k].curvilinearPositions[time][0])
            ylabel = "position on x axis"
        # if y_axis == 'x' :
        plt.plot(timeFile[k],x[k])
        # else :
        #     plt.plot(timeFile[k],v[k])

    plt.xlabel('t')
    plt.ylabel('x')
    plt.show()
    plt.close()
