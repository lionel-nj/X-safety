import os
from trafficintelligence import moving
import cars
import objectsofworld
import toolkit
import simulation
import numpy as np
import random as rd

volumes_to_test_on_0 = [900]
volumes_to_test_on_1 = [2]

encounters0 = { (i,j):0 for i in range(len(volumes_to_test_on_0)) for j in range(len(volumes_to_test_on_1)) }
encounters1 = { (i,j):0 for i in range(len(volumes_to_test_on_0)) for j in range(len(volumes_to_test_on_1)) }
encounters2 = { (i,j):0 for i in range(len(volumes_to_test_on_0)) for j in range(len(volumes_to_test_on_1)) }


world = objectsofworld.World.load('default.yml')

align0 = objectsofworld.Alignment()
align0.makeAlignment(entryPoint = moving.Point(-1000,0),exitPoint = moving.Point(1000,0))
align0.idx = 0

align1 = objectsofworld.Alignment()
align1.makeAlignment(entryPoint = moving.Point(0,-1000),exitPoint = moving.Point(0,1000))
align1.idx = 1

alignments = [align0, align1]

controlDevices = None

for volumes0 in volumes_to_test_on_0 :
    for volumes1 in volumes_to_test_on_1 :


        vehicleInputs0 = cars.VehicleInput(alignmentIdx = world.alignments[0].idx, fileName = "horizontal.yml", volume = volumes0)
        vehicleInputs1 = cars.VehicleInput(alignmentIdx = world.alignments[1].idx, fileName = "vertical.yml", volume = volumes1)
        vehicleInputs = [vehicleInputs0, vehicleInputs1]

        world.reset(alignments, controlDevices, vehicleInputs)

        sim = simulation.Simulation(100, 1/10, 30, 2, 7, 2, 1,.5) # second and meter

        #creation des vehicules
        vehicleInputs = world.vehicleInputs

        vehiclesTrajectories = []
        seedBucket = [780,45]
        for alignment, vehicleInput, seeds in zip(world.alignments, vehicleInputs, seedBucket):
            # for seeds in seedBucket :

            rd.seed(seeds)
            seed = rd.randint(1,100)
            # vehiclesTrajectories = []
            vehiclesTrajectories.append(vehicleInput.generateTrajectories(alignment = alignment,
                                                                        tSimul = sim.duration,
                                                                        TIVmin = sim.minimumTimeHeadway,
                                                                        averageVehicleLength = sim.averageVehicleWidth,
                                                                        averageVehicleWidth = sim.averageVehicleWidth,
                                                                        vehicleLengthSD = sim.vehicleLengthSD,
                                                                        vehicleWidthSD = sim.vehicleWidthSD,
                                                                        seed = seed,
                                                                        model = 'Naive')[0])

        toolkit.save_yaml('horizontal.yml', vehiclesTrajectories[0])
        toolkit.save_yaml('vertical.yml', vehiclesTrajectories[1])
#
#         # #calcul du nombre d'interactions
#         dmin = sim.interactionDistance
#
#         # affichage des nombres/matrices d'interactions
#         encounters0[volumes0,volumes1] = world.countAllEncounters(vehiclesTrajectories,dmin)[0]
#         encounters1[volumes0,volumes1] = world.countAllEncounters(vehiclesTrajectories,dmin)[1]
#         encounters2[volumes0,volumes1] = world.countAllEncounters(vehiclesTrajectories,dmin)[2]
#
#         print(seed)
#
#
# toolkit.save_yaml('encounters0.yml',encounters0)
# toolkit.save_yaml('encounters1.yml',encounters1)
# toolkit.save_yaml('encounters2.yml',encounters2)


os.system('say "travail terminé"')


        # print(world.countAllEncounters(vehiclesTrajectories,dmin)[1])
        # print(world.countAllEncounters(vehiclesTrajectories,dmin)[2])
        # print(world.countAllEncounters(vehiclesTrajectories,dmin)[3])
