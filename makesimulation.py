import numpy as np


# world = network.World.load('outputData/simple-net.yml')
# sim = simulation.Simulation.load('inputData/config.yml')

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
        al.users = []

    world.getGraph()
    world.prepare()
    userNum = 0
    world.users = []
    for i in range(int(np.floor(simulationParameters.duration/simulationParameters.timeStep))):
        # print('simulation step {}'.format(i))
        if world.controlDevices is not None:
            for cd in world.controlDevices:
                cd.cycle()
        userNum = world.initUsers(i, simulationParameters.timeStep, userNum)

        for al in world.alignments:
            if al.users is not None:
                for v in al.users:
                    # world.checkControlDevicesAtInstant(v, i, 200)
                    # world.comingThroughTraffic(v, i)
                    world.getVisitedAlignmentLength(v)
                    if v.curvilinearPositions is None:
                        currentAlignment = world.getAlignmentById(v.initialAlignmentIdx)
                    else:
                        currentAlignment = world.getAlignmentById(v.curvilinearPositions.lanes[-1])
                    v.updateCurvilinearPositions(method="newell",
                                                 instant=i,
                                                 timeStep=simulationParameters.timeStep,
                                                 currentAlignment=currentAlignment)

                    # world.assignUserAlignment(v)
                                                 # _nextAlignmentIdx=world.getNextAlignment(v, i, simulationParameters.timeStep))
    world.duplicateLastVelocities()
    # #
    # # display
    # # plt.figure()
    # # for ui in world.userInputs:
    # #     for v in ui.alignment.vehicles:
    # #         if v.timeInterval is not None:
    # #             v.plotCurvilinearPositions()
    # #     plt.xlabel('time(s/100)')
    # #     plt.ylabel('longitudinal coordinate (m)')
    # #     plt.show()
    return world
