from trafficintelligence import moving
import cars
import objectsofworld
import toolkit
import simulation
import numpy as np
import random as rd

volumes_to_test_on_0 = [1300,1600,1900]
volumes_to_test_on_1 = [1300,1600,1900]

matrix0 = { (i,j):0 for i in range(len(volumes_to_test_on_0)) for j in range(len(volumes_to_test_on_1)) }
matrix1 = { (i,j):0 for i in range(len(volumes_to_test_on_0)) for j in range(len(volumes_to_test_on_1)) }
matrix2 = { (i,j):0 for i in range(len(volumes_to_test_on_0)) for j in range(len(volumes_to_test_on_1)) }


for volumes0 in volumes_to_test_on_0 :
    for volumes1 in volumes_to_test_on_1 :

        world = objectsofworld.World.load('default.yml')

        align0 = objectsofworld.Alignment()
        align0.makeAlignment(entryPoint = moving.Point(-750,0),exitPoint = moving.Point(700,0))
        align0.idx = 0

        align1 = objectsofworld.Alignment()
        align1.makeAlignment( entryPoint = moving.Point(0,-700),exitPoint = moving.Point(0,750))
        align1.idx = 1

        alignments = [align0, align1]

        controlDevices = None

        vehicleInputs0 = cars.VehicleInput(alignmentIdx = align0.idx, fileName = "horizontal.yml", volume = volumes0)
        vehicleInputs1 = cars.VehicleInput(alignmentIdx = align1.idx, fileName = "vertical.yml", volume = volumes1)
        vehicleInputs = [vehicleInputs0, vehicleInputs1]

        world.makeDefault(alignments, controlDevices, vehicleInputs)

        sim = simulation.Simulation(72, 1., 30, 2, 7, 2, 1,.5) # second and meter

        #creation des vehicules
        vehicleInputs = world.vehicleInputs

        t_simul = sim.duration
        s_min = sim.minimumTimeHeadway
        averageVehicleWidth = sim.averageVehicleWidth
        averageVehicleLength = sim.averageVehicleLength
        vehicleLengthSD = sim.vehicleLengthSD
        vehicleWidthSD = sim.vehicleWidthSD

        # volumes_to_test_on_0 = [k*100 for k in range(5, 16)]
        # volumes_to_test_on_1 = [k*100 for k in range(5, 16)]

        vehiclesTrajectories = []
        seeds = [12,23]
        for seed1 in seeds :
            for alignment, vehicleInput in zip(world.alignments, vehicleInputs):
                rd.seed(seed1)
                seed = rd.random()
                vehiclesTrajectories.append(vehicleInput.generateTrajectories(alignment,t_simul,s_min,averageVehicleLength,
                averageVehicleWidth, vehicleLengthSD, vehicleWidthSD, seed)[0])

            toolkit.save_yaml('horizontal.yml', vehiclesTrajectories[0])
            toolkit.save_yaml('vertical.yml', vehiclesTrajectories[1])

            # #calcul du nombre d'interactions
            dmin = sim.interactionDistance

            # affichage des nombres/matrices d'interactions
            matrix0[volumes0,volumes1] = world.countAllEncounters(vehiclesTrajectories,dmin)[0]
            matrix1[volumes0,volumes1] = world.countAllEncounters(vehiclesTrajectories,dmin)[1]
            matrix2[volumes0,volumes1] = world.countAllEncounters(vehiclesTrajectories,dmin)[2]
            print(seed1)


        # print(world.countAllEncounters(vehiclesTrajectories,dmin)[1])
        # print(world.countAllEncounters(vehiclesTrajectories,dmin)[2])
        # print(world.countAllEncounters(vehiclesTrajectories,dmin)[3])
