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
#
# list_of_cars=[]
#
# for alignment, vehicleInput in zip(world.alignments, vehicleInputs):
#     np.random.seed(123)
#     list_of_cars.append(vehicleInput.generateTrajectories(alignment,t_simul,s_min,averageVehicleLength, averageVehicleWidth, vehicleLengthSD, vehicleWidthSD))
#
#
#
# #mise des vehicules dans le monde
# world.vehicles = [toolkit.load_yaml('horizontal.yml'),
#                   toolkit.load_yaml('vertical.yml')]
#
# #generation de vehicules fantomes pour pouvoir effectuer les calculs de rencontres
#
# world.generateGhostsIfVolumeAreDifferent(t_simul)
#
# #calcul du nombre d'interactions
# dmin = sim.interactionDistance
#
# # affichage des matrices d'interactions
# print(world.countAllEncounters(dmin)[-1])
# print(world.countAllEncounters(dmin)[-2])
# print(world.countAllEncounters(dmin)[-3])
# print(world.countAllEncounters(dmin)[-4])

list_of_volumes_h = [k*50 for k in range(1,13)]
list_of_volumes_v = [k*50 for k in range(1,13)]

matrix_crossing = [[0]*12]*12
matrix_sane_way_h = [[0]*12]*12
matrix_sane_way_v = [[0]*12]*12

h=0
v=0

for volumes in list_of_volumes_h :
    world.alignments[0].volume = volumes

    for volumes_vertical in list_of_volumes_v :
        world.alignments[1].volume = volumes_vertical
        list_of_cars=[]

        for alignment, vehicleInput in zip(world.alignments, vehicleInputs):
            np.random.seed(123)
            list_of_cars.append(vehicleInput.generateTrajectories(alignment,t_simul,s_min,averageVehicleLength, averageVehicleWidth, vehicleLengthSD, vehicleWidthSD))



    #mise des vehicules dans le monde
        world.vehicles = [toolkit.load_yaml('horizontal.yml'),
                          toolkit.load_yaml('vertical.yml')]
        world.generateGhostsIfVolumeAreDifferent(t_simul)
        #calcul du nombre d'interactions
        dmin = sim.interactionDistance
        matrix_sane_way_v[h][v] = world.countAllEncounters(dmin)[0]
        matrix_sane_way_h[h][v] = world.countAllEncounters(dmin)[1]
        matrix_crossing[h][v] = world.countAllEncounters(dmin)[2]

        v+=1
    h+=1
