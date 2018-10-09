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

    types = {'stop':0,
          'yield':1,
          'red light':2,
          'free':3}

    def __init__(self, position = None, alignment_id = None, category = None):
        self.position = position
        self.alignment_id = alignment_id
        self.category = category

    def __repr__(self):
        return "position:{}, alignment:{}, type{}".format(self.position, self.alignment_id, self.type)


class World():
    #monde
    def __init__(self,flow_vertical = None ,flow_horizontal = None,ped_h = None,ped_v = None,horizontal_alignment = None,vertical_alignment = None,control_device = None):
        self.flow_vertical = flow_vertical
        self.flow_horizontal = flow_horizontal
        self.ped_h = ped_h
        self.ped_v = ped_v
        self.horizontal_alignment = horizontal_alignment
        self.vertical_alignment = vertical_alignment
        self.control_device = control_device

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
        data[6] = self.control_device

        return create_yaml('world.yml',data)

    def initialiseWorld(self):
         self.flow_vertical = cars.flow(moving.Point(0,1),'verticale.yml').generateTrajectories()[0]
         self.flow_horizontal = cars.flow.generateTrajectories(cars.flow(moving.Point(1,0),'horizontale.yml'))[0]
         self.ped_h = None
         self.ped_v = None
         self.horizontal_alignment = None
         self.vertical_alignment = None
         self.control_device = None

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
                    if self.isAnEncounter(h,v,t,dmin)[0] == True and matrix[h][v] == (0,0) :
                        matrix[h][v] = self.isAnEncounter(h,v,t,dmin)[1]
                        c = c+1
        return matrix,c

    def adaptSpeedsAccordingToControlDeviceOnWays(self):
        if self.control_device_vertical.category == 0 and self.control_device_horizontal.category == 3:
            #blabla en cas de présence de stop sur la voie
            #modifier les vitesses des vehicules sur la voie verticale
            for vehicles in self.flow_vertical:
                while distance_to_stop(vehicle(t))>2:
                    t += 1

        elif self.control_device_vertical.category == 3 and self.control_device_horizontal.category == 0:
            #modifier les vitesse des vehicules sur la voie horizontale
