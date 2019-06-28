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

    def save(self, filename):
        toolkit.saveYaml(filename, self)

    @staticmethod
    def load(filename):
        toolkit.loadYaml(filename)

    def getInteractions(self):
        return list(self.interactions.values())

    def getInteractionsProperties(self, analysisZone=None):
        # todo : docstrings
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
            # else:
                # for item in toolkit.groupOnCriterion(self.interactions[key].getIndicators('Distance').getValues(), distance):
                #     duration.append(len(item))
                # pass

            minDistance.append(min(self.interactions[key].getIndicator('Distance').getValues()))
            meanDistance.append(np.mean(list(self.interactions[key].indicators['Distance'].getValues())))

        return minDistance, meanDistance

    def evaluate(self, seed, ttcFilter):
        # todo : docstrings
        self.interactions = {}
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
            if len(self.interactions[key].getIndicator('Time to Collision').getValues()) > 0:
                value = self.interactions[key].getIndicator('Time to Collision').getMostSevereValue(minNInstants=1)
                if ttcFilter is not None:
                    if value <= ttcFilter:
                        minTTCValues.append(value)
                    else:
                        minTTCValues.append(None)
                else:
                    minTTCValues.append(value)
            else:
                minTTCValues.append(None)

        user1Nums = [i[0] for i in list(self.interactions.keys())]
        user2Nums = [i[1] for i in list(self.interactions.keys())]

        minDistances, meanDistances = self.getInteractionsProperties()     # getting the number and duration of interactions for a distance of 5m

        return [seed]*len(user1Nums), user1Nums, user2Nums, minTTCValues, minDistances, meanDistances

    @staticmethod
    def store(evaluationOutput):
        df = pd.DataFrame({'seed':evaluationOutput[0], 'roadUser1Num':evaluationOutput[1], 'roadUserNum2':evaluationOutput[2], 'TTCmin':evaluationOutput[3], 'distmin':evaluationOutput[4], 'distmean':evaluationOutput[5]})
        try:
            df.to_csv('evaluation.csv', mode='a', header=False)
        except:
            df.to_csv('evaluation.csv')
            print('File has been created')

    def plotDistanceForUserPair(self, user1Num, user2Num):
        """script to plot distance between a pair of vehicles"""
        distances = self.getUserPairIndicatorValues(user1Num, user2Num, 'Distance')
        time = self.getUserPairIndicatorInstants(user1Num, user2Num, 'Distance')
        plt.plot(time, distances)

    def getUserPairIndicatorValues(self, user1Num, user2Num, indicatorName):
        return self.getUserPairIndicator(user1Num, user2Num, indicatorName).getValues()

    def getUserPairIndicatorInstants(self, user1Num, user2Num, indicatorName):
        return self.getUserPairIndicator(user1Num, user2Num, indicatorName).getKeys()

    def getUserPairIndicator(self, user1Num, user2Num, indicatorName):
        return self.interactions[(user1Num, user2Num)].getIndicator(indicatorName)

    def saveIndicators(self, fileName):
        storage.saveIndicatorsToSqlite(fileName, self.getInteractions())


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
