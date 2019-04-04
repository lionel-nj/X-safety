import itertools
import math

from trafficintelligence import moving, utils

import toolkit


class Alignment:
    """Description of road lanes (centre line of a lane)
    point represents the lane geometry (type is moving.Trajectory) """

    def __init__(self, idx=None, points=None, width=None, controlDevice=None, name=None):
        self.idx = idx
        self.points = points
        self.width = width
        self.controlDevice = controlDevice
        self.name = name

    def build(self, entryPoint, exitPoint, others=None):
        """builds an alignments from points,
         entryPoint and exitPoint : moving.Point
         others : list of intermediate moving.points"""

        if others is None:
            self.points = moving.Trajectory.fromPointList([entryPoint, exitPoint])
        else:
            self.points = moving.Trajectory.fromPointList([entryPoint] + others + [exitPoint])

    @staticmethod
    def load(filename):
        return toolkit.loadYaml(filename)

    def save(self, filename):
        toolkit.saveYaml(filename, self)

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

    def buildIntersection(self, other):
        """ adds a connectedAlignmentIdx & a crossingPoint member to the alignment
         identifie le point x,y de croisement"""
        self.connectedAlignmentIdx = other.idx  # mise en relation des aligments qui s"entrecroisent
        other.connectedAlignmentIdx = self.idx  # mise en relation des aligments qui s"entrecroisent
        self.crossingPoint = self.points.getIntersections(other.points[0], other.points[-1])[1][0]
        other.crossingPoint = other.points.getIntersections(self.points[0], self.points[-1])[1][0]

        self.insertCrossingPoint()
        other.insertCrossingPoint()

    def isConnectedTo(self, other):
        """boolean, detemines if two alignments are connected"""
        if self.connectedAlignmentIdx == other.idx and other.connectedAlignmentIdx == self.idx:
            return True
        else:
            return False

    def angleAtCrossingPoint(self, other):
        """determines the angle between two alignments at the crossing point
        it is assumed that the method connectAlignments has already been applied to the alignments
        which means that both of the alignments in input have a crossingPoint attribute
        inputs : alignments
        output : angle (degrees) at the crossing point of the alignments """

        firstPoint = self.getFirstPoint()
        secondPoint = other.getFirstPoint()

        p1 = self.crossingPoint - firstPoint
        p2 = self.crossingPoint - secondPoint

        p = p1 - p2
        angle = moving.Point.angle(p) * 180 / math.pi

        self.angleAtCrossingPoint = angle
        other.angleAtCrossingPoint = angle

    def getAngleAtCrossing(self):
        """ method returns the angle formed by the the crossing alignments"""
        if hasattr(self, 'angleAtCrossing'):
            return self.angleAtCrossingPoint

    def getPoint(self, i):
        """returns i-th point of an alignment"""
        return self.points[i]

    def getFirstPoint(self):
        "returns the first point of an alignment"
        return self.points[0]

    def getLastPoint(self):
        "returns the last point of an alignment"
        return self.points[-1]

    def isStartOf(self, point):
        "boolean : True if a moving.Point is the first point of an alignment"
        if self.points[0].x == point.x and self.points[0].y == point.y:
            return True
        else:
            return False

    def isEndOf(self, point):
        "boolean : True if a moving.Point is the last point of an alignment"

        if self.points[-1].x == point.x and self.points[-1].y == point.y:
            return True
        else:
            return False

    def addUserToAlignment(self, user):
        """adds an user to self.vehicles or self.user """
        if self.vehicles:
            self.vehicles.append(user)
        else:
            self.vehicles = [user]

    def getUserByNum(self, num):
        """returns a specific user by its id=num"""
        for v in self.vehicles:
            if v.num == num:
                return v

    def defineMovementProportions(self, proportions):
        """method to defice the proportions of movements"""
        if len(proportions) == len(self.reachableAlignments):
            if sum(proportions) == 1:
                self.movementProportions = {}
                for idx, reachableAlignment in enumerate(self.reachableAlignments):
                    self.movementProportions[reachableAlignment] = proportions[idx]
            else:
                print('sum of proportion is not equal to 100%')
        else:
            print(
                'proportion list and reachable alignment list have different size, cannot define movement proportions')


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
        toolkit.saveYaml(filename, self)

    @staticmethod
    def load(filename):
        return toolkit.loadYaml(filename)

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
        return "alignments: {}, control devices: {}, user inputs: {}".format(self.alignments, self.controlDevices,
                                                                             self.userInputs)

    @staticmethod
    def load(filename):
        """loads a yaml file"""
        return toolkit.loadYaml(filename)

    def save(self, filename):
        """saves data to yaml file"""
        toolkit.saveYaml(filename, self)

    @staticmethod
    def takeEntry(elem):
        return elem.getTimeInterval()[0]

    def reset(self, alignments, controlDevices, userInputs):
        """alignments = list of Alignment class objects"""
        self.getAlignmentById(0).connectAlignments(self.getAlignmentById(1))
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

    def isVehicleBeforeCrossingPointAt(self, alignmentIdx, vehicleIdx, t, vehiclesData):
        """ determines if a vehicle if located ahead of a crossing point in a world representation """
        d = vehiclesData[alignmentIdx][vehicleIdx].curvilinearPositions[t][0] - self.getAlignmentById(
            alignmentIdx).distanceToCrossingPoint
        if d < 0:
            return True
        else:
            return False

    def minDistanceChecked(self, leaderAlignmentIdx, followerAlignmentIdx, i, j, t, dmin):
        """ checks if the minimum distance headway between two vehicles is verified
        in a car following situation : i is the leader vehicle and j is the following vehicle"""

        tempLeader = self.getAlignmentById(leaderAlignmentIdx).vehicles[i]
        tempFollower = self.getAlignmentById(followerAlignmentIdx).vehicles[j]
        if tempLeader.timeInterval.first > tempFollower.timeInterval.first:
            leader = tempFollower
            follower = tempLeader
        else:
            leader = tempLeader
            follower = tempFollower
        if moving.Interval.intersection(leader.timeInterval,
                                        follower.timeInterval) is not None and leader.timeInterval.contains(t):
            if leaderAlignmentIdx == followerAlignmentIdx:
                d = UserInput.distanceGap(leader.getCurvilinearPositionAtInstant(t)[0],
                                          follower.getCurvilinearPositionAtInstant(t)[0],
                                          leader.geometry)
                if d >= dmin:
                    return True
                return False

            else:
                angle = self.getAlignmentById(leaderAlignmentIdx).angleAtCrossingPoint(self.getAlignmentById(followerAlignmentIdx))
                d1 = leader.curvilinearPositions[t][0] - self.getAlignmentById(
                    leaderAlignmentIdx).distanceToCrossingPoint
                d2 = follower.curvilinearPositions[t][0] - self.getAlignmentById(
                    followerAlignmentIdx).distanceToCrossingPoint
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

        # {(26,27):[1,1,1,0,0,0,1,1,1]
        #  (27,28):[1,1,1,0,0,0,1,1,1]}

        if method == "inLine":
            vehList = []
            for user in self.getAlignmentById(alignmentIdx).vehicles:
                if user.timeInterval is not None:
                    vehList.append(user)

            rows = len(vehList)
            result = {}

            for h in range(4, rows - 1):
                commonInterval = self.getAlignmentById(alignmentIdx).vehicles[h].commonTimeInterval(
                    self.getAlignmentById(alignmentIdx).vehicles[h + 1])
                result[(h, h + 1)] = []
                for t in commonInterval:
                    if self.isAnEncounter(alignmentIdx, alignmentIdx, h, h + 1, t, dmin):
                        result[(h, h + 1)].append(1)
                    else:
                        result[(h, h + 1)].append(0)

            return result

        elif method == "crossing":

            vehList = [[], []]

            for el in self.getAlignmentById(0).vehicles:
                if el.timeInterval is not None:
                    vehList[0].append(el)

            for el in self.getAlignmentById(1).vehicles:
                if el.timeInterval is not None:
                    vehList[1].append(el)

            rows = len(vehList[0])
            columns = len(vehList[1])
            interactionTime = []
            totalNumberOfCrossingEncounters = 0

            for h in range(rows):
                interactionTime.append([])
                for v in range(columns):
                    interactionTime[h].append([])
                    follower = self.getAlignmentById(1).vehicles[v].getLeader(self.getAlignmentById(1).vehicles[v])

                    for t in range(follower.timeInterval.first, follower.timeInterval.last + 1):
                        if self.isAnEncounter(0, 1, h, v, t, dmin):
                            interactionTime[h][v].append(1)
                        else:
                            interactionTime[h][v].append(0)

                    numberOfEncounters = toolkit.countElementInList(interactionTime[h][v], 1)  #
                    totalNumberOfCrossingEncounters += numberOfEncounters
            return totalNumberOfCrossingEncounters

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

        for ui in self.userInputs:
            futureCumulatedHeadways = []
            for h in ui.cumulatedHeadways:
                if i <= h / timeStep < i + 1:
                    ui.initUser(userNum, h)
                    userNum += 1
                else:
                    futureCumulatedHeadways.append(h)
            ui.cumulatedHeadways = futureCumulatedHeadways
        return userNum

    def findApproachingVehicleOnMainAlignment(self, time, mainAlignmentIdx):
        listOfVehiclesOnMainAlignment = self.getAlignmentById(mainAlignmentIdx).vehicles
        for k in range(len(listOfVehiclesOnMainAlignment)):
            distanceToCrossingPoint = self.getAlignmentById(mainAlignmentIdx).distanceToCrossingPoint - \
                                      listOfVehiclesOnMainAlignment[k].curvilinearPositions[time][0]
            if distanceToCrossingPoint > 0:
                return k

    def convertSYtoXY(self):
        """converts SY to XY for a set of vehicles in self"""
        for al in self.alignments:
            for user in al.vehicles:
                if user.timeInterval is not None:
                    user.positions = moving.Trajectory()
                    user.velocities = moving.Trajectory()
                    for cp in user.curvilinearPositions:
                        user.positions.addPosition(
                            moving.getXYfromSY(s=cp[0],
                                               y=cp[1],
                                               alignmentNum=cp[2],
                                               alignments=[al.points]))
                    for idx, cv in enumerate(user.curvilinearVelocities):
                        user.velocities.addPosition(
                            moving.getXYfromSY(s=cv[0],
                                               y=cv[1],
                                               alignmentNum=user.curvilinearPositions[idx][2],
                                               alignments=[self.getAlignmentById(0).points]))
                else:
                    pass

    def getNotNoneVehiclesInWorld(self):
        """returns all vehicles that have been launched on their initial alignment : user.initialAlignment"""
        users = [[] * len(self.alignments)]
        for al in self.alignments:
            for user in al.vehicles:
                if user.timeInterval is not None:
                    users[al.idx].append(user)
        return users

    def getSimulatedUsers(self):
        """returns all vehicles that could not be computed, kind of the reciprocate of the method
        getNotNoneVehicleInWorld"""
        # TODO a verifier pour plusieurs alignments comportant des vehicules
        self.simulatedUsers = []
        for idx, al in enumerate(self.alignments):
            self.simulatedUsers.append([])
            for user in al.vehicles:
                if user is not None and user.timeInterval is not None:
                    if user.getCurvilinearPositionAt(-1)[0] > self.getVisitedAlignmentsCumulatedDistance(
                            user):  # sum(self.getAlignmentById(al.idx].points.distances):
                        self.simulatedUsers[idx].append([user.num, None])
                        for instant, cp in enumerate(user.curvilinearPositions):
                            if cp[0] > sum(al.points.distances):
                                self.simulatedUsers[-1][-1][-1] = instant
                                break

    def connectAlignments(self):
        """method to link the alignments: for a given alignment, it associates all the other alignments
         that can be reached from it"""
        import copy
        for idx, al in enumerate(self.alignments):
            _alignments = copy.deepcopy(self.alignments)
            _alignments.pop(idx)
            al.reachableAlignments = []
            if not _alignments:
                print('your world only has 1 alignment')
                break
            for other in _alignments:
                if other.isStartOf(al.getLastPoint()):
                    al.reachableAlignments.append(other.idx)

    def getNextAlignment(self, user, instant, timeStep):
        """returns the next alignment an user will be assigned to, according to the instant"""
        # todo : corriger, probleme a lexecution
        if user.existsAt(instant) :#timeInterval is not None:
            if user.timeInterval is not None :
                if user.timeInterval.first <= instant:
                    # print('bonne nouvelle')
                    occupiedAlignmentAtBy = user.curvilinearPositions.getLaneAt(instant )
                    reachableAlignments = self.getAlignmentById(occupiedAlignmentAtBy).reachableAlignments
                    nextPositionIfNoAlignmentChange = user.computeNextCurvilinearPositions('newell', instant, timeStep)
                    if self.getAlignmentById(occupiedAlignmentAtBy).points.cumulativeDistances[-1] < nextPositionIfNoAlignmentChange:
                        # print('youhou')
                        if reachableAlignments:
                            # print('wassup')
                            nextAlignment = reachableAlignments[0]
                        else:
                            # print('hmm')
                            nextAlignment = None
                    else:
                        # print('on verra')
                        nextAlignment = None

                    return nextAlignment
                else:
                    # print('olala')
                    return None
            else:
                return None
        return None

    def getVisitedAlignmentsCumulatedDistance(self, user):
        """rebuilds the trajectory of user, then calculates total length of the alignment the user had been assigned to """
        visitedAlignmentsIndices = []
        tempUser = self.rebuildUserTrajectory(user)
        for cp in tempUser.curvilinearPositions:
            if cp[2] in visitedAlignmentsIndices:
                pass
            else:
                visitedAlignmentsIndices.append(cp[2])
        visitedAlignmentsCumulativeDistance = 0
        for alignmentIdx in visitedAlignmentsIndices:
            visitedAlignmentsCumulativeDistance += self.getAlignmentById(alignmentIdx).points.cumulativeDistances[-1]

        return visitedAlignmentsCumulativeDistance

    def moveUserToAlignment(self, user):
        """ replaces every chunk of user.curvilinearPosition in the right alignment.vehicles
        returns Boolean = True, if the user's trajectory has been chunked"""
        laneChange, laneChangeInstants, changesList = user.changedLane()
        if laneChange:
            for alignmentChange, inter in zip(changesList, laneChangeInstants):
                self.getAlignmentById(alignmentChange[-1]).addUserToAlignment(user.getObjectInTimeInterval(
                    moving.TimeInterval(inter.first + user.getFirstInstant(), inter.last + user.getFirstInstant())))
            return True

    @staticmethod
    def removePartiallyUserFromAlignment(user):
        """for now : removes the first parts of curvilinearPosition that doesn't belong to the correct alignment """
        # TODO : a verifier
        # TODO : adapter pour plusieurs changements d'alignment
        laneChange = user.changedLane()
        if laneChange[0]:
            i = laneChange[1][0]
            length = len(user.curvilinearPositions)
            del user.curvilinearPositions.positions[0][i - 1:length]
            del user.curvilinearPositions.positions[1][i - 1:length]
            del user.curvilinearPositions.lanes[i:length]
            del user.curvilinearVelocities.positions[0][i - 1:length]
            del user.curvilinearVelocities.positions[1][i - 1:length]
            del user.curvilinearVelocities.lanes[i:length]

    def rebuildUserTrajectory(self, user):
        """rebuilds the trajectpry of an user, loop on each alignment"""
        import copy
        obj = moving.MovingObject(num=user.num, timeInterval=user.timeInterval, geometry=user.geometry,
                                  userType=user.userType, nObjects=user.nObjects)
        obj.curvilinearPositions = user.curvilinearPositions
        obj.curvilinearVelocities = user.curvilinearVelocities
        for al in self.alignments:
            if al.idx != user.curvilinearPositions[0][2]:
                tempUser = copy.deepcopy(al.getUserByNum(user.num))
                order = obj.curvilinearPositions.sort(tempUser.curvilinearPositions)
                if order:
                    obj.curvilinearVelocities.append(tempUser.curvilinearVelocities)
                else:
                    obj.curvilinearVelocities = tempUser.curvilinearVelocities.append(obj.curvilinearVelocities)
        return obj

    def occupiedAlignmentLength(self, user):
        """return the total length of the alignment occupied by an user = its last position"""
        if user.curvilinearPositions is not None:
            alignmentIdx = user.curvilinearPositions.getLaneAt(-1)
            return self.getAlignmentById(alignmentIdx).points.cumulativeDistances[-1]
        else:
            return user.initialAlignmentIdx

    def defineLeader(self, user, t, timeStep):
        """method to search the leader of an user at a givent instant t"""
        # TODO : adapter pour le cas ou on n'aurait pas une suite d'alignment
        nextAlignmentIdx = self.getNextAlignment(user, t, timeStep)
        _users = []

        for users in self.getAlignmentById(nextAlignmentIdx).vehicles:
            if users != user and users.timeInterval.contains(t) and users.createdBefore(user):
                _users.append((users.num, users.getCurvilinearPositionAtInstant(t)[0]))
        return min(_users, key=lambda x: x[1])[0]

    def getAlignmentById(self, idx):
        """get an lignment given its id"""
        for al in self.alignments:
            if al.idx == idx:
                return al


class UserInput:
    def __init__(self, alignmentIdx,
                 seed, volume, distributions):
        self.alignmentIdx = alignmentIdx
        self.seed = seed
        self.volume = volume
        self.distributions = distributions

    def save(self, filename):
        toolkit.saveYaml(filename, self)

    @staticmethod
    def load(filename):
        return toolkit.loadYaml(filename)

    @staticmethod
    def distanceGap(sLeader, sFollowing, lengthLeader):
        """calculates distance gaps between two vehicles"""
        distance = sLeader - sFollowing - lengthLeader
        return distance

    def initDistributions(self):
        self.headwayDistribution = self.distributions['headway'].getDistribution()
        self.lengthDistribution = self.distributions['length'].getDistribution()
        self.speedDistribution = self.distributions['speed'].getDistribution()
        self.tauDistribution = self.distributions['tau'].getDistribution()
        self.dDistribution = self.distributions['dn'].getDistribution()

    def generateHeadways(self, duration):
        """ generates a set a headways"""
        self.headways = utils.maxSumSample(self.headwayDistribution, duration)
        self.cumulatedHeadways = list(itertools.accumulate(self.headways))

    def getUserInputDistribution(self, item):
        """returns the distribution parameters for an item : type, name, parameters"""
        return self.distributions[item].getDistribution()

    def initUser(self, userNum, initialCumulatedHeadway):
        """generates a MovingObject on the VehicleInput alignment"""

        obj = moving.MovingObject(userNum, geometry=self.lengthDistribution.rvs(), initCurvilinear=True)
        obj.addNewellAttributes(self.speedDistribution.rvs(),
                                self.tauDistribution.rvs(),
                                self.dDistribution.rvs(),
                                # kj=120 veh/km
                                initialCumulatedHeadway,
                                self.alignmentIdx)
        # utile?
        # obj.criticalGap = gapNorm.getDistribution().rvs(random_state=10*userNum + 2*self.alignmentIdx)

        if len(self.alignment.vehicles) > 0:
            obj.leader = self.alignment.vehicles[-1]
        self.alignment.vehicles.append(obj)

    def getUserByNum(self, num):
        """gets an user by its id"""
        for user in self.alignment.vehicles:
            if user.num == num:
                return user


class CarGeometry:
    def __init__(self, length=None, width=None, polygon=None):
        self.length = length
        self.width = width
        self.polygon = polygon


class Distribution(object):
    def __init__(self, distributionType, distributionName=None, loc=None, scale=None, cdf=None,
                 degeneratedConstant=None):
        self.distributionType = distributionType
        self.distributionName = distributionName
        self.loc = loc
        self.scale = scale
        self.cdf = cdf
        self.degeneratedConstant = degeneratedConstant

    def save(self, fileName):
        return toolkit.saveYaml(fileName, self)

    @staticmethod
    def load(fileName):
        return toolkit.loadYaml(fileName)

    def getDistribution(self):
        from scipy import stats
        from trafficintelligence import utils

        if self.distributionType == 'theoric':
            if self.distributionName == 'norm':
                return stats.norm(loc=self.loc, scale=self.scale)
            elif self.distributionName == 'expon':
                return stats.expon(loc=self.loc, scale=self.scale)
            else:
                raise NameError('error in distribution name')
        elif self.distributionType == 'empirical':
            return utils.EmpiricalContinuousDistribution(self.cdf[0], self.cdf[1])
        elif self.distributionType == 'degenerated':
            return utils.ConstantDistribution(self.degeneratedConstant)
        else:
            raise NameError('error in distribution type')


if __name__ == "__main__":
    import doctest

    doctest.testmod()
