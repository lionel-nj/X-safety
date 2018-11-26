import cars
from trafficintelligence import moving
import random
import toolkit
import math

class Alignment():
    '''Description of road lanes (centre line of a lane)
    point represents the lane geometry (type is moving.Trajectory) '''
    def __init__(self, idx = None, points = None, width = None, controlDevice = None):
        self.idx = idx
        self.points = points
        self.width = width
        self.controlDevice = controlDevice
        #self.volume = volume

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
        if self.crossing_point == self.points[0] :
            self.distance_to_crossing_point = 0


        elif self.points[-1] == self.crossing_point :
            self.distance_to_crossing_point = self.points.getCumulativeDistance(len(self.points))

        else:
            for k in range (len(self.points)-1):
                print(k)
                if Alignment.isBetween(self.points[k],self.points[k+1],self.crossing_point):
                    Alignment.insertPointAt(self,self.crossing_point,k+1)
                    self.points.computeCumulativeDistances()
                    self.distance_to_crossing_point = self.points.getCumulativeDistance(k+1)
                    break


    def connectAlignments(self,other):
        ''' adds a connected_alignment_idx & a crossing_point member to the alignment
         identifie le point x,y de croisement'''
        self.connected_alignment_idx = other.idx #mise en relation des aligments qui s'entrecroisent
        other.connected_alignment_idx = self.idx #mise en relation des aligments qui s'entrecroisent
        self.crossing_point = self.points.getIntersections(other.points[0],other.points[-1])[1][0]
        other.crossing_point = other.points.getIntersections(self.points[0],self.points[-1])[1][0]

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
        which means that both of the alignments in input have a crossing_point attribute
        inputs : alignments
        output : angle (degrees) at the crssoing point of the alignments '''

        crossing_point = self.crossing_point
        first_index_of_cp = 0
        second_index_of_cp = 0

        while self.points[first_index_of_cp] != crossing_point:
            first_index_of_cp += 1
        while other.points[second_index_of_cp] != crossing_point:
            second_index_of_cp += 1

        first_point = self.points.__getitem__(first_index_of_cp-1)
        second_point = other.points.__getitem__(second_index_of_cp-1)

        v1 = crossing_point - first_point
        v2 = crossing_point - second_point

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

    def __init__(self, position = None, alignmentIdx = None, category = None):
        self.position = position
        self.alignmentIdx = alignmentIdx
        self.category = category

    def __repr__(self):
        return "position:{}, alignment:{}, category:{}".format(self.position, self.alignmentIdx, self.category)


class World():
    '''Description of the world, including the road (alignments), control devices (signs, traffic lights) and crossing point '''
    def __init__(self,vehicles = None ,pedestrians = None, alignments = None, controlDevices = None, crossingPoint = None):
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

    def existingUsers(self,t):

        result = []
        for k in range(0,len(self.vehicles)):
            if moving.Interval.contains(self.vehicles[k].getTimeInterval(),t):
                result.append(self.vehicles[k])

        for k in range(0,len(self.pedestrians)):
            if moving.Interval.contains(self.pedestrians[k].getTimeInterval(),t):
                result.append(self.pedestrians[k])

        return sorted(result, key = takeEntry)

    def distanceMinVerifiee(self,alignment_idx_i,alignment_idx_j,i,j,t,dmin):
        ''' checks if the minimum distance headway between two vehicles is verified '''
        if alignment_idx_j == alignment_idx_i:
            d = cars.VehicleInput.gap(self.vehicles[alignment_idx_i][i].curvilinearPositions[t][0],self.vehicles[alignment_idx_j][j].curvilinearPositions[t][0],6)
            if d > dmin:
                return True,cars.VehicleInput.gap(self.vehicles[alignment_idx_i][i].curvilinearPositions[t][0],self.vehicles[alignment_idx_j][j].curvilinearPositions[t][0],6)
            return False,cars.VehicleInput.gap(self.vehicles[alignment_idx_i][i].curvilinearPositions[t][0],self.vehicles[alignment_idx_j][j].curvilinearPositions[t][0],6)

        else :
            angle = self.alignments[0].angleAtCrossingPoint(self.alignments[1])
            d1 = self.vehicles[alignment_idx_i][i].curvilinearPositions[t][0]-self.alignments[alignment_idx_i].distance_to_crossing_point
            d2 = self.vehicles[alignment_idx_j][j].curvilinearPositions[t][0]-self.alignments[alignment_idx_j].distance_to_crossing_point
            d = (d1**2+d2**2-2*d1*d2*math.cos(angle))**(0.5) #loi des cosinus
            if d > dmin:
                return True,d
            else:
                return False,d

    def isAnEncounter(self,alignment_idx_i,alignment_idx_j,i,j,t,dmin):
        ''' checks if there is an accounter between two vehicules
        alignment_idx_i and alignment_idx_j are integers
        i,j : integers
        t : time, integer
        dmin : float  '''
        d = self.distanceMinVerifiee(alignment_idx_i,alignment_idx_j,i,j,t,dmin)[1]
        if self.distanceMinVerifiee(alignment_idx_i,alignment_idx_j,i,j,t,dmin)[0] == True :
            return False,d
        else :
            return True,d

    def countAllEncounters(self,dmin):
        '''counts the encounters in a world
        dmin : float'''

        columns = len(self.vehicles[0])
        lines = len(self.vehicles[1])

        matrix_intersection = [([0]*columns)]*lines
        matrix_voie1 =[('x')]*columns
        matrix_voie0 = [('x')]*lines

        c0 = 0
        c1 = 0
        c2 = 0

        for v in range(columns):
            matrix_intersection[v] = [('x')]*lines

        #interactions sur la meme voie verticale
        for t in range(0,len(self.vehicles[1][0].curvilinearPositions)):
            for v in range(1,lines):
                if self.isAnEncounter(1,1,v,v-1,t,dmin)[0] == True and matrix_voie0[v] != 1 and 10 <= self.vehicles[1][v].curvilinearPositions[t][0]:
                    matrix_voie0[v] = 1
                    c0 = c0+1

        #interactions sur la meme voie horizontale
        for t in range(0,len(self.vehicles[0][0].curvilinearPositions)):
            for h in range(1,columns):
                if self.isAnEncounter(0,0,h,h-1,t,dmin)[0] == True and matrix_voie1[h] != 1 and 10 <= self.vehicles[0][h].curvilinearPositions[t][0] :
                    matrix_voie1[h] = 1
                    c1 = c1+1


        #interactions croisées
        for t in range(0,len(self.vehicles[0][0].curvilinearPositions)):
            for h in range(lines):
                for v in range(columns):
                    # print(h,v,self.isAnEncounter(h,v,t,500))
                    if self.isAnEncounter(0,1,h,v,t,dmin)[0] == True and matrix_intersection[h][v] == ('x') and 10 <= self.vehicles[0][h].curvilinearPositions[t][0] and 10 <= self.vehicles[1][v].curvilinearPositions[t][0]:
                        matrix_intersection[h][v] = 1
                        c2 = c2+1
                        break
        return c0,c1,c2,c0+c1+c2,matrix_intersection, matrix_voie0, matrix_voie1

    def addGhostVehiclesToFile(self, t_simul, alignment):
        ghostVehicle = cars.VehicleInput.generateGhostVehicle(t_simul,alignment)
        n = len(self.vehicles[alignment.idx])
        self.vehicles[alignment.idx][n] = ghostVehicle
        self.save(alignment.name)

    def generateGhostsIfVolumeAreDifferent(self, t_simul):
        if self.alignments[0].volume != self.alignments[1].volume:
            for k in range(round(abs((self.alignments[0].volume - self.alignments[1].volume) * t_simul)/3600)):
                if self.alignments[0].volume > self.alignments[1].volume:
                    self.addGhostVehiclesToFile(t_simul, self.alignments[1])
                else :
                    self.addGhostVehiclesToFile(t_simul, self.alignments[0])

    def trace(self,alignment_idx):
        import matplotlib.pyplot as plt
        temps = toolkit.load_yaml('intervals.yml')
        x = []
        # v = []

        for k in range (0,len(self.vehicles[alignment_idx])):
            x.append([])
            # v.append([])

            for time in range(0,len(self.vehicles[alignment_idx][0].curvilinearPositions)):
                # v[k].append(self.vehicles[alignment_idx][k].velocities[time])
                x[k].append(self.vehicles[alignment_idx][k].curvilinearPositions[time][0])
                ylabel = "position on x axis"

            plt.plot(temps[k],x[k])

        plt.xlabel('t')
        plt.ylabel('x')
        plt.show()
        plt.close()
