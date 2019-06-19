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

    def __init__(self, duration, timeStep, seed, threshold, verbose):
        self.duration = duration
        self.timeStep = timeStep
        self.seed = seed
        self.threshold = threshold
        self.verbose = verbose

    def save(self, filename):
        toolkit.saveYaml(filename, self)

    @staticmethod
    def load(filename):
        return toolkit.loadYaml(filename)

    def run(self, world):
        np.random.seed(self.seed)

        # initialize alignments
        for ui in world.userInputs:
            # link to alignment
            for al in world.alignments:
                al.points.computeCumulativeDistances()
                if al.idx == ui.alignmentIdx:
                    ui.alignment = al
            ui.initDistributions()
            ui.generateHeadways(self.duration)
        
        world.prepare()
        userNum = 0
        world.users = []
        for i in range(int(np.floor(self.duration / self.timeStep))):
            if self.verbose:
                print('simulation step {}'.format(i) + '/' + str(int(np.floor(self.duration / self.timeStep))))
            # if world.controlDevices is not None:
            #    for cd in world.controlDevices:
            #        cd.cycle(self.timeStep)
            userNum = world.initUsers(i, self.timeStep, userNum)

            for u in world.users:
                u.getUserCurrentAlignment(world)
                u.updateCurvilinearPositions(method="newell",
                                             instant=i,
                                             timeStep=self.timeStep,
                                             world=world)

        world.duplicateLastVelocities()


if __name__ == "__main__":
    import doctest

    doctest.testmod()
