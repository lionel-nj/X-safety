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

    def __init__(self, duration, timeStep, interactionDistance, minimumTimeHeadway, seed, visibilityThreshold,
                 threshold):
        self.duration = duration
        self.timeStep = timeStep
        self.interactionDistance = interactionDistance
        self.minimumTimeHeadway = minimumTimeHeadway
        self.seed = seed
        self.visibilityThreshold = visibilityThreshold
        self.threshold = threshold

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
            # print('simulation step {}'.format(i) + '/' + str(int(np.floor(self.duration / self.timeStep))))
            if world.controlDevices is not None:
                for cd in world.controlDevices:
                    cd.cycle()
            userNum = world.initUsers(i, self.timeStep, userNum)

            for ui in world.userInputs:
                # if ui.alignment.users is not None:
                for user in ui.alignment.users:
                    if user.inSimulation:
                        world.getUserCurrentAlignment(user)
                        try:
                            nextControlDeviceIdx = world.getNextControlDevice(user, i, self.visibilityThreshold).idx
                        except:
                            nextControlDeviceIdx = None
                        world.userHasToStop(user, nextControlDeviceIdx, self.visibilityThreshold, i, self.threshold,
                                            self.timeStep)
                        user.updateCurvilinearPositions(method="newell",
                                                        instant=i,
                                                        timeStep=self.timeStep)

        world.duplicateLastVelocities()

        # display
        # plt.figure()
        # for ui in world.userInputs:
        #     for user in ui.alignment.users:
        #         if user.timeInterval is not None:
        #             user.plotCurvilinearPositions()
        #     plt.xlabel('time(s/100)')
        #     plt.ylabel('longitudinal coordinate (m)')
        #     plt.show()
        return world


if __name__ == "__main__":
    import doctest

    doctest.testmod()
