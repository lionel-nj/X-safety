import sqlite3

from trafficintelligence import moving
from trafficintelligence.storage import printDBError

import events
import toolkit


class Analysis:
    def __init__(self, idx, world, seed, analysisZone=None):
        self.idx = idx
        self.world = world
        # self.interactions = world.completedInteractions
        self.analysisZone = analysisZone
        self.seed = seed

    def getIdx(self):
        return self.idx

    def save(self, filename):
        toolkit.saveYaml(filename, self)

    @staticmethod
    def load(filename):
        toolkit.loadYaml(filename)

    def getAnalysisZoneArea(self):
        if self.analysisZone is None:
            return None
        else:
            return self.analysisZone.getArea()

    def getInteractions(self):
        return self.interactions

    # def evaluate(self, timeStep, duration, analysisZone=None):
    #     # todo : docstrings
    #     self.interactions = {}
    #     idx = 0
    #     for user in self.world.completed + self.world.users:  # computing indicators : distance and ttc, for each pair of vehicles in a CF situation
    #         idx += 1
    #         if user.leader is not None:
    #             roadUser1 = user.leader
    #             roadUser2 = user
    #             if roadUser2.timeInterval is not None:
    #                 i = events.Interaction(num=idx, roadUser1=roadUser1, roadUser2=roadUser2, useCurvilinear=True)
    #                 i.computeDistance(self.world, analysisZone)
    #                 i.computeTTC(timeStep, 20, analysisZone)
    #                 self.interactions[(roadUser1.num, roadUser2.num)] = i
    #
    #     idx += 1
    #
    #     crossingInteractions = []
    #     for t in range(int(np.floor(duration / timeStep))):
    #         user, crossingUser = self.world.getCrossingPairAtInstant(t)
    #         if user is not None and crossingUser is not None:
    #             if not ((user.num, crossingUser.num) in self.interactions):
    #                 idx += 1
    #                 i = events.Interaction(num=idx, roadUser1=user, roadUser2=crossingUser, useCurvilinear=True)
    #                 i.addIndicator(indicators.SeverityIndicator('Time to Collision', {}, mostSevereIsMax=False))
    #                 i.addIndicator(indicators.SeverityIndicator('Distance', {}, mostSevereIsMax=False))
    #                 self.interactions[(user.num, crossingUser.num)] = i
    #                 crossingInteractions.append(i)
    #             else:
    #                 i = self.interactions[(user.num, crossingUser.num)]
    #
    #             i.computeTTCAtInstant(self.world, timeStep, t, 20, 0, analysisZone)
    #
    #     for inter in crossingInteractions:
    #        inter.computeDistance(self.world, analysisZone)
    #        inter.computePETAtInstant(self.world, timeStep)

    def saveIndicators(self, fileName):
        self.saveIndicatorsToSqlite(fileName, self.getInteractions())

    def saveParametersToTable(self, fileName):
        connection = sqlite3.connect(fileName)
        cursor = connection.cursor()
        for ui in self.world.userInputs:
            values = [self.idx, self.getAnalysisZoneArea(), ui.idx]
            for distribution in ui.distributions:
                dist = ui.distributions[distribution]
                values.extend([dist.getType(), dist.getName(), dist.getLoc(), dist.getScale(), dist.getMinThreshold(), dist.getMaxThreshold(), dist.getCdf()])
            query = "INSERT INTO analysis VALUES("+"?,"*len(values)
            query = query[:-1]
            query += ")"
            cursor.execute(query, values)
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
        cursor.execute('CREATE TABLE IF NOT EXISTS interactions (id INTEGER, analysis_id INTEGER, seed INTEGER, object_id1 INTEGER, object_id2 INTEGER, first_frame_number INTEGER, last_frame_number INTEGER, FOREIGN KEY(object_id1) REFERENCES objects(id), PRIMARY KEY(id, analysis_id, seed), FOREIGN KEY(object_id2) REFERENCES objects(id))')

    def createIndicatorTable(self, cursor):
        cursor.execute('CREATE TABLE IF NOT EXISTS indicators (interaction_id INTEGER, analysis_id INTEGER, seed INTEGER, indicator_type INTEGER, frame_number INTEGER, value REAL, FOREIGN KEY(interaction_id) REFERENCES interactions(id), PRIMARY KEY(interaction_id, analysis_id, seed, indicator_type, frame_number))')

    def saveInteraction(self, cursor, interaction):
        roadUserNumbers = list(interaction.getRoadUserNumbers())
        # category = interaction.categoryNum
        cursor.execute('INSERT INTO interactions VALUES({}, {}, {}, {}, {}, {}, {})'.format(interaction.getNum(), self.idx, self.seed, roadUserNumbers[0], roadUserNumbers[1], interaction.getFirstInstant(), interaction.getLastInstant()))

    def saveIndicator(self, cursor, interactionNum, indicator):
        for instant in indicator.getTimeInterval():
            if indicator[instant]:
                cursor.execute('INSERT INTO indicators VALUES({}, {}, {}, {}, {}, {})'.format(interactionNum, self.idx, self.seed, events.Interaction.indicatorNameToIndices[indicator.getName()], instant, indicator[instant]))


class AnalysisZone:
    def __init__(self, intersection, area):
        self.intersection = intersection  # moving.Point
        self.minAlignment = []
        self.maxAlignment = []
        self.area = area
        for entryAlignment in intersection.entryAlignments:
            self.minAlignment.append([entryAlignment.getTotalDistance() - self.area ** .5, entryAlignment.idx])
        for exitAlignment in intersection.exitAlignments:
            self.maxAlignment.append([self.area ** .5, exitAlignment.idx])

    def getLimits(self):
        """return limits of analysis zone"""
        return self.minAlignment, self.maxAlignment

    def getArea(self):
        """returns area of analysis zone"""
        return self.area

    def getIntersection(self):
        """returns center of analysis zone"""
        return self.intersection

    def userInAnalysisZoneAtInstant(self, user, t):
        """determines if a user is inside a predetermined analysis zone"""
        if t in list(user.timeInterval):
            cp = user.getCurvilinearPositionAtInstant(t)
            for minVal, maxVal in zip(self.minAlignment, self.maxAlignment):
                if (minVal[0] <= cp[0] and cp[2] == minVal[1]) or (cp[0] <= maxVal[0] and cp[2] == maxVal[1]):
                    return True
            return False

    def positionInAnalysisZone(self, curvilinearPosition):
        for minVal, maxVal in zip(self.minAlignment, self.maxAlignment):
            if (minVal[0] <= curvilinearPosition[0] and curvilinearPosition[2] == minVal[1]) or (curvilinearPosition[0] <= maxVal[0] and curvilinearPosition[2] == maxVal[1]):
                return True
        return False

    def getUserIntervalInAnalysisZone(self, user):
        firstInstant = None
        lastInstant = None
        for t in list(user.timeInterval):
            if self.userInAnalysisZoneAtInstant(user, t):
                firstInstant = t
                break
        if firstInstant is None:
            return None
        else:
            for instant in range(firstInstant, user.getLastInstant() + 1):
                if not self.userInAnalysisZoneAtInstant(user, instant):
                    lastInstant = instant - 1
                    break
            if lastInstant is None:
                lastInstant = user.getLastInstant()
            return moving.TimeInterval(firstInstant, lastInstant)


def createAnalysisTable(fileName):
    connection = sqlite3.connect(fileName)
    cursor = connection.cursor()
    tableName = 'analysis'
    cursor.execute("CREATE TABLE IF NOT EXISTS " + tableName + " (analysis_id INTEGER, area REAL, userInput_id INTEGER, deltaDistribution_type TEXT, deltaDistribution_name TEXT, deltaDistribution_loc REAL, deltaDistribution_scale REAL, deltaDistribution_a REAL, deltaDistribution_b REAL, deltaDistribution_cdf LIST, headwayDistribution_type TEXT, headwayDistribution_name TEXT, headwayDistribution_loc REAL, headwayDistribution_scale REAL, headwayDistribution_a REAL, headwayDistribution_b REAL, headwayDistribution_cdf LIST, geometryDistribution_type TEXT, geometryDistribution_name TEXT, geometryDistribution_loc REAL, geometryDistribution_scale REAL, geometryDistribution_a REAL, geometryDistribution_b REAL, geometryDistribution_cdf LIST, speedDistribution_type TEXT, speedDistribution_name TEXT, speedDistribution_loc REAL, speedDistribution_scale REAL, speedDistribution_a REAL, speedDistribution_b REAL, speedDistribution_cdf LIST, tauDistribution_type TEXT, tauDistribution_name TEXT, tauDistribution_loc REAL, tauDistribution_scale REAL, tauDistribution_a REAL, tauDistribution_b REAL, tauDistribution_cdf LIST, criticalGapDistribution_type TEXT, criticalGapDistribution_name TEXT, criticalGapDistribution_loc REAL, criticalGapDistribution_scale REAL, criticalGapDistribution_a REAL, criticalGapDistribution_b REAL, criticalGapDistribution_cdf LIST, PRIMARY KEY(analysis_id, area, userInput_id))")
    connection.commit()