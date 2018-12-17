from trafficintelligence import moving
import decimal
import random as rd
import numpy as np
import matplotlib.pyplot as plt
import math
import collections
import carFollowingModels as models
import toolkit
import itertools
import shapely.geometry
from math import sqrt
import objectsofworld
import random as rd

class VehicleInput(object):
    def __init__(self, alignmentIdx, volume, desiredSpeedParameters, seed, tSimul, headwayDistributionParameters = None):
        self.alignmentIdx = alignmentIdx
        self.volume = volume
        self.headwayDistributionParameters = headwayDistributionParameters
        self.desiredSpeedParameters = desiredSpeedParameters
        self.seed = seed
        self.tSimul = tSimul

    def save(self):
        toolkit.save_yaml(self.fileName, self)

    @staticmethod
    def gap(sLeader,sFollowing,lengthLeader):
        "calculates gaps between two vehicles"
        distance = sLeader-sFollowing-lengthLeader
        return distance

    def generateHeadways(self, sample_size, seed, scale = None, tiv = None, tivprobcum = None):
        return toolkit.generateSample(sample_size = sample_size, scale = scale, seed = seed , tiv = None, tivprobcum = None)


    #fonction de génération des trajectoires
    def generateTrajectories(self, alignment, tSimul, TIVmin, averageVehicleLength, averageVehicleWidth,
                            vehicleLengthSD, vehicleWidthSD, seed, model):
        '''generates trajectories on an alignment class object
        tSimul : int
        sMin : float'''

        #définition des instants de création des véhicules
        sampleSize = round(self.volume*tSimul/3600)
        tiv = self.generateHeadways(sample_size = round(self.volume*tSimul/3600),
                                    scale = 3600/self.volume,
                                    tiv = None,
                                    tivprobcum = None,
                                    seed = seed)

        h = list(itertools.accumulate(tiv))

        intervals = [None]*sampleSize

        moving.prepareAlignments([alignment.points])
        step = 0.1
        N_Step = tSimul/step
        for k in range(0,sampleSize):
            intervals[k] = [h[k]]

            for t in range(1,round(N_Step)):
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
        v0 = rd.normalvariate(self.desiredSpeedParameters[0],self.desiredSpeedParameters[1])

        curvilinearpositions = moving.CurvilinearTrajectory()
        curvilinearpositions = curvilinearpositions.generate(0,v0,1,alignment.idx)
        positions.addPosition(moving.getXYfromSY(0,0,0,[alignment.points]))

        speed = []
        for t in range(0,round(N_Step)):
            speed.append(v0)

        for t in range(1,round(N_Step)):
            v = speed[t]
            curvilinearpositions.addPositionSYL(curvilinearpositions[-1][0]+v0*step,0,alignment.idx)
            positions.addPosition(moving.getXYfromSY(curvilinearpositions[t][0],curvilinearpositions[t][1],0,[alignment.points]))

        dataVehicles[0].timeInterval = moving.TimeInterval(0,300)
        dataVehicles[0].curvilinearPositions = curvilinearpositions
        dataVehicles[0].velocities = speed
        dataVehicles[0].userType = 1
        dataVehicles[0].positions = positions
        dataVehicles[0].vehicleLength = L[0]
        dataVehicles[0].accelerations = [speed[0]/step]*round(N_Step)



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
            v0 = rd.normalvariate(self.desiredSpeedParameters[0],self.desiredSpeedParameters[1])
            dataVehicles[k].velocities = [0]
            dataVehicles[k].userType = 1

            curvilinearpositions = moving.CurvilinearTrajectory()
            curvilinearpositions = curvilinearpositions.generate(0,0,1,alignment.idx)

            dataVehicles[k].curvilinearPositions = curvilinearpositions

            if model == 'Naive':
                dataVehicles[k].accelerations = [None]
            elif model == 'IDM' :
                dataVehicles[k].accelerations = [0]


            leader = dataVehicles[k-1]
            following = dataVehicles[k]

            if model == 'Naive':
                for t in range(1,round(N_Step)):

                    #
                    # leader = dataVehicles[k-1]
                    # following = dataVehicles[k]


                    dataVehicles[k].velocities.append(models.Models.Naive.speed(leader.curvilinearPositions[t][0],
                                                  following.curvilinearPositions[t-1][0],
                                                  v0,
                                                  leader.vehicleLength,
                                                  TIVmin))
                    curvilinearpositions.addPositionSYL(models.Models.Naive.position(curvilinearpositions[t-1][0], dataVehicles[k].velocities[t], step), 0, alignment.idx)
                    dataVehicles[k].accelerations.append(None)

                dataVehicles[k].curvilinearPositions = curvilinearpositions
                dataVehicles[k].vehicleLength = L[0]


            elif model == 'IDM' :

                for t in range(1,round(N_Step)):

                    dataVehicles[k].velocities.append(models.Models.IDM.speed(
                                                                             following.velocities[t-1],
                                                                             following.accelerations[t-1],
                                                                             step))

                    curvilinearpositions.addPositionSYL(models.Models.IDM.position(
                                                                                   curvilinearpositions[t-1][0],
                                                                                   dataVehicles[k].velocities[t-1],
                                                                                   following.accelerations[t-1],
                                                                                   step),
                                                        0,
                                                        alignment.idx)
                    dataVehicles[k].accelerations.append(models.Models.IDM.acceleration(
                                                                                       s0 = 2, #m,
                                                                                       v = following.velocities[t],
                                                                                       T = 2,
                                                                                       delta_v = following.velocities[t] - leader.velocities[t],
                                                                                       a = 0.73, #m/s2
                                                                                       b = 2, #m/s2,
                                                                                       delta = 4,
                                                                                       v0 = v0 ,
                                                                                       s = VehicleInput.gap(leader.curvilinearPositions[t][0],
                                                                                                            following.curvilinearPositions[t][0],
                                                                                                            leader.vehicleLength)))

                dataVehicles[k].curvilinearPositions = curvilinearpositions
                dataVehicles[k].vehicleLength = L[0]


        if alignment.idx == 0 :
            toolkit.save_yaml('intervalsHorizontal.yml',intervals)
        else :
            toolkit.save_yaml('intervalsVertical.yml',intervals)



        return dataVehicles, intervals

    def generateNewellTrajectories(self, alignment, tSimul, TIVmin, averageVehicleLength, averageVehicleWidth,
                            vehicleLengthSD, vehicleWidthSD, seed):
        '''generates trajectories on an alignment class object
        tSimul : int
        sMin : float'''

        #définition des instants de création des véhicules
        sampleSize = round(self.volume*tSimul/3600)
        tiv = toolkit.generateSample(seed, sampleSize,3600/self.volume, tiv = None, tivprobcum = None)

        moving.prepareAlignments([alignment.points])
        headways = list(itertools.accumulate(tiv))
        step = 0.1
        N_Step = tSimul/step

        intervals = toolkit.prepareIntervals(headways,sampleSize,N_Step)

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
        # v0 = 13
        v0 = rd.normalvariate(14,2)
        rd.seed(seed+3)
        a0 = 1


        curvilinearpositions = moving.CurvilinearTrajectory()
        curvilinearpositions = curvilinearpositions.generate(0,v0,1,alignment.idx)
        positions.addPosition(moving.getXYfromSY(0,0,0,[alignment.points]))


        for t in range(1,round(N_Step)):
            curvilinearpositions.addPositionSYL(curvilinearpositions[-1][0]+v0*step,0,alignment.idx)
            # positions.addPosition(moving.getXYfromSY(curvilinearpositions[t][0],curvilinearpositions[t][1],0,[alignment.points]))

        dataVehicles[0].timeInterval = moving.TimeInterval(0,tSimul)
        dataVehicles[0].curvilinearPositions = curvilinearpositions
        dataVehicles[0].velocities = [v0]*round(N_Step)
        dataVehicles[0].userType = 1
        dataVehicles[0].positions = positions
        dataVehicles[0].vehicleLength = L[0]
        dataVehicles[0].accelerations = [a0]*round(N_Step)


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
            # v0 = 13
            dataVehicles[k].velocities = [0,0]
            dataVehicles[k].userType = 1

            curvilinearpositions = moving.CurvilinearTrajectory()
            curvilinearpositions = curvilinearpositions.generate(0,v0,2,alignment.idx)

            dataVehicles[k].curvilinearPositions = curvilinearpositions
            # positions.addPosition(moving.getXYfromSY(0,0,0,[alignment.points]))

            dataVehicles[k].accelerations = [0,0]
            dataVehicles[k].vehicleLength = L[0]
            rd.seed(seed+5*k)
            d_n = rd.normalvariate(2,1.5)


            leader = dataVehicles[k-1]
            following = dataVehicles[k]

            for t in range(2,round(N_Step)):


                curvilinearpositions.addPositionSYL(following.curvilinearPositions[t-1][0] + step*following.velocities[t-1] + 0.5*(step**2)*following.accelerations[t-1],
                                                    0,
                                                    alignment.idx)

                velocity = dataVehicles[k].velocities[t-1] + (leader.curvilinearPositions[t-1][0]-following.curvilinearPositions[t-1][0]-d_n)/(step/2)

                dataVehicles[k].velocities.append(velocity)
                curvilinearpositions.addPositionSYL(following.curvilinearPositions[t-2][0] + (0.5)*((0.5*step)**2)*following.accelerations[t-2],
                                                    0,
                                                    alignment.idx)

                dataVehicles[k].accelerations.append((leader.velocities[t-1]-following.velocities[t-1])/(2*step))

            dataVehicles[k].curvilinearPositions = curvilinearpositions



        # toolkit.save_yaml(self.fileName,dataVehicles)
        if alignment.idx == 0 :
            toolkit.save_yaml('intervalsHorizontal.yml',intervals)
        else :
            toolkit.save_yaml('intervalsVertical.yml',intervals)

        import matplotlib.pyplot as plt

        vehiclesFile = toolkit.load_yaml('horizontal.yml')
        timeFile  = toolkit.load_yaml('intervalsHorizontal.yml')

        x = []
        v = []

        for k in range (0,len(vehiclesFile)):
            x.append([])

            for time in range(len(vehiclesFile[0].curvilinearPositions)):
                x[k].append(vehiclesFile[k].curvilinearPositions[time][0])

            plt.plot(timeFile[k],x[k])
            ylabel = "longitudinal positions"
            plt.xlabel('t')
            plt.ylabel('x')

        plt.show()
        plt.close()


        return dataVehicles, intervals
