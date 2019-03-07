from trafficintelligence import moving
from trafficintelligence import events
from trafficintelligence import prediction
import makesimulation

o1 = makesimulation.world.alignments[0].vehicles[0]
o2 = makesimulation.world.alignments[0].vehicles[1]
# moving.MovingObject.generate(1, moving.Point(-5., 0.), moving.Point(1., 0.), moving.TimeInterval(0, 10))
# o2 = moving.MovingObject.generate(2, moving.Point(0., -5.), moving.Point(0., 1.), moving.TimeInterval(0, 10))

inter = events.Interaction(roadUser1=o1, roadUser2=o2)
inter.computeIndicators()
predictionParams = prediction.ConstantPredictionParameters(10.)
inter.computeCrossingsCollisions(predictionParams, 0.1, 10)
ttc = inter.getIndicator("Time to Collision")

#conversion of curvilinearPositions into positions
o1.velocities = moving.Trajectory()
o1.positions = moving.Trajectory()
o2.velocities = moving.Trajectory()
o2.positions = moving.Trajectory()

for el in o1.curvilinearPositions:
    o1.positions.addPosition(moving.getXYfromSY(el[0], el[1], el[2], [makesimulation.world.alignments[0].points]))

for el in o2.curvilinearPositions:
    o2.positions.addPosition(moving.getXYfromSY(el[0], el[1], el[2], [makesimulation.world.alignments[0].points]))

for el in o1.curvilinearVelocities:
    o1.velocities.addPosition(moving.getXYfromSY(el[0], el[1], 0, [makesimulation.world.alignments[0].points]))

for el in o2.curvilinearVelocities:
    o2.velocities.addPosition(moving.getXYfromSY(el[0], el[1], 0, [makesimulation.world.alignments[0].points]))