import cars
from trafficintelligence import moving
import random as rd
import toolkit
import math

class Alignment():
    '''Description of road lanes (centre line of a lane)
    point represents the lane geometry (type is moving.Trajectory) '''
    def __init__(self, idx = None, points = None, width = None, controlDevice = None, name = None):
        self.idx = idx
        self.points = points
        self.width = width
        self.controlDevice = controlDevice
        self.name = name
        #self.volume = volume

    def makeAlignment(self,entryPoint, exitPoint, others = None):
        '''builds an alignments from points,
         entryPoint and exitPoint : moving.Point
         others : list of intermediate moving.points'''

        if others == None :
            self.points = moving.Trajectory.fromPointList([entryPoint,exitPoint])
        else:
            self.points = moving.Trajectory.fromPointList([entryPoint]+others+[exitPoint])

    @staticmethod
    def load(filename):
        return toolkit.load_yaml(filename)

    def save(self, filename):
        toolkit.save_yaml(filename, self)

    def addPoint(self,x,y):
        self.points.addPositionXY(x,y)

    def setPoint(self,i,x,y):
        self.points.setPositionXY(i,x,y)

    def insertPointAt(self,p,i):
        '''inserts a moving.Point p at index i '''
        avant = moving.Trajectory()

        for k in range(0,i):
            avant.addPosition(self.points[k])

        avant.addPosition(p)

        alignment_until_point = avant

        for k in range(i,len(self.points)):
            avant.addPosition(self.points[k])

        self.points = avant

    @staticmethod
    def isBetween(a,b,c):
        return moving.Point.distanceNorm2(a,c) + moving.Point.distanceNorm2(c,b) == moving.Point.distanceNorm2(a,b)

    def insertCrossingPoint(self):
        '''inserts a crossing point : moving.Point in the alignment sequence'''
        if self.crossingPoint == self.points[0] :
            self.distance_to_crossing_point = 0


        elif self.points[-1] == self.crossingPoint :
            self.distance_to_crossing_point = self.points.getCumulativeDistance(len(self.points))

        else:
            for k in range (len(self.points)-1):
                if Alignment.isBetween(self.points[k],self.points[k+1],self.crossingPoint):
                    Alignment.insertPointAt(self,self.crossingPoint,k+1)
                    self.points.computeCumulativeDistances()
                    self.distance_to_crossing_point = self.points.getCumulativeDistance(k+1)
                    break


    def connectAlignments(self,other):
        ''' adds a connected_alignment_idx & a crossingPoint member to the alignment
         identifie le point x,y de croisement'''
        self.connected_alignment_idx = other.idx #mise en relation des aligments qui s'entrecroisent
        other.connected_alignment_idx = self.idx #mise en relation des aligments qui s'entrecroisent
        self.crossingPoint = self.points.getIntersections(other.points[0],other.points[-1])[1][0]
        other.crossingPoint = other.points.getIntersections(self.points[0],self.points[-1])[1][0]

        self.insertCrossingPoint()
        other.insertCrossingPoint()

    def isConnectedTo(self,other):
        '''boolean, detemines if two alignments are connected'''
        if self.connected_alignment_idx == other.idx and other.connected_alignment_idx == self.idx:
            return True
        else:
            return False

    def angleAtCrossingPoint(self,other):
        '''determinates the angle between two alignments at the crossing point
        it is assumed that the method connectAlignments has already been applied to the alignlents
        which means that both of the alignments in input have a crossingPoint attribute
        inputs : alignments
        output : angle (degrees) at the crssoing point of the alignments '''

        crossingPoint = self.crossingPoint
        first_index_of_cp = 0
        second_index_of_cp = 0

        while self.points[first_index_of_cp] != crossingPoint:
            first_index_of_cp += 1
        while other.points[second_index_of_cp] != crossingPoint:
            second_index_of_cp += 1

        first_point = self.points.__getitem__(first_index_of_cp-1)
        second_point = other.points.__getitem__(second_index_of_cp-1)

        v1 = crossingPoint - first_point
        v2 = crossingPoint - second_point

        v = v1 - v2
        angle = moving.Point.angle(v)*180/math.pi

        self.angle_at_crossing = angle
        other.angle_at_crossing = angle

        return angle


class ControlDevice():
    '''generic traffic control devices'''
    categories = {'stop' : 0,
                  'yield' : 1,
                  'traffic light' : 2}

    def __init__(self, curvilinearPosition = None, alignmentIdx = None, category = None):
        self.curvilinearPosition = curvilinearPosition
        self.alignmentIdx = alignmentIdx
        self.category = category

    def __repr__(self):
        return "position:{}, alignment:{}, category:{}".format(self.curvilinearPosition, self.alignmentIdx, self.category)


class World():
    '''Description of the world, including the road (alignments), control devices (signs, traffic lights) and crossing point '''
    def __init__(self,vehicles = None ,pedestrians = None, alignments = None, controlDevices = None, crossingPoint = None):
        # self.vehicleInput = vehicleInput
        self.vehicles = vehicles # dict de veh
        self.pedestrians = pedestrians #sorted dict de ped
        self.alignments = alignments #liste de alignements
        self.controlDevices = controlDevices #liste de CD
        self.crossingPoint = crossingPoint #moving.Point

    def __repr__(self):
        return "vehicles: {}, pedestrians: {}, alignments: {}, control devices: {}".format(self.vehicles,self.pedestrians,self.alignments,self.controlDevices)

    @staticmethod
    def load(filename):
        return toolkit.load_yaml(filename)

    def save(self, filename):
        toolkit.save_yaml(filename, self)

    @staticmethod
    def takeEntry(elem):
        return elem.getTimeInterval()[0]

    def reset(self,alignments, controlDevices, vehicleInputs):
        '''alignments = list of Alignment class objects'''
        alignments[0].connectAlignments(alignments[1])
        self.alignments = alignments
        self.vehicleInputs = vehicleInputs
        self.save('default.yml')

    def showAlignments(self):
        import matplotlib.pyplot as plt

        moving.Trajectory.plot(world.alignments[0].points)
        moving.Trajectory.plot(world.alignments[1].points)
        plt.show()

    def existingUsers(self,t):

        result = []
        for k in range(0,len(self.vehicles)):
            if moving.Interval.contains(self.vehicles[k].getTimeInterval(),t):
                result.append(self.vehicles[k])

        for k in range(0,len(self.pedestrians)):
            if moving.Interval.contains(self.pedestrians[k].getTimeInterval(),t):
                result.append(self.pedestrians[k])

        return sorted(result, key = takeEntry)

    def minDistanceChecked(self,vehiclesData,alignment_idx_i,alignment_idx_j,i,j,t,dmin):
        ''' checks if the minimum distance headway between two vehicles is verified
        in a car following situation : i is the leader vehicle j is the following vehicle'''
        if alignment_idx_j == alignment_idx_i:
            vehicle_length = vehiclesData[alignment_idx_i][i].vehicleLength
            d = cars.VehicleInput.gap(vehiclesData[alignment_idx_i][i].curvilinearPositions[t][0],vehiclesData[alignment_idx_j][j].curvilinearPositions[t][0],vehicle_length)
            if d > dmin:
                return True,d
            return False,d

        else :
            angle = self.alignments[0].angleAtCrossingPoint(self.alignments[1])
            d1 = vehiclesData[alignment_idx_i][i].curvilinearPositions[t][0]-self.alignments[alignment_idx_i].distance_to_crossing_point
            d2 = vehiclesData[alignment_idx_j][j].curvilinearPositions[t][0]-self.alignments[alignment_idx_j].distance_to_crossing_point
            d = ((d1**2)+(d2**2)-(2*d1*d2*math.cos(angle)))**(0.5) #loi des cosinus
            if d > dmin:
                return True,d
            else:
                return False,d

    def isAnEncounter(self,vehiclesData,alignment_idx_i,alignment_idx_j,i,j,t,dmin):
        ''' checks if there is an accounter between two vehicules
        alignment_idx_i and alignment_idx_j are integers
        i,j : integers
        t : time, integer
        dmin : float  '''
        d = self.minDistanceChecked(vehiclesData,alignment_idx_i,alignment_idx_j,i,j,t,dmin)[1]
        if self.minDistanceChecked(vehiclesData,alignment_idx_i,alignment_idx_j,i,j,t,dmin)[0] == True :
            return False,d
        else :
            return True,d

    def countAllEncounters(self,vehiclesData,dmin):
        '''counts the encounters in a world
        vehiclesData : list of list of moving objects
        dmin : float'''

        rows = len(vehiclesData[0])
        columns = len(vehiclesData[1])


        matrix_intersection = [[0]*columns]*rows
        matrix_voie0 =[0]*rows
        matrix_voie1 = [0]*columns

        numberOfEncountersSameWayHorizontal = 0
        numberOfEncountersSameWayVertical = 0
        numberOfEncounterCrossingPaths = 0

        #interactions sur la meme voie horizontale

        for h in range(columns-1):
            c = 0
            while t < vehiclesData[0][0].curvilinearPositions :
                if self.isAnEncounter(vehiclesData,0,0,h,h+1,t,dmin)[0] == True and self.isAnEncounter(vehiclesData,0,0,h,h+1,t+1,dmin)[0] == False 0 <= vehiclesData[0][h].curvilinearPositions[t][0]:
                    c=+1
            t+=1
            matrix_voie1[h] = c
        numberOfEncountersSameWayHorizontal = sum(matrix_voie0)

        #interactions sur la meme voie horizontale

        for v in range(rows-1):
            c = 0
            while t < vehiclesData[1][0].curvilinearPositions :
                if self.isAnEncounter(vehiclesData,1,1,v,v+1,t,dmin)[0] == True and self.isAnEncounter(vehiclesData,1,1,v,v+1,t+1,dmin)[0] == False 0 <= vehiclesData[0][h].curvilinearPositions[t][0]:
                    c=+1
            t+=1
            matrix_voie1[h] = c
        numberOfEncountersSameWayHorizontal = sum(matrix_voie1)

        #interactions croisées
        for h in range(rows):
            for v in range(columns):
                c = 0
                while t < len(vehiclesData[0][0].curvilinearPositions):

                    if self.isAnEncounter(vehiclesData,0,1,h,v,t,dmin)[0] == True and self.isAnEncounter(vehiclesData,0,1,h,v,t+1,dmin)[0] == False  and 10 <= vehiclesData[0][h].curvilinearPositions[t][0] and 10 <= vehiclesData[1][v].curvilinearPositions[t][0]:
                        c+=1
                t+=1

            matrix_intersection[h][v] = c

        return numberOfEncountersSameWayHorizontal,numberOfEncountersSameWayVertical,numberOfEncounterCrossingPaths,numberOfEncountersSameWayVertical+numberOfEncountersSameWayHorizontal+numberOfEncounterCrossingPaths,matrix_intersection, matrix_voie0, matrix_voie1


        # #interactions sur la meme voie horizontale
        #
        # for h in range(0,rows-1):
        #     t = 0
        #     while t < len(vehiclesData[0][0].curvilinearPositions)-1:
        #         if self.isAnEncounter(vehiclesData,0,0,h,h+1,t,dmin)[0] == True and 10 <= vehiclesData[0][h].curvilinearPositions[t][0] and 10 <= vehiclesData[0][h].curvilinearPositions[t][0]:
        #
        #             if self.isAnEncounter(vehiclesData,0,0,h,h+1,t+1,dmin)[0] == True :
        #                 numberOfEncountersSameWayHorizontal += 1
        #             matrix_voie0[h] += 1
        #         t +=1
        #
        # #interactions sur la meme voie verticale
        # for t in range(0,len(vehiclesData[1][0].curvilinearPositions)):
        #     for v in range(columns-1):
        #         if self.isAnEncounter(vehiclesData,1,1,v,v+1,t,dmin)[0] == True and matrix_voie1[v] == 0 and 10 <= vehiclesData[1][v].curvilinearPositions[t][0]:
        #             matrix_voie1[v] = 1
        #             numberOfEncountersSameWayVertical += 1


        # return matrix_voie0
    def initVehiclesOnAligment(self,alignmentIdx, numberOfVehicles, sim, v0):
        result = []

        for k in range(numberOfVehicles):
            temp = moving.MovingObject()
            rd.seed(self.vehicleInputs[alignmentIdx].seed + k)
            v0 = rd.normalvariate(self.vehicleInputs[alignmentIdx].desiredSpeedParameters[0], self.vehicleInputs[alignmentIdx].desiredSpeedParameters[1])

            temp.curvilinearPositions = moving.CurvilinearTrajectory.generate(-(k+1),
                                                                              v0,
                                                                              1,
                                                                              self.alignments[alignmentIdx].idx)
            rd.seed(self.vehicleInputs[alignmentIdx].seed + k)
            temp.vehicleLength = rd.normalvariate(7,1.5)
            temp.velocities = [v0]
            temp.accelerations = [None]
            rd.seed(self.vehicleInputs[alignmentIdx].seed + k)
            temp.desiredSpeed = rd.normalvariate(self.vehicleInputs[alignmentIdx].desiredSpeedParameters[0], self.vehicleInputs[alignmentIdx].desiredSpeedParameters[1])
            result.append(temp)

        return result
