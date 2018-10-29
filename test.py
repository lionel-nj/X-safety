# import carsvsped
import cars
from trafficintelligence.moving import *
from toolkit import *

parameters = load_yml('config.yml')

t_simul = parameters['simulation']['t_simulation']
delta_t = parameters['simulation']['delta_t']
number_of_cars = parameters['simulation']['number_of_cars']

# align=moving.Trajectory.generate(moving.Point(0,2000),moving.Point(6,0),334)[0]
align=[]
align1=[]
align2=[]

# p=moving.Point(0,2000)
# v=moving.Point(20,0)
# align1=moving.Trajectory.generate(p,v,150)[0]
# #
# p=moving.Point(2000,0)
# v=moving.Point(0,20)
# align2=moving.Trajectory.generate(p,v,150)[0]

# for k in range(255):
#     align1.append(Point(k,2*k))
#     align2.append(Point(2000,k))

align=moving.Trajectory.fromPointList([moving.Point(1,2), moving.Point(125,255), moving.Point(200,344), moving.Point(250,500)])
#align.computeDistances()
# align.append(align2)
alignments = [align]
for a in alignments:
    a.computeCumulativeDistances()
prepareAlignments(alignments)

test = vehicles('test.yml')
test.generateTrajectories(align)


# p=Point(1,1)
# v=Point(1,2)
#
# test=MovingObject.generate(3,p,v,TimeInterval(0,90))
# a=getSYfromXY(test.getPositionAt(50),alignments)
# # print(a)
#
# def getCurvilinearTrajectoryFromTrajectory(trajectory,alignments):
#     '''trajectory is a moving.Trajectory object
#     alignment is a list of trajectories (moving.Trajectory object)'''
#
#     CT = None
#     # preparation des splines
#     for elements in alignments:
#         elements.computeCumulativeDistances()
#     moving.prepareAlignments(alignments)
#
#     #XY->SY pour chaque moving.Point de la trajectory
#     S=[]
#     Y=[]
#     lanes=[]
#     for t in range(len(trajectory.positions)):
#
#         sy = getSYfromXY(moving.Point(trajectory.positions[t].x,trajectory.positions[t].y),[alignments])
#         S.append(sy[4])
#         Y.append(sy[5])
#         lanes.append(sy[0])
#
#     CT = CurvilinearTrajectory(S,Y,lanes)
#
#     return CT
