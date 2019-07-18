#! /usr/bin/env python
'''Libraries for events
Interactions, pedestrian crossing...'''

from trafficintelligence import moving, prediction, indicators, utils, cvutils, ml
from trafficintelligence.base import VideoFilenameAddable


def findRoute(prototypes, objects, i, j, noiseEntryNums, noiseExitNums, minSimilarity=0.3, spatialThreshold=1.0,
              delta=180):
    if i[0] not in noiseEntryNums:
        prototypesRoutes = [x for x in sorted(prototypes.keys()) if i[0] == x[0]]
    elif i[1] not in noiseExitNums:
        prototypesRoutes = [x for x in sorted(prototypes.keys()) if i[1] == x[1]]
    else:
        prototypesRoutes = [x for x in sorted(prototypes.keys())]
    routeSim = {}
    lcss = utils.LCSS(similarityFunc=lambda x, y: (distanceForLCSS(x, y) <= spatialThreshold), delta=delta)
    for y in prototypesRoutes:
        if y in prototypes:
            prototypesIDs = prototypes[y]
            similarity = []
            for x in prototypesIDs:
                s = lcss.computeNormalized(objects[j].positions, objects[x].positions)
                similarity.append(s)
            routeSim[y] = max(similarity)
    route = max(routeSim, key=routeSim.get)
    if routeSim[route] >= minSimilarity:
        return route
    else:
        return i


def getRoute(obj, prototypes, objects, noiseEntryNums, noiseExitNums, useDestination=True):
    route = (obj.startRouteID, obj.endRouteID)
    if useDestination:
        if route not in prototypes:
            route = findRoute(prototypes, objects, route, obj.getNum(), noiseEntryNums, noiseExitNums)
    return route


class Interaction(moving.STObject, VideoFilenameAddable):
    '''Class for an interaction between two road users
    or a road user and an obstacle

    link to the moving objects
    contains the indicators in a dictionary with the names as keys
    '''

    categories = {'Head On': 0,
                  'rearend': 1,
                  'side': 2,
                  'parallel': 3}

    indicatorNames = ['Collision Course Dot Product',
                      'Collision Course Angle',
                      'Distance',
                      'Minimum Distance',
                      'Velocity Angle',
                      'Speed Differential',
                      'Collision Probability',
                      'Time to Collision',  # 7
                      'Probability of Successful Evasive Action',
                      'predicted Post Encroachment Time',
                      'Post Encroachment Time']

    indicatorNameToIndices = utils.inverseEnumeration(indicatorNames)

    indicatorShortNames = ['CCDP',
                           'CCA',
                           'Dist',
                           'MinDist',
                           'VA',
                           'SD',
                           'PoC',
                           'TTC',
                           'P(SEA)',
                           'pPET',
                           'PET']

    indicatorUnits = ['',
                      'rad',
                      'm',
                      'm',
                      'rad',
                      'm/s',
                      '',
                      's',
                      '',
                      's',
                      's']

    timeIndicators = ['Time to Collision', 'predicted Post Encroachment Time']

    def __init__(self, useCurvilinear, num=None, timeInterval=None, roaduserNum1=None, roaduserNum2=None, roadUser1=None, roadUser2=None, categoryNum=None):
        moving.STObject.__init__(self, num, timeInterval)
        if timeInterval is None and roadUser1 is not None and roadUser2 is not None:
            self.timeInterval = roadUser1.commonTimeInterval(roadUser2)
        self.roadUser1 = roadUser1
        self.roadUser2 = roadUser2
        if roaduserNum1 is not None and roaduserNum2 is not None:
            self.roadUserNumbers = set([roaduserNum1, roaduserNum2])
        elif roadUser1 is not None and roadUser2 is not None:
            self.roadUserNumbers = set([roadUser1.getNum(), roadUser2.getNum()])
        else:
            self.roadUserNumbers = None
        self.categoryNum = categoryNum
        self.indicators = {}
        self.interactionInterval = None
        # list for collison points and crossing zones
        self.collisionPoints = None
        self.crossingZones = None
        self.useCurvilinear = useCurvilinear

    def getRoadUserNumbers(self):
        return self.roadUserNumbers

    def setRoadUsers(self, objects):
        nums = sorted(list(self.getRoadUserNumbers()))
        if nums[0] < len(objects) and objects[nums[0]].getNum() == nums[0]:
            self.roadUser1 = objects[nums[0]]
        if nums[1] < len(objects) and objects[nums[1]].getNum() == nums[1]:
            self.roadUser2 = objects[nums[1]]

        if self.roadUser1 is None or self.roadUser2 is None:
            self.roadUser1 = None
            self.roadUser2 = None
            i = 0
            while i < len(objects) and self.roadUser2 is None:
                if objects[i].getNum() in nums:
                    if self.roadUser1 is None:
                        self.roadUser1 = objects[i]
                    else:
                        self.roadUser2 = objects[i]
                i += 1

    def getIndicator(self, indicatorName):
        return self.indicators.get(indicatorName, None)

    def addIndicator(self, indicator):
        if indicator is not None:
            self.indicators[indicator.name] = indicator

    def getIndicatorValueAtInstant(self, indicatorName, instant):
        indicator = self.getIndicator(indicatorName)
        if indicator is not None:
            return indicator[instant]
        else:
            return None

    def updateTimeInterval(self):
        self.timeInterval = self.roadUser1.commonTimeInterval(self.roadUser2)

    def getIndicatorValuesAtInstant(self, instant):
        '''Returns list of indicator values at instant
        as dict (with keys from indicators dict)'''
        values = {}
        for k, indicator in self.indicators.items():
            values[k] = indicator[instant]
        return values

    def getIndicatorValuesInTimeInterval(self, timeInterval, indicatorName):
        # todo : verifier
        values = []
        for instant in list(timeInterval):
            values.append(self.getIndicatorValueAtInstant(indicatorName, instant))
        return values

    def plot(self, options='', withOrigin=False, timeStep=1, withFeatures=False, **kwargs):
        self.roadUser1.plot(options, withOrigin, timeStep, withFeatures, **kwargs)
        self.roadUser2.plot(options, withOrigin, timeStep, withFeatures, **kwargs)

    def plotOnWorldImage(self, nPixelsPerUnitDistance, options='', withOrigin=False, timeStep=1, **kwargs):
        self.roadUser1.plotOnWorldImage(nPixelsPerUnitDistance, options, withOrigin, timeStep, **kwargs)
        self.roadUser2.plotOnWorldImage(nPixelsPerUnitDistance, options, withOrigin, timeStep, **kwargs)

    def play(self, videoFilename, homography=None, undistort=False, intrinsicCameraMatrix=None,
             distortionCoefficients=None, undistortedImageMultiplication=1., allUserInstants=False):
        if self.roadUser1 is not None and self.roadUser2 is not None:
            if allUserInstants:
                firstFrameNum = min(self.roadUser1.getFirstInstant(), self.roadUser2.getFirstInstant())
                lastFrameNum = max(self.roadUser1.getLastInstant(), self.roadUser2.getLastInstant())
            else:
                firstFrameNum = self.getFirstInstant()
                lastFrameNum = self.getLastInstant()
            cvutils.displayTrajectories(videoFilename, [self.roadUser1, self.roadUser2], homography=homography,
                                        firstFrameNum=firstFrameNum, lastFrameNumArg=lastFrameNum, undistort=undistort,
                                        intrinsicCameraMatrix=intrinsicCameraMatrix,
                                        distortionCoefficients=distortionCoefficients,
                                        undistortedImageMultiplication=undistortedImageMultiplication)
        else:
            print(
                'Please set the interaction road user attributes roadUser1 and roadUser1 through the method setRoadUsers')

    def getUsersSituation(self, world, instant):
        if instant in list(self.roadUser1.timeInterval) and instant in list(self.roadUser2.timeInterval):
            p1 = self.roadUser1.getCurvilinearPositionAtInstant(instant)
            p2 = self.roadUser2.getCurvilinearPositionAtInstant(instant)

            if p1[2] == p2[2]:
                return 'CF'
            elif (self.roadUser1.leader is not None and self.roadUser1.leader.num == self.roadUser2.num) or (self.roadUser2.leader is not None and self.roadUser1.num == self.roadUser2.leader.num):
                return 'CF'
            elif world.alignments[p2[2]].transversalAlignments is not None:
                if world.alignments[p1[2]] in world.alignments[p2[2]].transversalAlignments:
                    return 'X'

    def computeDistance(self, world, instant, analysisZone=None):
        if self.getIndicator('Distance') is None:
            self.addIndicator(indicators.SeverityIndicator(Interaction.indicatorNames[2], {}, mostSevereIsMax=False))

        situation = self.getUsersSituation(world, instant)
        if situation == 'CF' or situation == 'X':
            if analysisZone is None:
                distance = world.distanceAtInstant(self.roadUser1, self.roadUser2, instant, situation=situation, method='euclidian')
                self.getIndicator('Distance').values[instant] = distance
            else:
                if analysisZone.userInAnalysisZoneAtInstant(self.roadUser1, instant) and analysisZone.userInAnalysisZoneAtInstant(self.roadUser2, instant):
                    distance = world.distanceAtInstant(self.roadUser1, self.roadUser2, instant, situation=situation, method='euclidian')
                    self.getIndicator('Distance').values[instant] = distance

    def computeTTCAtInstant(self, world, timeStep, instant, maxValue, buffer=0, analysisZone=None):
        crossingPoints = world.getNodesFromCrossingPoints(self.roadUser1, self.roadUser2, instant)[0]
        if crossingPoints is not None:

            v1 = self.roadUser1.getCurvilinearVelocityAtInstant(instant)[0] / timeStep
            v2 = self.roadUser2.getCurvilinearVelocityAtInstant(instant)[0] / timeStep

            if v1 > 0 and v2 > 0:

                d1 = world.distanceToCrossingAtInstant(self.roadUser1, self.roadUser2, instant)
                d2 = world.distanceToCrossingAtInstant(self.roadUser2, self.roadUser1, instant)
                t1 = moving.Interval(d1 / v1, (d1 + self.roadUser1.geometry + buffer) / v1)
                t2 = moving.Interval(d2 / v2, (d2 + self.roadUser2.geometry + buffer) / v2)

                if moving.Interval.intersection(t1, t2).first <= moving.Interval.intersection(t1, t2).last:
                    ttc = min(t1.first, t2.first)
                    if ttc <= maxValue:
                        if analysisZone is None:
                            self.getIndicator('Time to Collision').values[instant] = ttc
                        else:
                            if analysisZone.userInAnalysisZoneAtInstant(self.roadUser1, instant) and analysisZone.userInAnalysisZoneAtInstant(self.roadUser2, instant):
                                self.getIndicator('Time to Collision').values[instant] = ttc

    def computeTTC(self, timeStep, maxValue, analysisZone=None):
        ttc = {}
        for instant in self.timeInterval:
            self.roadUser1, self.roadUser2 = self.roadUser1.orderUsersByPositionAtInstant(self.roadUser2, instant)
            if len(self.roadUser1.curvilinearVelocities) > 0 and len(self.roadUser2.curvilinearVelocities) > 0:
                v1 = self.roadUser1.getCurvilinearVelocityAtInstant(instant)[0] / timeStep
                v2 = self.roadUser2.getCurvilinearVelocityAtInstant(instant)[0] / timeStep
                if v2 > v1:
                    if analysisZone is None:
                        value = self.indicators['Distance'].values[instant] / (v2 - v1)
                        if value <= maxValue:
                            # if analysisZone is None:
                            ttc[instant] = self.indicators['Distance'].values[instant] / (v2 - v1)
                    else:
                        if analysisZone.userInAnalysisZoneAtInstant(self.roadUser1, instant) and analysisZone.userInAnalysisZoneAtInstant(self.roadUser2, instant):
                            value = self.indicators['Distance'].values[instant] / (v2 - v1)
                            if value <= maxValue:
                                ttc[instant] = self.indicators['Distance'].values[instant] / (v2 - v1)

        self.addIndicator(indicators.SeverityIndicator(Interaction.indicatorNames[7], ttc, mostSevereIsMax=False))

    def computePETAtInstant(self, world, timeStep):
        instant = self.timeInterval.first
        pet = {}
        crossingPoints = world.getCrossingPointCurvilinearPosition(self.roadUser1, self.roadUser2, instant=instant)
        if crossingPoints is not None:
            roadUser1, roadUser2 = self.roadUser1.orderUsersByDistanceToPointAtInstant(world, self.roadUser2, instant)
            for cp in crossingPoints:
                if cp[2] == roadUser1.getCurvilinearPositionAtInstant(instant)[2]:
                    cp1 = cp
                if cp[2] == roadUser2.getCurvilinearPositionAtInstant(instant)[2]:
                    cp2 = cp
            t1 = roadUser1.getInstantAtCurvilinearPosition(cp1)
            t2 = roadUser2.getInstantAtCurvilinearPosition(cp2)
            if t1 is not None and t2 is not None:
                pet[instant] = abs(t1 - t2) * timeStep
        self.addIndicator(indicators.SeverityIndicator(Interaction.indicatorNames[10], pet, mostSevereIsMax=False))

    # @staticmethod
    # def computePET(obj1, obj2, collisionDistanceThreshold):
    #     '''Post-encroachment time based on distance threshold
    #
    #     Returns the smallest time difference when the object positions are within collisionDistanceThreshold
    #     and the instants at which each object is passing through its corresponding position'''
    #
    #     obj1.positions =
    #     obj2.positions =
    #     positions1 = [p.astuple() for p in obj1.getPositions()]
    #     positions2 = [p.astuple() for p in obj2.getPositions()]
    #     n1 = len(positions1)
    #     n2 = len(positions2)
    #     pets = zeros((n1, n2))
    #     for i, t1 in enumerate(obj1.getTimeInterval()):
    #         for j, t2 in enumerate(obj2.getTimeInterval()):
    #             pets[i, j] = abs(t1 - t2)
    #     distances = cdist(positions1, positions2, metric='euclidean')
    #     smallDistances = (distances <= collisionDistanceThreshold)
    #     if smallDistances.any():
    #         smallPets = pets[smallDistances]
    #         petIdx = smallPets.argmin()
    #         distanceIndices = np.argwhere(smallDistances)[petIdx]
    #         return smallPets[petIdx], obj1.getFirstInstant() + distanceIndices[0], obj2.getFirstInstant() + distanceIndices[1]
    #     else:
    #         return None, None, None


    # def computeIndicators(self, world=None, alignment1=None, alignment2=None):
    #     '''Computes the collision course cosine only if the cosine is positive'''
    #     collisionCourseDotProducts = {}  # [0]*int(self.timeInterval.length())
    #     collisionCourseAngles = {}
    #     velocityAngles = {}
    #     distances = {}  # [0]*int(self.timeInterval.length())
    #     speedDifferentials = {}
    #     interactionInstants = []
    #     for instant in self.timeInterval:
    #         if self.useCurvilinear:
                # p1 = moving.getXYfromSY(world.getUserDistanceOnAlignmentAt(self.roadUser1, instant),
                #                         self.roadUser1.getCurvilinearPositionAtInstant(instant)[1],
                #                         utils._set(self.roadUser1.curvilinearPositions.lanes).index(self.roadUser1.getCurvilinearPositionAtInstant(instant)[2]),
                #                         alignment1)
                #
                # p2 = moving.getXYfromSY(world.getUserDistanceOnAlignmentAt(self.roadUser2, instant),
                #                         self.roadUser2.getCurvilinearPositionAtInstant(instant)[1],
                #                         utils._set(self.roadUser2.curvilinearPositions.lanes).index(self.roadUser2.getCurvilinearPositionAtInstant(instant)[2]),
                #                         alignment2)
                # v1 = moving.getXYfromSY(self.roadUser1.getCurvilinearVelocityAtInstant(instant)[0],
                #                         self.roadUser1.getCurvilinearVelocityAtInstant(instant)[1],
                #                         utils._set(self.roadUser1.curvilinearPositions.lanes).index(self.roadUser1.getCurvilinearPositionAtInstant(instant)[2]),
                #                         alignment1)
                # v2 = moving.getXYfromSY(self.roadUser2.getCurvilinearVelocityAtInstant(instant)[0],
                #                         self.roadUser2.getCurvilinearVelocityAtInstant(instant)[1],
                #                         utils._set(self.roadUser2.curvilinearPositions.lanes).index(self.roadUser2.getCurvilinearPositionAtInstant(instant)[2]),
                #                         alignment2)
                # deltap = p1 - p2
                # deltav = v2 - v1
                # verifier si la liste des voies empruntée est la meme pour les deux vehicules
                # if utils._set(self.roadUser1.curvilinearPositions.lanes).index(
                # self.roadUser1.getCurvilinearPositionAtInstant(instant)[2]) ==  utils._set(self.roadUser2.curvilinearPositions.lanes).index(self.roadUser2.getCurvilinearPositionAtInstant(instant)[2]):

                # distance = world.distanceAtInstant(self.roadUser1, self.roadUser2, instant) - self.roadUser1.geometry
                # else:
                #     distance = world.distanceAtInstant(self.roadUser1, self.roadUser2, instant)
                # else:
                #     p1 = moving.getXYfromSY(world.getUserDistanceOnAlignmentAt(self.roadUser1, instant),
                #                             self.roadUser1.getCurvilinearPositionAtInstant(instant)[1],
                #                             utils._set(self.roadUser1.curvilinearPositions.lanes).index(
                #                                 self.roadUser1.getCurvilinearPositionAtInstant(instant)[2]),
                #                             alignment1)
                #
                #     p2 = moving.getXYfromSY(world.getUserDistanceOnAlignmentAt(self.roadUser2, instant),
                #                             self.roadUser2.getCurvilinearPositionAtInstant(instant)[1],
                #                             utils._set(self.roadUser2.curvilinearPositions.lanes).index(
                #                                 self.roadUser2.getCurvilinearPositionAtInstant(instant)[2]),
                #                             alignment2)
                #     v1 = moving.getXYfromSY(self.roadUser1.getCurvilinearVelocityAtInstant(instant)[0],
                #                             self.roadUser1.getCurvilinearVelocityAtInstant(instant)[1],
                #                             utils._set(self.roadUser1.curvilinearPositions.lanes).index(
                #                                 self.roadUser1.getCurvilinearPositionAtInstant(instant)[2]),
                #                             alignment1)
                #     v2 = moving.getXYfromSY(self.roadUser2.getCurvilinearVelocityAtInstant(instant)[0],
                #                             self.roadUser2.getCurvilinearVelocityAtInstant(instant)[1],
                #                             utils._set(self.roadUser2.curvilinearPositions.lanes).index(
                #                                 self.roadUser2.getCurvilinearPositionAtInstant(instant)[2]),
                #                             alignment2)
                #     deltap = p1 - p2
                #     deltav = v2 - v1
                #     if utils._set(self.roadUser1.curvilinearPositions.lanes).index(
                #             self.roadUser1.getCurvilinearPositionAtInstant(instant)[2]) == utils._set(
                #         self.roadUser2.curvilinearPositions.lanes).index(
                #         self.roadUser2.getCurvilinearPositionAtInstant(instant)[2]):
                #
                #         distance = world.distanceAtInstant(self.roadUser1, self.roadUser2,
                #                                            instant) - self.roadUser1.geometry
                #     else:
                #         distance = world.distanceAtInstant(self.roadUser1, self.roadUser2, instant)


            # else:
                # deltap = self.roadUser1.getPositionAtInstant(instant) - self.roadUser2.getPositionAtInstant(instant)
                # v1 = self.roadUser1.getVelocityAtInstant(instant)
                # v2 = self.roadUser2.getVelocityAtInstant(instant)
                # deltav = v2 - v1
                # distance = deltap.norm2() - self.roadUser1.geometry
            #
            # if self.roadUser1.initialAlignmentIdx != self.roadUser2.initialAlignmentIdx:
            #
            #     if self.areCrossing(907, 407, instant):
            #         if 850 <= self.roadUser1.getCurvilinearPositionAtInstant(instant)[0] <= 907 and 350 <= self.roadUser2.getCurvilinearPositionAtInstant(instant)[0] <= 407:
            #
            # velocityAngles[instant] = np.arccos(moving.Point.dot(v1, v2) / (v1.norm2() * v2.norm2()))
            # collisionCourseDotProducts[instant] = moving.Point.dot(deltap, deltav)

            # distances[instant] = distance
            # speedDifferentials[instant] = deltav.norm2()
            # if collisionCourseDotProducts[instant] > 0:
            #     interactionInstants.append(instant)
            # if distances[instant] != 0 and speedDifferentials[instant] != 0:
            #     collisionCourseAngles[instant] = np.arccos(
            #         collisionCourseDotProducts[instant] / (distances[instant] * speedDifferentials[instant]))
            # else:
            #     velocityAngles[instant] = np.arccos(moving.Point.dot(v1, v2) / (v1.norm2() * v2.norm2()))
            #     collisionCourseDotProducts[instant] = moving.Point.dot(deltap, deltav)
            #
            #     distances[instant] = distance
            #     speedDifferentials[instant] = deltav.norm2()
            #     if collisionCourseDotProducts[instant] > 0:
            #         interactionInstants.append(instant)
            #     if distances[instant] != 0 and speedDifferentials[instant] != 0:
            #         collisionCourseAngles[instant] = np.arccos(
            #             collisionCourseDotProducts[instant] / (distances[instant] * speedDifferentials[instant]))


        # if len(interactionInstants) >= 2:
        #     self.interactionInterval = moving.TimeInterval(interactionInstants[0], interactionInstants[-1])
        # else:
        #     self.interactionInterval = moving.TimeInterval()
        # self.addIndicator(indicators.SeverityIndicator(Interaction.indicatorNames[0], collisionCourseDotProducts))
        # self.addIndicator(indicators.SeverityIndicator(Interaction.indicatorNames[1], collisionCourseAngles))
        # self.addIndicator(indicators.SeverityIndicator(Interaction.indicatorNames[2], distances, mostSevereIsMax=False))
        # self.addIndicator(indicators.SeverityIndicator(Interaction.indicatorNames[4], velocityAngles))
        # self.addIndicator(indicators.SeverityIndicator(Interaction.indicatorNames[5], speedDifferentials))

        # # if we have features, compute other indicators
        # if self.roadUser1.hasFeatures() and self.roadUser2.hasFeatures():
        #     minDistances = {}
        #     for instant in list(self.indicators['Distance'].keys()):
        #         # if self.roadUser1.initialAlignmentIdx != self.roadUser2.initialAlignmentIdx:
        #         #     if 850 <= self.roadUser1.getCurvilinearPositionAtInstant(instant)[0] <= 907 and 350 <= self.roadUser2.getCurvilinearPositionAtInstant(instant)[0] <= 407:
        #         minDistances[instant] = moving.MovingObject.minDistance(self.roadUser1, self.roadUser2, instant)
        #         # else:
        #         #     minDistances[instant] = moving.MovingObject.minDistance(self.roadUser1, self.roadUser2, instant)
        #
        #     self.addIndicator(
        #         indicators.SeverityIndicator(Interaction.indicatorNames[3], minDistances, mostSevereIsMax=False))

    def computeCrossingsCollisions(self, predictionParameters, collisionDistanceThreshold, timeHorizon, useCurvilinear, alignment1, alignment2, computeCZ=False, debug=False, timeInterval=None):
        '''Computes all crossing and collision points at each common instant for two road users. '''
        TTCs = {}
        collisionProbabilities = {}
        if timeInterval is not None:
            commonTimeInterval = timeInterval
        else:
            commonTimeInterval = self.timeInterval
        self.collisionPoints, crossingZones = predictionParameters.computeCrossingsCollisions(obj1=self.roadUser1,
                                                                                              obj2=self.roadUser2,
                                                                                              collisionDistanceThreshold=collisionDistanceThreshold,
                                                                                              timeHorizon=timeHorizon,
                                                                                              useCurvilinear=useCurvilinear,
                                                                                              alignment1=alignment1,
                                                                                              alignment2=alignment2,
                                                                                              computeCZ=computeCZ,
                                                                                              debug=debug,
                                                                                              timeInterval=commonTimeInterval)
        for i, cps in self.collisionPoints.items():
            TTCs[i] = prediction.SafetyPoint.computeExpectedIndicator(cps)
            collisionProbabilities[i] = sum([p.probability for p in cps])
        if len(TTCs) > 0:
            self.addIndicator(indicators.SeverityIndicator(Interaction.indicatorNames[7], TTCs, mostSevereIsMax=False))
            self.addIndicator(indicators.SeverityIndicator(Interaction.indicatorNames[6], collisionProbabilities))

        # crossing zones and pPET
        if computeCZ:
            self.crossingZones = crossingZones
            pPETs = {}
            for i, cz in self.crossingZones.items():
                pPETs[i] = prediction.SafetyPoint.computeExpectedIndicator(cz)
            self.addIndicator(indicators.SeverityIndicator(Interaction.indicatorNames[9], pPETs, mostSevereIsMax=False))
        # TODO add probability of collision, and probability of successful evasive action

    def computePET(self, collisionDistanceThreshold):
        pet, t1, t2 = moving.MovingObject.computePET(self.roadUser1, self.roadUser2, collisionDistanceThreshold)
        if pet is not None:
            self.addIndicator(indicators.SeverityIndicator(Interaction.indicatorNames[10], {min(t1, t2): pet}, mostSevereIsMax=False))

    def setCollision(self, collision):
        '''indicates if it is a collision: argument should be boolean'''
        self.collision = collision

    def isCollision(self):
        if hasattr(self, 'collision'):
            return self.collision
        else:
            return None

    def getCollisionPoints(self):
        return self.collisionPoints

    def getCrossingZones(self):
        return self.crossingZones


def createInteractions(objects, _others=None):
    '''Create all interactions of two co-existing road users'''
    if _others is not None:
        others = _others

    interactions = []
    num = 0
    for i in range(len(objects)):
        if _others is None:
            others = objects[:i]
        for j in range(len(others)):
            commonTimeInterval = objects[i].commonTimeInterval(others[j])
            if not commonTimeInterval.empty():
                interactions.append(
                    Interaction(num, commonTimeInterval, objects[i].num, others[j].num, objects[i], others[j]))
                num += 1
    return interactions


def findInteraction(interactions, roadUserNum1, roadUserNum2):
    'Returns the right interaction in the set'
    i = 0
    while i < len(interactions) and set([roadUserNum1, roadUserNum2]) != interactions[i].getRoadUserNumbers():
        i += 1
    if i < len(interactions):
        return interactions[i]
    else:
        return None


def computeIndicators(interactions, computeMotionPrediction, computePET, predictionParameters, collisionDistanceThreshold, timeHorizon, computeCZ=False, debug=False, timeInterval=None):
    for inter in interactions:
        print('processing interaction {}'.format(inter.getNum()))  # logging.debug('processing interaction {}'.format(inter.getNum()))
        inter.computeIndicators()
        if computeMotionPrediction:
            inter.computeCrossingsCollisions(predictionParameters, collisionDistanceThreshold, timeHorizon, computeCZ, debug, timeInterval)
        if computePET:
            inter.computePET(collisionDistanceThreshold)
    return interactions


def aggregateSafetyPoints(interactions, pointType='collision'):
    '''Put all collision points or crossing zones in a list for display'''
    allPoints = []
    if pointType == 'collision':
        for i in interactions:
            for points in i.collisionPoints.values():
                allPoints += points
    elif pointType == 'crossing':
        for i in interactions:
            for points in i.crossingZones.values():
                allPoints += points
    else:
        print('unknown type of point: ' + pointType)
    return allPoints


def prototypeCluster(interactions, similarities, indicatorName, minSimilarity, similarityFunc=None, minClusterSize=None, randomInitialization=False):
    return ml.prototypeCluster([inter.getIndicator(indicatorName) for inter in interactions], similarities, minSimilarity, similarityFunc, minClusterSize, randomInitialization)


class Crossing(moving.STObject):
    '''Class for the event of a street crossing

    TODO: detecter passage sur la chaussee
    identifier origines et destination (ou uniquement chaussee dans FOV)
    carac traversee
    detecter proximite veh (retirer si trop similaire simultanement
    carac interaction'''

    def __init__(self, roaduserNum=None, num=None, timeInterval=None):
        moving.STObject.__init__(self, num, timeInterval)
        self.roaduserNum = roaduserNum


if __name__ == "__main__":
    import doctest
    import unittest

    suite = doctest.DocFileSuite('tests/events.txt')
    # suite = doctest.DocTestSuite()
    unittest.TextTestRunner().run(suite)
