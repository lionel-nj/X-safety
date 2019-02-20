from trafficintelligence import moving
import random as rd
import toolkit
import math
import cars


class Alignment():
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

        if others == None:
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
        avant = moving.Trajectory()

        for k in range(0, i):
            avant.addPosition(self.points[k])

        avant.addPosition(p)

        for k in range(i, len(self.points)):
            avant.addPosition(self.points[k])

        self.points = avant

    @staticmethod
    def isBetween(a, b, c):
        return moving.Point.distanceNorm2(a, c) + moving.Point.distanceNorm2(c, b) == moving.Point.distanceNorm2(a, b)

    def insertCrossingPoint(self):
        """inserts a crossing point : moving.Point in the alignment sequence"""
        if self.crossingPoint == self.points[0]:
            self.distance_to_crossing_point = 0


        elif self.points[-1] == self.crossingPoint:
            self.distance_to_crossing_point = self.points.getCumulativeDistance(len(self.points))

        else:
            for k in range(len(self.points) - 1):
                if Alignment.isBetween(self.points[k], self.points[k + 1], self.crossingPoint):
                    Alignment.insertPointAt(self, self.crossingPoint, k + 1)
                    self.points.computeCumulativeDistances()
                    self.distance_to_crossing_point = self.points.getCumulativeDistance(k + 1)
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
        if self.controlDevice == None:
            return True
        else:
            return False


class ControlDevice():
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


class World():
    """Description of the world, including the road (alignments), control devices (signs, traffic lights) and crossing point """

    def __init__(self, vehicles=None, pedestrians=None, alignments=None, controlDevices=None, crossingPoint=None):
        # self.vehicleInput = vehicleInput
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

    def reset(self, alignments, controlDevices, vehicleInputs):
        """alignments = list of Alignment class objects"""
        alignments[0].connectAlignments(alignments[1])
        self.controlDevices = controlDevices
        self.alignments = alignments
        self.vehicleInputs = vehicleInputs
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

    def isVehicleBeforeCrossingPointAt(self, alignment_idx, vehicle_idx, t, vehiclesData):
        """ determines if a vehicle if located ahead of a crossing point in a world representation """
        d = vehiclesData[alignment_idx][vehicle_idx].curvilinearPositions[t][0] - self.alignments[
            alignment_idx].distance_to_crossing_point
        if d < 0:
            return True
        else:
            return False

    def findApproachingVehicleOnMainAlignment(self, time, mainAlignment, listOfVehiclesOnMainAlignment):
        for k in range(len(listOfVehiclesOnMainAlignment)):
            distanceToCrossingPoint = self.alignments[mainAlignment].distance_to_crossing_point - \
                                      listOfVehiclesOnMainAlignment[k].curvilinearPositions[time][0]
            if distanceToCrossingPoint > 0:
                return k

    def initVehicleOnAlignment(self, alignmentIdx, intervalOfVehicleExistence):
        """generates a MovingObject """

        result = moving.MovingObject()
        result.curvilinearPositions = moving.CurvilinearTrajectory()
        result.velocities = moving.CurvilinearTrajectory()
        result.timeInterval = moving.TimeInterval(first=intervalOfVehicleExistence[0],
                                                  last=intervalOfVehicleExistence[1])

        result.desiredSpeed = self.vehicleInputs[alignmentIdx].driverDistribution.distribution.rvs(
            self.vehicleInputs[alignmentIdx].desiredSpeedParameters[0],
            self.vehicleInputs[alignmentIdx].desiredSpeedParameters[1])

        result.desiredSpeed = self.vehicleInputs[alignmentIdx].driverDistribution.distribution.rvs(
            self.vehicleInputs[alignmentIdx].desiredSpeedParameters[0],
            self.vehicleInputs[alignmentIdx].desiredSpeedParameters[1])

        result.vehicleLength = self.vehicleInputs[alignmentIdx].driverDistribution.distribution.rvs(
            self.vehicleInputs[alignmentIdx].geometryParam[0],
            self.vehicleInputs[alignmentIdx].geometryParam[1])

        result.reactionTime = self.vehicleInputs[alignmentIdx].driverDistribution.distribution.rvs(
            self.vehicleInputs[alignmentIdx].driverParam["tn"]["scale"],
            self.vehicleInputs[alignmentIdx].driverParam["tn"]["sd"])

        result.tiv_min = self.vehicleInputs[alignmentIdx].driverDistribution.distribution.rvs(
            self.vehicleInputs[alignmentIdx].driverParam["tiv_min"]["scale"],
            self.vehicleInputs[alignmentIdx].driverParam["tiv_min"]["sd"])

        result.criticalGap = self.vehicleInputs[alignmentIdx].driverDistribution.distribution.rvs(
            self.vehicleInputs[alignmentIdx].driverParam["critGap"]["scale"],
            self.vehicleInputs[alignmentIdx].driverParam["critGap"]["sd"])

        result.dn = result.desiredSpeed * result.tiv_min

        return result


    if __name__ == "__main__":
        import doctest
        doctest.testmod()
