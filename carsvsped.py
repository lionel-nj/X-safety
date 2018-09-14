import cars
from trafficintelligence import moving
import random

voie_verticale=cars.voie(moving.Point(0,1),'verticale.yml')
voie_horizontale=cars.voie(moving.Point(1,0),'horizontale.yml')

traj_v=cars.voie.generate_trajectories(voie_verticale)[0]
traj_h=cars.voie.generate_trajectories(voie_horizontale)[0]

for k in traj_v:
    traj_v[k].etiquette='verticale'

for k in traj_h:
    traj_h[k].etiquette='horizontale'

p=moving.Point(0,1000)
n=10
v=moving.Point(1,0).__mul__(random.normalvariate(1,0.2))
ped=moving.MovingObject()
ped.userType=2 #pieton
ped.timeInterval=moving.Interval(30,40)
ped.positions=moving.Trajectory.generate(p,v,n)[0]
ped.velocities=[]
ped.type_voie="test"
ped.etiquette='horizontale'

pietons=dict()
pietons[0]=ped

class essai():

    def __init__(self,voie1,voie2,ped):
        self.voie1=voie1
        self.voie2=voie2
        self.ped=ped

    def calcul_DY(self,i,j,t):
        a=moving.MovingObject.getPositionAt(self.voie1[i],t).y
        b=moving.MovingObject.getPositionAt(self.voie2[j],t).y
        return a-b

    def calcul_DX(self,i,j,t):
        a=moving.MovingObject.getPositionAt(self.voie1[i],t).x
        b=moving.MovingObject.getPositionAt(self.voie2[j],t).x
        return a-b

    def distanceMinVerifiee(self,direction,voie,i,j,t,dmin):
        if direction=='horizontale':
            if voie==1:
                if cars.gap(self.voie1[i].positions[t].x,self.voie1[j].positions[t].x,(self.voie1[i].geometry.length-2*1.8)/2)>dmin:
                    return True
            elif voie==2:
                if cars.gap(self.voie2[i].positions[t].x,self.voie2[j].positions[t].x,(self.voie2[i].geometry.length-2*1.8)/2)>dmin:
                    return True
                return False

        elif direction=='verticale':
            if voie==2:
                if cars.gap(self.voie2[i].positions[t].y,self.voie2[j].positions[t].y,(self.voie2[i].geometry.length-2*1.8)/2)>dmin:
                    return True
            elif voie==1:
                if cars.gap(self.voie1[i].positions[t].y,self.voie1[j].positions[t].y,(self.voie1[i].geometry.length-2*1.8)/2)>dmin:
                    return True
                return False

    def existingUsers(self,t):
        rep=[]
        for k in range(0,len(self.voie1)):
            if moving.Interval.contains(self.voie1[k].getTimeInterval(),t):
                rep.append(self.voie1[k])
        for k in range(0,len(self.voie2)):
            if moving.Interval.contains(self.voie2[k].getTimeInterval(),t):
                rep.append(self.voie2[k])
        for k in range(0,len(self.ped)):
            if moving.Interval.contains(self.ped[k].getTimeInterval(),t):
                rep.append(self.ped[k])
        return rep

    def type_of_user_ahead(self,objet,t):
        dist=[]
        utilisateurs_existants=essai.existingUsers(self,t)

        if objet.etiquette=='verticale':
            a=objet.positions[t].y
            for k in utilisateurs_existants:
                b=k.positions[t].y
                d=b-a
                if d<0:
                    dist.append(float('inf'))
                else:
                    dist.append(d)

        elif objet.etiquette=='horizontale':
            a=objet.positions[t].x
            for k in utilisateurs_existants:
                b=k.positions[t].x
                d=b-a
                if d<0:
                    dist.append(float('inf'))
                else:
                    dist.append(d)

        return moving.MovingObject.getUserType(utilisateurs_existants[dist.index(min(dist))])

# t=30
#
# def calcul_vitesse_distance(leader,follower,t):
#     if not distanceMinVerifiee(leader,follower,t):
#         v=moving.Point.norm2(leader.velocities[t])
#         L=leader.geometry.length-2*1.8)/2
#         new_speed=(v*t-L-10)/t
#         modifier_vitesse(follower,t,new_speed)
#
# for k in range(0,len(traj_v)):
#     print(type_of_user_ahead(traj_h[k],t,traj_v,traj_h))

# if ped.commonTimeInterval(voie_verticale[0].getTimeInterval()) not None:
    # k=0
#     while traj[0].position[k].y<1000:
#         calculer_DTy(car)
#         calculder_DTx(ped)
#         if DTy<DTx:
#             modifier_vitesse(voiture,ped)
#             distance_min_verifiee(leader,follower)
    # k=k+1

    # traj[0].velocities[k].y=v_souhaitee
    # if not distance_min_verifiee(leader,follower):
    #     modifier_vitesse(voiture,voiture)

# ped.timeInterval=
