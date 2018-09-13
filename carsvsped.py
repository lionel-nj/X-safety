import cars
from trafficintelligence import moving
import random

voie_verticale=cars.voie(moving.Point(0,1),'verticale.yml')
voie_horizontale=cars.voie(moving.Point(1,0),'horizontale.yml')

traj_v=cars.voie.generate_trajectories(voie_verticale)[0]
traj_h=cars.voie.generate_trajectories(voie_horizontale)[0]

for k in traj_v:
    traj_v[k].type_voie='verticale'

for k in traj_h:
    traj_h[k].type_voie='horizontale'

p=moving.Point(0,1000)
n=10
v=moving.Point(1,0).__mul__(random.normalvariate(1,0.2))
ped=moving.MovingObject()
ped.userType=2 #pieton
ped.timeInterval=moving.Interval(30,40)
ped.positions=moving.Trajectory.generate(p,v,n)[0]
ped.velocities=[]
ped.type_voie="test"

# traj_h[7]=ped

def calcul_DY(obj1,obj2):
    a=moving.MovingObject.getPositionAt(obj1,0).y
    b=moving.MovingObject.getPositionAt(obj2,0).y
    return a-b

def calcul_DX(obj1,obj2):
    a=moving.MovingObject.getPositionAt(obj1,0).x
    b=moving.MovingObject.getPositionAt(obj2,0).x
    return a-b

def modifier_vitesse(veh,t,new_speed):
    veh.velocities[t]=new_speed

def distance_min_verifiee_x(objet1_leader,objet2_follower,t):
    if cars.gap(objet1_leader.positions[t].x,objet2_follower.positions[t].x,(objet1_leader.geometry.length-2*1.8)/2)>10:
        return True
    return False

def distance_min_verifiee_y(objet1_leader,objet2_follower,t):
    if cars.gap(objet1_leader.positions[t].y,objet2_follower.positions[t].y,(objet1_leader.geometry.length-2*1.8)/2)>10:
        return True
    return False

def existing_users(voie1,voie2,t):
    rep=[]
    for k in range(0,len(voie1)):
        if moving.Interval.contains(voie1[k].getTimeInterval(),t):
            rep.append(voie1[k])
    for k in range(0,len(voie2)):
        if moving.Interval.contains(voie2[k].getTimeInterval(),t):
            rep.append(voie2[k])
    return rep

def type_of_user_ahead(objet,t,voie1,voie2):
    dist=[]
    utilisateurs_existants=existing_users(voie1,voie2,t)
    for k in utilisateurs_existants:
        if calcul_DY(objet,k)<0:
            dist.append(float('inf'))
        else:
            dist.append(calcul_DY(objet,k))
    return moving.MovingObject.getUserType(utilisateurs_existants[dist.index(min(dist))])

# t=30
#
# def calcul_vitesse_distance(leader,follower,t):
#     if not distance_min_verifiee_y(leader,follower,t):
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
