import trafficintelligence
import cars
import objectsofworld
import toolkit
import simulation
import numpy as np

world = objectsofworld.World.load('default.yml')

sim = simulation.Simulation(72, 1., 25, 45, 7, 2, 1,.5) # second and meter
 # [cars.VehicleInput(0, 'horizontal.yml', 1000), cars.VehicleInput(1, 'vertical.yml', 500)]
#creation des vehicules
# world.vehicle
vehicleInputs = world.vehicleInputs

t_simul = sim.duration
s_min = sim.minimumDistanceHeadway
averageVehicleWidth = sim.averageVehicleWidth
averageVehicleLength = sim.averageVehicleLength
vehicleLengthSD = sim.vehicleLengthSD
vehicleWidthSD = sim.vehicleWidthSD

vehiclesTrajectories = []
for alignment, vehicleInput in zip(world.alignments, vehicleInputs):
    vehiclesTrajectories.append(vehicleInput.generateTrajectories(alignment,t_simul,s_min,averageVehicleLength, averageVehicleWidth, vehicleLengthSD, vehicleWidthSD)[0])

# #calcul du nombre d'interactions
dmin = sim.interactionDistance
#
# affichage des matrices d'interactions
print(world.countAllEncounters(vehiclesTrajectories,dmin)[0])
print(world.countAllEncounters(vehiclesTrajectories,dmin)[1])
print(world.countAllEncounters(vehiclesTrajectories,dmin)[2])
print(world.countAllEncounters(vehiclesTrajectories,dmin)[-4])
