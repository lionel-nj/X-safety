import argparse

import pandas

import analysis
import network
import simulation
import toolkit

parser = argparse.ArgumentParser()
parser.add_argument("--area", type=int, help="area of analysis zone")
parser.add_argument("--h1", type=int, help="mean headway on first alignment")
parser.add_argument("--h2", type=int, help="mean headway on second alignment")
parser.add_argument("--rep", type=int, help="number of replication for one experiment")
args = parser.parse_args()

TTC = {}#np.zeros([args.rep])
PET = {}#np.zeros([args.rep])
meanCollisionNumber = {}
userCount = {}# np.zeros([args.rep])
meanConflictNumber5 = {}#np.zeros([args.rep])
meanConflictNumber10 = {}#np.zeros([args.rep])
meanConflictNumber15 = {}#np.zeros([args.rep])

for k in range(0, args.rep):
    world = network.World.load('cross-net.yml')
    sim = simulation.Simulation.load('config.yml')
    indicators = analysis.evaluateModel(world, sim, k, args.area)
    TTC[k] = indicators[0]
    PET[k] = indicators[1]
    meanCollisionNumber[k] = indicators[3]
    meanConflictNumber5[k] = indicators[4]
    meanConflictNumber10[k] = indicators[5]
    meanConflictNumber15[k] = indicators[6]

data = pandas.DataFrame(data=[TTC, minDistance, meanDistance, userCount, meanConflictNumber5, meanConflictNumber10, meanConflictNumber15],
                        index=['TTC', 'minDistance', 'meanDistance', 'userCount', 'meanConflictNumber5', 'meanConflictNumber10', 'meanConflictNumber15'])

data.to_csv('outputData/zone-analysis/data-area={}-h1={}-h2={}.csv'.format(args.area, args.h1, args.h2))
toolkit.callWhenDone()
