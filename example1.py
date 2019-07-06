#! /usr/bin/env python3

import analysis as an
import network
import simulation

world = network.World.load('cross-net.yml')
sim = simulation.Simulation.load('config.yml')
sim.run(world)
# world.plotUserTrajectories(sim.timeStep)
# world.saveTrajectoriesToDB(sim.dbName)
analysis = an.Analysis(idx=0, world=world, seed=sim.seed)
a = analysis.evaluate(sim.timeStep, sim.collisionThreshold, sim.duration)
# analysis.saveIndicators(sim.dbName)

# analysis.saveParametersToTable(sim.dbName)
