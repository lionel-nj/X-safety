import numpy as np

import network
import simulation

world = network.World.load('simple-net.yml')
sim = simulation.Simulation.load('config.yml')


def run(world, simulationParameters):

    np.random.seed(simulationParameters.seed)
    # world.connectAlignments()
    for ui in world.userInputs:
        # link to alignment
        for al in world.alignments:
            al.points.computeCumulativeDistances()
            if al.idx == ui.alignmentIdx:
                ui.alignment = al
        ui.initDistributions()
        ui.generateHeadways(simulationParameters.duration)

    # suggestion, a voir si c'est le plus pratique
    for al in world.alignments:
        al.vehicles = []

    userNum = 0
    for i in range(int(np.floor(simulationParameters.duration/simulationParameters.timeStep))):
        # print('simulation step {}'.format(i))
        userNum = world.initUsers(i, simulationParameters.timeStep, userNum)

        for al in world.alignments:
            for v in al.vehicles:
                # if v is not None :
                    # if v.timeInterval is not None:
                # v.updateCurvilinearPositions("newell", i, simulationParameters.timeStep)
                v.updateCurvilinearPositions("newell", i, simulationParameters.timeStep, world.getNextAlignment(v, i, simulationParameters.timeStep), world.occupiedAlignmentLength(v))

    # for al in world.alignments:
    #     for v in al.vehicles:
    #         world.moveUserToAlignment(v)


    # display
    # plt.figure()
    # for al in world.alignments:
    #     for v in al.vehicles:
    #         if v.timeInterval is not None:
    #             v.plotCurvilinearPositions()
    # plt.xlabel('time(s/100)')
    # plt.ylabel('longitudinal coordinate (m)')
    # plt.show()

    return world
