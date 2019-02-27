from trafficintelligence import moving
import toolkit
import math


class Alignment:
    """Description of road lanes (centre line of a lane)
    point represents the lane geometry (type is moving.Trajectory) """

    def __init__(self, idx=None, points=None, width=None, controlDevice=None, name=None):
        self.idx = idx
        self.points = points
        self.width = width
        self.controlDevice = controlDevice
        self.name = name

    def makeAlignment(self, entryPoint, exitPoint, others=None):
        """builds an alignments from points,
         entryPoint and exitPoint : moving.Point
         others : list of intermediate moving.points"""

        if others is None:
            self.points = moving.Trajectory.fromPointList([entryPoint, exitPoint])
        else:
            self.points = moving.Trajectory.fromPointList([entryPoint] + others + [exitPoint])

    @staticmethod
    def load(filename):
        return toolkit.load_yaml(filename)

    def save(self, filename):
        toolkit.save_yaml(filename, self)

    def addPoint(self, x, y):
        self.points.addPositionXY(x, y)

    def setPoint(self, i, x, y):
        self.points.setPositionXY(i, x, y)

    def insertPointAt(self, p, i):
        """inserts a moving.Point p at index i """
        previousPart = moving.Trajectory()

        for k in range(0, i):
            previousPart.addPosition(self.points[k])

        previousPart.addPosition(p)

        for k in range(i, len(self.points)):
            previousPart.addPosition(self.points[k])

        self.points = previousPart

    @staticmethod
    def isBetween(a, b, c):
        return moving.Point.distanceNorm2(a, c) + moving.Point.distanceNorm2(c, b) == moving.Point.distanceNorm2(a, b)

    def insertCrossingPoint(self):
        """inserts a crossing point : moving.Point in the alignment sequence"""
        if self.crossingPoint == self.points[0]:
            self.distanceToCrossingPoint = 0

        elif self.points[-1] == self.crossingPoint:
            self.distanceToCrossingPoint = self.points.getCumulativeDistance(len(self.points))

        else:
            for k in range(len(self.points) - 1):
                if Alignment.isBetween(self.points[k], self.points[k + 1], self.crossingPoint):
                    Alignment.insertPointAt(self, self.crossingPoint, k + 1)
                    self.points.computeCumulativeDistances()
                    self.distanceToCrossingPoint = self.points.getCumulativeDistance(k + 1)
                    break

    def connectAlignments(self, other):
        """ adds a connected_alignment_idx & a crossingPoint member to the alignment
         identifie le point x,y de croisement"""
        self.connected_alignment_idx = other.idx  # mise en relation des aligments qui s"entrecroisent
        other.connected_alignment_idx = self.idx  # mise en relation des aligments qui s"entrecroisent
        self.crossingPoint = self.points.getIntersections(other.points[0], other.points[-1])[1][0]
        other.crossingPoint = other.points.getIntersections(self.points[0], self.points[-1])[1][0]

        self.insertCrossingPoint()
        other.insertCrossingPoint()

    def isConnectedTo(self, other):
        """boolean, detemines if two alignments are connected"""
        if self.connected_alignment_idx == other.idx and other.connected_alignment_idx == self.idx:
            return True
        else:
            return False

    def angleAtCrossingPoint(self, other):
        """determinates the angle between two alignments at the crossing point
        it is assumed that the method connectAlignments has already been applied to the alignlents
        which means that both of the alignments in input have a crossingPoint attribute
        inputs : alignments
        output : angle (degrees) at the crssoing point of the alignments """

        crossingPoint = self.crossingPoint
        first_index_of_cp = 0
        second_index_of_cp = 0

        while self.points[first_index_of_cp] != crossingPoint:
            first_index_of_cp += 1
        while other.points[second_index_of_cp] != crossingPoint:
            second_index_of_cp += 1

        first_point = self.points.__getitem__(first_index_of_cp - 1)
        second_point = other.points.__getitem__(second_index_of_cp - 1)

        v1 = crossingPoint - first_point
        v2 = crossingPoint - second_point

        v = v1 - v2
        angle = moving.Point.angle(v) * 180 / math.pi

        self.angle_at_crossing = angle
        other.angle_at_crossing = angle

        return angle

    def alignmentHasROW(self):
        if self.controlDevice is None:
            return True
        else:
            return False


class ControlDevice:
    """generic traffic control devices"""
    categories = {0: "stop",
                  1: "yield",
                  2: "traffic light"}

    def __init__(self, curvilinearPosition=None, alignmentIdx=None, category=None):
        self.curvilinearPosition = curvilinearPosition
        self.alignmentIdx = alignmentIdx
        self.category = category

    def __repr__(self):
        return "position:{}, alignment:{}, category:{}".format(self.curvilinearPosition, self.alignmentIdx,
                                                               self.categories[self.category])

    def save(self, filename):
        toolkit.save_yaml(filename, self)

    @staticmethod
    def load(filename):
        return toolkit.load_yaml(filename)

    def isVehicleAtControlDevice(self, vehicle, time, precision):
        if self.curvilinearPosition >= vehicle.curvilinearPositions[time][0] >= self.curvilinearPosition - precision:
            return True
        else:
            return False


class World:
    """Description of the world, including the road (alignments), control devices (signs, traffic lights) and crossing point """

    def __init__(self, alignments=None, controlDevices=None, crossingPoint=None):
        self.alignments = alignments  # liste d alignements
        self.controlDevices = controlDevices  # liste de CD
        self.crossingPoint = crossingPoint  # moving.Point

    def __repr__(self):
        return "alignments: {}, control devices: {}".format(self.alignments, self.controlDevices)

    @staticmethod
    def load(filename):
        """loads a yaml file"""
        return toolkit.load_yaml(filename)

    def save(self, filename):
        """saves data to yaml file"""
        toolkit.save_yaml(filename, self)

    @staticmethod
    def takeEntry(elem):
        return elem.getTimeInterval()[0]

    def reset(self, alignments, controlDevices, userInputs):
        """alignments = list of Alignment class objects"""
        alignments[0].connectAlignments(alignments[1])
        self.controlDevices = controlDevices
        self.alignments = alignments
        self.userInputs = userInputs
        self.save("default.yml")

    def showAlignments(self):
        """plots alignments in a word representation file"""
        import matplotlib.pyplot as plt
        for alignments in self.alignments:
            moving.Trajectory.plot(alignments.points)
            moving.Trajectory.plot(alignments.points)
        plt.show()
        plt.close()

    def getAlignments(self):
        result = []
        for alignment in self.alignments:
            result.append(alignment)
        return result

    #
    # def existingUsers(self, t):
    #     """determines all existing users in a word file"""
    #
    #     result = []
    #     for k in range(0, len(self.vehicles)):
    #         if moving.Interval.contains(self.vehicles[k].getTimeInterval(), t):
    #             result.append(self.vehicles[k])
    #
    #     for k in range(0, len(self.pedestrians)):
    #         if moving.Interval.contains(self.pedestrians[k].getTimeInterval(), t):
    #             result.append(self.pedestrians[k])
    #
    #     return sorted(result, key=takeEntry)

    def isVehicleBeforeCrossingPointAt(self, alignmentIdx, vehicleIdx, t, vehiclesData):
        """ determines if a vehicle if located ahead of a crossing point in a world representation """
        d = vehiclesData[alignmentIdx][vehicleIdx].curvilinearPositions[t][0] - self.alignments[
            alignmentIdx].distanceToCrossingPoint
        if d < 0:
            return True
        else:
            return False

    def minDistanceChecked(self, leaderAlignmentIdx, followerAlignmentIdx, i, j, t, dmin):
        """ checks if the minimum distance headway between two vehicles is verified
        in a car following situation : i is the leader vehicle and j is the following vehicle"""

        tempLeader = self.alignments[leaderAlignmentIdx].vehicles[i]
        tempFollower = self.alignments[followerAlignmentIdx].vehicles[j]
        if tempLeader.timeInterval.first > tempFollower.timeInterval.first:
            leader = tempFollower
            follower = tempLeader
        else:
            leader = tempLeader
            follower = tempFollower

        if leader.vehiclesCoexistAt(follower, t):
            if leaderAlignmentIdx == followerAlignmentIdx:
                d = UserInput.distanceGap(leader.curvilinearPositions[t-leader.timeInterval.first][0],
                                          follower.curvilinearPositions[t - follower.timeInterval.first][0],
                                          leader.geometry)
                if d >= dmin:
                    return True
                return False

            else:
                angle = self.alignments[leaderAlignmentIdx].angleAtCrossingPoint(self.alignments[followerAlignmentIdx])
                d1 = leader.curvilinearPositions[t][0] - self.alignments[
                    leaderAlignmentIdx].distanceToCrossingPoint
                d2 = follower.curvilinearPositions[t][0] - self.alignments[
                    followerAlignmentIdx].distanceToCrossingPoint
                d = ((d1 ** 2) + (d2 ** 2) - (2 * d1 * d2 * math.cos(angle))) ** 0.5  # loi des cosinus
                if d >= dmin:
                    return True
                else:
                    return False
        else:
            return True

    def isAnEncounter(self, leaderAlignmentIdx, followerAlignmentIdx, i, j, t, dmin):
        """ checks if there is an encounter between two vehicules
        leaderAlignmentIdx and followerAlignmentIdx are integers
        i,j : integers
        t : time, integer
        dmin : float  """
        if self.minDistanceChecked(leaderAlignmentIdx, followerAlignmentIdx, i, j, t, dmin):
            return False
        else:
            return True

    def count(self, method, dmin, alignmentIdx=None):
        """ counts according to the selected method (cross or in line)
         the number of interactions taking place at a distance smaller than dmin.
        """
        if method == "inLine":
            vehList = []
            for el in self.alignments[alignmentIdx].vehicles:
                if el.timeInterval is not None:
                    vehList.append(el)

            rows = len(vehList)

            interactionTime = []
            totalNumberOfEncountersSameWay = 0

            for h in range(0, rows - 1):
                interactionTime.append([])

                for t in range(self.alignments[alignmentIdx].vehicles[h + 1].timeInterval.first,
                               self.alignments[alignmentIdx].vehicles[h + 1].timeInterval.last + 1):
                    if self.isAnEncounter(alignmentIdx, alignmentIdx, h, h + 1, t, dmin):
                        interactionTime[h].append(1)
                    else:
                        interactionTime[h].append(0)

                numberOfEncountersSameWay = toolkit.countElementInList(interactionTime[h], 1)
                totalNumberOfEncountersSameWay += numberOfEncountersSameWay

            return totalNumberOfEncountersSameWay
        #
        # elif method == "crossing":
        #     rows = len(vehiclesData[0])
        #     columns = len(vehiclesData[1])
        #     interactionTime = []
        #     totalNumberOfCrossingEncounters = 0
        #
        #     for h in range(rows):
        #         interactionTime.append([])
        #         for v in range(columns):
        #             interactionTime[h].append([])
        #
        #             t = 0
        #             while t < len(vehiclesData[0][0].curvilinearPositions):
        #                 if ((self.isAnEncounter(vehiclesData, 0, 1, h, v, t, dmin)[0]
        #                      and 0 < vehiclesData[0][h].velocities[t][0]
        #                      and 0 < vehiclesData[1][v].velocities[t][0])):
        #                     interactionTime[h][v].append(t)
        #                 t += 1
        #
        #             if len(interactionTime[h][v]) < 2:
        #                 numberOfEncounters = len(interactionTime[h][v])
        #
        #             else:
        #                 numberOfEncounters = 1
        #                 for k in range(len(interactionTime[h][v]) - 1):
        #                     if interactionTime[h][v][k + 1] != interactionTime[h][v][k] + 1:
        #                         numberOfEncounters += 1
        #
        #             totalNumberOfCrossingEncounters += numberOfEncounters

        else:
            print('error in method name')

    def countAllEncounters(self, vehiclesData, dmin):
        """counts the encounters in a world
        vehiclesData : list of list of moving objects
        dmin : float"""

        totalNumberOfEncounters = []

        for alignment in self.alignments:
            totalNumberOfEncounters.append(self.count(method="inLine", vehiclesData=vehiclesData,
                                                      alignmentIdx=alignment.idx, dmin=dmin))

        totalNumberOfEncounters.append(self.count(method="crossing", vehiclesData=vehiclesData, dmin=dmin))

        return totalNumberOfEncounters, sum(totalNumberOfEncounters)

    def initUsers(self, i, timeStep, userNum):
        """Initializes new users on their respective alignments """
        for vi in self.userInputs:
            futureCumulatedHeadways = []
            for h in vi.cumulatedHeadways:
                if i <= h / timeStep < i + 1:
                    vi.initUser(userNum, h)
                    userNum += 1
                else:
                    futureCumulatedHeadways.append(h)
            vi.cumulatedHeadways = futureCumulatedHeadways
        return userNum

    def findApproachingVehicleOnMainAlignment(self, time, mainAlignment, listOfVehiclesOnMainAlignment):
        for k in range(len(listOfVehiclesOnMainAlignment)):
            distanceToCrossingPoint = self.alignments[mainAlignment].distanceToCrossingPoint - \
                                      listOfVehiclesOnMainAlignment[k].curvilinearPositions[time][0]
            if distanceToCrossingPoint > 0:
                return k


class UserInput:
    def __init__(self, alignmentIdx, desiredSpeedParameters, headwayDistribution, headwayParam,
                 seed, volume, geometryParam, driverDistribution, headways=None,
                 driverParam={'tn': {'scale': None, 'sd': None}, 'tiv_min': {'scale': None, 'sd': None},
                              'critGap': {'scale': None, 'sd': None}}):
        self.alignmentIdx = alignmentIdx
        self.desiredSpeedParameters = desiredSpeedParameters
        self.headways = headways
        self.headwayDistribution = headwayDistribution
        self.headwayParam = headwayParam
        self.seed = seed
        self.volume = volume
        self.geometryParam = geometryParam
        self.driverParam = driverParam
        self.driverDistribution = driverDistribution.distribution

    def save(self, filename):
        toolkit.save_yaml(filename, self)

    @staticmethod
    def distanceGap(sLeader, sFollowing, lengthLeader):
        """calculates distance gaps between two vehicles"""
        distance = sLeader - sFollowing - lengthLeader
        return distance

    def generateHeadways(self, duration, seed):
        """ generates a set a headways"""
        self.headways = toolkit.generateSample(duration=duration,
                                               seed=seed,
                                               distribution=self.distributions['headways'])

    def initUser(self, userNum, initialCumulatedHeadway):
        """generates a MovingObject on the VehicleInput alignment"""
        geomNorm = self.distributions['geometry'].getDistribution()
        speedNorm = self.distributions['speed'].getDistribution()
        tauNorm = self.distributions['tau'].getDistribution()
        dNorm = self.distributions['dn'].getDistribution()

        obj = moving.MovingObject(userNum, geometry=geomNorm.rvs(), initCurvilinear=True)
        obj.addNewellAttributes(speedNorm.rvs(),
                                tauNorm.rvs(),
                                dNorm.rvs(),  # kj=120 veh/km TODO get from distribution #obj.desiredSpeed * obj.tiv_min
                                initialCumulatedHeadway,
                                self.alignmentIdx)

        # # utile?
        # obj.criticalGap = self.driverDistribution.distribution.rvs(
        #     self.driverParam["critGap"]["scale"],
        #     self.driverParam["critGap"]["sd"])

        if len(self.alignment.vehicles) > 0:
            obj.leader = self.alignment.vehicles[-1]  # TODO verify?
        self.alignment.vehicles.append(obj)


class CarGeometry:
    def __init__(self, length=None, width=None, polygon=None):
        self.length = length
        self.width = width
        self.polygon = polygon


class Distribution:
    def __init__(self, typeOfDistribution, distributionName, loc=None, scale=None, cdf=None, constant=None):
        self.typeOfDistribution = typeOfDistribution
        self.distributionName = distributionName
        self.loc = loc
        self.scale = scale
        self.cdf = cdf
        self.constant = constant

    def save(self, fileName):
        return toolkit.save_yaml(fileName, self)

    @staticmethod
    def load(fileName):
        return toolkit.load_yaml(fileName)

    def getDistribution(self):
        from scipy import stats
        from trafficintelligence import utils
        if self.typeOfDistribution == 'theoric':
            if self.distributionName == 'norm':
                return stats.norm(self.loc, self.scale)
            elif self.distributionName == 'expon':
                return stats.expon(self.loc)
            else:
                print('error in distribution name')
        elif self.typeOfDistribution == 'empirical':
            return utils.EmpiricalContinuousDistribution(self.cdf[0], self.cdf[1])
        elif self.typeOfDistribution == 'degenerated':
            return self.constant
        else:
            print('error in distribution type')


if __name__ == "__main__":
    import doctest

    doctest.testmod()
