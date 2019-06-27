import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from trafficintelligence import storage

import events
import toolkit


class Analysis:
    def __init__(self, world, analysisZone=None):
        self.world = world
        self.interactions = {}
        self.analysisZone = analysisZone

    def getInteractionsProperties(self, distance, analysisZone=None, computeDistanceDict=False):
        # todo : docstrings
        number = []
        duration = []
        minDistance = []
        meanDistance = []
        for key in self.interactions:
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
                number.append(len(toolkit.groupOnCriterion(self.interactions[key].indicators['Distance'].values.values(), distance)))
                for item in toolkit.groupOnCriterion(self.interactions[key].indicators['Distance'].values.values(), distance):
                    duration.append(len(item))

            if computeDistanceDict:
                minDistance.append(min(self.interactions[key].indicators['Distance'].values.values()))
                meanDistance.append(np.mean(list(self.interactions[key].indicators['Distance'].values.values())))

        return minDistance, meanDistance, np.sum(number), duration

    def evaluate(self):
        # todo : docstrings
        for user in self.world.completed:  # + self.world.users:  # computing indicators : distance and ttc, for each pair of vehicles in a CF situation
            if user.leader is not None:
                roadUser1 = user.leader
                roadUser2 = user
                if roadUser2.timeInterval is not None:
                    i = events.Interaction(num=user.num-1, roadUser1=roadUser1, roadUser2=roadUser2, useCurvilinear=True)
                    i.computeDistance(self.world)
                    i.computeTTC()
                    self.interactions[(roadUser1.num, roadUser2.num)] = i

        minTTCValues = []

        for key in self.interactions:
            if len(self.interactions[key].indicators['Time to Collision'].values.values()) > 0 and min(self.interactions[key].indicators['Time to Collision'].values.values()) < 20:  # 20 : valeur seuil pour le ttc a placer en parametre
                minTTCValues.append(min(self.interactions[key].indicators['Time to Collision'].values.values()))

        # parametres 5, 10, 15 a passer en parametres
        minDistanceList, meanDistanceList, nInter5, interDuration5 = self.getInteractionsProperties(5, computeDistanceDict=True)     # getting the number and duration of interactions for a distance of 5m
        _, _, nInter10, interDuration10 = self.getInteractionsProperties(10)  # getting the number and duration of interactions for a distance of 10m
        _, _, nInter15, interDuration15 = self.getInteractionsProperties(15)  # getting the number and duration of interactions for a distance of 15m

        ttcData = pd.DataFrame(minTTCValues, columns=['TTC'])
        minDistanceData = pd.DataFrame(minDistanceList, columns=['minDistance'])
        meanDistanceData = pd.DataFrame(meanDistanceList, columns=['meanDistance'])
        interactionNumber = pd.DataFrame([nInter5, nInter10, nInter15], columns=['interaction number'])
        interactionDuration = pd.DataFrame([interDuration5, interDuration10, interDuration15]).transpose()

        ttcData.to_csv('outputData/single-evaluations/ttc/data-headway{}.csv'.format(self.world.userInputs[0].distributions['headway'].scale + 1))
        minDistanceData.to_csv('outputData/single-evaluations/minDistance/data-headway{}.csv'.format(self.world.userInputs[0].distributions['headway'].scale + 1))
        meanDistanceData.to_csv('outputData/single-evaluations/meanDistance/data-headway{}.csv'.format(self.world.userInputs[0].distributions['headway'].scale + 1))
        interactionNumber.to_csv('outputData/single-evaluations/interaction-number/data-headway{}.csv'.format(self.world.userInputs[0].distributions['headway'].scale + 1))
        interactionDuration.to_csv('outputData/single-evaluations/interaction-duration/data-headway{}.csv'.format(self.world.userInputs[0].distributions['headway'].scale + 1))

        return minTTCValues, minDistanceList, meanDistanceList, [nInter5], [nInter10], [nInter15], interDuration5, interDuration10, interDuration15

    def plotDistanceForUserPair(self, user1Num, user2Num):
        """script to plot distance between a pair of vehicles"""
        distances = list(self.getUserPairIndicatorValues(user1Num, user2Num, 'Distance'))
        time = list(self.getUserPairIndicatorInstants(user1Num, user2Num, 'Distance'))
        plt.plot(time, distances)

    def getUserPairIndicatorValues(self, user1Num, user2Num, indicatorName):
        return self.getUserPairIndicator(user1Num, user2Num, indicatorName).values.values()

    def getUserPairIndicatorInstants(self, user1Num, user2Num, indicatorName):
        return self.getUserPairIndicator(user1Num, user2Num, indicatorName).values.keys()

    def getUserPairIndicator(self, user1Num, user2Num, indicatorName):
        return self.interactions[(user1Num, user2Num)].getIndicator(indicatorName)

    def saveIndicatorsToTable(self, fileName):
        storage.saveIndicatorsToSqlite(fileName, list(self.interactions.values()))


class AnalysisZone:
    def __init__(self, world, area):
        self.center = world.getIntersectionXYcoords()  # moving.Point
        if self.center is None:
            self.center = world.alignments[world.userInputs[0].alignmentIdx].points[-1]
        self.minAlignment = []
        self.maxAlignment = []
        self.area = area
        for al in world.alignments:
            if al.connectedAlignmentIndices is not None:
                self.minAlignment.append([al.getTotalDistance() - self.area ** .5, al.idx])
            else:
                self.maxAlignment.append([self.minAlignment[-1][0] + 2 * (self.area ** .5), al.idx])

    def getLimits(self):
        return self.minAlignment, self.maxAlignment

    def getArea(self):
        return self.area

    def getCenter(self):
        return self.center

    def userInAnalysisZone(self, user, t):
        """determines if a user is inside a predetermined analysis zone"""
        if t in list(user.timeInterval):
            cp = user.getCurvilinearPositionAtInstant(t)
            for minVal, maxVal in zip(self.minAlignment, self.maxAlignment):
                if (minVal[0] <= cp[0] and cp[2] == minVal[1]) or (cp[0] <= maxVal[0] - user.getTravelledDistance(minVal[1], maxVal[1]) and cp[2] == maxVal[1]):
                    return True
            return False
