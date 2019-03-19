import matplotlib.pyplot as plt
import numpy as np
from trafficintelligence import moving
import network, simulation

world = network.World.load('simple-net.yml')
sim = simulation.Simulation.load('config.yml')


def run(worldFile, configFile):

    np.random.seed(configFile.seed)
    for ui in worldFile.userInputs:
        # link to alignment
        for al in worldFile.alignments:
            al.points.computeCumulativeDistances()
            if al.idx == ui.alignmentIdx:
                ui.alignment = al
        ui.initDistributions()
        ui.generateHeadways(configFile.duration)

    # suggestion, a voir si c'est le plus pratique
    for al in worldFile.alignments:
        al.vehicles = []

    userNum = 0
    for i in range(int(np.floor(configFile.duration/configFile.timeStep))):
        # print('simulation step {}'.format(i))
        userNum = worldFile.initUsers(i, configFile.timeStep, userNum)

        for al in worldFile.alignments:
            for v in al.vehicles:
                v.updateCurvilinearPositions("newell", i, configFile.timeStep)

    outOfWorldVehicles = worldFile.getUsersOutOfWorld()

    # display
    # plt.figure()
    # for al in worldFile.alignments:
    #     for v in al.vehicles:
    #         if v.timeInterval is not None:
    #             v.plotCurvilinearPositions()
    # plt.xlabel('time(s/100)')
    # plt.ylabel('longitudinal coordinate (m)')
    # plt.show()

    worldFile.save('world.yml')


run(world, sim)