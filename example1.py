#! /usr/bin/env python3

import network
import simulation

world = network.World.load('simple-net.yml')
sim = simulation.Simulation.load('config.yml')
sim.run(world)
world.plotUserTrajectories(sim.timeStep)