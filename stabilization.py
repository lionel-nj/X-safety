import argparse

import analysis
import network
import simulation
import toolkit

parser = argparse.ArgumentParser()
parser.add_argument("--rep", type=int, help="number of replications")
parser.add_argument("--duration", type=int, help="duration of each experiment in seconds")

args = parser.parse_args()


TTC = {}#np.zeros([args.rep])
userCount = {}# np.zeros([args.rep])
minDistance = {}#np.zeros([args.rep])
meanDistance = {}#np.zeros([args.rep])
meanConflictNumber5 = {}#np.zeros([args.rep])
meanConflictNumber10 = {}#np.zeros([args.rep])
meanConflictNumber15 = {}#np.zeros([args.rep])

for k in range(args.rep, 4*args.rep, 3):
    print('Processing: ' + str(k) + '/{}'.format(k))
    world = network.World.load('simple-net.yml')
    sim = simulation.Simulation.load('config.yml')
    sim.duration = args.duration
    simOutput = analysis.evaluateModel(world, sim, k)

    TTC[k] = simOutput[0]
    minDistance[k] = simOutput[1]
    meanDistance[k] = simOutput[2]
    userCount[k] = simOutput[3]
    meanConflictNumber5[k] = simOutput[4]
    meanConflictNumber10[k] = simOutput[5]
    meanConflictNumber15[k] = simOutput[6]

toolkit.saveYaml('outputData/stabilization-data/TTC-values.yml', TTC)
toolkit.saveYaml('outputData/stabilization-data/minDistance-values.yml', minDistance)
toolkit.saveYaml('outputData/stabilization-data/meanDistance-values.yml', meanDistance)
toolkit.saveYaml('outputData/stabilization-data/userCount-values.yml', userCount)
toolkit.saveYaml('outputData/stabilization-data/meanConflictNumber5-values.yml', meanConflictNumber5)
toolkit.saveYaml('outputData/stabilization-data/meanConflictNumber10-values.yml', meanConflictNumber10)
toolkit.saveYaml('outputData/stabilization-data/meanConflictNumber15-values.yml', meanConflictNumber15)

toolkit.callWhenDone()
