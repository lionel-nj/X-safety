import os
from trafficintelligence import moving
import cars
import objectsofworld
import toolkit
import simulation
import numpy as np
import random as rd

world = objectsofworld.World.load('default.yml')
sim = toolkit.load_yaml('config.yml')

def run(worldFile,configFile):

    volumes_to_test_on_0 = [800,]
    volumes_to_test_on_1 = [20,]
    #
    # encounters0 = { (i,j):0 for i in range(len(volumes_to_test_on_0)) for j in range(len(volumes_to_test_on_1)) }
    # encounters1 = { (i,j):0 for i in range(len(volumes_to_test_on_0)) for j in range(len(volumes_to_test_on_1)) }
    # encounters2 = { (i,j):0 for i in range(len(volumes_to_test_on_0)) for j in range(len(volumes_to_test_on_1)) }

    alignments = [worldFile.alignments[0], worldFile.alignments[1]]

    seedBucket = [45,90]

    for volumes0 in volumes_to_test_on_0 :
        for volumes1 in volumes_to_test_on_1 :

            worldFile.vehicleInputs[0].volume = volumes0
            worldFile.vehicleInputs[1].volume = volumes1

            vehicleInputs = [worldFile.vehicleInputs[0], worldFile.vehicleInputs[1]]

            vehiclesTrajectories = []
            for alignment, vehicleInput, seeds in zip(worldFile.alignments, vehicleInputs, seedBucket):

                rd.seed(seeds)
                seed = rd.randint(1,100)
                vehiclesTrajectories.append(vehicleInput.generateTrajectories(alignment = alignment,
                                                                            tSimul = sim.duration,
                                                                            TIVmin = sim.minimumTimeHeadway,
                                                                            averageVehicleLength = sim.averageVehicleWidth,
                                                                            averageVehicleWidth = sim.averageVehicleWidth,
                                                                            vehicleLengthSD = sim.vehicleLengthSD,
                                                                            vehicleWidthSD = sim.vehicleWidthSD,
                                                                            seed = seed,
                                                                            model = 'Naive')[0])
                # vehiclesTrajectories.append(vehicleInput.generateNewellTrajectories(alignment = alignment,
                #                                                             tSimul = sim.duration,
                #                                                             TIVmin = sim.minimumTimeHeadway,
                #                                                             averageVehicleLength = sim.averageVehicleWidth,
                #                                                             averageVehicleWidth = sim.averageVehicleWidth,
                #                                                             vehicleLengthSD = sim.vehicleLengthSD,
                #                                                             vehicleWidthSD = sim.vehicleWidthSD,
                #                                                             seed = seed)[0])

            toolkit.save_yaml('horizontal.yml', vehiclesTrajectories[0])
            toolkit.save_yaml('vertical.yml', vehiclesTrajectories[1])

run(world,sim)
#
#         # #calcul du nombre d'interactions
#         #et remplissage des matrices
#         encounters0[volumes0,volumes1] = world.countAllEncounters(vehiclesTrajectories,sim.interactionDistance)
#         encounters1[volumes0,volumes1] = world.countAllEncounters(vehiclesTrajectories,sim.interactionDistance)[1]
#         encounters2[volumes0,volumes1] = world.countAllEncounters(vehiclesTrajectories,sim.interactionDistance)[2]
#
# toolkit.save_yaml(config['output']['fileName']['encounterMatrices'][0],encounters0)
# toolkit.save_yaml(config['output']['fileName']['encounterMatrices'][1],encounters1)
# toolkit.save_yaml(config['output']['fileName']['encounterMatrices'][2],encounters2)

# print(world.countAllEncounters(vehiclesTrajectories,sim.interactionDistance)[1])
# print(world.countAllEncounters(vehiclesTrajectories,sim.interactionDistance)[2])
# print(world.countAllEncounters(vehiclesTrajectories,sim.interactionDistance)[3])
