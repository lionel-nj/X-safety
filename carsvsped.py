import cars
from trafficintelligence import moving
import random
import toolkit


class Alignment(object):
    #représentation des voies : liste de points
    def __init__(self,alignment_number = None,points = [],width = None,control_device = None):
        self.alignment_number = alignment_number
        self.points = points
        self.width = width
        self.control_device = control_device

    def __repr__(self):

        return "alignment_number: {}, width:{}".format(self.alignment_number, self.width)

class ControlDevice():
    #outil de control

    types = {'stop':0,
          'yield':1,
          'red light':2}

    def __init__(self,curvilinear_position = None,alignment_number = None,type = None):

        self.curvilinearPositions = curvilinear_position
        self.alignment_number = alignment_number
        self.type = type

    def __repr__(self):

        return "abscisse curviligne:{}, alignment:{}, type{}".format(self.curvilinear_position, self.alignment_number, self.type)



class World():
    #monde
    def __init__(self,flow_vertical = None,flow_horizontal = None,ped_h = None,ped_v = None,horizontal_alignment = None,vertical_alignment = None,control_device = None):
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

        return toolkit.load_yml(file)

    def saveWorld(self):

        data = dict()
        data[0] = self.flow_vertical
        data[1] = self.flow_horizontal
        data[2] = self.ped_h
        data[3] = self.ped_v
        data[4] = self.horizontal_alignment
        data[5] = self.vertical_alignment
        data[6] = self.control_device

        return toolkit.create_yaml('world.yml',data)

    def initialiseWorld(self):

         self.flow_vertical = cars.flow(moving.Point(0,1),'verticale.yml').generateTrajectories()[0]
         self.flow_horizontal = cars.flow.generateTrajectories(cars.flow(moving.Point(1,0),'horizontale.yml'))[0]
         self.ped_h = None
         self.ped_v = None
         self.horizontal_alignment = None
         self.vertical_alignment = None

    def addPedestriansToWorld(self,pedestrians_horizontal = None,pedestrians_vertical = None):

        if self.ped_h is None:
            self.ped_h = pedestrians_horizontal
        if self.ped_v is None:
            self.ped_v = pedestrians_vertical


    def existingUsers(self,t):

        rep = []
        if self.flow_vertical is not None:
            for k in range(0,len(self.flow_vertical)):
                if moving.Interval.contains(self.flow_vertical[k].getTimeInterval(),t):
                    rep.append(self.flow_vertical[k])

        if self.flow_horizontal is not None:
            for k in range(0,len(self.flow_horizontal)):
                if moving.Interval.contains(self.flow_horizontal[k].getTimeInterval(),t):
                    rep.append(self.flow_horizontal[k])

        if self.ped_h is not None:
            for k in range(0,len(self.ped_h)):
                if moving.Interval.contains(self.ped_h[k].getTimeInterval(),t):
                    rep.append(self.ped_h[k])

        if self.ped_v is not None:
            for k in range(0,len(self.ped_v)):
                if moving.Interval.contains(self.ped_v[k].getTimeInterval(),t):
                    rep.append(self.ped_v[k])
        return rep

    # def typeOfUserAhead(self,objet,t):
    #
    #     dist = []
    #     utilisateurs_existants = World.existingUsers(self,t)
    #
    #     for k in range(0,len(utilisateurs_existants)):
    #         if utilisateurs_existants[k] == objet:
    #             utilisateurs_existants.pop(k)
    #             break
    #
    #     if objet.etiquette  ==   'verticale':
    #         a = objet.positions[t].y
    #         for k in range (len(utilisateurs_existants)):
    #             b = utilisateurs_existants[k].positions[t].y
    #             d = b - a
    #             if d<0:
    #                 dist.append(float('inf'))
    #             else:
    #                 dist.append(d)
    #
    #     elif objet.etiquette  ==   'horizontale':
    #         a = objet.positions[t].x
    #         for k in range (len(utilisateurs_existants)):
    #             b = utilisateurs_existants[k].positions[t].y
    #             d = b - a
    #             if d < 0:
    #                 dist.append(float('inf'))
    #             else:
    #                 dist.append(d)
    #
    #     return moving.MovingObject.getUserType(utilisateurs_existants[dist.index(min(dist))])


    def isAnEncounter(self,h,v,t,dmin):

        s1 = moving.Point(2000,moving.CurvilinearTrajectory.getSCoordinates(self.flow_vertical[h].curvilinearPositions)[t])
        s2 = moving.Point(moving.CurvilinearTrajectory.getSCoordinates(self.flow_horizontal[v].curvilinearPositions)[t],2000)

        # p1 = self.flow_vertical[i].positions[t]
        # p2 = self.flow_horizontal[j].positions[t]
        distance = moving.Point.distanceNorm2(s1,s2)

        if distance <=  dmin:
            return True,distance
        else:
            return False,distance

    def countEncounters(self,dmin):

        columns = len(self.flow_vertical)
        lines = len(self.flow_horizontal)
        matrix = [([0]*columns)] * lines
        c = 0

        for h in range(columns):
            matrix[h] = [(0,0)] * lines

        for t in range(90): #90 = t_simul, a mettre en parametre
            for v in range(columns):
                for h in range(lines):
                    # print(h,v,self.isAnEncounter(h,v,t,500))
                    if self.isAnEncounter(h,v,t,dmin)[0] == True and matrix[h][v] == (0,0) :
                        matrix[h][v] = self.isAnEncounter(h,v,t,dmin)[1]
                        c +=  1
        if c > lines*columns:
            print("something went wrong")
        return matrix,c
