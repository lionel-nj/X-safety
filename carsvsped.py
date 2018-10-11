import cars
from trafficintelligence import moving
import random
# from toolkit import *
import toolkit



class Alignment(object):
    #représentation des voies : liste de points
    def __init__(self,id = None,points = [],width = None,control_device = None):
        self.id = id
        self.points = points
        self.width = width
        self.control_device = control_device

    def __repr__(self):
        return "id: {}, width:{}".format(self.id, self.width)

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
    def __init__(self,flow_vertical = None ,flow_horizontal = None,ped_h = None,ped_v = None,horizontal_alignment = None,vertical_alignment = None,control_device_horizontal = None, control_device_vertical = None, crossing_zone = None, crossing_point = None):
        self.flow_vertical = flow_vertical
        self.flow_horizontal = flow_horizontal
        self.ped_h = ped_h
        self.ped_v = ped_v
        self.horizontal_alignment = horizontal_alignment
        self.vertical_alignment = vertical_alignment
        self.control_device_vertical = control_device_vertical
        self.control_device_horizontal = control_device_horizontal
        self.crossing_point = crossing_point
        self.crossing_zone = crossing_zone

    def __repr__(self):
        return "flow_vertical: {}, flow_horizontal: {}, ped_h: {}, ped_v: {}, horizontal_alignment: {}, vertical_alignment: {}, control_device: {}".format(self.flow_vertical,self.flow_horizontal,self.ped_h,self.ped_v,self.horizontal_alignment,self.vertical_alignment,self.control_device)

    def loadWorld(self,file):
        return load_yml(file)

    def saveWorld(self):
        data = dict()
        data[0] = self.flow_vertical
        data[1] = self.flow_horizontal
        data[2] = self.ped_h
        data[3] = self.ped_v
        data[4] = self.horizontal_alignment
        data[5] = self.vertical_alignment
        data[6] = self.control_device_vertical
        data[7] = self.control_device_horizontal
        data[8] = self.crossing_zone
        data[9] = self.crossing_point

        return create_yaml('world.yml',data)

    def initialiseWorld(self):
        self.flow_vertical = cars.flow(moving.Point(0,1),'verticale.yml').generateTrajectories()[0]
        self.flow_horizontal = cars.flow.generateTrajectories(cars.flow(moving.Point(1,0),'horizontale.yml'))[0]
        self.ped_h = None
        self.ped_v = None
        self.horizontal_alignment = None
        self.vertical_alignment = None
        self.control_device = None
        self.crossing_point = moving.Trajectory.getIntersections(self.horizontal_alignment,self.vertical_alignment[0],self.vertical_alignment[-1])
        self.p1 = shapelyPoint(self.crossing_point.x+width/2,self.crossing_point.y+width/2)
        self.p2 = shapelyPoint(self.crossing_point.x+width/2,self.crossing_point.y-width/2)
        self.pi1 = moving.Point(self.crossing_point.x-width/2,self.crossing_point.y)
        self.pi2 = moving.Point(self.crossing_point.x,self.crossing_point.y-width/2)
        self.p3 = shapelyPointshapelyPoint(self.crossing_point.x-width/2,self.crossing_point.y-width/2)
        self.p4 = shapelyPoint(self.crossing_point.x-width/2,self.crossing_point.y+width/2)
        self.pointList = p1, p2, p3, p4]
        self.crossing_zone = Polygon([[p.x, p.y] for p in pointList])

         for k in range(0,len(self.flow_vertical)):
             if self.horizontal_alignment == None:
                 self.flow_vertical[k].curvilinearPositions = moving.CurvilinearTrajectory()
             else:
                 self.flow_vertical[k].curvilinearPositions = getCurvilinearTrajectoryFromTrajectory(vehicle.positions,[horizontal_alignment,vertical_alignment])

         for k in range(0,len(self.flow_horizontal)):
             if self.vertical_alignment == None:
                 self.flow_horizontal[k].curvilinearPositions = moving.CurvilinearTrajectory()
             else:
                 self.flow_horizontal[k].curvilinearPositions = getCurvilinearTrajectoryFromTrajectory(vehicle.positions,[horizontal_alignment,vertical_alignment])


    def distanceMinVerifiee(self,direction,flow,i,j,t,dmin):

        if direction == 'horizontale':
            if flow == 1:
                if cars.gap(self.flow_vertical[i].positions[t].x,self.flow_vertical[j].positions[t].x,(self.flow_vertical[i].geometry.length-2*1.8)/2) > dmin:
                    return True
            elif flow == 2:
                if cars.gap(self.flow_horizontal[i].positions[t].x,self.flow_horizontal[j].positions[t].x,(self.flow_horizontal[i].geometry.length-2*1.8)/2) > dmin:
                    return True
                return False
        elif direction == 'verticale':
            if flow == 2:
                if cars.gap(self.flow_horizontal[i].positions[t].y,self.flow_horizontal[j].positions[t].y,(self.flow_horizontal[i].geometry.length-2*1.8)/2) > dmin:
                    return True
            elif flow == 1:
                if cars.gap(self.flow_vertical[i].positions[t].y,self.flow_vertical[j].positions[t].y,(self.flow_vertical[i].geometry.length-2*1.8)/2) > dmin:
                    return True
                return False

    def existingUsers(self,t):

        rep = []
        for k in range(0,len(self.flow_vertical)):
            if moving.Interval.contains(self.flow_vertical[k].getTimeInterval(),t):
                rep.append(self.flow_vertical[k])
        for k in range(0,len(self.flow_horizontal)):
            if moving.Interval.contains(self.flow_horizontal[k].getTimeInterval(),t):
                rep.append(self.flow_horizontal[k])
        for k in range(0,len(self.ped_h)):
            if moving.Interval.contains(self.ped_h[k].getTimeInterval(),t):
                rep.append(self.ped_h[k])
        for k in range(0,len(self.ped_v)):
            if moving.Interval.contains(self.ped_v[k].getTimeInterval(),t):
                rep.append(self.ped_v[k])
        return rep

    def typeOfUserAhead(self,objet,t):

        dist = []
        utilisateurs_existants = World.existingUsers(self,t)

        for k in range(0,len(utilisateurs_existants)):
            if utilisateurs_existants[k] == objet:
                utilisateurs_existants.pop(k)
                break

        if objet.etiquette == 'verticale':
            a = objet.positions[t].y
            for k in range (len(utilisateurs_existants)):
                b = utilisateurs_existants[k].positions[t].y
                d = b-a
                if d < 0:
                    dist.append(float('inf'))
                else:
                    dist.append(d)

        elif objet.etiquette == 'horizontale':
            a = objet.positions[t].x
            for k in range (len(utilisateurs_existants)):
                b = utilisateurs_existants[k].positions[t].y
                d = b-a
                if d < 0:
                    dist.append(float('inf'))
                else:
                    dist.append(d)

        return moving.MovingObject.getUserType(utilisateurs_existants[dist.index(min(dist))])

    def isAnEncounter(self,i,j,t,dmin):

        p1 = self.flow_vertical[i].positions[t]
        p2 = self.flow_horizontal[j].positions[t]
        distance = moving.Point.distanceNorm2(p1,p2)

        if distance <= dmin:
            return True,distance
        else:
            return False,distance

    def countEncounters(self,dmin):

        columns = len(self.flow_vertical)
        lines = len(self.flow_horizontal)
        matrix = [([0]*columns)]*lines
        c = 0

        for h in range(columns):
            matrix[h] = [(0,0)]*lines

        for t in range(90):
            for v in range(columns):
                for h in range(lines):
                    # print(h,v,self.isAnEncounter(h,v,t,500))
                    if self.isAnEncounter(h,v,t,dmin)[0] == True and matrix[h][v] == (0,0):
                        matrix[h][v] = self.isAnEncounter(h,v,t,dmin)[1]
                        c = c+1
        return matrix,c

    def distanceToCD(vehicle,time,control_device):
        p1=vehicle.positions[time]
        p2=control_device.position
        return moving.distanceNorm2(p1,p2)

    def stopsAt(vehicle,time):
        for k in range(time,len(vehicle.positions)):
            vehicle.velocities[k] = moving.Point(0,0)
            vehicle.positions[k] = vehicle.positions[k-1]

    def hasPassedCrossingZoneAt(vehicle,t,crossing_point):
        x_veh = vehicle.positions[t].x
        y_veh = vehicle.positions[t].y
        right_edge = moving.Point(crossing_point.x+3.5/2,crossing_point.y)
        upper_edge = moving.Point(crossing_point.x,crossing_point.y+3.5/2)
        if (x_veh > right_edge.x) or (y_veh > upper_edge.y):
            return True
        else:
            return False

    def takeSecond(elem):
        '''utile pour la fonction getDistanceToZone, permet par la suite d'effectuer un tri'''
        return elem[1]

    def getDistanceToZone(vehicle,t,crossing_point):
        '''renvoiela distance d'un vehicule a la zone de croisement au moment t'''
        left_edge=moving.Point(crossing_point.x-3.5/2,crossing_point.y)

        d = moving.distanceNorm2(vehicle.positions[t],left_edge)
        return d


    def sortListOfVehiclesByDistanceToCrossingZone(liste_of_vehicles,crossing_point,t):
        ''' fonctin de tri des vehicules selon la distance à la zone de croisement'''
        temp = [] #liste de la forme [(vehicle,distance to zone),...,(vehicle,distance to zone)]
        for key, value in liste_of_vehicles:
            temp.append((value,getDistanceToZone(value,t,crossing_point))
        return sorted(temp, key = takeSecond)

    def detectNextVehiclesToEnterZone(self,flow,time):
        '''fonction de détection qui renvoie les prochains vehicules à pénétrer la zone, au moment t'''
        list_of_vehicles = []
        zone = self.crossing_zone
        for key, value in self.flow_horizontal.items():
            if not hasPassedCrossingZoneAt(value,time,self.crossing_point):
                list_of_vehicles.append(value)
        return sortListOfVehiclesByDistanceToCrossingZone(list_of_vehicles,zone,time)

    def getCurvilinearTrajectoryFromTrajectoryUntil(ct,t):
    def putCurvilinearTrajectoriesTogetherFrom(ct1,ct2,t):

    def go(vehicle,time,t_simul):
        v0 = moving.Point(2,3).__mul__(45) #récupérer vitesse souhaitée par le véhicule à l'instant  t=0 so .. ligne à modifier radicalement
        for time in range (time, len(t_simul)):
            vehicle.velocities.append(v0)
            vehicle.positions[t] = cars.flow.positionV(vehicle.positions[t-1],v0,t,2000)
        vehicle.getCurvilinearTrajectoryFromTrajectoryUntil(time)
        vehicle.putTogetherCurvilinearTrajectoriesFrom(time)
    #
    # def followingVehiclesAdapt(veh_key,flow,time,stopped):
    #     if stopped == True:
    #         #blabla d'Adaptation des vitesses/position des vehicules suiveurs
    #         for k in range(veh_key+1,len(flow_horizontal)):
    #             for t in range(time+1,len(flow_horizontal.positions)):

    def adaptSpeedsByControlDevice(self):
        stopped = False
        pointI = self.p4
        pointD = self.p1
        if self.control_device_vertical.category == 0 and self.control_device_horizontal.category == 3:
            for key, value in self.flow_vertical.items():
                for t in range(len(self.flow_vertical)):
                    s = 0
                    if distanceToCD(value,t,stop_sign) > 1:
                        stopped = False
                        followingVehiclesAdapt(self.flow_vertical,time,stopped)
                    else:
                        stopped = True
                        stopsAt(value,time)
                        followingVehiclesAdapt(self.flow_vertical,time,stopped)
                        # waitNSecondsAtStop(2)
                        next_vehicles_to_enter_zone = detectNextVehiclesToEnterZone(self.flow_horizontal,time)
                        d = moving.distanceNorm2(next_vehicles_to_enter_zone[0].positions[time],pointI)
                        v = next_vehicle_to_enter_zone.velocities[time]
                        time_window = d/v

                        d = moivng.distanceNorm2(value.positions[t],pointD)
                        v = value.velocites[time]
                        time_to_pass = d/v

                        c = 0

                        while time_window > time_to_pass:
                            c += 1
                            d = moving.distanceNorm2(next_vehicles_to_enter_zone[c].positions[time],pointI)
                            v = next_vehicles_to_enter_zone[c].velocities[time]
                            time_window = d/v #avec le prochain vehicule a entrer la zone
                            s += time_window
                            stopped = True
                            followingVehiclesAdapt(self.flow_vertical,time,stopped)



                        stopped = False
                        go(value,time+t_stop+s)
                        followingVehiclesAdapt(self.flow_vertical,time,stopped)
                    break
