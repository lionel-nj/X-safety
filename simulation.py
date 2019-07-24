import numpy as np

import toolkit


class Simulation(object):
    """Stores all simulation and world parameters"""
    units = [
        'sec',
        'sec',
        'sec',
        'N/A'
    ]

    def __init__(self, duration, timeStep, seed, verbose, dbName=None, computeInteractions=False):
        self.duration = duration
        self.timeStep = timeStep
        self.seed = seed
        self.verbose = verbose
        self.dbName = dbName
        self.computeInteractions = computeInteractions

    def save(self, filename):
        toolkit.saveYaml(filename, self)

    @staticmethod
    def load(filename):
        return toolkit.loadYaml(filename)

    def run(self, world):
        np.random.seed(self.seed)

        # preparing simulation
        world.prepare(self.timeStep, self.duration)

        # main loop
        userNum = 0
        i = 0
        while len(world.completed) < self.minimumCompletedUsers:
        # for i in range(int(np.floor(self.duration / self.timeStep))):
            if self.verbose:
                print('simulation step {}: {} users ({} completed), {} interactions ({} completed)'.format(i, len(world.users), len(world.completed), len(world.interactions), len(world.completedInteractions)))
            world.updateControlDevices()
            userNum = world.initUsers(i, userNum, self.safetyDistance)
            world.updateUsers(i)
            world.updateFirstUsers()
            world.updateInteractions(i, self.computeInteractions)
            i += 1

        world.duplicateLastVelocities()
        world.finalize(i)
        world.computePET()
        return i

if __name__ == "__main__":
    import doctest

    doctest.testmod()
