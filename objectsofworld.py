from trafficintelligence import moving
import random as rd
import toolkit
import math
import cars


class Alignment:
    """Description of road lanes (centre line of a lane)
    point represents the lane geometry (type is moving.Trajectory) """

    def __init__(self, idx=None, points=None, width=None, controlDevice=None, name=None):
        self.idx = idx
        self.points = points
        self.width = width
        self.controlDevice = controlDevice
        self.name = name
        # self.volume = volume

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
        """ adds a connectedAlignmentIdx & a crossingPoint member to the alignment
         identifie le point x,y de croisement"""
        self.connectedAlignmentIdx = other.idx  # mise en relation des aligments qui s'entrecroisent
        other.connectedAlignmentIdx = self.idx  # mise en relation des aligments qui s'entrecroisent
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
        """determinates the angle between two alignments at the crossing point
        it is assumed that the method connectAlignments has already been applied to the alignlents
        which means that both of the alignments in input have a crossingPoint attribute
        inputs : alignments
        output : angle (degrees) at the crossing point of the alignments """

        crossingPoint = self.crossingPoint
        firstIndexOfCrossingPoint = 0
        secondIndexOfCrossingPoint = 0

        while self.points[firstIndexOfCrossingPoint] != crossingPoint:
            firstIndexOfCrossingPoint += 1
        while other.points[secondIndexOfCrossingPoint] != crossingPoint:
            secondIndexOfCrossingPoint += 1

        first_point = self.points.__getitem__(firstIndexOfCrossingPoint - 1)
        second_point = other.points.__getitem__(secondIndexOfCrossingPoint - 1)

        v1 = crossingPoint - first_point
        v2 = crossingPoint - second_point

        v = v1 - v2
        angle = moving.Point.angle(v) * 180 / math.pi

        self.angleAtCrossing = angle
        other.angleAtCrossing = angle

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

    def __init__(self, vehicles=None, pedestrians=None, alignments=None, controlDevices=None, crossingPoint=None):
        # self.UserInput = UserInput
        self.vehicles = vehicles  # dict de veh
        self.pedestrians = pedestrians  # sorted dict de ped
        self.alignments = alignments  # liste d alignements
        self.controlDevices = controlDevices  # liste de CD
        self.crossingPoint = crossingPoint  # moving.Point

    def __repr__(self):
        return "vehicles: {}, pedestrians: {}, alignments: {}, control devices: {}".format(self.vehicles,
                                                                                           self.pedestrians,
                                                                                           self.alignments,
                                                                                           self.controlDevices)

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

    def existingUsers(self, t):
        """determines all existing users in a word file"""

        result = []
        for k in range(0, len(self.vehicles)):
            if moving.Interval.contains(self.vehicles[k].getTimeInterval(), t):
                result.append(self.vehicles[k])

        for k in range(0, len(self.pedestrians)):
            if moving.Interval.contains(self.pedestrians[k].getTimeInterval(), t):
                result.append(self.pedestrians[k])

        return sorted(result, key=takeEntry)

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

        first = self.alignments[leaderAlignmentIdx].vehicles[i]
        second = self.alignments[followerAlignmentIdx].vehicles[j]

        if first.timeInterval.first >= second.timeInterval.first:
            leader = first
            follower = second
        else:
            leader = second
            follower = first

        if self.alignments[leaderAlignmentIdx].vehicles[i].vehiclesCoexistAt(
                self.alignments[followerAlignmentIdx].vehicles[j], t):
            if leaderAlignmentIdx == followerAlignmentIdx:
                d = cars.UserInput.distanceGap(leader.curvilinearPositions[t][0],
                                               follower.curvilinearPositions[t][0],
                                               leader.geometry)
            else:
                angle = self.alignments[0].angleAtCrossingPoint(self.alignments[1])
                d1 = self.alignments[leaderAlignmentIdx].vehicles[i].curvilinearPositions[t][0] - self.alignments[
                    leaderAlignmentIdx].distanceToCrossingPoint
                d2 = self.alignment[followerAlignmentIdx].vehicles[j].curvilinearPositions[t][0] - self.alignments[
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
            vehiclesData = self.alignments[alignmentIdx].vehicles
            listVeh = []
            for k in vehiclesData:
                if k.timeInterval is not None:
                    listVeh.append(k)

            rows = len(listVeh)
            interactionTime = []
            totalNumberOfEncountersSameWay = 0

            for h in range(0, rows - 1):
                interactionTime.append([])

                for t in range(vehiclesData[h+1].timeInterval.first, vehiclesData[h+1].timeInterval.last+1):
                    if self.isAnEncounter(alignmentIdx, alignmentIdx, h, h + 1, t-vehiclesData[h+1].timeInterval.first, dmin):
                        interactionTime[h].append(1)
                    else:
                        interactionTime[h].append(0)

                if interactionTime[h][-1] == 1:
                    numberOfEncountersSameWay = 1
                else:
                    numberOfEncountersSameWay = 0

                for el in range(len(interactionTime[h])-1):
                    if interactionTime[h][el] == 1 and interactionTime[h][el+1] == 0:
                        numberOfEncountersSameWay += 1

                totalNumberOfEncountersSameWay += numberOfEncountersSameWay

            return totalNumberOfEncountersSameWay

        elif method == "crossing":
            # TODO: verifier cette partie du code pour des interactions croisees
            vehiclesData = [self.alignments[0].vehicles, self.alignments[1].vehicles]
            listVeh = [[], []]

            for k in vehiclesData[0]:
                if k.timeInterval is not None:
                    listVeh[0].append(k)
            for k in vehiclesData[1]:
                if k.timeInterval is not None:
                    listVeh[1].append(k)

            rows = len(listVeh[0])
            columns = len(listVeh[1])
            interactionTime = []
            totalNumberOfCrossingEncounters = 0

            for h in range(rows):
                interactionTime.append([])
                for v in range(columns):
                    interactionTime[h].append([])

                    for t in range(vehiclesData[0][h+1].timeInterval.first, vehiclesData[0][h+1].timeInterval.last+1):
                        if self.isAnEncounter(0, 1, h, v, t - vehiclesData[0][h][h + 1].timeInterval.first, dmin):

                            interactionTime[h][v].append(1)
                        else:
                            interactionTime[h][v].append(0)

                    else:
                        numberOfEncounters = 1
                        for k in range(len(interactionTime[h][v]) - 1):
                            if interactionTime[h][v][k] == 1 and interactionTime[h][v][k + 1] == 0:
                                numberOfEncounters += 1

                    totalNumberOfCrossingEncounters += numberOfEncounters

        else:
            return None

    def countAllEncounters(self, dmin):
        """counts the encounters in a world
        vehiclesData : list of list of moving objects
        dmin : float"""

        totalNumberOfEncounters = []

        for alignment in self.alignments:
            totalNumberOfEncounters.append(self.count(method="inLine", alignmentIdx=alignment.idx, dmin=dmin))

        totalNumberOfEncounters.append(self.count(method="crossing", dmin=dmin))

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

    if __name__ == "__main__":
        import doctest
        doctest.testmod()
