import matplotlib.pyplot as plt
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

    def __init__(self, duration, timeStep, seed, threshold):
        self.duration = duration
        self.timeStep = timeStep
        self.seed = seed
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
        # for al in world.alignments:
        #     al.users = []

        world.getGraph()
        world.timeStep = self.timeStep
        world.prepare()
        userNum = 0
        world.users = []
        for i in range(int(np.floor(self.duration / self.timeStep))):
            # print('simulation step {}'.format(i) + '/' + str(int(np.floor(self.duration / self.timeStep))))
            if world.controlDevices is not None:
                for cd in world.controlDevices:
                    cd.cycle()
                    # if cd.user is not None:
                    #     print(cd.user.num)
                    # else:
                    #     print(None)
            userNum = world.initUsers(i, self.timeStep, userNum)

            for u in world.users:
                if u.inSimulation:# in world.users:
                    world.getUserCurrentAlignment(u)
                    # world.isGapAcceptable(u, i)
                    u.updateCurvilinearPositions(method="newell",
                                                    instant=i,
                                                    timeStep=self.timeStep,
                                                    world=world)
                    # if world.controlDevices[0].user is not None:
                    #     print(world.controlDevices[0].user.num, world.controlDevices[0].userTimeAtStop)

        world.duplicateLastVelocities()

        # display
        plt.figure()
        for ui in world.userInputs:
            for u in ui.users:
                if u.timeInterval is not None:
                    u.plotCurvilinearPositions()
            plt.xlabel('time(s/10)')
            plt.ylabel('longitudinal coordinate (m)')
            plt.show()
        return world


if __name__ == "__main__":
    import doctest

    doctest.testmod()
