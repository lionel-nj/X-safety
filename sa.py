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

problem = dict(num_vars=5,
               names=['d', 'headway', 'length', 'speed', 'tau'],
               bounds=[[7.33, 9.33],
                       [0.5, 1.9],
                       [6, 8],
                       [11, 17],
                       [1.5, 2.5],
                       ])
paramValues = saltelli.sample(problem, args.nop, seed=0)

_ttc = [0] * paramValues.shape[0]
_userCount = [0] * paramValues.shape[0]
_conflict5 = [0] * paramValues.shape[0]
_conflict10 = [0] * paramValues.shape[0]
_conflict15 = [0] * paramValues.shape[0]
_minDistance = [0] * paramValues.shape[0]
_meanDistance = [0] * paramValues.shape[0]

# _ttc = np.zeros([paramValues.shape[0]])
for i, X in enumerate(paramValues):
    world = network.World.load('simple-net.yml')
    sim = simulation.Simulation.load('config.yml')
    sim.duration = args.duration

    world.userInputs[0].distributions['dn'].loc = X[0]
    world.userInputs[0].distributions['headway'].loc = X[1]
    world.userInputs[0].distributions['length'].loc = X[2]
    world.userInputs[0].distributions['speed'].loc = X[3]
    world.userInputs[0].distributions['tau'].loc = X[4]

    ttc = []
    userCount = []
    conflict5 = []
    conflict10 = []
    conflict15 = []
    minDistance = []
    meanDistance = []

    for k in range(0, args.rep):
        simOutput = analysis.evaluateModel(world, sim, k)
        ttc.append(simOutput[0])
        minDistance.append(simOutput[1])
        meanDistance.append(simOutput[2])
        userCount.append(simOutput[3])
        conflict5.append(simOutput[4])
        conflict10.append(simOutput[5])
        conflict15.append(simOutput[6])

    _ttc[i] = ttc
    _minDistance[i] = minDistance
    _meanDistance[i] = meanDistance
    _userCount[i] = userCount
    _conflict5[i] = conflict5
    _conflict10[i] = conflict10
    _conflict15[i] = conflict15

ttc = np.zeros([paramValues.shape[0]])
minDistance = np.zeros([paramValues.shape[0]])
meanDistance = np.zeros([paramValues.shape[0]])
userCount = np.zeros([paramValues.shape[0]])
conflict5 = np.zeros([paramValues.shape[0]])
conflict10 = np.zeros([paramValues.shape[0]])
conflict15 = np.zeros([paramValues.shape[0]])

for i in range(paramValues.shape[0]):
    ttc[i] = toolkit.notNoneMean(_ttc[i])
    minDistance[i] = toolkit.notNoneMean(_minDistance[i])
    meanDistance[i] = toolkit.notNoneMean(_meanDistance[i])
    userCount[i] = toolkit.notNoneMean(_userCount[i])
    conflict5[i] = toolkit.notNoneMean(_conflict5[i])
    conflict10[i] = toolkit.notNoneMean(_conflict10[i])
    conflict15[i] = toolkit.notNoneMean(_conflict15[i])

toolkit.saveYaml('outputData/sensitivity-analysis/ttc.yml', ttc)
toolkit.saveYaml('outputData/sensitivity-analysis/mindistance.yml', minDistance)
toolkit.saveYaml('outputData/sensitivity-analysis/meandistance.yml', meanDistance)
toolkit.saveYaml('outputData/sensitivity-analysis/usercount.yml', userCount)
toolkit.saveYaml('outputData/sensitivity-analysis/conflict5.yml', conflict5)
toolkit.saveYaml('outputData/sensitivity-analysis/conflict10.yml', conflict10)
toolkit.saveYaml('outputData/sensitivity-analysis/conflict15.yml', conflict15)

# Si = sobol.analyze(problem, _ttc, print_to_console=False)
toolkit.callWhenDone()
