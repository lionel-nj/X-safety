import toolkit


class Simulation(object):
    """Stores all simulation and world parameters"""
    units = [
        'sec',
        'sec',
        'm',
        'sec',
        'm',
        'm',
        'm',
        'm'
    ]

    def __init__(self, duration, timeStep, interactionDistance, minimumTimeHeadway, averageVehicleLength,
                 averageVehicleWidth, vehicleLengthSD, vehicleWidthSD):
        self.duration = duration
        self.timeStep = timeStep
        self.interactionDistance = interactionDistance
        self.minimumTimeHeadway = minimumTimeHeadway
        self.averageVehicleLength = averageVehicleLength
        self.averageVehicleWidth = averageVehicleWidth
        self.vehicleLengthSD = vehicleLengthSD
        self.vehicleWidthSD = vehicleWidthSD

    def save(self, filename):
        toolkit.saveYaml(filename, self)

    @staticmethod
    def load(filename):
        return toolkit.loadYaml(filename)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
