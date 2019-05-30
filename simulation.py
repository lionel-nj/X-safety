import numpy as np

import toolkit


class Simulation(object):
    """Stores all simulation and world parameters"""
    units = [
        'sec',
        'sec',
        'm',
        'sec',
        'N/A'
            ]
    duration: 500
    interactionDistance: 25
    minimumTimeHeadway: 500
    timeStep: 0.1
    seed: 45

    def __init__(self, duration, timeStep, interactionDistance, minimumTimeHeadway, seed):
        self.duration = duration
        self.timeStep = timeStep
        self.interactionDistance = interactionDistance
        self.minimumTimeHeadway = minimumTimeHeadway
        self.seed = seed

    def save(self, filename):
        toolkit.saveYaml(filename, self)

    @staticmethod
    def load(filename):
        return toolkit.loadYaml(filename)

    def run(self, world):

        np.random.seed(self.seed)
        # world.connectAlignments()
        for ui in world.userInputs:
            # link to alignment
            for al in world.alignments:
                al.points.computeCumulativeDistances()
                if al.idx == ui.alignmentIdx:
                    ui.alignment = al
            ui.initDistributions()
            ui.generateHeadways(self.duration)

        # suggestion, a voir si c'est le plus pratique
        for al in world.alignments:
            al.users = []

        world.getGraph()
        world.prepare()
        userNum = 0
        world.users = []
        for i in range(int(np.floor(self.duration / self.timeStep))):
            # print('simulation step {}'.format(i))
            if world.controlDevices is not None:
                for cd in world.controlDevices:
                    cd.cycle()
            userNum = world.initUsers(i, self.timeStep, userNum)

            for ui in world.userInputs:
                # if ui.alignment.users is not None:
                for v in ui.alignment.users:
                    if v.inSimulation:
                        world.getUserCurrentAlignment(v)
                        # nextControlDeiceState = world.getNextControlDeviceState(v, i, self.visibilityThreshold)
                        # world.getTimeGap(v, i)
                        v.updateCurvilinearPositions(method="newell",
                                                     instant=i,
                                                     timeStep=self.timeStep)

        world.duplicateLastVelocities()

        # display
        # plt.figure()
        # for ui in world.userInputs:
        #     for v in ui.alignment.users:
        #         if v.timeInterval is not None:
        #             v.plotCurvilinearPositions()
        #     plt.xlabel('time(s/100)')
        #     plt.ylabel('longitudinal coordinate (m)')
        #     plt.show()
        return world


if __name__ == "__main__":
    import doctest

    doctest.testmod()
