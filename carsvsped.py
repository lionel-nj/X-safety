import cars
from trafficintelligence import moving
import random

flow_verticale=cars.flow(moving.Point(0,1),'verticale.yml')
flow_horizontale=cars.flow(moving.Point(1,0),'horizontale.yml')

traj_v=cars.flow(moving.Point(0,1),'verticale.yml').generateTrajectories()[0]
cars.flow.generateTrajectories(cars.flow(moving.Point(1,0),'horizontale.yml'))[0]
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

class world():

    def __init__(self,flow_vertical,flow_horizontal,ped):
        self.flow_vertical=flow_vertical
        self.flow_horizontal=flow_horizontal
        self.ped=ped

    # def calcul_DY(self,i,j,t):
    #     a=moving.MovingObject.getPositionAt(self.flow_vertical[i],t).y
    #     b=moving.MovingObject.getPositionAt(self.flow_horizontal[j],t).y
    #     return a-b
    #
    # def calcul_DX(self,i,j,t):
    #     a=moving.MovingObject.getPositionAt(self.flow_vertical[i],t).x
    #     b=moving.MovingObject.getPositionAt(self.flow_horizontal[j],t).x
    #     return a-b
    def initialise(self):
         self.flow_vertical=cars.flow(moving.Point(0,1),'verticale.yml').generateTrajectories()[0]
         self.flow_horizontal=cars.flow.generateTrajectories(cars.flow(moving.Point(1,0),'horizontale.yml'))[0]
         self.ped=None

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
        for k in range(0,len(self.ped)):
            if moving.Interval.contains(self.ped[k].getTimeInterval(),t):
                rep.append(self.ped[k])
        return rep

    def typeOfUserAhead(self,objet,t):
        dist=[]
        utilisateurs_existants=world.existingUsers(self,t)

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
        #non fonctunneol pour 'instant'
        colonnes=len(self.flow_vertical)
        lignes=len(self.flow_horizontal)
        matrix=[([0]*colonnes)]*lignes

        for h in range(colonnes):
            matrix[h]=[(h,None)]*lignes

        for h in range(colonnes):
            for v in range(lignes):
                matrix[h][v]=(h,v)

                # for t in range(0,90):
                #     if world.isAnEncounter(self,v,h,t,dmin) == True:
                #         matrix[flow_vertical.keys())[flow_vertical.values().index(v)]][flow_horizontal.keys())[flow_horizontal.values().index(h)]]
        return matrix

    def countEncounters(self,dmin):
        colonnes=len(self.flow_vertical)
        lignes=len(self.flow_horizontal)
        matrice=world.matrixHV(self)
        c=0

        for line in matrice:
            for pair in range(0,len(line)):
                for t in range(90):
                    if world.isAnEncounter(self,line[pair][1],line[pair][0],t,dmin)[0]==True and :
                        line[pair]=t
        return matrice
