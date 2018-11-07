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
        # self.connected_alignment_idx = connected_alignment_idx
        # self.crossing_point = self.points.getIntersections(connected_alignment_idx[0],connected_alignment_idx[-1])

        #point de croisement à créer par la suite !
        #ajouter l'id de l'Alignment aveec lequel il y a le croisement
        #
    #
    # def __repr__(self):
    #     return "id: {}, width:{}, control device:{}, connected to alignment:{}, at:{}".format(self.id, self.width, self.controlDevice, self.connected_alignment_id)

    def addPoint(self,x,y):
        self.points.addPositionXY(x,y)
        # print("le point:({},{}) a été ajouté".format(x,y))

    def setPoint(self,i,x,y):
        self.points.setPositionXY(i,x,y)
        #print("le point:({},{}) a été mis à la position{}".format(x,y,i))

    def insertPointAt(self,p,i):
        '''insere un point p dans un alignement à une position i'''
        avant = moving.Trajectory()

        for k in range(0,i):
            avant.addPosition(self.points[k])

        avant.addPosition(p)

        alignment_until_point = avant

        for k in range(i,len(self.points)):
            avant.addPosition(self.points[k])

        self.points = avant

    def insertCrossingPoint(self):
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
        '''ajoute un membre connected_alignment_idx à l'alignement : identifie l'alignement avec lequel il y a croisement
        ajoute un membre crossing_point : identifie le point x,y de croisement'''
        self.connected_alignment_idx = other.idx #mise en relation des aligments qui s'entrecroisent
        other.connected_alignment_idx = self.idx #mise en relation des aligments qui s'entrecroisent
        self.crossing_point = self.points.getIntersections(other.points[0],other.points[-1])[1][0]
        other.crossing_point = other.points.getIntersections(self.points[0],self.points[-1])[1][0]

        self.insertCrossingPoint()
        other.insertCrossingPoint()

    def isConnectedTo(self,other):
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
    '''Description of the world, including the road (alignments), control devices (signs, traffic lights) and crossing points '''
    def __init__(self,vehicles = None ,pedestrians = None, alignments = None, controlDevices = None, crossingPoints = None):
        self.vehicles = vehicles # dict de veh
        self.pedestrians = pedestrians #sorted dict de ped
        self.alignments = alignments #liste de alignements
        self.controlDevices = controlDevices #liste de CD
        self.crossingPoints = crossingPoints #point

    def __repr__(self):
        return "vehicles: {}, pedestrians: {}, alignments: {}, control devices: {}".format(self.vehicles,self.pedestrians,self.alignments,self.controlDevices)

    @staticmethod
    def load(filename):
        return toolkit.load_yaml(filename)

    def save(self, filename):
        toolkit.save_yaml(filename, self)

    # def initialiseWorld(self):
    #     # self.vehicles = cars.vehicles(moving.Point(0,1),'verticale.yml').generateTrajectories()[0]
    #     self.pedestrians = None
    #     self.alignment = None
    #     self.controlDevice = None
    #
    #     if self.horizontal_alignment != None or self.vertical_alignment != None :
    #         self.crossing_point = moving.Trajectory.getIntersections(self.horizontal_alignment,self.vertical_alignment[0],self.vertical_alignment[-1])
    #         p1 = shapelyPoint(self.crossing_point.x+width/2,self.crossing_point.y+width/2)
    #         p2 = shapelyPoint(self.crossing_point.x+width/2,self.crossing_point.y-width/2)
    #         pi1 = moving.Point(self.crossing_point.x-width/2,self.crossing_point.y)
    #         pi2 = moving.Point(self.crossing_point.x,self.crossing_point.y-width/2)
    #         p3 = shapelyPointshapelyPoint(self.crossing_point.x-width/2,self.crossing_point.y-width/2)
    #         p4 = shapelyPoint(self.crossing_point.x-width/2,self.crossing_point.y+width/2)
    #         pointList = [p1, p2, p3, p4]
    #         self.crossing_zone = Polygon([[p.x, p.y] for p in pointList])
        #
        # for k in range(0,len(self.vehicles)):
        #     if self.horizontal_alignment == None:
        #         self.vehicles[k].curvilinearPositions = moving.CurvilinearTrajectory()
        #     else:
        #         self.vehicles[k].curvilinearPositions = getCurvilinearTrajectoryFromTrajectory(vehicle.positions,[horizontal_alignment,vertical_alignment])
        #
        # for k in range(0,len(self.vehicles)):
        #     if self.vertical_alignment == None:
        #         self.vehicles[k].curvilinearPositions = moving.CurvilinearTrajectory()
        #     else:
        #         self.vehicles[k].curvilinearPositions = getCurvilinearTrajectoryFromTrajectory(vehicle.positions,[horizontal_alignment,vertical_alignment])

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

        #
        # def typeOfUserAhead(self,i,t):
        #
        #     dist = []
        #     existing_users = World.existingUsers(self,t)
        #
        #     if i > 0 :
        #         a = self.vehicles[i].positions[t]
        #         for k in range (len(existing_users)):
        #             b = existing_users[k].positions[t]
        #             d = b-a
        #             if d < 0:
        #                 dist.append(float('inf'))
        #             else:
        #                 dist.append(d)
        #
        #         return moving.MovingObject.getUserType(existing_users[dist.index(min(dist))])

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
        import matlplotlib.pyplot as plt
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
#
#     def stopsAt(self,vehicle,time):
#         '''arrête un véhicule à partir d'un instant t
#         TODO : mettre à jour les curvilinearPosition: necessitera les alignements'''
#         for k in range(time,len(vehicle.positions)):
#
#             vehicle.velocities[k] = moving.Point('x')
#             vehicle.positions.setPositionXY(k,vehicle.positions[k-1].x,vehicle.positions[k-1].y)
#
#     def hasPassedCrossingZoneAt(self,vehicle,t,crossing_point):
#         '''fonction retournant True si le vehicule etudie a dépassé la zone de croisement, False sinon'''
#         x_veh = vehicle.positions[t].x
#         y_veh = vehicle.positions[t].y
#         right_edge = moving.Point(crossing_point.x+3.5/2,crossing_point.y)
#         upper_edge = moving.Point(crossing_point.x,crossing_point.y+3.5/2)
#         if (x_veh > right_edge.x) or (y_veh > upper_edge.y):
#             return True
#         else:
#             return False
#
#     def detectNextVehiclesToEnterZone(self,vehicles,time,crossing_point):
#         '''fonction de détection qui renvoie les prochains vehicules à pénétrer la zone, au moment t'''
#         list_of_vehicles = sortedListOfVehiclesByDistanceToCrossingZone(self.vehicles,crossing_point,time)
#         result = []
#         for value in list_of_vehicles:
#             if not self.hasPassedCrossingZoneAt(value,time,crossing_point):
#                 result.append(value)
#         return result
#
#     def followingVehiclesAdapt(self,stopped_vehicle_key,time,stopped):
#         ''' fonction d'adaptation des vitesses/position des vehicules suiveurs'''
#         if stopped == True: # si le vehicule est arrêté alors on adapte la vitesse des vehicules suiveurs.
#
#             p1 = self.vehicles[stopped_vehicle_key].positions[time]
#             v1 = self.vehicles[stopped_vehicle_key].velocities[time]
#
#             for k in range(stopped_vehicle_key+1,len(self.vehicles)): #a partir du premier vehicule suiveur
#
#                 v0 = self.direction.__mul__(random.normalvariate(30,3.2)) #vitesse random..idéalement récupérer la vitesse souhaitée initialement !!
#                 l = (monde.vehicles[k].geometry.length-3.6)/2
#
#                 for t in range(time,len(self.vehicles.positions)):
#
#                     p = self.vehicles[k].positions[t-1].y #position précédente du vehicule (à t-1)
#                     v = moving.Point.norm2(moving.MovingObject.getVelocities(self.vehicles[k-1])[t]) #vitesse du vehicule précédent à l'instant t
#                     velocite = moving.Point(0,1).__mul__(moving.Point.norm2(v0))
#                     new_position = vehicles.positionV(p,moving.Point.norm2(velocite),t,2000)
#                     # s = gap(moving.MovingObject.getPositions(data_vehicles[k-1])[t].y,new_position.y,L[k-1])
#                     l = (monde.vehicles[k-1].geometry.length-3.6)/2
#                     s = vehicles.gap(data_vehicles[k-1].positions[t].y,new_position.y,L[k-1])
#                     smin = 25
#
#                     if s < smin:
#                         velocite = self.direction.__mul__((v*t-L[k-1]-smin)/t)
#
#                     if velocite.y < 0:
#                         velocite = moving.Point('x')
#
#                 self.vehicles[k].velocities = velocite
#                 moving.Trajectory.setPositionXY(k,positionV(p,moving.Point.norm2(velocite),1,2000).x,positionV(p,moving.Point.norm2(velocite),1,2000).y)
#
#         else:
#             None
#
#     def adaptSpeedsByControlDevice(self):
#         stopped = False
#         pointI = self.p4
#         pointD = self.p1
#         if self.controlDevice_vertical.category == 0 and self.controlDevice_horizontal.category == 3:
#             for key, value in self.vehicles.items():
#                 for t in range(len(self.vehicles)):
#                     s = 0
#                     if distanceToCD(value,t,stop_sign) > 1:
#                         stopped = False
#                         followingVehiclesAdapt(self,key,t,stopped)
#                     else:
#                         stopped = True
#                         stopsAt(value,time)
#                         followingVehiclesAdapt(self,key,t,stopped)
#                         # waitNSecondsAtStop(2)
#                         next_vehiclesto_enter_zone = detectNextVehiclesToEnterZone(self.vehicles,time)
#                         time_window = moving.distanceNorm2(next_vehiclesto_enter_zone[0].positions[time],pointI)/(next_vehicle_to_enter_zone.velocities[time])
#                         time_to_pass = moving.distanceNorm2(value.positions[t],pointD)/(value.velocites[time])
#
#                         c = 0
#
#
#                         while time_window > time_to_pass:
#                             c += 1
#                             d = moving.distanceNorm2(next_vehiclesto_enter_zone[c].positions[time],pointI)
#                             v = next_vehiclesto_enter_zone[c].velocities[time]
#                             time_window = d/v #avec le prochain vehicule a entrer la zone
#                             s += time_window
#                             stopped = True
#                             followingVehiclesAdapt(self,key,t,stopped)
#
#
#
#                         stopped = False
#                         go(value,time+t_stop+s)
#                         followingVehiclesAdapt(self.vehicles,time,stopped)
#                     break
#         create_yaml('horizontale.yml',self)
#
# def getCurvilinearTrajectoryUntil(ct,t):
#     '''récupère les informations d'une curvilinear trajectory jusqu'à l'instant t'''
#     new_ct = moving.CurvilinearTrajectory()
#     for k in range(t+1):
#         new_ct.addPositionSYL(ct[k][0],ct[k][1],ct[k][2])
#     return new_ct
#
# def putCurvilinearTrajectoriesTogetherFrom(ct1,ct2,t):
#     '''assemble deux curvilinear trajectory, à partir d'un instant t'''
#     new_ct = getCurvilinearTrajectoryUntil(ct1,t)
#     for k in range(t,len(ct2)):
#         new_ct.addPositionSYL(ct2[k][0],ct2[k][1],ct2[k][2])
#     return new_ct
#
# def distanceToCD(vehicle,time,controlDevice):
#     '''calcule la distance restante a l'outil de controle'''
#     if controlDevice.alignment_idx == vehicle.curvilinearPositions.lanes[0]:
#         p1=vehicle.positions[time]
#         p2=controlDevice.position
#         return moving.Point.distanceNorm2(p1,p2)
#     else:
#         return ('Erreur, vehicule et CD pas sur le même alignement : calcul non realisable')
#
# def getDistanceToZone(vehicle,t,crossing_point):
#     '''renvoiela distance d'un vehicule a la zone de croisement au moment t'''
#     left_edge=moving.Point(crossing_point.x-3.5/2,crossing_point.y)
#     d = moving.Point.distanceNorm2(vehicle.positions[t],left_edge)
#     return d
#
# def takeSecond(elem):
#     '''fonction annexe qui permet de récupérer le 2e element d'une liste, utilisé après pour etre un critère de tri'''
#     return elem[1]
#
# def sortedListOfVehiclesByDistanceToCrossingZone(liste_of_vehicles,crossing_point,t):
#     '''fonction de tri des vehicules selon la distance à la zone de croisement, au temps t'''
#     result = []
#     temp = [] #liste de la forme [(vehicle,distance to zone),...,(vehicle,distance to zone)]
#     for key, value in liste_of_vehicles.items():
#         temp.append((value,getDistanceToZone(value,t,crossing_point)))
#     temp = sorted(temp, key = takeSecond)
#     for k in range(len(temp)):
#         result.append(temp[k][0])
#     return result
#
# def go(vehicle,time,t_simul):
#     '''fonction donnant l'ordre à un vehicule de repartir
#     TODO : recupérer la vitesse souhaitee par le vehicule avant qu'il ne s'arrête !!! '''
#     v0 = moving.Point(2,3).__mul__(45) #ligne exemple pour pouvoir faire fourner le truc
#     for t in range (time,t_simul):
#         vehicle.velocities[t] = v0
#         vehicle.positions.setPositionXY(t,cars.vehicles.positionV(vehicle.positions[t-1].x,v0.norm2(),1,2000).x,cars.vehicles.positionV(vehicle.positions[t-1].x,v0.norm2(),1,2000).y)
#     #
#         # vehicle.getCurvilinearTrajectoryUntil(time)
        # vehicle.putCurvilinearTrajectoriesTogetherFrom(time)
