from trafficintelligence import moving
import cars
import objectsofworld
import toolkit
import simulation
import numpy as np

world = objectsofworld.World.load('default.yml')

align0 = objectsofworld.Alignment()
align0.makeAlignment(entryPoint = moving.Point(-500,0),exitPoint = moving.Point(500,0))
align0.idx = 0

align1 = objectsofworld.Alignment()
align1.makeAlignment( entryPoint = moving.Point(0,-500),exitPoint = moving.Point(0,500))
align1.idx = 1

alignments = [align0, align1]

controlDevices = None

vehicleInputs0 = cars.VehicleInput(alignmentIdx = align0.idx, fileName = "horizontal.yml", volume = 1000)
vehicleInputs1 = cars.VehicleInput(alignmentIdx = align1.idx, fileName = "vertical.yml", volume = 1000)
vehicleInputs = [vehicleInputs0, vehicleInputs1]

world.makeDefault(alignments, controlDevices, vehicleInputs)

sim = simulation.Simulation(72, 1., 30, 2, 7, 2, 1,.5) # second and meter
 # [cars.VehicleInput(0, 'horizontal.yml', 1000), cars.VehicleInput(1, 'vertical.yml', 500)]
#creation des vehicules
# world.vehicle
vehicleInputs = world.vehicleInputs

t_simul = sim.duration
s_min = sim.minimumTimeHeadway
averageVehicleWidth = sim.averageVehicleWidth
averageVehicleLength = sim.averageVehicleLength
vehicleLengthSD = sim.vehicleLengthSD
vehicleWidthSD = sim.vehicleWidthSD

vehiclesTrajectories = []
for alignment, vehicleInput in zip(world.alignments, vehicleInputs):
    vehiclesTrajectories.append(vehicleInput.generateTrajectories(alignment,t_simul,s_min,averageVehicleLength, averageVehicleWidth, vehicleLengthSD, vehicleWidthSD)[0])

toolkit.save_yaml('horizontal.yml', vehiclesTrajectories[0])
toolkit.save_yaml('vertical.yml', vehiclesTrajectories[1])

# #calcul du nombre d'interactions
dmin = sim.interactionDistance
#
# affichage des matrices d'interactions
print(world.countAllEncounters(vehiclesTrajectories,dmin)[0])
print(world.countAllEncounters(vehiclesTrajectories,dmin)[1])
print(world.countAllEncounters(vehiclesTrajectories,dmin)[2])
print(world.countAllEncounters(vehiclesTrajectories,dmin)[3])
