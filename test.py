import trafficintelligence
import cars
import objectsofworld
import toolkit
import simulation
import numpy as np

world = objectsofworld.World.load('default.yml')

sim = simulation.Simulation(72, 1., 25, 45, 7, 2, 1,.5) # second and meter

#creation des vehicules

vehicleInputs = [cars.VehicleInput(0, 'horizontal.yml'), cars.VehicleInput(1, 'vertical.yml')]

t_simul = sim.duration
s_min = sim.minimumDistanceHeadway
averageVehicleWidth = sim.averageVehicleWidth
averageVehicleLength = sim.averageVehicleLength
vehicleLengthSD = sim.vehicleLengthSD
vehicleWidthSD = sim.vehicleWidthSD

world.vehicles = []
for alignment, vehicleInput in zip(world.alignments, vehicleInputs):
    world.vehicles.append(vehicleInput.generateTrajectories(alignment,t_simul,s_min,averageVehicleLength, averageVehicleWidth, vehicleLengthSD, vehicleWidthSD)[0])



#mise des vehicules dans le monde
# world.vehicles = [toolkit.load_yaml('horizontal.yml'),
#                   toolkit.load_yaml('vertical.yml')]

#generation de vehicules fantomes pour pouvoir effectuer les calculs de rencontres

world.generateGhostsIfVolumeAreDifferent(t_simul)


#calcul du nombre d'interactions
dmin = sim.interactionDistance

# affichage des matrices d'interactions
print(world.countAllEncounters(dmin)[0])
print(world.countAllEncounters(dmin)[1])
print(world.countAllEncounters(dmin)[2])
print(world.countAllEncounters(dmin)[-4])
#
# list_of_volumes_h = [k*50 for k in range(15,30)]
# list_of_volumes_v = [k*50 for k in range(15,30)]
#
# matrix_crossing = [[0]*14]*14
# matrix_same_way_h = [[0]*14]*14
# matrix_same_way_v = [[0]*14]*14
#
# h=0
# v=0
#
# for volumes1 in list_of_volumes_h :
#     world.alignments[0].volume = volumes1
#
#     for volumes2 in list_of_volumes_v :
#         world.alignments[1].volume = volumes2
#
#         for alignment, vehicleInput in zip(world.alignments, vehicleInputs):
#             np.random.seed(123)
#             vehicleInput.generateTrajectories(alignment,t_simul,s_min,averageVehicleLength, averageVehicleWidth, vehicleLengthSD, vehicleWidthSD)
#     #mise des vehicules dans le monde
#         world.vehicles = [toolkit.load_yaml('horizontal.yml'),
#                           toolkit.load_yaml('vertical.yml')]
#         world.generateGhostsIfVolumeAreDifferent(t_simul)
#         #calcul du nombre d'interactions
#         dmin = sim.interactionDistance
#         matrix_same_way_v[h][v] = world.countAllEncounters(dmin)[0]
#         matrix_same_way_h[h][v] = world.countAllEncounters(dmin)[1]
#         matrix_crossing[h][v] = world.countAllEncounters(dmin)[2]
#
#         v+=1
#     h+=1
