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

    def __init__(self, duration, timeStep, seed, verbose, dbName=None):
        self.duration = duration
        self.timeStep = timeStep
        self.seed = seed
        self.verbose = verbose
        self.dbName = dbName

    def save(self, filename):
        toolkit.saveYaml(filename, self)

    @staticmethod
    def load(filename):
        return toolkit.loadYaml(filename)

    def run(self, world):
        np.random.seed(self.seed)

        # preparing simulation
        world.prepare(self.timeStep, self.duration, self.seed)

        # main loop
        userNum = 0
        for i in range(int(np.floor(self.duration / self.timeStep))):
            if self.verbose:
                print('simulation step {}/{}'.format(i, int(np.floor(self.duration / self.timeStep))))
            world.updateControlDevices()
            userNum = world.initUsers(i, userNum)
            world.updateUsers(i)
            world.updateFirstUsers()
            world.updateInteractions()
            print(world.interactions, i)
            # world.computeDistances(i)

        world.duplicateLastVelocities()
        world.finalize(i)



if __name__ == "__main__":
    import doctest

    doctest.testmod()
