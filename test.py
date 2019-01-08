import os
from trafficintelligence import moving
import cars
import objectsofworld
import toolkit
import simulation
import numpy as np
import random as rd
import carFollowingModels as models

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

    for alignment in alignments :
        v0 = rd.normalvariate(15,3)
        v1 = rd.normalvariate(15,3)

        leaderVehicleInput0 = moving.MovingObject(curvilinearPositions = moving.CurvilinearTrajectory.generate(0,
                                                                                                              v0*sim.timeStep,
                                                                                                              round(configFile.duration/configFile.timeStep),
                                                                                                              alignment.idx),
                                                  velocities = [v0 for k in range (round(configFile.duration/configFile.timeStep))],
                                                  vehicleLength = 7)

        leaderVehicleInput1 = moving.MovingObject(curvilinearPositions = moving.CurvilinearTrajectory.generate(0,
                                                                                                              v1,
                                                                                                              round(configFile.duration/configFile.timeStep),
                                                                                                              alignment.idx),
                                                  velocities = [v1 for k in range (round(configFile.duration/configFile.timeStep))],
                                                  vehicleLength = 7)

        vehiclesGeneratedByVehicleInput0 = [leaderVehicleInput0] + worldFile.initVehiclesOnAligment(0,
                                                                                            round(worldFile.vehicleInputs[0].volume*configFile.duration/3600)-1,
                                                                                            configFile,
                                                                                            15)
        vehiclesGeneratedByVehicleInput1 = [leaderVehicleInput1] + worldFile.initVehiclesOnAligment(1,
                                                                                            round(worldFile.vehicleInputs[0].volume*configFile.duration/3600)-1,
                                                                                            configFile,
                                                                                            15)
        for k in range (1, len(vehiclesGeneratedByVehicleInput0)):
            for t in range(1,round(configFile.duration/configFile.timeStep)):
                #acceleration = ?? donné par le modèle
                vehiclesGeneratedByVehicleInput0[k].updateVelocities(previousVelocity = vehiclesGeneratedByVehicleInput0[k].velocities[t-1],
                                                                    acceleration = acceleration,
                                                                    configFile.timeStep,
                                                                    vehiclesGeneratedByVehicleInput0[k].maxSpeed)
                                                                    # models.Models.Naive.speed(curvilinearPositionLeader = vehiclesGeneratedByVehicleInput0[k-1].curvilinearPositions[t][0],
                                                                    #                     curvilinearPositionFollowing = vehiclesGeneratedByVehicleInput0[k].curvilinearPositions[t-1][0],
                                                                    #                     desiredSpeed = vehiclesGeneratedByVehicleInput0[k].desiredSpeed,
                                                                    #                     TIVmin = configFile.minimumTimeHeadway))

                vehiclesGeneratedByVehicleInput0[k].updateCurvilinearPositions(vehiclesGeneratedByVehicleInput0[k].curvilinearPositions[t-1],
                                                                                speed = vehiclesGeneratedByVehicleInput0[k].velocities[t-1] ,
                                                                                acceleration = acceleration,
                                                                                sim.timeStep,
                                                                                vehiclesGeneratedByVehicleInput0[k].curvilinearPositions[0].lanes[0]
                                                                                # [models.Models.Naive.position(previousPosition = vehiclesGeneratedByVehicleInput0[k].curvilinearPositions[t-1][0],
                                                                                #                      velocity = vehiclesGeneratedByVehicleInput0[k].velocities[t-1],
                                                                                #                      step = configFile.timeStep), 0, alignment.idx])

                #
                # vehiclesGeneratedByVehicleInput0[k].updateMovingObject(newCurvilinearPosition = [models.Models.Naive.position(vehiclesGeneratedByVehicleInput0[k].curvilinearPositions[t-1][0],
                #                                                                                             vehiclesGeneratedByVehicleInput0[k].velocities[t-1],
                #                                                                                             configFile.timeStep),
                #                                                                            0,
                #                                                                            worldFile.alignments[0].idx],
                #                                                 newVelocity = models.Models.Naive.speed(curvilinearPositionLeader = vehiclesGeneratedByVehicleInput0[k-1].curvilinearPositions[t][0],
                #                                                                                         curvilinearPositionFollowing = models.Models.Naive.position(vehiclesGeneratedByVehicleInput0[k].curvilinearPositions[t-1][0],
                #                                                                                                                      vehiclesGeneratedByVehicleInput0[k].velocities[t-1],
                #                                                                                                                      configFile.timeStep),
                #                                                                                         previousVelocity = vehiclesGeneratedByVehicleInput0[k].velocities[t-1],
                #                                                                                         TIVmin = configFile.minimumTimeHeadway),
                #                                                 newAcceleration = None)
        toolkit.save_yaml(alignment.name, vehiclesGeneratedByVehicleInput0)
        print(worldFile.countAllEncounters([vehiclesGeneratedByVehicleInput0], sim.interactionDistance))
        return vehiclesGeneratedByVehicleInput0

a = run(world,sim)
# vehiclesData[alignment_idx_i][i].curvilinearPositions[t][0]

    # for volumes0 in volumes_to_test_on_0 :
    #     for volumes1 in volumes_to_test_on_1 :
    #
    #         worldFile.vehicleInputs[0].volume = volumes0
    #         worldFile.vehicleInputs[1].volume = volumes1
    #
    #         vehicleInputs = [worldFile.vehicleInputs[0], worldFile.vehicleInputs[1]]
    #
    #         vehiclesTrajectories = []
    #         for alignment, vehicleInput,   in zip(worldFile.alignments, vehicleInputs, seedBucket):
    #
    #             rd.seed(seeds)
    #             seed = rd.randint(1,100)
    #             vehiclesTrajectories.append(vehicleInput.generateTrajectories(alignment = alignment,
    #                                                                         tSimul = configFile.duration,
    #                                                                         TIVmin = configFile.minimumTimeHeadway,
    #                                                                         averageVehicleLength = configFile.averageVehicleWidth,
    #                                                                         averageVehicleWidth = configFile.averageVehicleWidth,
    #                                                                         vehicleLengthSD = configFile.vehicleLengthSD,
    #                                                                         vehicleWidthSD = configFile.vehicleWidthSD,
    #                                                                         seed = seed,
    #                                                                         model = 'Naive')[0])
    #             # vehiclesTrajectories.append(vehicleInput.generateNewellTrajectories(alignment = alignment,
    #             #                                                             tSimul = configFile.duration,
    #             #                                                             TIVmin = configFile.minimumTimeHeadway,
    #             #                                                             averageVehicleLength = configFile.averageVehicleWidth,
    #             #                                                             averageVehicleWidth = configFile.averageVehicleWidth,
    #             #                                                             vehicleLengthSD = configFile.vehicleLengthSD,
    #             #                                                             vehicleWidthSD = configFile.vehicleWidthSD,
    #             #                                                             seed = seed)[0])
    #
    #         toolkit.save_yaml('horizontal.yml', vehiclesTrajectories[0])
    #         toolkit.save_yaml('vertical.yml', vehiclesTrajectories[1])

#
#         # #calcul du nombre d'interactions
#         #et remplissage des matrices
#         encounters0[volumes0,volumes1] = world.countAllEncounters(vehiclesTrajectories,configFile.interactionDistance)
#         encounters1[volumes0,volumes1] = world.countAllEncounters(vehiclesTrajectories,configFile.interactionDistance)[1]
#         encounters2[volumes0,volumes1] = world.countAllEncounters(vehiclesTrajectories,configFile.interactionDistance)[2]
#
# toolkit.save_yaml(config['output']['fileName']['encounterMatrices'][0],encounters0)
# toolkit.save_yaml(config['output']['fileName']['encounterMatrices'][1],encounters1)
# toolkit.save_yaml(config['output']['fileName']['encounterMatrices'][2],encounters2)

# print(world.countAllEncounters(vehiclesTrajectories,configFile.interactionDistance)[1])
# print(world.countAllEncounters(vehiclesTrajectories,configFile.interactionDistance)[2])
# print(world.countAllEncounters(vehiclesTrajectories,configFile.interactionDistance)[3])
