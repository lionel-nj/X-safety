import argparse

import pandas

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
args = parser.parse_args()

headways = [1.5, 1.8, 2.1, 2.4]
seeds = [k for k in range(0, 25)]

for h in headways:

    for seed in seeds:

        sim = simulation.Simulation.load('config.yml')
        sim.duration = args.duration
        sim.seed = seed
        world = network.World.load('cross-net.yml')

        world.userInputs[1].distributions['headway'].scale = h - 1
        world.userInputs[0].distributions['speed'].loc = args.speed
        world.userInputs[0].distributions['dn'].loc = args.dn
        world.userInputs[0].distributions['tau'].loc = args.tau
        world.userInputs[0].distributions['length'].loc = args.l

        simOutput = analysis.evaluateModel2(world, sim, seed, '1eval')

        ttc = simOutput[0]
        pet = simOutput[-1]

        data = pandas.DataFrame(data=[ttc, pet],
                                index=['ttc', 'pet'])
        if len(world.alignments) > 2:
            data.to_csv('outputData/evaluation1rep-crossing-h={}-seed={}.csv'.format(h, seed))
        else:
            data.to_csv('outputData/evaluation1rep-CF-h={}-seed={}.csv'.format(h, seed))

toolkit.callWhenDone()