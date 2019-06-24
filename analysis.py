import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from trafficintelligence import moving, utils

import events
import toolkit


def plotDistanceForUserPair(world, roadUser1, roadUser2):
    """script to plot distance between a pair of vehicles"""
    distances = []
    for t in moving.TimeInterval.intersection(roadUser1.timeInterval, roadUser1.timeInterval):
        distances.append(world.distanceAtInstant(roadUser1, roadUser2, t))
    timeList = list(moving.TimeInterval.intersection(roadUser1.timeInterval, roadUser1.timeInterval))
    plt.plot(timeList, distances)


def plotVariations(indicatorValues, fileName, figName):
    nRep = [k for k in range(1, len(indicatorValues) + 1)]
    meanValues = [indicatorValues[0]]
    for k in range(1, len(indicatorValues)):
        meanValues.append(np.mean(indicatorValues[:k + 1]))
    plt.plot(nRep, meanValues)
    plt.title(figName)
    plt.savefig(fileName)
    plt.close('all')


def timeToCollisionAtInstant(user, t, world, X):
    if X:
        if user.leader is not None:
            leader = user.leader
            if t in list(moving.TimeInterval.intersection(user.timeInterval, user.leader.timeInterval)):
                v0 = leader.getCurvilinearVelocityAtInstant(t)[0]
                v1 = user.getCurvilinearVelocityAtInstant(t)[0]
                if v1 > v0:
                    ttc = (world.distanceAtInstant(user, user.leader, t)) / (v1 - v0)  # world.distanceAtInstant(user, user.leader, t)) = x0-x1-longueur leader
                    return ttc
            else:
                return None
        else:
            return None
    else:
        if user.leader is not None:
            leaderCP = user.leader.getCurvilinearPositionAtInstant(t)
            if leaderCP[0] > world.getControlDevicePositionOnAlignment(leaderCP[2]):
                # if world.analysisZone.userInAnalysisZone(user, t):
                t1 = world.distanceAtInstant(user, world.controlDevices[0], t) / (
                            user.getCurvilinearVelocityAtInstant(t)[0] / world.timeStep)
                world.checkTraffic(user, t)
                adjacentUser = user.comingUser
                if adjacentUser is not None:
                    if world.analysisZone.userInAnalysisZone(adjacentUser, t):
                        t2 = world.distanceAtInstant(adjacentUser, world.controlDevices[0], t) / (
                                    adjacentUser.getCurvilinearVelocityAtInstant(t)[0] / world.timeStep)
                        return max(t1, t2)

        else:
            t1 = world.distanceAtInstant(user, world.controlDevices[0], t) / user.getCurvilinearVelocityAtInstant(t)[0]
            world.checkTraffic(user, t)
            adjacentUser = user.comingUser
            if adjacentUser is not None:
                if world.analysisZone.userInAnalysisZone(adjacentUser, t):
                    t2 = world.distanceAtInstant(adjacentUser, world.controlDevices[0], t) / (
                                adjacentUser.getCurvilinearVelocityAtInstant(t)[0] / world.timeStep)
                    return max(t1, t2)


def timeToCollision(user, world, X):
    ttc = []
    inter = moving.TimeInterval.intersection(user.timeInterval, user.leader.timeInterval)
    for t in list(inter):
        if world.analysisZone is not None:
            if world.analysisZone.userInAnalysisZone(user, t):
                ttcValue = timeToCollisionAtInstant(user, t, world, X)
                if ttcValue is not None:
                    ttc.append(ttcValue)
        else:
            ttcValue = timeToCollisionAtInstant(user, t, world, X)
            if ttcValue is not None:
                ttc.append(ttcValue)
    return ttc


def countInteractions(distance, interactions, analysisZone=None):
    number = []
    duration = []
    for key in interactions:
        if analysisZone is not None:
            pass
            # if (analysisZone.getUserTimeIntervalInAZ(interactions[key][0].roadUser1) is not None and
            #         analysisZone.getUserTimeIntervalInAZ(interactions[key][0].roadUser2) is not None):
            #     timeInterval = moving.TimeInterval.intersection(
            #         analysisZone.getUserTimeIntervalInAZ(interactions[key][0].roadUser1),
            #         analysisZone.getUserTimeIntervalInAZ(interactions[key][0].roadUser2))
            # else:
            #     timeInterval = None
            # if timeInterval is not None:
            #     val = interactions[key][0].getIndicatorValuesInTimeInterval(timeInterval, 'Distance')
            #     if not (None in val):
            #         number.append(len(toolkit.groupOnCriterion(val, distance)))
        else:
            number.append(len(toolkit.groupOnCriterion(interactions[key].indicators['Distance'].values.values(), distance)))
            for item in toolkit.groupOnCriterion(interactions[key].indicators['Distance'].values.values(), distance):
                duration.append(len(item))
    interactionNumber = np.sum(number)
    return interactionNumber, duration


def postEncroachmentTimeAtInstant(user, t, world):
    if len(world.alignments) > 2:
        if user.leader is not None:
            leaderCP = user.leader.getCurvilinearPositionAtInstant(t)
            if leaderCP[0] > world.getControlDevicePositionOnAlignment(leaderCP[2]):
                t1 = world.distanceAtInstant(user, world.controlDevices[0], t) / (
                            user.getCurvilinearVelocityAtInstant(t)[0] / world.timeStep)
                world.checkTraffic(user, t)
                adjacentUser = user.comingUser
                if adjacentUser is not None:
                    if world.analysisZone.userInAnalysisZone(adjacentUser, t):
                        t2 = (adjacentUser.geometry + world.distanceAtInstant(adjacentUser, world.controlDevices[0],
                                                                              t)) / (
                                         adjacentUser.getCurvilinearVelocityAtInstant(t)[0] / world.timeStep)
                        return abs(t2 - t1)

        else:
            t1 = world.distanceAtInstant(user, world.controlDevices[0], t) / user.getCurvilinearVelocityAtInstant(t)[0]
            world.checkTraffic(user, t)
            adjacentUser = user.comingUser
            if adjacentUser is not None:
                if world.analysisZone.userInAnalysisZone(adjacentUser, t):
                    t2 = (adjacentUser.geometry + world.distanceAtInstant(adjacentUser, world.controlDevices[0], t)) / (
                                adjacentUser.getCurvilinearVelocityAtInstant(t)[0] / world.timeStep)
                    return abs(t2 - t1)


def postEncroachmentTime(user, world):
    pet = []
    for t in list(user.timeInterval):
        if world.analysisZone.userInAnalysisZone(user, t) is not None:
            if world.analysisZone.userInAnalysisZone(user, t):
                if postEncroachmentTimeAtInstant(user, t, world) is not None:
                    pet.append(postEncroachmentTimeAtInstant(user, t, world))
        else:
            pet.append(postEncroachmentTimeAtInstant(user, t, world))
    return pet


# def getDistance(val, interactions, seeds):
#     distance = {}  # liste des distances minimales pour chaque repetition de simulation
#     if val == 'min':
#         for seed in seeds:
#             distance[seed] = []
#             for inter in interactions[seed]:
#                 distance[seed].append(min(interactions[seed][inter][0].indicators['Distance'].values.values()))
#             distance[seed] = np.mean(distance[seed])
#
#     if val == 'mean':
#         for seed in seeds:
#             distance[seed] = []
#             for inter in interactions[seed]:
#                 distance[seed].append(
#                     np.mean(list(interactions[seed][inter][0].indicators['Distance'].values.values())))
#             distance[seed] = np.mean(distance[seed])
#
#     return distance


def evaluateSimpleModel(world, sim):
    # todo : a tester
    interactions = {}
    sim.run(world)

    for user in world.completed[1:] + world.users:
        roadUser1 = user.leader
        roadUser2 = user
        i = events.Interaction(roadUser1=roadUser1, roadUser2=roadUser2, useCurvilinear=True)
        i.computeDistance(world)
        i.computeTTC()
        interactions[(roadUser1.num, roadUser2.num)] = i

    minTTCValues = {}
    minDistanceValues = {}
    meanDistanceValues = {}
    for key in interactions:
        ttcList = toolkit.groupOnCriterion(interactions[key].indicators['Time to Collision'].values.values(), 20)
        if ttcList != []:
            minTTCValues[key] = []
        for value in ttcList:
            minTTCValues[key].append(min(value))
        minDistanceValues[key] = min(interactions[key].indicators['Distance'].values.values())
        meanDistanceValues[key] = np.mean(list(interactions[key].indicators['Distance'].values.values()))

    interactionNumber5, duration5 = countInteractions(5, interactions)
    interactionNumber10, duration10 = countInteractions(10, interactions)
    interactionNumber15, duration15 = countInteractions(15, interactions)

    ttcData = pd.DataFrame.from_dict(minTTCValues, orient='index').transpose()
    minDistanceData = pd.DataFrame.from_dict(minDistanceValues, orient='index')
    meanDistanceData = pd.DataFrame.from_dict(meanDistanceValues, orient='index')
    interactionNumber = pd.DataFrame.from_dict({5: interactionNumber5,
                                                10: interactionNumber10,
                                                15: interactionNumber15}, orient='index')
    interactionDuration = pd.DataFrame.from_dict({5: duration5,
                                                 10: duration10,
                                                 15: duration15}, orient='index').transpose()

    ttcData.to_csv('outputData/single-evaluations/ttc/data-seed={}-headway{}.csv'.format(sim.seed, world.getUserInputById(0).distributions['headway'].scale+1))
    minDistanceData.to_csv('outputData/single-evaluations/minDistance/data-seed={}-headway{}.csv'.format(sim.seed, world.getUserInputById(0).distributions['headway'].scale+1))
    meanDistanceData.to_csv('outputData/single-evaluations/meanDistance/data-seed={}-headway{}.csv'.format(sim.seed, world.getUserInputById(0).distributions['headway'].scale+1))
    interactionNumber.to_csv('outputData/single-evaluations/interaction-number/data-seed={}-headway{}.csv'.format(sim.seed, world.getUserInputById(0).distributions['headway'].scale+1))
    interactionDuration.to_csv('outputData/single-evaluations/interaction-duration/data-seed={}-headway{}.csv'.format(sim.seed, world.getUserInputById(0).distributions['headway'].scale+1))

    ttc = []
    for key in list(ttcData.keys()):
        ttc.append(min(ttcData[key]))

    return ttc, list(minDistanceValues.values()), list(meanDistanceValues.values()), interactionNumber5, interactionNumber10, interactionNumber15, duration5, duration10, duration15


def evaluateModel(world, sim, seed, file, zoneArea=None):
    interactions = {}
    usersCount = {}
    if zoneArea is not None:
        world.analysisZone = AnalysisZone(world, zoneArea)
    else:
        world.analysisZone = None

    interactions[seed] = {}
    sim.seed = seed
    sim.run(world)
    usersCount[seed] = world.getNotNoneVehiclesInWorld()[0]

    for userNum in range(len(usersCount[seed]) - 1):
        roadUser1 = world.getUserByNum(usersCount[seed][userNum].num)
        roadUser2 = world.getUserByNum(usersCount[seed][userNum + 1].num)
        interactions[seed][(roadUser1.num, roadUser2.num)] = []
        i = events.Interaction(useCurvilinear=True, roadUser1=roadUser1, roadUser2=roadUser2)
        i.computeDistance(world)
        interactions[seed][(roadUser1.num, roadUser2.num)].append(i)

        t = roadUser1.timeInterval.first
        while t in list(roadUser1.timeInterval):
            world.checkTraffic(roadUser1, t)
            if roadUser1.comingUser is not None:
                roadUser2 = roadUser1.comingUser
                print(roadUser1.num, roadUser2.num)
                interactions[seed][(roadUser1.num, roadUser2.num)] = []
                j = events.Interaction(useCurvilinear=True, roadUser1=roadUser1, roadUser2=roadUser2)
                j.computeDistance(world)
                interactions[seed][(roadUser1.num, roadUser2.num)].append(j)
                t = roadUser1.timeInterval.last + 5
            else:
                t += 1

    ### TTC sur un lien ###
    TTCCF = {}
    TTCminCF = {}

    for user in usersCount[seed]:
        if user.leader is not None:
            ttc_CF = timeToCollision(user, world, X=False)
            num0 = user.leader.num
            TTCCF[num0, user.num] = ttc_CF
        if ttc_CF != []:
            if min(TTCCF[num0, user.num]) < 30:
                TTCminCF[num0, user.num] = min(TTCCF[num0, user.num])

    n, bins = np.histogram(list(TTCminCF.values()))
    mids = 0.5 * (bins[1:] + bins[:-1])
    if sum(n) != 0:
        meanTTCminCF = np.average(mids, weights=n)
    else:
        meanTTCminCF = None

    ### TTC sur un deux liens ###
    TTCX = {}
    TTCminX = {}

    for user in usersCount[seed]:
        if user.leader is not None:
            ttcX = timeToCollision(user, world, X=True)
            TTCX[user.num] = ttcX
        if ttcX != []:
            if min(TTCX[user.num]) < 30:
                TTCminX[user.num] = min(TTCX[user.num])

    n, bins = np.histogram(list(TTCminX.values()))
    mids = 0.5 * (bins[1:] + bins[:-1])
    if sum(n) != 0:
        meanTTCminX = np.average(mids, weights=n)
    else:
        meanTTCminX = None

    if len(world.alignments) > 2:
        PET = {}
        PETmin = {}
        for user in usersCount[seed]:
            pet = postEncroachmentTime(user, world)

            PET[user.num] = pet
            if pet != []:
                if min(PET[user.num]) < 30:
                    PETmin[user.num] = min(PET[user.num])

        _n, _bins = np.histogram(list(PETmin.values()))
        _mids = 0.5 * (_bins[1:] + _bins[:-1])
        if sum(_n) != 0:
            meanPETmin = np.average(_mids, weights=_n)
        else:
            meanPETmin = None
    else:
        meanPETmin = None

    ### nombre d'interactions quand d<5, 10, 15 ###
    minDistance = getDistance('min', interactions, seed)
    meanDistance = getDistance('mean', interactions, seed)
    interactionNumber5 = countInteractions(5, interactions, world.analysisZone)
    interactionNumber10 = countInteractions(10, interactions, world.analysisZone)
    interactionNumber15 = countInteractions(15, interactions, world.analysisZone)

    data = pandas.DataFrame(data=[meanTTCminCF, list(minDistance.values())[0], list(meanDistance.values())[0],
                                  len(usersCount[seed]), list(interactionNumber5.values())[0],
                                  list(interactionNumber10.values())[0], list(interactionNumber15.values())[0], meanPETmin, meanTTCminX],
                            index=['TTCCF', 'minDistance', 'meanDistance', 'userCount', 'meanInteractionNumber5',
                                   'meanInteractionNumber10', 'meanInteractionNumber15', 'pet (min)', 'TTCX'])

    data.to_csv('outputData/evaluations/{}-data-seed={}-area{}.csv'.format(file, seed, zoneArea))

    return meanTTCminCF, list(minDistance.values())[0], list(meanDistance.values())[0], len(usersCount[seed]), \
           list(interactionNumber5.values())[0], list(interactionNumber10.values())[0], list(interactionNumber15.values())[
               0], meanPETmin, meanTTCminX


class AnalysisZone:
    def __init__(self, world, area):
        self.center = world.getIntersectionXYcoords()  # moving.Point
        if self.center is None:
            self.center = world.getAlignmentById(world.userInputs[0].alignmentIdx).points[-1]
        self.minAlignment = []
        self.maxAlignment = []
        self.area = area
        for al in world.alignments:
            if al.connectedAlignmentIndices is not None:
                self.minAlignment.append([al.getCumulativeDistances(-1) - self.area ** .5, al.idx])
            else:
                self.maxAlignment.append([self.minAlignment[-1][0] + 2 * (self.area ** .5), al.idx])

    def userInAnalysisZone(self, user, t):
        """determines if a user is inside a predetermined analysis zone"""
        rep = False
        if t in list(user.timeInterval):
            cp = user.getCurvilinearPositionAtInstant(t)
            for minVal, maxVal in zip(self.minAlignment, self.maxAlignment):
                if (minVal[0] <= cp[0] <= maxVal[0]) and (cp[2] == minVal[1] or cp[2] == maxVal[1]):
                    rep = True
                    break
            return rep
        else:
            return rep

    def getUserTimeIntervalInAZ(self, user):
        timeInterval = moving.TimeInterval()
        userLanes = utils._set(user.curvilinearPositions.lanes)
        for lane in userLanes:
            for x in self.minAlignment:
                if x[1] == lane:
                    if np.argmax(np.array(user.curvilinearPositions.positions[0]) > x[0]) != 0:
                        timeInterval.first = np.argmax(
                            np.array(user.curvilinearPositions.positions[0]) > x[0]) + user.getFirstInstant()
            for x in self.maxAlignment:
                if x[1] == lane:
                    if np.argmin(np.array(user.curvilinearPositions.positions[0]) <= x[0]) != 0:
                        timeInterval.last = np.argmin(
                            np.array(user.curvilinearPositions.positions[0]) <= x[0]) + user.getFirstInstant() - 1
        if timeInterval.last == -1:
            if timeInterval.first == 0:
                timeInterval = None
            else:
                timeInterval.last = user.getLastInstant()

        return timeInterval
