import sqlite3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from trafficintelligence.storage import printDBError

import events
import toolkit


class Analysis:
    def __init__(self, idx, world, analysisZone=None):
        self.idx = idx
        self.world = world
        self.interactions = {}
        self.analysisZone = analysisZone

    def getIdx(self):
        return self.idx

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
                    i = events.Interaction(num=user.num - 1, roadUser1=roadUser1, roadUser2=roadUser2, useCurvilinear=True)
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

        minDistances, meanDistances = self.getInteractionsProperties()  # getting the number and duration of interactions for a distance of 5m

        return [seed] * len(user1Nums), user1Nums, user2Nums, minTTCValues, minDistances, meanDistances

    @staticmethod
    def store(evaluationOutput):
        df = pd.DataFrame({'seed': evaluationOutput[0], 'roadUser1Num': evaluationOutput[1], 'roadUserNum2': evaluationOutput[2], 'TTCmin': evaluationOutput[3], 'distmin': evaluationOutput[4], 'distmean': evaluationOutput[5]})
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
        self.saveIndicatorsToSqlite(fileName, self.getInteractions())

    def saveParametersToTable(self, fileName):
        connection = sqlite3.connect(fileName)
        cursor = connection.cursor()
        for ui in self.world.userInputs:
            values = [self.idx, ui.idx]
            for distribution in ui.distributions:
                dist = ui.distributions[distribution]
                values.extend([dist.getType(), dist.getName(), dist.getLoc(), dist.getScale(), dist.getMinThreshold(), dist.getMaxThreshold(), dist.getCdf()])
            query = "INSERT INTO analysis VALUES("+"?,"*len(values)
            query = query[:-1]
            query += ")"
            cursor.execute(query, values)#, values[1], values[2], values[3], values[4], values[5], values[6], values[7], values[8]))
        connection.commit()

    def createAnalysisTable(self, fileName):
        connection = sqlite3.connect(fileName)
        cursor = connection.cursor()
        tableName = 'analysis'
        cursor.execute("CREATE TABLE IF NOT EXISTS " + tableName + " (analysis_id INTEGER, userInput_id INTEGER, headwayDistribution_type TEXT, headwayDistribution_name TEXT, headwayDistribution_loc REAL, headwayDistribution_scale REAL, headwayDistribution_a REAL, headwayDistribution_b REAL, headwayDistribution_cdf LIST, speedDistribution_type TEXT, speedDistribution_name TEXT, speedDistribution_loc REAL, speedDistribution_scale REAL, speedDistribution_a REAL, speedDistribution_b REAL, speedDistribution_cdf LIST, tauDistribution_type TEXT, tauDistribution_name TEXT, tauDistribution_loc REAL, tauDistribution_scale REAL, tauDistribution_a REAL, tauDistribution_b REAL, tauDistribution_cdf LIST, deltaDistribution_type TEXT, deltaDistribution_name TEXT, deltaDistribution_loc REAL, deltaDistribution_scale REAL, deltaDistribution_a REAL, deltaDistribution_b REAL, deltaDistribution_cdf LIST, criticalGapDistribution_type TEXT, criticalGapDistribution_name TEXT, criticalGapDistribution_loc REAL, criticalGapDistribution_scale REAL, criticalGapDistribution_a REAL, criticalGapDistribution_b REAL, criticalGapDistribution_cdf LIST, geometryDistribution_type TEXT, geometryDistribution_name TEXT, geometryDistribution_loc REAL, geometryDistribution_scale REAL, geometryDistribution_a REAL, geometryDistribution_b REAL, geometryDistribution_cdf LIST, amberDistribution_type TEXT, amberDistribution__name TEXT, amberDistribution_loc REAL, amberDistribution_scale REAL, amberDistribution_a REAL,amberDistribution_b REAL, amberDistribution_cdf LIST, PRIMARY KEY(analysis_id))")
        connection.commit()

    def saveIndicatorsToSqlite(self, filename, interactions, indicatorNames=events.Interaction.indicatorNames):
        'Saves the indicator values in the table'
        with sqlite3.connect(filename) as connection:
            cursor = connection.cursor()
            try:
                self.createInteractionTable(cursor)
                self.createIndicatorTable(cursor)
                for inter in interactions:
                    self.saveInteraction(cursor, inter)
                    for indicatorName in indicatorNames:
                        indicator = inter.getIndicator(indicatorName)
                        if indicator is not None:
                           self.saveIndicator(cursor, inter.getNum(), indicator)
            except sqlite3.OperationalError as error:
                printDBError(error)
            connection.commit()

    def createInteractionTable(self, cursor):
        cursor.execute('CREATE TABLE IF NOT EXISTS interactions (id INTEGER PRIMARY KEY, analysis_id INTEGER, object_id1 INTEGER, object_id2 INTEGER, first_frame_number INTEGER, last_frame_number INTEGER, FOREIGN KEY(object_id1) REFERENCES objects(id), FOREIGN KEY(object_id2) REFERENCES objects(id))')

    def createIndicatorTable(self, cursor):
        cursor.execute('CREATE TABLE IF NOT EXISTS indicators (interaction_id INTEGER, analysis_id INTEGER, indicator_type INTEGER, frame_number INTEGER, value REAL, FOREIGN KEY(interaction_id) REFERENCES interactions(id), PRIMARY KEY(interaction_id, indicator_type, frame_number))')

    def saveInteraction(self, cursor, interaction):
        roadUserNumbers = list(interaction.getRoadUserNumbers())
        cursor.execute('INSERT INTO interactions VALUES({}, {}, {}, {}, {}, {})'.format(interaction.getNum(), self.idx, roadUserNumbers[0], roadUserNumbers[1], interaction.getFirstInstant(), interaction.getLastInstant()))

    def saveIndicator(self, cursor, interactionNum, indicator):
        for instant in indicator.getTimeInterval():
            if indicator[instant]:
                cursor.execute('INSERT INTO indicators VALUES({}, {}, {}, {}, {})'.format(interactionNum, self.idx, events.Interaction.indicatorNameToIndices[indicator.getName()], instant, indicator[instant]))


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

