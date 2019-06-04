import argparse

import numpy as np
from SALib.sample import saltelli

import analysis
import network
import simulation
import toolkit

parser = argparse.ArgumentParser()
parser.add_argument("--nop", type=int, help="number of points for a parameter")
parser.add_argument("--rep", type=int, help="number of repetitions for an experiment")
parser.add_argument("--duration", type=int, help="duration in seconds of each experiments")

args = parser.parse_args()

problem = dict(num_vars=4,
               names=['d', 'headway', 'length', 'speed'],#, 'tau'],
               bounds=[[7.33, 9.33],
                       [0.5, 1.9],
                       [6, 8],
                       [11, 17],
                       ])
                       # [1.5, 2.5],
paramValues = saltelli.sample(problem, args.nop, seed=0)

_ttc = [0] * paramValues.shape[0]
# _userCount = [0] * paramValues.shape[0]
# _conflict5 = [0] * paramValues.shape[0]
# _conflict10 = [0] * paramValues.shape[0]
# _conflict15 = [0] * paramValues.shape[0]
# _minDistance = [0] * paramValues.shape[0]
# _meanDistance = [0] * paramValues.shape[0]

# _ttc = np.zeros([paramValues.shape[0]])
for i, X in enumerate(paramValues):
    world = network.World.load('simple-net.yml')
    sim = simulation.Simulation.load('config.yml')
    sim.duration = args.duration

    world.userInputs[0].distributions['dn'].loc = X[0]
    world.userInputs[0].distributions['headway'].loc = X[1]
    world.userInputs[0].distributions['length'].loc = X[2]
    world.userInputs[0].distributions['speed'].loc = X[3]
    # world.userInputs[0].distributions['tau'].loc = X[4]

    ttc = []
    for k in range(0, args.rep):
        simOutput = analysis.evaluateModel(world, sim, k)
        ttc.append(simOutput[0])
    _ttc[i] = ttc

ttc = np.zeros([paramValues.shape[0]])
for i, el in enumerate(_ttc):
    ttc[i] = toolkit.notNoneMean(el)

toolkit.saveYaml('outputData/sensitivity-analysis/simulationOutput.yml', ttc)
# Si = sobol.analyze(problem, _ttc, print_to_console=False)
toolkit.callWhenDone()
