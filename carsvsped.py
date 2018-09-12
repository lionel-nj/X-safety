import cars
from trafficintelligence import moving
import random

voie_verticale=cars.voie(moving.Point(0,1),'verticale.yml')
traj=cars.voie.generate_trajectories(voie_verticale)

p=moving.Point(0,1000)
n=7
v=moving.Point(1,0).__mul__(random.normalvariate(1,0.2))
ped=moving.MovingObject()
ped.userType=2 #pieton
ped.positions=moving.Trajectory.generate(p,v,n)[0]
ped.velocities=[]
ped.timeInterval=
