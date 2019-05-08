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


if __name__ == "__main__":
    import doctest

    doctest.testmod()
