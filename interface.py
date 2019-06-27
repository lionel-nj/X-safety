import os

import toolkit


class Interface:
    def __init__(self, world):
        self.world = world

    def save(self, filename):
        toolkit.saveYaml(filename, self)

    @staticmethod
    def load(filename):
        toolkit.loadYaml(filename)

    def getParametersAsInputs(self):
        defaultValues = input('Compute with defaut values ? y or n ?\n')
        if defaultValues =='n':
            for ui in self.world.userInputs:
                print('enter distribution parameters for userInput {}'.format(ui.getIdx()))
                for dist in ui.distributions:
                    distribution = ui.distributions[dist]
                    # print('Choose distribution type for {}, 1: theoretic, 2: degenerated, 3: empirical'.format(dist))
                    distType = int(input('Choose distribution type for {}\n1: theoretic \n2: degenerated \n3: empirical \n'.format(dist)))

                    if distType == 1:
                        distribution.distributionType = 'theoretic'
                        distName = int(input('Choose distribution for {}\n1: shifted exponential \n2: normal \n3: truncnorm \n'.format(dist)))
                        if distName == 1:
                            distribution.distributionName = 'expon'
                            distribution.loc = float(input('Enter loc value \n'))
                            shift = float(input('Enter shift \n'))
                            distribution.scale = float(input('Enter scale value \n')) - shift
                        elif distName == 2:
                            distribution.distributionName = 'norm'
                            distribution.loc = float(input('Enter loc value \n'))
                            distribution.scale = float(input('Enter scale value \n'))
                        else:
                            distribution.distributionName = 'truncnorm'
                            distribution.loc = float(input('Enter loc value \n'))
                            distribution.scale = float(input('Enter scale value \n'))
                            distribution.a = float(input('Enter minimum number of loc \n'))
                            distribution.b = float(input('Enter maximum number of loc \n'))

                    elif distType == 2:
                        degeneratedConstant = float(input('Enter the value of degenerated constant \n'))
                        distribution.distributionType = 'degenerated'
                        distribution.degeneratedConstant = degeneratedConstant

                    else:
                        distribution.distributionType = 'empirical'
                        cdf = input('Pass cdf \n')
                        distribution.cdf = cdf
                    os.system('clear')
        else:
            pass
