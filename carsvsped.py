import cars
from trafficintelligence import moving
import random
import toolkit

# flow_verticale=cars.flow(moving.Point(0,1),'verticale.yml')
# flow_horizontale=cars.flow(moving.Point(1,0),'horizontale.yml')
#
# traj_v=cars.flow(moving.Point(0,1),'verticale.yml').generateTrajectories()[0]
# cars.flow.generateTrajectories(cars.flow(moving.Point(1,0),'horizontale.yml'))[0]
#
# for k in traj_v:
#     traj_v[k].etiquette='verticale'
#
# for k in traj_h:
#     traj_h[k].etiquette='horizontale'
#
# p=moving.Point(0,1000)
# n=90
# v=moving.Point(1,0).__mul__(random.normalvariate(1,0.2))
# ped=moving.MovingObject()
# ped.userType=2 #pieton
# ped.timeInterval=moving.Interval(30,40)
# ped.positions=moving.Trajectory.generate(p,v,n)[0]
# ped.velocities=[]
# ped.type_flow='test'
# ped.etiquette='horizontale'
#
# pietons=dict()
# pietons[0]=ped

class Alignment():
    #voie
    def __init__(self,alignment_number,points,width,control_device,flow,pedestrians=None):
        self.points=points
        self.width=width
        self.controlDevice=controlDevice
        self.flow=flow
        self.pedestrians=None


class ControlDevice():
    #outil de control
    def __init__(self,point,alignment):
        self.point=point
        self.alignment=alignment

    def getPositionOfControlDevice(self):
        return moving.MovingObject.Point(moving.MovingObject.getXCoordinates(self),moving.MovingObject.getYCoordinates(self))

    def getAlignmentOfControlDevice(self):
        return self.alignment_number

class World():
    #monde
    def __init__(self,flow_vertical,flow_horizontal,ped_h,ped_v):
        self.flow_vertical=flow_vertical
        self.flow_horizontal=flow_horizontal
        self.ped_h=ped_h
        self.ped_v=ped_v

    def saveWorld(self):
        toolkit.create_yaml('World.yml',dict(self))

    def initialise(self):
         self.flow_vertical=cars.flow(moving.Point(0,1),'verticale.yml').generateTrajectories()[0]
         self.flow_horizontal=cars.flow.generateTrajectories(cars.flow(moving.Point(1,0),'horizontale.yml'))[0]
         self.ped_h=None
         self.ped_v=None

    def distanceMinVerifiee(self,direction,flow,i,j,t,dmin):
        if direction=='horizontale':
            if flow==1:
                if cars.gap(self.flow_vertical[i].positions[t].x,self.flow_vertical[j].positions[t].x,(self.flow_vertical[i].geometry.length-2*1.8)/2)>dmin:
                    return True
            elif flow==2:
                if cars.gap(self.flow_horizontal[i].positions[t].x,self.flow_horizontal[j].positions[t].x,(self.flow_horizontal[i].geometry.length-2*1.8)/2)>dmin:
                    return True
                return False

        elif direction=='verticale':
            if flow==2:
                if cars.gap(self.flow_horizontal[i].positions[t].y,self.flow_horizontal[j].positions[t].y,(self.flow_horizontal[i].geometry.length-2*1.8)/2)>dmin:
                    return True
            elif flow==1:
                if cars.gap(self.flow_vertical[i].positions[t].y,self.flow_vertical[j].positions[t].y,(self.flow_vertical[i].geometry.length-2*1.8)/2)>dmin:
                    return True
                return False

    def existingUsers(self,t):
        rep=[]
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
        dist=[]
        utilisateurs_existants=World.existingUsers(self,t)

        for k in range(0,len(utilisateurs_existants)):
            if utilisateurs_existants[k]==objet:
                utilisateurs_existants.pop(k)
                break

        if objet.etiquette=='verticale':
            a=objet.positions[t].y
            for k in range (len(utilisateurs_existants)):
                b=utilisateurs_existants[k].positions[t].y
                d=b-a
                if d<0:
                    dist.append(float('inf'))
                else:
                    dist.append(d)

        elif objet.etiquette=='horizontale':
            a=objet.positions[t].x
            for k in range (len(utilisateurs_existants)):
                b=utilisateurs_existants[k].positions[t].y
                d=b-a
                if d<0:
                    dist.append(float('inf'))
                else:
                    dist.append(d)

        return moving.MovingObject.getUserType(utilisateurs_existants[dist.index(min(dist))])

    def isAnEncounter(self,i,j,t,dmin):
        p1=self.flow_vertical[i].positions[t]
        p2=self.flow_horizontal[j].positions[t]
        d=moving.Point.distanceNorm2(p1,p2)

        if d<=dmin:
            return True,d
        else:
            return False,d

    def matrixHV(self):
        colonnes=len(self.flow_vertical)
        lignes=len(self.flow_horizontal)
        matrix=[([0]*colonnes)]*lignes

        for h in range(colonnes):
            matrix[h]=[(h,None)]*lignes

        for h in range(colonnes):
            for v in range(lignes):
                matrix[h][v]=(h,v)

        return matrix

    def countEncounters(self,dmin):
        columns=len(self.flow_vertical)
        lines=len(self.flow_horizontal)
        matrice=World.matrixHV(self)
        matrix=[([0]*columns)]*lines
        c=0

        for v in range(columns):
            for h in range(lines):
                for t in range(90):
                    if self.isAnEncounter(matrice[h][v][0],matrice[h][v][1],t,dmin)==True:
                        matrix[h][v]=(h,v,t)
                        break
        return matrix
