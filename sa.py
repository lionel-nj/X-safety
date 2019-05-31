import argparse

import numpy as np
from SALib.sample import saltelli
from progress.bar import Bar

import analysis
import network
import simulation
import toolkit

parser = argparse.ArgumentParser()
parser.add_argument("nop", type=int, help="number of points for a parameter")
args = parser.parse_args()


problem = dict(num_vars=4,
               names=['d', 'headway', 'length', 'speed'],
               bounds=[[7.33, 9.33],
                       [0.5, 1.9],
                       [6, 8],
                       [11, 17]
                       ])
paramValues = saltelli.sample(problem, args.nop)

TTC = np.zeros([paramValues.shape[0]])
PET = np.zeros([paramValues.shape[0]])
collisionNumber = np.zeros([paramValues.shape[0]])
minDistanceAtCrossing = np.zeros([paramValues.shape[0]])
bar = Bar('Processing', max=paramValues.shape[0])

for i, X in enumerate(paramValues):
    world = network.World.load('simple-net.yml')
    sim = simulation.Simulation.load('config.yml')
    simOutput = analysis.evaluateModel(X, world, sim)
    TTC[i] = simOutput#[0]
    # PET[i] = simOutput[1]
    # collisionNumber[i] = simOutput[2]
    # minDistanceAtCrossing[i] = simOutput[3]
    bar.next()

toolkit.saveYaml('outputData/sensitivity-analysis/simulationOutput.yml', simOutput)
# Si = sobol.analyze(problem, TTC, print_to_console=False)
toolkit.callWhenDone()
bar.finish()
