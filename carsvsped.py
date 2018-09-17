import cars
from trafficintelligence import moving
import random

voie_verticale=cars.voie(moving.Point(0,1),'verticale.yml')
voie_horizontale=cars.voie(moving.Point(1,0),'horizontale.yml')

traj_v=voie_verticale.generateTrajectories()[0]
traj_h=cars.voie.generateTrajectories(voie_horizontale)[0]

for k in traj_v:
    traj_v[k].etiquette='verticale'

for k in traj_h:
    traj_h[k].etiquette='horizontale'

p=moving.Point(0,1000)
n=90
v=moving.Point(1,0).__mul__(random.normalvariate(1,0.2))
ped=moving.MovingObject()
ped.userType=2 #pieton
ped.timeInterval=moving.Interval(30,40)
ped.positions=moving.Trajectory.generate(p,v,n)[0]
ped.velocities=[]
ped.type_voie='test'
ped.etiquette='horizontale'

pietons=dict()
pietons[0]=ped

class essai():

    def __init__(self,flow1,flow2,ped):
        self.flow1=flow1
        self.flow2=flow2
        self.ped=ped

    # def calcul_DY(self,i,j,t):
    #     a=moving.MovingObject.getPositionAt(self.flow1[i],t).y
    #     b=moving.MovingObject.getPositionAt(self.flow2[j],t).y
    #     return a-b
    #
    # def calcul_DX(self,i,j,t):
    #     a=moving.MovingObject.getPositionAt(self.flow1[i],t).x
    #     b=moving.MovingObject.getPositionAt(self.flow2[j],t).x
    #     return a-b

    def distanceMinVerifiee(self,direction,voie,i,j,t,dmin):
        if direction=='horizontale':
            if voie==1:
                if cars.gap(self.flow1[i].positions[t].x,self.flow1[j].positions[t].x,(self.flow1[i].geometry.length-2*1.8)/2)>dmin:
                    return True
            elif voie==2:
                if cars.gap(self.flow2[i].positions[t].x,self.flow2[j].positions[t].x,(self.flow2[i].geometry.length-2*1.8)/2)>dmin:
                    return True
                return False

        elif direction=='verticale':
            if voie==2:
                if cars.gap(self.flow2[i].positions[t].y,self.flow2[j].positions[t].y,(self.flow2[i].geometry.length-2*1.8)/2)>dmin:
                    return True
            elif voie==1:
                if cars.gap(self.flow1[i].positions[t].y,self.flow1[j].positions[t].y,(self.flow1[i].geometry.length-2*1.8)/2)>dmin:
                    return True
                return False

    def existingUsers(self,t):
        rep=[]
        for k in range(0,len(self.flow1)):
            if moving.Interval.contains(self.flow1[k].getTimeInterval(),t):
                rep.append(self.flow1[k])
        for k in range(0,len(self.flow2)):
            if moving.Interval.contains(self.flow2[k].getTimeInterval(),t):
                rep.append(self.flow2[k])
        for k in range(0,len(self.ped)):
            if moving.Interval.contains(self.ped[k].getTimeInterval(),t):
                rep.append(self.ped[k])
        return rep

    def typeOfUserAhead(self,objet,t):
        dist=[]
        utilisateurs_existants=essai.existingUsers(self,t)

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
        p1=self.flow1[i].positions[t]
        p2=self.flow2[j].positions[t]
        d=moving.Point.distanceNorm2(p1,p2)

        if d<=dmin:
            return True
        else:
            return False


    def countEncounters(self,dmin):
        c=0
        for t in range(len(self.flow1[0].positions)):
            for h in range(0,len(self.flow1)):
                for v in range(len(self.flow2)):
                    if essai.isAnEncounter(self,h,v,t,dmin):
                        c+=1
        return c
