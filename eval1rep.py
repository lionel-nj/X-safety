import argparse

import pandas

import analysis
import network
import simulation

parser = argparse.ArgumentParser()
parser.add_argument("--headway", type=float, help="mean headway")
parser.add_argument("--speed", type=float, help="mean desired velocity")
parser.add_argument("--dn", type=float, help="mean delta")
parser.add_argument("--tau", type=float, help="mean tau")
parser.add_argument("--l", type=float, help="mean vehicle length")
parser.add_argument("--duration", type=int, help="duration")
parser.add_argument("--seed", type=int, help="seed")

args = parser.parse_args()
sim = simulation.Simulation.load('config.yml')
sim.duration = args.duration
world = network.World.load('simple-net.yml')
world.assignValue(args)
simOutput = analysis.evaluateModel2(world, sim, args.seed, '1eval')

ttc = simOutput[0]
pet = simOutput[-1]

data = pandas.DataFrame(data=[ttc, pet],
                        index=['ttc', 'pet'])

data.to_csv('outputData/evaluation1rep.csv')
