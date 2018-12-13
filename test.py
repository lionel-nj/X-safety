import os
from trafficintelligence import moving
import cars
import objectsofworld
import toolkit
import simulation
import numpy as np
import random as rd

config = toolkit.load_yaml('config.yml')

volumes_to_test_on_0 = config['simulation']['volumes'][0]
volumes_to_test_on_1 = config['simulation']['volumes'][1]

encounters0 = { (i,j):0 for i in range(len(volumes_to_test_on_0)) for j in range(len(volumes_to_test_on_1)) }
encounters1 = { (i,j):0 for i in range(len(volumes_to_test_on_0)) for j in range(len(volumes_to_test_on_1)) }
encounters2 = { (i,j):0 for i in range(len(volumes_to_test_on_0)) for j in range(len(volumes_to_test_on_1)) }


world = objectsofworld.World.load('default.yml')

align0 = objectsofworld.Alignment()
align0.makeAlignment(entryPoint = moving.Point(config['alignments'][0]['entry_x'],config['alignments'][0]['entry_y']),
                    exitPoint = moving.Point(config['alignments'][0]['exit_x'],config['alignments'][0]['exit_y']))
align0.idx = config['alignments'][0]['id']

align1 = objectsofworld.Alignment()
align1.makeAlignment(entryPoint = moving.Point(config['alignments'][1]['entry_x'],config['alignments'][1]['entry_y']),
                    exitPoint = moving.Point(config['alignments'][1]['exit_x'],config['alignments'][1]['exit_y']))
align1.idx = config['alignments'][1]['id']

alignments = [align0, align1]

controlDevices = None
seedBucket = config['seeds']

sim = simulation.Simulation(tSimul = config['simulation']['duration'],
                            step = config['simulation']['step'],
                            interactionDistance = config['safetyParameters']['interactionDistance'],
                            minimumTimeHeadway = config['safetyParameters']['minimumTimeHeadway'],
                            averageVehicleLength = config['vehicleCaracteristics']['averageVehicleLength'],
                            SDVehicleLength = config['vehicleCaracteristics']['SDVehicleLength'],
                            averageVehicleWidth = config['vehicleCaracteristics']['averageVehicleWidth'],
                            SDVehicleWidth = config['vehicleCaracteristics']['SDVehicleWidth'])


for volumes0 in volumes_to_test_on_0 :
    for volumes1 in volumes_to_test_on_1 :


        vehicleInputs0 = cars.VehicleInput(alignmentIdx = world.alignments[0].idx,
                                           volume = volumes0,
                                           headwayDistributionParameters = None, # [tiv, tivprobcum],
                                           desiredSpeedParameters = [config['alignments'][0]['desiredSpeed'], config['alignments'][1]['speedSD']],
                                           seed = config['seeds'][0],
                                           tSimul = sim.duration)

        vehicleInputs1 = cars.VehicleInput(alignmentIdx = world.alignments[1].idx,
                                          volume = volumes1,
                                          headwayDistributionParameters = None, # [tiv, tivprobcum],
                                          desiredSpeedParameters = [config['alignments'][0]['desiredSpeed'], config['alignments'][1]['speedSD']],
                                          seed = config['seeds'][1],
                                          tSimul = sim.duration)

        vehicleInputs = [vehicleInputs0, vehicleInputs1]

        world.reset(alignments, controlDevices, vehicleInputs)


        #creation des vehicules
        vehicleInputs = world.vehicleInputs

        vehiclesTrajectories = []
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

        toolkit.save_yaml(config['fileName']['trajectoires'][0], vehiclesTrajectories[0])
        toolkit.save_yaml(config['fileName']['trajectoires'][1], vehiclesTrajectories[1])
#
        # #calcul du nombre d'interactions
        #et remplissage des matrices
        encounters0[volumes0,volumes1] = world.countAllEncounters(vehiclesTrajectories,sim.interactionDistance)[0]
        encounters1[volumes0,volumes1] = world.countAllEncounters(vehiclesTrajectories,sim.interactionDistance)[1]
        encounters2[volumes0,volumes1] = world.countAllEncounters(vehiclesTrajectories,sim.interactionDistance)[2]

        print(seed)


toolkit.save_yaml(config['fileName']['encounterMatrices'][0],encounters0)
toolkit.save_yaml(config['fileName']['encounterMatrices'][1],encounters1)
toolkit.save_yaml(config['fileName']['encounterMatrices'][2],encounters2)

# print(world.countAllEncounters(vehiclesTrajectories,sim.interactionDistance)[1])
# print(world.countAllEncounters(vehiclesTrajectories,sim.interactionDistance)[2])
# print(world.countAllEncounters(vehiclesTrajectories,sim.interactionDistance)[3])

os.system('say "travail terminé"')
