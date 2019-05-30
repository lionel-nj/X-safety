import numpy as np
from SALib.sample import saltelli

import analysis
import network
import simulation
import toolkit

problem = dict(num_vars=5,
               names=['d', 'headway', 'length', 'speed', 'tau'],
               bounds=[[7.33, 9.33],
                       [2.0001633772214027,
                        6.936204757259126],
                       [6, 8],
                       [11, 17],
                       [1.5, 3]
                       ])
paramValues = saltelli.sample(problem, 1)

TTC = np.zeros([paramValues.shape[0]])
PET = np.zeros([paramValues.shape[0]])
collisionNumber = np.zeros([paramValues.shape[0]])
minDistanceAtCrossing = np.zeros([paramValues.shape[0]])

for i, X in enumerate(paramValues):
    world = network.World.load('simple-net.yml')
    sim = simulation.Simulation.load('config.yml')
    simOutput = analysis.evaluateModel(X, world, sim)
    TTC[i] = simOutput[0]
    PET[i] = simOutput[1]
    collisionNumber[i] = simOutput[2]
    minDistanceAtCrossing[i] = simOutput[3]

toolkit.saveYaml('outputData/sensitivity-analysis/simulationlOutput.yml', simOutput)
# Si = sobol.analyze(problem, TTC, print_to_console=False)
toolkit.callWhenDone()