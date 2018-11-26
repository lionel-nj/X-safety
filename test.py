import trafficintelligence
import cars
import objectsofworld
import toolkit
import simulation
import numpy as np


# distribution = toolkit.generateDistribution('data.csv')
# toolkit.save_yaml('distribution.yaml',distribution)

# world = World.load('world.yml')
world = objectsofworld.World.load('default.yml')

sim = simulation.Simulation(world, 72, 1., 160, 25, 6, 1, 3,.5) # second and meter
# toolkit.save_yaml('config.yml', sim)
# sim = toolkit.load_yaml('config.yml')

#creation des vehicules

vehicleInputs = [cars.VehicleInput(1, 'horizontal.yml'), cars.VehicleInput(2, 'vertical.yml')]

t_simul = sim.duration
s_min = sim.minimumDistanceHeadway
averageVehicleWidth = sim.averageVehicleWidth
averageVehicleLength = sim.averageVehicleLength
vehicleLengthSD = sim.vehicleLengthSD
vehicleWidthSD = sim.vehicleWidthSD

list_of_cars=[]

for alignment, vehicleInput in zip(world.alignments, vehicleInputs):
    np.random.seed(123)
    list_of_cars.append(vehicleInput.generateTrajectories(alignment,t_simul,s_min,averageVehicleLength, averageVehicleWidth, vehicleLengthSD, vehicleWidthSD))



#mise des vehicules dans le monde
world.vehicles = [toolkit.load_yaml('horizontal.yml'),
                  toolkit.load_yaml('vertical.yml')]

#generation de vehicules fantomes pour pouvoir effectuer les calculs de rencontres

world.generateGhostsIfVolumeAreDifferent(t_simul)

#calcul du nombre d'interactions
dmin = sim.interactionDistance
print(world.countAllEncounters(dmin)[-1])
print(world.countAllEncounters(dmin)[-2])
print(world.countAllEncounters(dmin)[-3])
print(world.countAllEncounters(dmin)[-4])


# world.trace(0)
# world.trace(1)
