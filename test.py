from trafficintelligence import *
from cars import *
from carsvsped import *
import toolkit
import simulation

world = World.load('world.yml')

#sim = simulation.Simulation(world, 290, 1., 25, 25) # second and meter
#toolkit.save_yaml('config.yml', sim)
sim = toolkit.load_yaml('config.yml')

#creation des vehicules

vehicleInputs = [VehicleInput(1, 'horizontal.yml'), VehicleInput(2, 'vertical.yml')]

t_simul = sim.duration
s_min = sim.minimumDistanceHeadway
cars=[]
for alignment, vehicleInput in zip(world.alignments, vehicleInputs):
    cars.append(vehicleInput.generateTrajectories(alignment,t_simul,s_min))

#mise des vehicules dans le monde
world.vehicles = [toolkit.load_yaml('horizontal.yml'),
                  toolkit.load_yaml('vertical.yml')]

#calcul du nombre d'interactions
dmin = sim.interactionDistance
# print(world.countEncounters(dmin)[1])
print(world.countEncounters(dmin)[3])
world.trace(0)
