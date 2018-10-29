import cars
from trafficintelligence import moving
import random
from toolkit import *
import toolkit

parameters = load_yml('config.yml')

t_simul = parameters['simulation']['t_simulation']
delta_t = parameters['simulation']['delta_t']
number_of_cars = parameters['simulation']['number_of_cars']
dmin = parameters['interactions']['dmin']

class Alignment():
    #représentation des voies : liste de points
    def __init__(self, id = None, points = [], width = None, control_device = None, debit = None):
        self.id = id
        self.points = points
        self.width = width
        self.control_device = control_device
        self.debit = debit


    def __repr__(self):
        return "id: {}, width:{}".format(self.id, self.width)

    def addPoint(self,x,y):
        self.points.addPositionXY(x,y)
        # print("le point:({},{}) a été ajouté".format(x,y))

    def setPoint(self,i,x,y):
        self.points.setPositionXY(i,x,y)
        print("le point:({},{}) a été mis à la position{}".format(x,y,i))

class ControlDevice():
    #outil de control

    cat = {'stop' : 0,
          'yield' : 1,
          'red light' : 2,
          'free' : 3}

    def __init__(self, position = None, alignment_id = None, category = None):
        self.position = position
        self.alignment_id = alignment_id
        self.category = category

    def __repr__(self):
        return "position:{}, alignment:{}, type{}".format(self.position, self.alignment_id, self.type)


class World():
    #monde
    def __init__(self,vehicles = None ,pedestrians = None, alignments = None, control_devices = None, crossing_point = None):
        self.vehicles = vehicles #sorted dict de veh
        self.pedestrians = pedestrians #sorted dict de ped
        self.alignments = alignments #liste de alignements
        self.control_devices = control_devices #liste de CD
        self.crossing_point = crossing_point #point

    def __repr__(self):
        return "vehicles: {}, pedestrians: {}, alignments: {}, control_device: {}".format(self.vehicles,self.vehicles,self.pedestrians,self.ped_v,self.horizontal_alignment,self.vertical_alignment,self.control_device)

    def loadWorld(self,file):
        return load_yml(file)

    def saveWorld(self):
        data = dict()
        data[0] = self.vehicles
        data[1] = self.pedestrians
        data[2] = self.alignments
        data[3] = self.control_devices
        data[4] = self.crossing_point

        return create_yaml('world.yml',data)

    # def initialiseWorld(self):
    #     # self.vehicles = cars.vehicles(moving.Point(0,1),'verticale.yml').generateTrajectories()[0]
    #     self.pedestrians = None
    #     self.alignment = None
    #     self.control_device = None
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


    def distanceMinVerifiee(self,alignment_id_i,alignment_id_j,vehicles,i,j,t):
        if alignment_id_j == alignment_id_i:
            if cars.vehicles.gap(vehicles[alignment_id_i][i].positions[t],self.vehicles[alignment_id_j][j].positions[t],6) > dmin:
                return True
            return False
        else :
            if moving.Point.distanceNorm2(vehicles[alignment_id_i][i].positions[t],self.vehicles[alignment_id_j][j].positions[t]) > dmin:
                return True
            else:
                return False

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

    def isAnEncounter(self,i,j,alignment_id_i,alignment_id_j,t):
        ''' verifie s'il y a une rencontre entre deux vehicules '''

        if distanceMinVerifiee(alignment_id_i,alignment_id_j,i,j,t) == True:
            return False
        else :
            return True

    def countEncounters(self):

        vehicles_first_alignment = [] #dictionnaire
        vehicles_second_alignment = [] #dictionnaire

        for k in range(number_of_cars):
            vehicles_first_alignment.append(self.vehicles[0][k])
            vehicles_second_alignment.append(self.vehicles[0][k])

        columns = len(vehicles_first_alignment)
        lines = len(vehicles_second_alignment)

        matrix_intersection = [([0]*columns)]*lines
        matrix_voie1 =[([0]*columns)]*columns
        matrix_voie2 = [([0]*lines)]*lines

        c0 = 0
        c1 = 0
        c2 = 0

        for v in range(columns):
            matrix_intersection[v] = [(0,0)]*lines
            matrix_voie1[v] = [(0,0)]*lines

        for h in range(lines):
            matrix_voie2[v] = [(0,0)]*lines

        #interactions sur la meme voie verticale
        for t in range(t_simul):
            for v1 in range(columns):
                for v2 in range(columns):
                    if self.isAnEncounter(v1,v2,0,0,t) == True and matrix[v1][v2] == (0,0):
                        matrix[v1][v2] = (self.isAnEncounter(v1,v2,0,0,t),t)
                        c0 = c0+1


        #interactions sur la meme voie horizontale
        for t in range(t_simul):
            for h1 in range(lines):
                for h2 in range(lines):
                    if self.isAnEncounter(h1,h2,1,1,t) == True and matrix[h1][h2] == (0,0):
                        matrix[h1][h2] = (self.isAnEncounter(h1,h2,1,1,t),t)
                        c1 = c1+1

        #interactions croisées
        for t in range(t_simul):
            for v in range(columns):
                for h in range(lines):
                    # print(h,v,self.isAnEncounter(h,v,t,500))
                    if self.isAnEncounter(h,v,1,0,t) == True and matrix[h][v] == (0,0):
                        matrix[h][v] = (self.isAnEncounter(h,v,1,0,t),t)
                        c2 = c2+1

        return matrix_intersection,matrix_voie1,matrix_voie2,c2+(c0+c1)/2


#
#     def stopsAt(self,vehicle,time):
#         '''arrête un véhicule à partir d'un instant t
#         TODO : mettre à jour les curvilinearPosition: necessitera les alignements'''
#         for k in range(time,len(vehicle.positions)):
#
#             vehicle.velocities[k] = moving.Point(0,0)
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
#                         velocite = moving.Point(0,0)
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
#         if self.control_device_vertical.category == 0 and self.control_device_horizontal.category == 3:
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
# def distanceToCD(vehicle,time,control_device):
#     '''calcule la distance restante a l'outil de controle'''
#     if control_device.alignment_id == vehicle.curvilinearPositions.lanes[0]:
#         p1=vehicle.positions[time]
#         p2=control_device.position
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
