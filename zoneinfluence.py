import argparse

import analysis as an
import network
import simulation
import toolkit

parser = argparse.ArgumentParser()
parser.add_argument("--rep", type=int, help="number of replications")
parser.add_argument("--area", type=int, help="analysis zone area")
parser.add_argument("--duration", type=int, help="duration of each experiment in seconds")
args = parser.parse_args()

world = network.World.load('cross-net.yml')
minDistance = {}
sim = simulation.Simulation.load('config.yml')
seeds = [sim.seed+i*sim.increment for i in range(sim.rep)]
surfaces = [400, 1000, 10000]

for seed in seeds:
    sim.run(world)
    world.saveObjects(sim.dbName, seed, seed)
    world.saveTrajectoriesToDB(sim.dbName, seed, seed)

    anIdx = 0
    for surface in surfaces:
        analysis = an.Analysis(idx=anIdx, seed=seed, world=world)
        analysisZone = an.AnalysisZone(world, surface)
        analysis.evaluate(sim.timeStep, sim.duration)
        analysis.createAnalysisTable(sim.dbName)
        analysis.saveIndicators(sim.dbName)

    analysis.saveParametersToTable(sim.dbName)
    anIdx += 1

toolkit.callWhenDone()
