import matplotlib.pyplot as plt
import numpy as np
from trafficintelligence import moving, events

import toolkit


def getHeadwayValues(world):
    """ script to return headway values of generated vehicules in world"""
    headways = []
    for ui in world.userInputs:
        headways.append(ui.headways[0:len(ui.alignment.users)])
    return headways


def getDistanceValuesBetweenUsers(world, roadUser1, roadUser2, plot=False):
    """script to get distance between a pair of vehicles"""
    if roadUser1.timeInterval is not None and roadUser2.timeInterval is not None:
        i = events.Interaction(useCurvilinear=True, roadUser1=roadUser1, roadUser2=roadUser2)
        i.computeIndicators(world=world, alignment1=world.travelledAlignments(roadUser1),
                            alignment2=world.travelledAlignments(roadUser2))
        if plot:
            plt.plot(i.indicators['Distance'].values.keys(), list(i.indicators['Distance'].values.values()))
        return list(i.indicators['Distance'].values.values())


def getMinDistanceBetweenEachPairCF(world):
    """script to get min of distances between each pair of vehicles"""
    minDistances = []
    for ui in world.userInputs:
        for k in range(len(ui.alignment.users) - 1):
            if getDistanceValuesBetweenUsers(world, ui.alignment.users[k], ui.alignment.users[k + 1]):
                minDistances.append(
                    min(getDistanceValuesBetweenUsers(world, ui.alignment.users[k], ui.alignment.users[k + 1])))
    return minDistances


def minDistanceChecked(world, user0, user1, t, dmin):
    """ checks if the minimum distance headway between two vehicles is verified
    in a car following situation : i is the leader vehicle and j is the following vehicle"""
    d = world.distanceAtInstant(user0, user1, t)
    if d is not None:
        if d >= dmin:
            return True
        else:
            return False
    else:
        return None


def isAnEncounter(world, user0, user1, t, dmin):
    """ checks if there is an encounter between two vehicules
    leaderAlignmentIdx and followerAlignmentIdx are integers
    i,j : integers
    t : time, integer
    dmin : float  """
    if minDistanceChecked(world, user0, user1, t, dmin) is not None:
        if minDistanceChecked(world, user0, user1, t, dmin):
            return False
        else:
            return True
    else:
        return None


def getInteractionsDuration(world, dmin, inLine=False):
    """ counts according to the selected method (cross or inLine)
     the number of interactions taking place at a distance smaller than dmin.
    """
    if inLine:
        result = {}
        # pour chaque userInput
        for uiIdx, ui in enumerate(world.userInputs):
            # pour chaque vehicule présent : sauf le dernier
            for h in range(0, len(ui.alignment.users) - 1):
                # si les deux vehicules sont générés
                if ui.alignment.users[h].timeInterval is not None and ui.alignment.users[
                    h + 1].timeInterval is not None:
                    # recuperer l'intervalle de coexistence des vehicules
                    inter = moving.TimeInterval.intersection(ui.alignment.users[h].timeInterval,
                                                             ui.alignment.users[h + 1].timeInterval)
                    # initialiser resultat(paire de vehicules concernées : leader.num, follower.num)
                    result[(ui.alignment.users[h].num, ui.alignment.users[h + 1].num)] = []
                    # pour chaque instant de l'intervalle de coexistence
                    for t in list(inter):
                        # si il y a une rencontre entre les 2 vehicules à l'instant t : ajouter 1 à la liste des rencontres :resultat(paire)
                        if isAnEncounter(world, ui.alignment.users[h], ui.alignment.users[h + 1], t, dmin):
                            result[(ui.alignment.users[h].num, ui.alignment.users[h + 1].num)].append(1)
                        # sinon : ajouter 0 à cette même liste
                        else:
                            result[(ui.alignment.users[h].num, ui.alignment.users[h + 1].num)].append(0)
        # une fois les listes complétées
        # pour chaque liste dans resultat(paire) : transformer la liste en [décompte des 1 = nombre d'interactions, longueur des interactions]
        for pair in result:
            result[pair] = [toolkit.countElementInList(result[pair], 1)] + toolkit.makeSubListFromList(result[pair], 1)
        return result

    elif not inLine:
        pass
    else:
        print('error in method name, method name should be "inline" or "crossing"')


def timeToCollisionAtInstant(user, t, world):
    if not world.crossing:
        if user.leader is not None:
            leader = user.leader
            x0 = leader.getCurvilinearPositionAtInstant(t)[0]
            v0 = leader.getCurvilinearVelocityAtInstant(t)[0]
            x1 = user.getCurvilinearPositionAtInstant(t)[0]
            v1 = user.getCurvilinearVelocityAtInstant(t)[0]
            if v1 > v0:
                ttc = (x0 - x1 - leader.geometry) / (v1 - v0)
                return ttc
        else:
            return None
    else:
        if user.leader is not None:
            leaderCP = user.leader.getCurvilinearPositionAtInstant(t)
            if leaderCP[0] > world.getControlDevicePositionOnAlignment(leaderCP[2]):
                if world.analysisZone.userInAnalysisZone(user, t):
                    t1 = world.distanceAtInstant(user, world.controlDevices[0], t)/ (user.getCurvilinearVelocityAtInstant(t)[0]/world.timeStep)
                    adjacentUser = world.checkTraffic(user, t)
                    if adjacentUser is not None :
                        if world.analysisZone.userInAnalysisZone(adjacentUser, t):
                            t2 = world.distanceAtInstant(adjacentUser, world.controlDevices[0], t)/ (adjacentUser.getCurvilinearVelocityAtInstant(t)[0]/world.timeStep)
                            return max(t1, t2)
                        else:
                            return None
                    else:
                        return None
                else:
                    return None
            else:
                return None
        else:
            t1 = world.distanceAtInstant(user, world.controlDevices[0], t)/user.getCurvilinearVelocityAtInstant(t)[0]
            adjacentUser = world.checkTraffic(user, t)
            if adjacentUser is not None:
                if world.analysisZone.userInAnalysisZone(adjacentUser, t):
                    t2 = world.distanceAtInstant(adjacentUser, world.controlDevices[0], t) / (adjacentUser.getCurvilinearVelocityAtInstant(t)[0]/world.timeStep)
                    return max(t1, t2)

def timeToCollision(user, world=None, zoneArea=None):
    ttc = []
    if world is not None and zoneArea is not None:
        analysisZone = AnalysisZone(world, zoneArea)
        world.analysisZone = analysisZone
        if user.leader is not None:
            inter = moving.TimeInterval.intersection(user.timeInterval, user.leader.timeInterval)
            for t in list(inter):
                if analysisZone.userInAnalysisZone(user, t):
                    if len(world.alignments) > 2:
                        world.crossing = True
                    else:
                        world.crossing = False
                    if timeToCollisionAtInstant(user, t, world) is not None:
                        ttc.append(timeToCollisionAtInstant(user, t, world))

        return ttc


def countConflict(threshold, interactions, seeds):
    conflictNumber = {}
    number = []
    for seed in seeds:
        for inter in interactions[seed]:
            number.append(
                len(toolkit.groupOnCriterion(interactions[seed][inter][0].indicators['Distance'].values.values(),
                                             threshold)))
        conflictNumber[seed] = np.sum(number)
    return conflictNumber


def getDistance(val, interactions, seeds):
    distance = {}  # liste des distances minimales pour chaque repetition de simulation
    if val == 'min':
        for seed in seeds:
            distance[seed] = []
            for inter in interactions[seed]:
                distance[seed].append(min(interactions[seed][inter][0].indicators['Distance'].values.values()))
            distance[seed] = np.mean(distance[seed])

    if val == 'mean':
        for seed in seeds:
            distance[seed] = []
            for inter in interactions[seed]:
                distance[seed].append(np.mean(list(interactions[seed][inter][0].indicators['Distance'].values.values())))
            distance[seed] = np.mean(distance[seed])

    return distance


def evaluateModel(world, sim, k, zoneArea=None):
    seeds = [k]
    interactions = {}
    usersCount = {}

    for seed in seeds:

        interactions[seed] = {}
        sim.seed = seed
        sim.run(world)
        usersCount[seed] = world.getNotNoneVehiclesInWorld()[0]

        for userNum in range(len(usersCount[seed]) - 1):
            roadUser1 = world.getUserByNum(userNum)
            roadUser2 = world.getUserByNum(userNum + 1)
            #                 print(len(roadUser1.curvilinearVelocities), len(roadUser2.curvilinearVelocities))
            interactions[seed][(roadUser1.num, roadUser2.num)] = []
            i = events.Interaction(useCurvilinear=True, roadUser1=roadUser1, roadUser2=roadUser2)
            i.computeDistance(world)
            # i.computeIndicators(world=world, alignment1=world.travelledAlignments(roadUser1, None),
            #                     alignment2=world.travelledAlignments(roadUser2, None))

            interactions[seed][(roadUser1.num, roadUser2.num)].append(i)
    # simulatedUsers = world.getNotNoneVehiclesInWorld()[0]

    ### TTC sur un lien ###
    TTC = {}
    TTCmin = {}

    for user in usersCount[seed]:
        ttc = timeToCollision(user, world, zoneArea)
        user0 = user.leader
        if user0 is None:
            num0 = None
        else:
            num0 = user0.num

        TTC[num0, user.num] = ttc
        if ttc != []:
            if min(TTC[num0, user.num]) < 30:
                TTCmin[num0, user.num] = min(TTC[num0, user.num])

    n, bins = np.histogram(list(TTCmin.values()))
    mids = 0.5 * (bins[1:] + bins[:-1])
    if sum(n) != 0:
        meanTTCmin = np.average(mids, weights=n)
    else:
        meanTTCmin = None

    ### nombre de conflits quand d<5, 10, 15 ###
    minDistance = getDistance('min', interactions, seed)
    meanDistance = getDistance('mean', interactions, seed)
    conflictNumber5 = countConflict(5, interactions, seeds)
    conflictNumber10 = countConflict(10, interactions, seeds)
    conflictNumber15 = countConflict(15, interactions, seeds)

    return meanTTCmin, list(minDistance.values())[0], list(meanDistance.values())[0], len(usersCount[seed]), \
           list(conflictNumber5.values())[0], list(conflictNumber10.values())[0], list(conflictNumber15.values())[0]


def plotVariations(indicatorValues, fileName, figName):
    nRep = [k for k in range(1, len(indicatorValues) + 1)]
    meanValues = [indicatorValues[0]]
    for k in range(1, len(indicatorValues)):
        meanValues.append(np.mean(indicatorValues[:k + 1]))
    plt.plot(nRep, meanValues)
    plt.title(figName)
    plt.savefig(fileName)
    plt.close('all')


def rms(indicatorValues):
    s = 0
    for el in indicatorValues:
        s += el**2
    s /= len(indicatorValues)
    s = s**.5
    return s


class AnalysisZone:
    def __init__(self, world, area):
        self.center = world.getIntersectionXYcoords()  # moving.Point
        if self.center is None:
            self.center = world.userInputs[0].alignment.points[-1]
        self.minAlignment = []
        self.maxAlignment = []
        self.area = area
        for al in world.alignments:
            if al.connectedAlignmentIndices is not None:
                self.minAlignment.append([al.points.cumulativeDistances[-1] - self.area**.5, al.idx])
            else:
                self.maxAlignment.append([self.minAlignment[-1][0] + 2*(self.area**.5), al.idx])

    def userInAnalysisZone(self, user, t):
        """determines if a user is inside a predetermined analysis zone"""
        rep = False
        if t in list(user.timeInterval):
            cp = user.getCurvilinearPositionAtInstant(t)
            for minVal, maxVal in zip(self.minAlignment, self.maxAlignment):
                if (minVal[0] <= cp[0] <= maxVal[0]) and (cp[2] == minVal[1] or cp[2] == maxVal[1]):  # or (self.minAlignment[1] <= cp <= self.maxAlignment[1]):
                    rep = True
                    break
            return rep
        else:
            return rep

