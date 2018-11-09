import cars
from trafficintelligence import moving
import random
import toolkit

class Alignment():
    '''Description of road lanes (centre line of a lane)
    point represents the lane geometry (type is moving.Trajectory) '''
    def __init__(self, idx = None, points = None, width = None, controlDevice = None):
        self.idx = idx
        self.points = points
        self.width = width
        self.controlDevice = controlDevice
        #self.volume = volume

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

    def insertCrossingPoint(self):
        '''inserts a crossing point : moving.Point in the alignment sequence'''
        if self.crossing_point == self.points[0] :
            self.distance_to_crossing_point = 0

        elif self.points[-1] == self.crossing_point:
            self.distance_to_crossing_point = self.points.getCumulativeDistance(len(self.points))

        else:
            for k in range (len(self.points)-1):
                if self.points[k].x < self.crossing_point.x and self.crossing_point.x < self.points[k+1].x:
                    Alignment.insertPointAt(self,self.crossing_point,k+1)
                    self.points.computeCumulativeDistances()
                    self.distance_to_crossing_point = self.points.getCumulativeDistance(k+1)
                    break
            # elif self.points[k+1].x < self.crossing_point.x:
            #     Alignment.insertPointAt(self,self.crossing_point,k)

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
    def __init__(self,vehicles = None ,pedestrians = None, alignments = None, controlDevices = None, crossingPoints = None):
        self.vehicles = vehicles # dict de veh
        self.pedestrians = pedestrians #sorted dict de ped
        self.alignments = alignments #liste de alignements
        self.controlDevices = controlDevices #liste de CD
        self.crossingPoints = crossingPoints #list of moving.Point

    def __repr__(self):
        return "vehicles: {}, pedestrians: {}, alignments: {}, control devices: {}".format(self.vehicles,self.pedestrians,self.alignments,self.controlDevices)

    @staticmethod
    def load(filename):
        return toolkit.load_yaml(filename)

    def save(self, filename):
        toolkit.save_yaml(filename, self)

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
        '''verifie si la distance min specifiee est respectee'''
        if alignment_idx_j == alignment_idx_i:
            d = cars.VehicleInput.gap(self.vehicles[alignment_idx_i][i].curvilinearPositions[t][0],self.vehicles[alignment_idx_j][j].curvilinearPositions[t][0],6)
            if d > dmin:
                return True,cars.VehicleInput.gap(self.vehicles[alignment_idx_i][i].curvilinearPositions[t][0],self.vehicles[alignment_idx_j][j].curvilinearPositions[t][0],6)
            return False,cars.VehicleInput.gap(self.vehicles[alignment_idx_i][i].curvilinearPositions[t][0],self.vehicles[alignment_idx_j][j].curvilinearPositions[t][0],6)

        else :
            d1 = self.vehicles[alignment_idx_i][i].curvilinearPositions[t][0]-self.alignments[alignment_idx_i].distance_to_crossing_point
            d2 = self.vehicles[alignment_idx_j][j].curvilinearPositions[t][0]-self.alignments[alignment_idx_j].distance_to_crossing_point
            d = (d1**2+d2**2)**(0.5)
            if d > dmin:
                return True,d
            else:
                return False,d

    def isAnEncounter(self,alignment_idx_i,alignment_idx_j,i,j,t,dmin):
        ''' verifie s'il y a une rencontre entre deux vehicules '''
        d = self.distanceMinVerifiee(alignment_idx_i,alignment_idx_j,i,j,t,dmin)[1]
        if self.distanceMinVerifiee(alignment_idx_i,alignment_idx_j,i,j,t,dmin)[0] == True :
            return False,d
        else :
            return True,d

    def countEncounters(self,dmin):
        '''compte les rencontres entre vehicules d'un monde'''

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

        #interactions sur la meme voie horizobntale
        for t in range(200,len(self.vehicles[0][0].curvilinearPositions)):
            for h in range(1,columns):
                if self.isAnEncounter(0,0,h,h-1,t,dmin)[0] == True and matrix_voie1[h] != 1:
                    matrix_voie1[h] = 1

                    # matrix_voie1[h1][h2] = (t,self.isAnEncounter(0,0,h1,h2,t,dmin)[1])
                    c1 = c1+1


        #interactions sur la meme voie verticale
        for t in range(200,len(self.vehicles[0][0].curvilinearPositions)):
            for v in range(1,lines):
                if self.isAnEncounter(1,1,v,v-1,t,dmin)[0] == True and matrix_voie0[v] != 1 :
                    matrix_voie0[v] = 1

                        # matrix_voie0[v1][v2] = (t,self.isAnEncounter(1,1,v1,v2,t,dmin)[1])
                    c0 = c0+1

        #interactions croisées
        for t in range(0,len(self.vehicles[0][0].curvilinearPositions)):
            for h in range(lines):
                for v in range(columns):
                    # print(h,v,self.isAnEncounter(h,v,t,500))
                    if self.isAnEncounter(0,1,h,v,t,dmin)[0] == True and matrix_intersection[h][v] == ('x') :
                        matrix_intersection[h][v] = (h,v,t)
                        # matrix_intersection[h][v] = (t,self.isAnEncounter(0,0,h,v,t,dmin)[1])
                        c2 = c2+1
                        break


        return c0,c1,c2,c0+c1+c2,matrix_intersection

    def trace(self,alignment_idx):
        import matplotlib.pyplot as plt
        temps = toolkit.load_yaml('intervals.yml')
        x = []
        # v = []

        for k in range (0,len(self.vehicles[alignment_idx])):
            x.append([])
            # v.append([])

            for time in range(0,len(self.vehicles[alignment_idx][0].curvilinearPositions)):
                # v[k].append(moving.Point.norm2(list_of_vehicles[k].velocities[time]))
                x[k].append(self.vehicles[alignment_idx][k].curvilinearPositions[time][0])
                ylabel = "position selon l'axe x"

            plt.plot(temps[k],x[k])

        plt.xlabel('t')
        plt.ylabel('x')
        plt.show()
        plt.close()
