#! /usr/bin/env python3

import analysis as an
import network
import simulation

world = network.World.load('simple-net.yml')
sim = simulation.Simulation.load('config.yml')
sim.run(world)
# world.plotUserTrajectories(sim.timeStep)
world.saveCurvilinearTrajectoriesToSqlite('world.db')
analysis = an.Analysis(idx=0, world=world, seed=sim.seed)
analysis.evaluate(sim.seed, 20)
analysis.saveIndicators('world.db')
# self.createAnalysisTable('world.db')
analysis.saveParametersToTable('world.db', sim.seed)