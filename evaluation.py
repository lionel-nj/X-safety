import argparse

import pandas as pd

import analysis
import network
import simulation
import toolkit

parser = argparse.ArgumentParser()
parser.add_argument("--speed", type=float, help="mean desired velocity")
parser.add_argument("--dn", type=float, help="mean delta")
parser.add_argument("--tau", type=float, help="mean tau")
parser.add_argument("--l", type=float, help="mean vehicle length")
parser.add_argument("--duration", type=int, help="duration")
parser.add_argument("--seed", type=int, help="seed")
parser.add_argument("--increment", type=int, help="seed increment")
parser.add_argument("--headways", type=list, help="list of headways to try")
args = parser.parse_args()

seeds = [k for k in range(args.seed, args.increment*25+1, args.increment)]

ttc = {}
minDistanceValues = {}
meanDistanceValues = {}
interactionNumber5 = {}
interactionNumber10 = {}
interactionNumber15 = {}
duration5 = {}
duration10 = {}
duration15 = {}

for h in args.headways:
    ttc[h] = dict()
    minDistanceValues[h] = dict
    meanDistanceValues[h] = dict()
    interactionNumber5[h] = dict()
    interactionNumber10[h] = dict()
    interactionNumber15[h] = dict()
    duration5[h] = dict()
    duration10[h] = dict()
    duration15[h] = dict()

    for seed in seeds:
        sim = simulation.Simulation.load('config.yml')
        sim.duration = args.duration
        sim.seed = seed
        world = network.World.load('simple-net.yml')

        world.userInputs[1].distributions['headway'].scale = h - 1
        world.userInputs[0].distributions['speed'].loc = args.speed
        world.userInputs[0].distributions['dn'].loc = args.dn
        world.userInputs[0].distributions['tau'].loc = args.tau
        world.userInputs[0].distributions['length'].loc = args.l

        ttc[h][seed],  minDistanceValues[h][seed], meanDistanceValues[h][seed], interactionNumber5[h][seed], interactionNumber10[h][seed], interactionNumber15[h][seed], \
            duration5[h][seed], duration10[h][seed], duration15[h][seed] = analysis.evaluateSimpleModel(world, sim)

data = pd.DataFrame(data=[ttc, minDistanceValues, meanDistanceValues, interactionNumber5, interactionNumber10, interactionNumber15, duration5, duration10, duration15],
                    index=['TTC', 'minDistance', 'meanDistance', 'interactionNumber5', 'interactionNumber10', 'interactionNumber15', 'interactionDuration5', 'interactionDuration10', 'interactionDuration15'])

data.to_csv('outputData/stabilization-data/data.csv')

toolkit.callWhenDone()
