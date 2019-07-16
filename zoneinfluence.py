import argparse

import analysis as an
import network
import simulation

parser = argparse.ArgumentParser()
parser.add_argument("--rep", type=int, help="number of replications")
parser.add_argument("--duration", type=int, help="duration of each experiment in seconds")
args = parser.parse_args()

world = network.World.load('cross-net.yml')
sim = simulation.Simulation.load('config.yml')

sim.rep = args.rep
sim.duration = args.duration

seeds = [sim.seed+i*sim.increment for i in range(sim.rep)]
surfaces = [400, 1000, 10000]
anIdx = 0

network.createNewellMovingObjectsTable(sim.dbName)
an.createAnalysisTable(sim.dbName)
for surface in surfaces:
    analysisZone = an.AnalysisZone(world.intersections[0], surface)
    analysis = an.Analysis(idx=anIdx, seed=seed, world=world, analysisZone=analysisZone)

    for seed in seeds:

        sim.run(world)
        analysis.evaluate(sim.timeStep, sim.duration, analysisZone)

        world.saveObjects(sim.dbName, seed, anIdx)
        world.saveTrajectoriesToDB(sim.dbName, seed, anIdx)
        analysis.saveIndicators(sim.dbName)

    analysis.saveParametersToTable(sim.dbName)
    anIdx += 1