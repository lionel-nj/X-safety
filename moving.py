#! /usr/bin/env python
'''Libraries for moving objects, trajectories...'''

import copy
from math import sqrt, atan2, cos, sin

from matplotlib.pyplot import plot, text
from numpy import median, mean, array, arange, zeros, ones, hypot, NaN, std, floor, argwhere, minimum
from scipy.signal import savgol_filter
from scipy.spatial.distance import cdist
from scipy.stats import scoreatpercentile

try:
    from shapely.geometry import Polygon, Point as shapelyPoint
    from shapely.prepared import prep, PreparedGeometry

    shapelyAvailable = True
except ImportError:
    print('Shapely library could not be loaded')
    shapelyAvailable = False

from trafficintelligence import utils, cvutils
from trafficintelligence.base import VideoFilenameAddable


class Interval(object):
    '''Generic interval: a subset of real numbers (not iterable)'''

    def __init__(self, first=0, last=-1, revert=False):
        if revert and last < first:
            self.first = last
            self.last = first
        else:
            self.first = first
            self.last = last

    def __str__(self):
        return '{0}-{1}'.format(self.first, self.last)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return ((self.first == other.first) and (self.last == other.last)) or (
                    (self.first == other.last) and (self.last == other.first))

    def empty(self):
        return self.first > self.last

    def center(self):
        return (self.first + self.last) / 2.

    def length(self):
        '''Returns the length of the interval'''
        return float(max(0, self.last - self.first))

    def equal(self, i2):
        return self.first == i2.first and self.last == i2.last

    def getList(self):
        return [self.first, self.last]

    def contains(self, instant):
        return (self.first <= instant and self.last >= instant)

    def inside(self, interval2):
        '''Indicates if the temporal interval of self is comprised in interval2'''
        return (self.first >= interval2.first) and (self.last <= interval2.last)

    def shift(self, offset):
        self.first += offset
        self.last += offset

    @classmethod
    def parse(cls, s):
        if '-' in s:
            tmp = s.split('-')
            if len(tmp) == 2:
                return cls(int(tmp[0]), int(tmp[1]))  # TODO with floats?
        print(s + ' is not a valid representation of an interval')
        return None

    @classmethod
    def union(cls, interval1, interval2):
        '''Smallest interval comprising self and interval2'''
        return cls(min(interval1.first, interval2.first), max(interval1.last, interval2.last))

    @classmethod
    def intersection(cls, interval1, interval2):
        '''Largest interval comprised in both self and interval2'''
        return cls(max(interval1.first, interval2.first), min(interval1.last, interval2.last))

    def distance(self, interval2):
        if not Interval.intersection(self, interval2).empty():
            return 0
        elif self.first > interval2.last:
            return self.first - interval2.last
        elif self.last < interval2.first:
            return interval2.first - self.last
        else:
            return None

    @classmethod
    def unionIntervals(cls, intervals):
        'returns the smallest interval containing all intervals'
        inter = cls(intervals[0].first, intervals[0].last)
        for i in intervals[1:]:
            inter = cls.union(inter, i)
        return inter


class TimeInterval(Interval):
    '''Temporal interval: set of instants at fixed time step, between first and last, included

    For example: based on frame numbers (hence the modified length method)
    It may be modified directly by setting first and last
    It also (mostly) works with datetime.datetime'''

    def __init__(self, first=0, last=-1, revert=False):
        super(TimeInterval, self).__init__(first, last, revert)

    @staticmethod
    def fromInterval(inter):
        return TimeInterval(inter.first, inter.last)

    def __getitem__(self, i):
        if not self.empty():
            if isinstance(i, int):
                return self.first + i
            else:
                raise TypeError("Invalid argument type.")
            # elif isinstance( key, slice ):

    def __iter__(self):
        self.iterInstantNum = -1
        return self

    def __next__(self):
        if self.iterInstantNum >= self.length() - 1:
            raise StopIteration
        else:
            self.iterInstantNum += 1
            return self[self.iterInstantNum]

    def length(self):
        '''Returns the length of the interval'''
        return float(max(0, self.last - self.first + 1))

    def __len__(self):
        return self.length()


# class BoundingPolygon:
#     '''Class for a polygon bounding a set of points
#     with methods to create intersection, unions...
#     '''
# We will use the polygon class of Shapely

class STObject(object):
    '''Class for spatio-temporal object, i.e. with temporal and spatial existence
    (time interval and bounding polygon for positions (e.g. rectangle)).

    It may not mean that the object is defined
    for all time instants within the time interval'''

    def __init__(self, num=None, timeInterval=None, boundingPolygon=None):
        self.num = num
        self.timeInterval = timeInterval
        self.boundingPolygon = boundingPolygon

    def empty(self):
        return self.timeInterval.empty()  # or not self.boudingPolygon

    def getNum(self):
        return self.num

    def __len__(self):
        return self.timeInterval.length()

    def length(self):
        return self.timeInterval.length()

    def getFirstInstant(self):
        return self.timeInterval.first

    def getLastInstant(self):
        return self.timeInterval.last

    def setFirstInstant(self, t):
        if t <= self.timeInterval.last:
            self.timeInterval.first = t
        else:
            print('new first instant is after last, not changing')

    def setLastInstant(self, t):
        if t >= self.timeInterval.first:
            self.timeInterval.last = t
        else:
            print('new last instant is before first, not changing')

    def getTimeInterval(self):
        return self.timeInterval

    def existsAtInstant(self, t):
        return self.timeInterval.contains(t)

    def commonTimeInterval(self, obj2):
        return TimeInterval.intersection(self.getTimeInterval(), obj2.getTimeInterval())

    def shiftTimeInterval(self, offset):
        self.timeInterval.shift(offset)


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return '({:f},{:f})'.format(self.x, self.y)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __neg__(self):
        return Point(-self.x, -self.y)

    def __mul__(self, alpha):
        'Warning, returns a new Point'
        return Point(self.x * alpha, self.y * alpha)

    def divide(self, alpha):
        'Warning, returns a new Point'
        return Point(self.x / alpha, self.y / alpha)

    def __getitem__(self, i):
        if i == 0:
            return self.x
        elif i == 1:
            return self.y
        else:
            raise IndexError()

    def orthogonal(self, clockwise=True):
        'Returns the orthogonal vector'
        if clockwise:
            return Point(self.y, -self.x)
        else:
            return Point(-self.y, self.x)

    def normalize(self):
        return self.divide(self.norm2())

    def projectLocal(self, v, clockwise=True):
        'Projects point projected on v, v.orthogonal()'
        e1 = v.normalize()
        e2 = e1.orthogonal(clockwise)
        return Point(Point.dot(self, e1), Point.dot(self, e2))

    def rotate(self, theta):
        return Point(self.x * cos(theta) - self.y * sin(theta), self.x * sin(theta) + self.y * cos(theta))

    def plot(self, options='o', **kwargs):
        plot([self.x], [self.y], options, **kwargs)

    @staticmethod
    def plotSegment(p1, p2, options='o', **kwargs):
        plot([p1.x, p2.x], [p1.y, p2.y], options, **kwargs)

    def angle(self):
        return atan2(self.y, self.x)

    def norm2Squared(self):
        '''2-norm distance (Euclidean distance)'''
        return self.x ** 2 + self.y ** 2

    def norm2(self):
        '''2-norm distance (Euclidean distance)'''
        return sqrt(self.norm2Squared())

    def norm1(self):
        return abs(self.x) + abs(self.y)

    def normMax(self):
        return max(abs(self.x), abs(self.y))

    def aslist(self):
        return [self.x, self.y]

    def astuple(self):
        return (self.x, self.y)

    def asint(self):
        return Point(int(self.x), int(self.y))

    if shapelyAvailable:
        def asShapely(self):
            return shapelyPoint(self.x, self.y)

    def homographyProject(self, homography):
        projected = cvutils.homographyProject(array([[self.x], [self.y]]), homography)
        return Point(projected[0], projected[1])

    def inPolygon(self, polygon):
        '''Indicates if the point x, y is inside the polygon
        (array of Nx2 coordinates of the polygon vertices)

        taken from http://www.ariel.com.au/a/python-point-int-poly.html

        Use Polygon.contains if Shapely is installed'''

        n = polygon.shape[0];
        counter = 0;

        p1 = polygon[0, :];
        for i in range(n + 1):
            p2 = polygon[i % n, :];
            if self.y > min(p1[1], p2[1]):
                if self.y <= max(p1[1], p2[1]):
                    if self.x <= max(p1[0], p2[0]):
                        if p1[1] != p2[1]:
                            xinters = (self.y - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1]) + p1[0];
                        if p1[0] == p2[0] or self.x <= xinters:
                            counter += 1;
            p1 = p2
        return (counter % 2 == 1);

    @staticmethod
    def fromList(p):
        return Point(p[0], p[1])

    @staticmethod
    def dot(p1, p2):
        'Scalar product'
        return p1.x * p2.x + p1.y * p2.y

    @staticmethod
    def cross(p1, p2):
        'Cross product'
        return p1.x * p2.y - p1.y * p2.x

    @staticmethod
    def parallel(p1, p2):
        return Point.cross(p1, p2) == 0.

    @staticmethod
    def cosine(p1, p2):
        return Point.dot(p1, p2) / (p1.norm2() * p2.norm2())

    @staticmethod
    def distanceNorm2(p1, p2):
        return (p1 - p2).norm2()

    @staticmethod
    def plotAll(points, options='', **kwargs):
        plot([p.x for p in points], [p.y for p in points], options, **kwargs)

    def similarOrientation(self, refDirection, cosineThreshold):
        'Indicates whether the cosine of the vector and refDirection is smaller than cosineThreshold'
        return Point.cosine(self, refDirection) >= cosineThreshold

    @staticmethod
    def timeToCollision(p1, p2, v1, v2, collisionThreshold):
        '''Computes exact time to collision with a distance threshold
        The unknown of the equation is the time to reach the intersection
        between the relative trajectory of one road user
        and the circle of radius collisionThreshold around the other road user'''
        dv = v1 - v2
        dp = p1 - p2
        a = dv.norm2Squared()  # (v1.x-v2.x)**2 + (v1.y-v2.y)**2
        b = 2 * Point.dot(dv, dp)  # 2 * ((p1.x-p2.x) * (v1.x-v2.x) + (p1.y-p2.y) * (v1.y-v2.y))
        c = dp.norm2Squared() - collisionThreshold ** 2  # (p1.x-p2.x)**2 + (p1.y-p2.y)**2 - collisionThreshold**2

        delta = b ** 2 - 4 * a * c
        if delta >= 0:
            deltaRoot = sqrt(delta)
            ttc1 = (-b + deltaRoot) / (2 * a)
            ttc2 = (-b - deltaRoot) / (2 * a)
            if ttc1 >= 0 and ttc2 >= 0:
                return min(ttc1, ttc2)
            elif ttc1 >= 0:
                return ttc1
            elif ttc2 >= 0:
                return ttc2
            else:  # ttc1 < 0 and ttc2 < 0:
                return None
        else:
            return None

    @staticmethod
    def midPoint(p1, p2):
        'Returns the middle of the segment [p1, p2]'
        return Point(0.5 * p1.x + 0.5 * p2.x, 0.5 * p1.y + 0.5 * p2.y)

    @staticmethod
    def agg(points, aggFunc=mean):
        return Point(aggFunc([p.x for p in points]), aggFunc([p.y for p in points]))

    @staticmethod
    def boundingRectangle(points, v):
        '''Returns the bounding rectangle of the points, aligned on the vector v
        A list of points is returned: front left, front right, rear right, rear left'''
        e1 = v.normalize()
        e2 = e1.orthogonal()
        xCoords = []
        yCoords = []
        for p in points:
            xCoords.append(Point.dot(e1, p))
            yCoords.append(Point.dot(e2, p))
        xmin = min(xCoords)
        xmax = max(xCoords)
        ymin = min(yCoords)
        ymax = max(yCoords)
        frontLeft = Point(xmax, ymin)
        frontRight = Point(xmax, ymax)
        rearLeft = Point(xmin, ymin)
        rearRight = Point(xmin, ymax)
        return [Point(Point.dot(e1, p), Point.dot(e2, p)) for p in [frontLeft, frontRight, rearRight, rearLeft]]


if shapelyAvailable:
    def pointsInPolygon(points, polygon):
        '''Optimized tests of a series of points within (Shapely) polygon (not prepared)'''
        if type(polygon) == PreparedGeometry:
            prepared_polygon = polygon
        else:
            prepared_polygon = prep(polygon)
        return list(filter(prepared_polygon.contains, points))


# Functions for coordinate transformation
# From Paul St-Aubin's PVA tools
def prepareAlignments(alignments):
    '''Prepares alignments (list of splines, each typically represented as a Trajectory)
    - computes cumulative distances
    - approximates slope singularity by giving some slope roundoff (account for roundoff error)'''
    for alignment in alignments:
        alignment.computeCumulativeDistances()
        p1 = alignment[0]
        for i in range(len(alignment) - 1):
            p2 = alignment[i + 1]
            if (round(p1.x, 10) == round(p2.x, 10)):
                p2.x += 0.0000000001
            if (round(p1.y, 10) == round(p2.y, 10)):
                p2.y += 0.0000000001
            p1 = p2


def ppldb2p(qx, qy, p0x, p0y, p1x, p1y):
    ''' Point-projection (Q) on line defined by 2 points (P0,P1).
        http://cs.nyu.edu/~yap/classes/visual/03s/hw/h2/math.pdf
        '''
    if (p0x == p1x and p0y == p1y):
        return None
    try:
        # Approximate slope singularity by giving some slope roundoff; account for roundoff error
        # if(round(p0x, 10) == round(p1x, 10)):
        #     p1x += 0.0000000001
        # if(round(p0y, 10) == round(p1y, 10)):
        #     p1y += 0.0000000001
        # make the calculation
        Y = (-(qx) * (p0y - p1y) - (qy * (p0y - p1y) ** 2) / (p0x - p1x) + p0x ** 2 * (p0y - p1y) / (
                    p0x - p1x) - p0x * p1x * (p0y - p1y) / (p0x - p1x) - p0y * (p0x - p1x)) / (
                        p1x - p0x - (p0y - p1y) ** 2 / (p0x - p1x))
        X = (-Y * (p1y - p0y) + qx * (p1x - p0x) + qy * (p1y - p0y)) / (p1x - p0x)
    except ZeroDivisionError:
        print('Error: Division by zero in ppldb2p. Please report this error with the full traceback:')
        print('qx={0}, qy={1}, p0x={2}, p0y={3}, p1x={4}, p1y={5}...'.format(qx, qy, p0x, p0y, p1x, p1y))
        import pdb;
        pdb.set_trace()
    return Point(X, Y)


def getSYfromXY(p, alignments, goodEnoughAlignmentDistance=0.5):
    ''' Snap a point p to its nearest subsegment of it's nearest alignment (from the list alignments).
    A alignment is a list of points (class Point), most likely a trajectory.

    Output:
    =======
    [alignment index,
    subsegment leading point index,
    snapped point,
    subsegment distance,
    alignment distance,
    orthogonal point offset]

    or None
    '''
    minOffsetY = float('inf')
    # For each alignment
    for alignmentIdx in range(len(alignments)):
        # For each alignment point index
        for alignment_p in range(len(alignments[alignmentIdx]) - 1):
            # Get closest point on alignment
            closestPoint = ppldb2p(p.x, p.y, alignments[alignmentIdx][alignment_p][0],
                                   alignments[alignmentIdx][alignment_p][1],
                                   alignments[alignmentIdx][alignment_p + 1][0],
                                   alignments[alignmentIdx][alignment_p + 1][1])
            if closestPoint is None:
                print(
                    'Error: Alignment {0}, segment {1} has identical bounds and therefore is not a vector. Projection cannot continue.'.format(
                        alignmentIdx, alignment_p))
                return None
            # check if the projected point is in between the current segment of the alignment bounds
            if utils.inBetween(alignments[alignmentIdx][alignment_p][0], alignments[alignmentIdx][alignment_p + 1][0],
                               closestPoint.x) and utils.inBetween(alignments[alignmentIdx][alignment_p][1],
                                                                   alignments[alignmentIdx][alignment_p + 1][1],
                                                                   closestPoint.y):
                offsetY = Point.distanceNorm2(closestPoint, p)
                if offsetY < minOffsetY:
                    minOffsetY = offsetY
                    snappedAlignmentIdx = alignmentIdx
                    snappedAlignmentLeadingPoint = alignment_p
                    snappedPoint = Point(closestPoint.x, closestPoint.y)
                # Jump loop if significantly close
                if offsetY < goodEnoughAlignmentDistance:
                    break

    # Get sub-segment distance
    if minOffsetY != float('inf'):
        subsegmentDistance = Point.distanceNorm2(snappedPoint,
                                                 alignments[snappedAlignmentIdx][snappedAlignmentLeadingPoint])
        # Get cumulative alignment distance (total segment distance)
        alignmentDistanceS = alignments[snappedAlignmentIdx].getCumulativeDistance(
            snappedAlignmentLeadingPoint) + subsegmentDistance
        orthogonalAlignmentVector = (
                    alignments[snappedAlignmentIdx][snappedAlignmentLeadingPoint + 1] - alignments[snappedAlignmentIdx][
                snappedAlignmentLeadingPoint]).orthogonal()
        offsetVector = p - snappedPoint
        if Point.dot(orthogonalAlignmentVector, offsetVector) < 0:
            minOffsetY = -minOffsetY
        return [snappedAlignmentIdx, snappedAlignmentLeadingPoint, snappedPoint, subsegmentDistance, alignmentDistanceS,
                minOffsetY]
    else:
        print(
            'Offset for point {} is infinite (check with prepareAlignments if some alignment segments are aligned with axes)'.format(
                p))
        return None


def getXYfromSY(s, y, alignmentNum, alignments):
    ''' Find X,Y coordinate from S,Y data.
    if mode = 0 : return Snapped X,Y
    if mode !=0 : return Real X,Y
    '''
    alignment = alignments[alignmentNum]
    i = 1
    while s > alignment.getCumulativeDistance(i) and i < len(alignment):
        i += 1
    if i < len(alignment):
        d = s - alignment.getCumulativeDistance(i - 1)  # distance on subsegment
        # Get difference vector and then snap
        dv = alignment[i] - alignment[i - 1]
        normalizedV = dv.normalize()
        # snapped = alignment[i-1] + normalizedV*d # snapped point coordinate along alignment
        # add offset finally
        orthoNormalizedV = normalizedV.orthogonal()
        return alignment[i - 1] + normalizedV * d + orthoNormalizedV * y
    else:
        print('Curvilinear point {} is past the end of the alignement'.format((s, y, alignmentNum)))
        return None


class NormAngle(object):
    '''Alternate encoding of a point, by its norm and orientation'''

    def __init__(self, norm, angle):
        self.norm = norm
        self.angle = angle

    @staticmethod
    def fromPoint(p):
        norm = p.norm2()
        if norm > 0:
            angle = p.angle()
        else:
            angle = 0.
        return NormAngle(norm, angle)

    def __add__(self, other):
        'a norm cannot become negative'
        return NormAngle(max(self.norm + other.norm, 0), self.angle + other.angle)

    def getPoint(self):
        return Point(self.norm * cos(self.angle), self.norm * sin(self.angle))


def predictPositionNoLimit(nTimeSteps, initialPosition, initialVelocity, initialAcceleration=Point(0, 0)):
    '''Predicts the position in nTimeSteps at constant speed/acceleration'''
    return initialVelocity + initialAcceleration.__mul__(nTimeSteps), initialPosition + initialVelocity.__mul__(
        nTimeSteps) + initialAcceleration.__mul__(nTimeSteps ** 2 * 0.5)


def predictPosition(position, speedOrientation, control, maxSpeed=None):
    '''Predicts the position (moving.Point) at the next time step with given control input (deltaSpeed, deltaTheta)
    speedOrientation is the other encoding of velocity, (speed, orientation)
    speedOrientation and control are NormAngle'''
    predictedSpeedTheta = speedOrientation + control
    if maxSpeed is not None:
        predictedSpeedTheta.norm = min(predictedSpeedTheta.norm, maxSpeed)
    predictedPosition = position + predictedSpeedTheta.getPoint()
    return predictedPosition, predictedSpeedTheta


class FlowVector(object):
    '''Class to represent 4-D flow vectors,
    ie a position and a velocity'''

    def __init__(self, position, velocity):
        'position and velocity should be Point instances'
        self.position = position
        self.velocity = velocity

    def __add__(self, other):
        return FlowVector(self.position + other.position, self.velocity + other.velocity)

    def __mul__(self, alpha):
        return FlowVector(self.position.__mul__(alpha), self.velocity.__mul__(alpha))

    def plot(self, options='', **kwargs):
        plot([self.position.x, self.position.x + self.velocity.x], [self.position.y, self.position.y + self.velocity.y],
             options, **kwargs)
        self.position.plot(options + 'x', **kwargs)

    @staticmethod
    def similar(f1, f2, maxDistance2, maxDeltavelocity2):
        return (f1.position - f2.position).norm2Squared() < maxDistance2 and (
                    f1.velocity - f2.velocity).norm2Squared() < maxDeltavelocity2


def intersection(p1, p2, p3, p4):
    ''' Intersection point (x,y) of lines formed by the vectors p1-p2 and p3-p4
        http://paulbourke.net/geometry/pointlineplane/'''
    dp12 = p2 - p1
    dp34 = p4 - p3
    # det = (p4.y-p3.y)*(p2.x-p1.x)-(p4.x-p3.x)*(p2.y-p1.y)
    det = float(dp34.y * dp12.x - dp34.x * dp12.y)
    if det == 0.:
        return None
    else:
        ua = (dp34.x * (p1.y - p3.y) - dp34.y * (p1.x - p3.x)) / det
        return p1 + dp12.__mul__(ua)


# def intersection(p1, p2, dp1, dp2):
#     '''Returns the intersection point between the two lines
#     defined by the respective vectors (dp) and origin points (p)'''
#     from numpy import matrix
#     from numpy.linalg import linalg
#     A = matrix([[dp1.y, -dp1.x],
#                 [dp2.y, -dp2.x]])
#     B = matrix([[dp1.y*p1.x-dp1.x*p1.y],
#                 [dp2.y*p2.x-dp2.x*p2.y]])

#     if linalg.det(A) == 0:
#         return None
#     else:
#         intersection = linalg.solve(A,B)
#         return Point(intersection[0,0], intersection[1,0])

def segmentIntersection(p1, p2, p3, p4):
    '''Returns the intersecting point of the segments [p1, p2] and [p3, p4], None otherwise'''

    if (Interval.intersection(Interval(p1.x, p2.x, True), Interval(p3.x, p4.x, True)).empty()) or (
    Interval.intersection(Interval(p1.y, p2.y, True), Interval(p3.y, p4.y, True)).empty()):
        return None
    else:
        inter = intersection(p1, p2, p3, p4)
        if (inter is not None
                and utils.inBetween(p1.x, p2.x, inter.x)
                and utils.inBetween(p3.x, p4.x, inter.x)
                and utils.inBetween(p1.y, p2.y, inter.y)
                and utils.inBetween(p3.y, p4.y, inter.y)):
            return inter
        else:
            return None


def segmentLineIntersection(p1, p2, p3, p4):
    '''Indicates if the line going through p1 and p2 intersects inside p3, p4'''
    inter = intersection(p1, p2, p3, p4)
    if inter is not None and utils.inBetween(p3.x, p4.x, inter.x) and utils.inBetween(p3.y, p4.y, inter.y):
        return inter
    else:
        return None


class Trajectory(object):
    '''Class for trajectories: temporal sequence of positions

    The class is iterable'''

    def __init__(self, positions=None):
        if positions is not None:
            self.positions = positions
        else:
            self.positions = [[], []]

    @staticmethod
    def generate(p, v, nPoints):
        t = Trajectory()
        p0 = Point(p.x, p.y)
        t.addPosition(p0)
        for i in range(nPoints - 1):
            p0 += v
            t.addPosition(p0)
        return t

    @staticmethod
    def load(line1, line2):
        return Trajectory([[float(n) for n in line1.split(' ')],
                           [float(n) for n in line2.split(' ')]])

    @staticmethod
    def fromPointList(points):
        t = Trajectory()
        if isinstance(points[0], list) or isinstance(points[0], tuple):
            for p in points:
                t.addPositionXY(p[0], p[1])
        else:
            for p in points:
                t.addPosition(p)
        return t

    def __len__(self):
        return len(self.positions[0])

    def length(self):
        return self.__len__()

    def empty(self):
        return self.__len__() == 0

    def __getitem__(self, i):
        if isinstance(i, int):
            return Point(self.positions[0][i], self.positions[1][i])
        elif isinstance(i, slice):
            return Trajectory([self.positions[0][i], self.positions[1][i]])
        else:
            raise TypeError("Invalid argument type.")

    def __str__(self):
        return ' '.join([self.__getitem__(i).__str__() for i in range(self.length())])

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        self.iterInstantNum = 0
        return self

    def __next__(self):
        if self.iterInstantNum >= self.length():
            raise StopIteration
        else:
            self.iterInstantNum += 1
            return self[self.iterInstantNum - 1]

    def __eq__(self, other):
        if self.length() == other.length():
            result = True
            for p, po in zip(self, other):
                result = result and (p == po)
            return result
        else:
            return False

    def setPositionXY(self, i, x, y):
        if i < self.__len__():
            self.positions[0][i] = x
            self.positions[1][i] = y

    def setPosition(self, i, p):
        self.setPositionXY(i, p.x, p.y)

    def addPositionXY(self, x, y):
        self.positions[0].append(x)
        self.positions[1].append(y)

    def addPosition(self, p):
        self.addPositionXY(p.x, p.y)

    def duplicateLastPosition(self):
        self.positions[0].append(self.positions[0][-1])
        self.positions[1].append(self.positions[1][-1])

    @staticmethod
    def _plot(positions, options='', withOrigin=False, lastCoordinate=None, timeStep=1, objNum=None, **kwargs):
        if lastCoordinate is None:
            plot(positions[0][::timeStep], positions[1][::timeStep], options, **kwargs)
        elif 0 <= lastCoordinate <= len(positions[0]):
            plot(positions[0][:lastCoordinate:timeStep], positions[1][:lastCoordinate:timeStep], options, **kwargs)
        if withOrigin:
            plot([positions[0][0]], [positions[1][0]], 'ro', **kwargs)
        if objNum is not None:
            text(positions[0][0], positions[1][0], '{}'.format(objNum))

    def homographyProject(self, homography):
        return Trajectory(cvutils.homographyProject(array(self.positions), homography).tolist())

    def newCameraProject(self, newCameraMatrix):
        return Trajectory(cvutils.newCameraProject(array(self.positions), newCameraMatrix).tolist())

    def plot(self, options='', withOrigin=False, timeStep=1, objNum=None, **kwargs):
        Trajectory._plot(self.positions, options, withOrigin, None, timeStep, objNum, **kwargs)

    def plotAt(self, lastCoordinate, options='', withOrigin=False, timeStep=1, objNum=None, **kwargs):
        Trajectory._plot(self.positions, options, withOrigin, lastCoordinate, timeStep, objNum, **kwargs)

    def plotOnWorldImage(self, nPixelsPerUnitDistance, options='', withOrigin=False, timeStep=1, objNum=None, **kwargs):
        imgPositions = [[x * nPixelsPerUnitDistance for x in self.positions[0]],
                        [x * nPixelsPerUnitDistance for x in self.positions[1]]]
        Trajectory._plot(imgPositions, options, withOrigin, None, timeStep, objNum, **kwargs)

    def getXCoordinates(self):
        return self.positions[0]

    def getYCoordinates(self):
        return self.positions[1]

    def asArray(self):
        return array(self.positions)

    def xBounds(self):
        # look for function that does min and max in one pass
        return Interval(min(self.getXCoordinates()), max(self.getXCoordinates()))

    def yBounds(self):
        # look for function that does min and max in one pass
        return Interval(min(self.getYCoordinates()), max(self.getYCoordinates()))

    def add(self, traj2):
        '''Returns a new trajectory of the same length'''
        if self.length() != traj2.length():
            print('Trajectories of different lengths')
            return None
        else:
            return Trajectory([[a + b for a, b in zip(self.getXCoordinates(), traj2.getXCoordinates())],
                               [a + b for a, b in zip(self.getYCoordinates(), traj2.getYCoordinates())]])

    def subtract(self, traj2):
        '''Returns a new trajectory of the same length'''
        if self.length() != traj2.length():
            print('Trajectories of different lengths')
            return None
        else:
            return Trajectory([[a - b for a, b in zip(self.getXCoordinates(), traj2.getXCoordinates())],
                               [a - b for a, b in zip(self.getYCoordinates(), traj2.getYCoordinates())]])

    def __mul__(self, alpha):
        '''Returns a new trajectory of the same length'''
        return Trajectory([[alpha * x for x in self.getXCoordinates()],
                           [alpha * y for y in self.getYCoordinates()]])

    def differentiate(self, doubleLastPosition=False):
        diff = Trajectory()
        for i in range(1, self.length()):
            diff.addPosition(self[i] - self[i - 1])
        if doubleLastPosition:
            diff.addPosition(diff[-1])
        return diff

    def differentiateSG(self, window_length, polyorder, deriv=0, delta=1.0, axis=-1, mode='interp', cval=0.0,
                        nInstantsIgnoredAtEnds=2):
        '''Differentiates the trajectory using the Savitsky Golay filter

        window_length : The length of the filter window (i.e. the number of coefficients). window_length must be a positive odd integer.
        polyorder : The order of the polynomial used to fit the samples. polyorder must be less than window_length.
        deriv : The order of the derivative to compute. This must be a nonnegative integer. The default is 0, which means to filter the data without differentiating.
        delta : The spacing of the samples to which the filter will be applied. This is only used if deriv > 0. Default is 1.0.
        axis : The axis of the array x along which the filter is to be applied. Default is -1.
        mode : Must be mirror, constant, nearest, wrap or interp. This determines the type of extension to use for the padded signal to which the filter is applied. When mode is constant, the padding value is given by cval. See the Notes for more details on mirror, constant, wrap, and nearest. When the interp mode is selected (the default), no extension is used. Instead, a degree polyorder polynomial is fit to the last window_length values of the edges, and this polynomial is used to evaluate the last window_length // 2 output values.
        cval : Value to fill past the edges of the input if mode is constant. Default is 0.0.

        https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html#scipy.signal.savgol_filter'''
        if removeBothEnds >= 1:
            pos = [self.positions[0][nInstantsIgnoredAtEnds:-nInstantsIgnoredAtEnds],
                   self.positions[1][nInstantsIgnoredAtEnds:-nInstantsIgnoredAtEnds]]
        else:
            pos = self.positions
        filtered = savgol_filter(pos, window_length, polyorder, deriv, delta, axis, mode, cval)
        return Trajectory(filtered)

    def norm(self):
        '''Returns the list of the norms at each instant'''
        return hypot(self.positions[0], self.positions[1])

    def computeCumulativeDistances(self):
        '''Computes the distance from each point to the next and the cumulative distance up to the point
        Can be accessed through getDistance(idx) and getCumulativeDistance(idx)'''
        self.distances = []
        self.cumulativeDistances = [0.]
        p1 = self[0]
        cumulativeDistance = 0.
        for i in range(self.length() - 1):
            p2 = self[i + 1]
            self.distances.append(Point.distanceNorm2(p1, p2))
            cumulativeDistance += self.distances[-1]
            self.cumulativeDistances.append(cumulativeDistance)
            p1 = p2

    def getDistance(self, i):
        '''Return the distance between points i and i+1'''
        if i < self.length() - 1:
            return self.distances[i]
        else:
            print('Index {} beyond trajectory length {}-1'.format(i, self.length()))

    def getCumulativeDistance(self, i):
        '''Return the cumulative distance between the beginning and point i'''
        if i < self.length():
            return self.cumulativeDistances[i]
        else:
            print('Index {} beyond trajectory length {}'.format(i, self.length()))

    def getMaxDistance(self, metric):
        'Returns the maximum distance between points in the trajectory'
        positions = self.getPositions().asArray().T
        return cdist(positions, positions, metric=metric).max()

    def getClosestPoint(self, p1, maxDist2=None):
        '''Returns the instant of the closest position in trajectory to p1 (and the point)
        if maxDist is not None, will check the distance is smaller
        TODO: could use cdist for different metrics'''
        distances2 = []
        minDist2 = float('inf')
        i = -1
        for p2 in self:
            distances2.append(Point.distanceNorm2(p1, p2))
            if distances2[-1] < minDist2:
                minDist2 = distances2[-1]
                i = len(distances2) - 1
        if maxDist2 is not None and minDist2 < maxDist2:
            return None
        else:
            return i

    def similarOrientation(self, refDirection, cosineThreshold, minProportion=0.5):
        '''Indicates whether the minProportion (<=1.) (eg half) of the trajectory elements (vectors for velocity)
        have a cosine with refDirection is smaller than cosineThreshold'''
        count = 0
        lengthThreshold = float(self.length()) * minProportion
        for p in self:
            if p.similarOrientation(refDirection, cosineThreshold):
                count += 1
        return count >= lengthThreshold

    def wiggliness(self):
        straightDistance = Point.distanceNorm2(self.__getitem__(0), self.__getitem__(self.length() - 1))
        if straightDistance > 0:
            return self.getCumulativeDistance(self.length() - 1) / float(straightDistance)
        else:
            return None

    def getIntersections(self, p1, p2):
        '''Returns a list of the indices at which the trajectory
        intersects with the segment of extremities p1 and p2
        Returns an empty list if there is no crossing'''
        indices = []
        intersections = []

        for i in range(self.length() - 1):
            q1 = self.__getitem__(i)
            q2 = self.__getitem__(i + 1)
            p = segmentIntersection(q1, q2, p1, p2)
            if p is not None:
                if q1.x != q2.x:
                    ratio = (p.x - q1.x) / (q2.x - q1.x)
                elif q1.y != q2.y:
                    ratio = (p.y - q1.y) / (q2.y - q1.y)
                else:
                    ratio = 0
                indices.append(i + ratio)
                intersections.append(p)
        return indices, intersections

    def getLineIntersections(self, p1, p2):
        '''Returns a list of the indices at which the trajectory
        intersects with the line going through p1 and p2
        Returns an empty list if there is no crossing'''
        indices = []
        intersections = []

        for i in range(self.length() - 1):
            q1 = self.__getitem__(i)
            q2 = self.__getitem__(i + 1)
            p = segmentLineIntersection(p1, p2, q1, q2)
            if p is not None:
                if q1.x != q2.x:
                    ratio = (p.x - q1.x) / (q2.x - q1.x)
                elif q1.y != q2.y:
                    ratio = (p.y - q1.y) / (q2.y - q1.y)
                else:
                    ratio = 0
                indices.append(i + ratio)
                intersections.append(p)
        return indices, intersections

    def subTrajectoryInInterval(self, inter):
        'Returns all position between index inter.first and index.last (included)'
        if inter.first >= 0 and inter.last <= self.length():
            return Trajectory([self.positions[0][inter.first:inter.last + 1],
                               self.positions[1][inter.first:inter.last + 1]])
        else:
            return None

    def subSample(self, step):
        'Returns the positions very step'
        return Trajectory([self.positions[0][::step],
                           self.positions[1][::step]])

    if shapelyAvailable:
        def getInstantsInPolygon(self, polygon):
            '''Returns the list of instants at which the trajectory is in the polygon'''
            instants = []
            n = self.length()
            for t, x, y in zip(range(n), self.positions[0], self.positions[1]):
                if polygon.contains(shapelyPoint(x, y)):
                    instants.append(t)
            return instants

        def getTrajectoryInPolygon(self, polygon, t2=None):
            '''Returns the trajectory built with the set of points inside the (shapely) polygon
            The polygon could be a prepared polygon (faster) from prepared.prep

            t2 is another trajectory (could be velocities)
            which is filtered based on the first (self) trajectory'''
            traj = Trajectory()
            inPolygon = []
            for x, y in zip(self.positions[0], self.positions[1]):
                inPolygon.append(polygon.contains(shapelyPoint(x, y)))
                if inPolygon[-1]:
                    traj.addPositionXY(x, y)
            traj2 = Trajectory()
            if t2 is not None:
                for inp, x, y in zip(inPolygon, t2.positions[0], t2.positions[1]):
                    if inp:
                        traj2.addPositionXY(x, y)
            return traj, traj2

        def proportionInPolygon(self, polygon, minProportion=0.5):
            instants = self.getInstantsInPolygon(polygon)
            lengthThreshold = float(self.length()) * minProportion
            return len(instants) >= lengthThreshold
    else:
        def getTrajectoryInPolygon(self, polygon, t2=None):
            '''Returns the trajectory built with the set of points inside the polygon
            (array of Nx2 coordinates of the polygon vertices)'''
            traj = Trajectory()
            inPolygon = []
            for p in self:
                inPolygon.append(p.inPolygon(polygon))
                if inPolygon[-1]:
                    traj.addPosition(p)
            traj2 = Trajectory()
            if t2 is not None:
                for inp, x, y in zip(inPolygon, t2.positions[0], t2.positions[1]):
                    if inp:
                        traj2.addPositionXY(p.x, p.y)
            return traj, traj2

        def proportionInPolygon(self, polygon, minProportion=0.5):
            inPolygon = [p.inPolygon(polygon) for p in self]
            lengthThreshold = float(self.length()) * minProportion
            return sum(inPolygon) >= lengthThreshold

    @staticmethod
    def lcss(t1, t2, lcss):
        return lcss.compute(t1, t2)


class CurvilinearTrajectory(Trajectory):
    '''Sub class of trajectory for trajectories with curvilinear coordinates and lane assignements
    longitudinal coordinate is stored as first coordinate (exterior name S)
    lateral coordinate is stored as second coordinate
    the third "lane" coordinate is for an alignment id,
    whether explicit for a list/dict of alignments,
    or implicit for a road with lane numbers'''

    def __init__(self, S=None, Y=None, lanes=None):
        if S is None or Y is None or len(S) != len(Y):
            self.positions = [[], []]
            if S is not None and Y is not None and len(S) != len(Y):
                print("S and Y coordinates of different lengths\nInitializing to empty lists")
        else:
            self.positions = [S, Y]
        if lanes is None or len(lanes) != self.length():
            self.lanes = [None] * int(self.length())
        else:
            self.lanes = lanes

    @staticmethod
    def generate(s, v, nPoints, lane, y=0):
        '''s is initial position, v is velocity
        0 in lateral coordinate by default
        TODO 2D velocity for lane change?'''
        S = [s]
        for i in range(nPoints - 1):
            S.append(S[-1] + v)
        Y = [y] * nPoints
        lanes = [lane] * nPoints
        return CurvilinearTrajectory(S, Y, lanes)

    def append(self, other):
        '''adds positions of other to the curvilinear trajectory (in-place modification)'''
        for p in other:
            self.addPosition(p)

    @staticmethod
    def fromTrajectoryProjection(t, alignments, halfWidth=3):
        ''' Add, for every object position, the class 'moving.CurvilinearTrajectory()'
            (curvilinearPositions instance) which holds information about the
            curvilinear coordinates using alignment metadata.
            From Paul St-Aubin's PVA tools
            ======

            Input:
            ======
            alignments   = a list of alignments, where each alignment is a list of
                           points (class Point).
            halfWidth = moving average window (in points) in which to smooth
                           lane changes. As per tools_math.cat_mvgavg(), this term
                           is a search *radius* around the center of the window.

            '''
        curvilinearPositions = CurvilinearTrajectory()

        # For each point
        for i in range(int(t.length())):
            result = getSYfromXY(t[i], alignments)

            # Error handling
            if (result is None):
                print(
                    'Warning: trajectory at point {} {} has alignment errors (alignment snapping)\nCurvilinear trajectory could not be computed'.format(
                        i, t[i]))
            else:
                [align, alignPoint, snappedPoint, subsegmentDistance, S, Y] = result
                curvilinearPositions.addPositionSYL(S, Y, align)

        ## Go back through points and correct lane
        # Run through objects looking for outlier point
        smoothed_lanes = utils.filterCategoricalMovingWindow(curvilinearPositions.getLanes(), halfWidth)
        ## Recalculate projected point to new lane
        lanes = curvilinearPositions.getLanes()
        if (lanes != smoothed_lanes):
            for i in range(len(lanes)):
                if (lanes[i] != smoothed_lanes[i]):
                    result = getSYfromXY(t[i], [alignments[smoothed_lanes[i]]])

                    # Error handling
                    if (result is None):
                        ## This can be triggered by tracking errors when the trajectory jumps around passed another alignment.
                        print(
                            '    Warning: trajectory at point {} {} has alignment errors during trajectory smoothing and will not be corrected.'.format(
                                i, t[i]))
                    else:
                        [align, alignPoint, snappedPoint, subsegmentDistance, S, Y] = result
                        curvilinearPositions.setPosition(i, S, Y, align)
        return curvilinearPositions

    def __getitem__(self, i):
        if isinstance(i, int):
            return [self.positions[0][i], self.positions[1][i], self.lanes[i]]
        else:
            raise TypeError("Invalid argument type.")
            # elif isinstance( key, slice ):

    def getSCoordinates(self):
        return self.getXCoordinates()

    def getLanes(self):
        return self.lanes

    def getSCoordAt(self, i):
        return self.positions[0][i]

    def getYCoordAt(self, i):
        return self.positions[1][i]

    def getLaneAt(self, i):
        return self.lanes[i]

    def subTrajectoryInInterval(self, inter):
        'Returns all curvilinear positions between index inter.first and index.last (included)'
        if inter.first >= 0 and inter.last <= self.length():
            return CurvilinearTrajectory(self.positions[0][inter.first:inter.last + 1],
                                         self.positions[1][inter.first:inter.last + 1],
                                         self.lanes[inter.first:inter.last + 1])
        else:
            return None

    def addPositionSYL(self, s, y, lane=None):
        self.addPositionXY(s, y)
        self.lanes.append(lane)

    def addPosition(self, p):
        'Adds position in the point format for curvilinear of list with 3 values'
        self.addPositionSYL(p[0], p[1], p[2])

    def duplicateLastPosition(self):
        super(CurvilinearTrajectory, self).duplicateLastPosition()
        self.lanes.append(self.lanes[-1])

    def setPosition(self, i, s, y, lane):
        self.setPositionXY(i, s, y)
        if i < self.__len__():
            self.lanes[i] = lane

    def differentiate(self, doubleLastPosition=False):
        diff = CurvilinearTrajectory()
        p1 = self[0]
        for i in range(1, self.length()):
            p2 = self[i]
            if p2[2] == p1[2]:
                laneChange = None
            else:
                laneChange = (p1[2], p2[2])
            diff.addPositionSYL(p2[0] - p1[0], p2[1] - p1[1], laneChange)
            p1 = p2
        if doubleLastPosition and self.length() > 1:
            diff.addPosition(diff[-1])
        return diff

    def getIntersections(self, S1, lane=None):
        '''Returns a list of the indices at which the trajectory
        goes past the curvilinear coordinate S1
        (in provided lane if lane is not None)
        Returns an empty list if there is no crossing'''
        indices = []
        for i in range(self.length() - 1):
            q1 = self.__getitem__(i)
            q2 = self.__getitem__(i + 1)
            if q1[0] <= S1 < q2[0] and (lane is None or (self.lanes[i] == lane and self.lanes[i + 1] == lane)):
                indices.append(i + (S1 - q1[0]) / (q2[0] - q1[0]))
        return indices


##################
# Moving Objects
##################

userTypeNames = ['unknown',
                 'car',
                 'pedestrian',
                 'motorcycle',
                 'bicycle',
                 'bus',
                 'truck']

userType2Num = utils.inverseEnumeration(userTypeNames)


class CarClassifier:
    def predict(self, hog):
        return userType2Num['car']


carClassifier = CarClassifier()


class MovingObject(STObject, VideoFilenameAddable):
    '''Class for moving objects: a spatio-temporal object
    with a trajectory and a geometry (constant volume over time)
    and a usertype (e.g. road user) coded as a number (see userTypeNames)
    '''

    def __init__(self, num=None, timeInterval=None, positions=None, velocities=None, geometry=None,
                 userType=userType2Num['unknown'], nObjects=None, initCurvilinear=False):
        super(MovingObject, self).__init__(num, timeInterval)
        if initCurvilinear:
            self.curvilinearPositions = positions
            self.curvilinearVelocities = velocities  # third component is (previousAlignmentIdx, newAlignmentIdx) or None if no change
        else:
            self.positions = positions
            self.velocities = velocities
        self.geometry = geometry
        self.userType = userType
        self.setNObjects(nObjects)  # a feature has None for nObjects
        self.features = None
        # compute bounding polygon from trajectory

    @staticmethod
    def croppedTimeInterval(obj, value, after=True):
        newTimeInterval = TimeInterval(obj.getFirstInstant(),
                                       min(value, obj.getLastInstant())) if after else TimeInterval(
            max(obj.getFirstInstant(), value), obj.getLastInstant())
        if obj.positions is not None:
            newPositions = obj.positions[slice(newTimeInterval.first, newTimeInterval.last + 1)]
        else:
            newPositions = None
        if obj.velocities is not None:
            newVelocities = obj.velocities[slice(newTimeInterval.first, newTimeInterval.last + 1)]
        else:
            newVelocities = None
        if obj.hasFeatures():
            newFeatures = [f.croppedTimeInterval(value, after) for f in obj.features]
        else:
            newFeatures = None
        res = MovingObject(obj.getNum(), newTimeInterval, newPositions, newVelocities, obj.geometry, obj.userType,
                           obj.nObjects)
        res.features = newFeatures
        res.featureNumbers = obj.featureNumbers
        # if hasattr(obj, 'projectedPositions'):
        #    res.projectedPositions = obj.projectedPositions[slice(newTimeInterval.first, newTimeInterval.last+1)]
        return res

    @staticmethod
    def aggregateTrajectories(features, interval=None, aggFunc=mean):
        'Computes the aggregate trajectory from list of MovingObject features'
        positions = Trajectory()
        velocities = Trajectory()
        if interval is None:
            inter = TimeInterval.unionIntervals([f.getTimeInterval() for f in features])
        else:
            inter = interval
        for t in inter:
            points = []
            vels = []
            for f in features:
                if f.existsAtInstant(t):
                    points.append(f.getPositionAtInstant(t))
                    vels.append(f.getVelocityAtInstant(t))
            positions.addPosition(Point.agg(points, aggFunc))
            velocities.addPosition(Point.agg(vels, aggFunc))
        return inter, positions, velocities

    @staticmethod
    def generate(num, p, v, timeInterval):
        nPoints = int(timeInterval.length())
        positions = Trajectory.generate(p, v, nPoints)
        return MovingObject(num=num, timeInterval=timeInterval, positions=positions,
                            velocities=Trajectory([[v.x] * nPoints, [v.y] * nPoints]))

    def updatePositions(self):
        inter, self.positions, self.velocities = MovingObject.aggregateTrajectories(self.features,
                                                                                    self.getTimeInterval())

    def addNewellAttributes(self, desiredSpeed, tau, d, initialCumulatedHeadway, initialAlignmentIdx):
        '''adds attributes necessary for Newell car following model
        using curvilinear trajectories'''
        # Newell model parameters
        self.desiredSpeed = desiredSpeed
        self.tau = tau
        self.d = d
        self.leader = None
        # other attributes necessary for computation
        self.initialCumulatedHeadway = initialCumulatedHeadway
        self.initialAlignmentIdx = initialAlignmentIdx
        self.timeAtS0 = None  # time at which the vehicle's position is s=0 on the alignment,

    # def areCrossing(self, other, firstThreshold, secondThreshold, instant):
    #
    #     if self.leader is not None and other.leader is not None:
    #         return self.leader.getCurvilinearPositionAtInstant(instant) >= firstThreshold and other.leader.getCurvilinearPositionAtInstant(instant) >= secondThreshold
    #     elif self.leader is not None and other.leader is None:
    #         return self.leader.getCurvilinearPositionAtInstant(instant) >= firstThreshold
    #     elif self.leader is None and other.leader is not None:
    #         return other.leader.getCurvilinearPositionAtInstant(instant) >= secondThreshold
    #     else:
    #         return True

    def updateCurvilinearPositions(self, method, instant, timeStep, maxSpeed=None,
                                   acceleration=None):
        '''Update curvilinear position of user at new instant'''
        # TODO changer nextAlignmentIdx pour l'alignment en cours, reflechir pour des control devices
        if method == 'newell':
            if self.curvilinearPositions is None:  # vehicle without positions
                if self.timeAtS0 is None:
                    if self.leader is None:
                        self.timeAtS0 = self.initialCumulatedHeadway
                    elif self.leader.curvilinearPositions is not None and self.leader.curvilinearPositions.getSCoordAt(
                            -1) > self.d and len(self.leader.curvilinearPositions) >= 2:
                        firstInstantAfterD = self.leader.getLastInstant()
                        while self.leader.existsAtInstant(firstInstantAfterD) and \
                                self.leader.getCurvilinearPositionAtInstant(firstInstantAfterD - 1)[
                                    0] > self.d:  # find first instant after d
                            firstInstantAfterD -= 1  # if not recorded position before self.d, we extrapolate linearly from first known position
                        leaderSpeed = self.leader.getCurvilinearVelocityAtInstant(firstInstantAfterD - 1)[0]
                        self.timeAtS0 = self.tau + firstInstantAfterD * timeStep - (
                                    self.leader.getCurvilinearPositionAtInstant(firstInstantAfterD)[
                                        0] - self.d) * timeStep / leaderSpeed  # second part is the time at which leader is at self.d
                        if self.timeAtS0 < self.initialCumulatedHeadway:  # obj appears at instant initialCumulatedHeadway at x=0 with desiredSpeed
                            self.timeAtS0 = self.initialCumulatedHeadway
                elif instant * timeStep > self.timeAtS0:
                    # firstInstant = int(ceil(self.timeAtS0/timeStep))# this first instant is instant by definition
                    leaderInstant = instant - self.tau / timeStep
                    if self.leader is None:
                        s = (timeStep * instant - self.timeAtS0) * self.desiredSpeed
                        self.timeInterval = TimeInterval(instant, instant)
                        self.curvilinearPositions = CurvilinearTrajectory([s], [0.], [self.initialAlignmentIdx])
                        self.curvilinearVelocities = CurvilinearTrajectory()
                    elif self.leader.existsAtInstant(leaderInstant):
                        self.timeInterval = TimeInterval(instant, instant)
                        freeFlowCoord = (instant * timeStep - self.timeAtS0) * self.desiredSpeed
                        # constrainedCoord at instant = xn-1(t = instant*timeStep-self.tau)-self.d
                        constrainedCoord = self.leader.interpolateCurvilinearPositions(leaderInstant)[0] - self.d
                        self.curvilinearPositions = CurvilinearTrajectory([min(freeFlowCoord, constrainedCoord)], [0.],
                                                                          [self.initialAlignmentIdx])
                        self.curvilinearVelocities = CurvilinearTrajectory()
            else:
                s1 = self.curvilinearPositions.getSCoordAt(-1)
                freeFlowCoord = s1 + self.desiredSpeed * timeStep

                if self.leader is not None:
                    if not self.leader.inSimulation:
                        self.leader = None

                if self.leader is None:
                    if self.getLastInstant() < instant:
                        s2 = freeFlowCoord
                        nextAlignment = self.currentAlignment.getNextAlignment(self, s2)
                        if nextAlignment is None:
                            nextAlignmentIdx = self.curvilinearPositions.getLaneAt(-1)
                        else:
                            if nextAlignment:
                                nextAlignmentIdx = nextAlignment.idx
                        if self.inSimulation:
                            self.curvilinearPositions.addPositionSYL(freeFlowCoord, 0., nextAlignmentIdx)
                else:
                    constrainedCoord = self.leader.interpolateCurvilinearPositions(instant - self.tau / timeStep)[
                                           0] - self.d
                    s2 = min(freeFlowCoord, constrainedCoord)
                    nextAlignment = self.currentAlignment.getNextAlignment(self, s2)
                    if nextAlignment is None:
                        nextAlignmentIdx = self.curvilinearPositions.getLaneAt(-1)
                    else:
                        nextAlignmentIdx = nextAlignment.idx
                    self.curvilinearPositions.addPositionSYL(s2, 0., nextAlignmentIdx)
                if self.inSimulation:
                    if nextAlignment is not None:
                        laneChange = (self.curvilinearPositions.getLaneAt(-1), nextAlignmentIdx)
                    else:
                        laneChange = None
                    self.setLastInstant(instant)
                    self.curvilinearVelocities.addPositionSYL(s2 - s1, 0., laneChange)

    @staticmethod
    def concatenate(obj1, obj2, num=None, newFeatureNum=None, computePositions=False):
        '''Concatenates two objects, whether overlapping temporally or not

        Positions will be recomputed only if computePositions is True
        Otherwise, only featureNumbers and/or features will be merged'''
        if num is None:
            newNum = obj1.getNum()
        else:
            newNum = num
        commonTimeInterval = obj1.commonTimeInterval(obj2)
        if commonTimeInterval.empty():
            # print('The two objects\' time intervals do not overlap: obj1 {} and obj2 {}'.format(obj1.getTimeInterval(), obj2.getTimeInterval()))
            emptyInterval = TimeInterval(min(obj1.getLastInstant(), obj2.getLastInstant()),
                                         max(obj1.getFirstInstant(), obj2.getFirstInstant()))
            if obj1.existsAtInstant(emptyInterval.last):
                firstObject = obj2
                secondObject = obj1
            else:
                firstObject = obj1
                secondObject = obj2
            v = (secondObject.getPositionAtInstant(emptyInterval.last) - firstObject.getPositionAtInstant(
                emptyInterval.first)).divide(emptyInterval.length() - 1)
            positions = copy.deepcopy(firstObject.getPositions())
            velocities = copy.deepcopy(firstObject.getPositions())
            featurePositions = Trajectory()
            featureVelocities = Trajectory()
            p = firstObject.getPositionAtInstant(emptyInterval.first) + v
            for t in range(emptyInterval.first + 1, emptyInterval.last):
                positions.addPosition(p)
                velocities.addPosition(v)
                featurePositions.addPosition(p)
                featureVelocities.addPosition(v)
                p = p + v
            for t in secondObject.getTimeInterval():
                positions.addPosition(secondObject.getPositionAtInstant(t))
                velocities.addPosition(secondObject.getVelocityAtInstant(t))
            newObject = MovingObject(newNum, TimeInterval(firstObject.getFirstInstant(), secondObject.getLastInstant()),
                                     positions, velocities, nObjects=1)
            if hasattr(obj1, 'featureNumbers') and hasattr(obj2, 'featureNumbers'):
                if newFeatureNum is not None:
                    newObject.featureNumbers = obj1.featureNumbers + obj2.featureNumbers + [newFeatureNum]
                else:
                    print('Issue, new created feature has no num id')
            if obj1.hasFeatures() and obj2.hasFeatures():
                newObject.features = obj1.getFeatures() + obj2.getFeatures() + [
                    MovingObject(newFeatureNum, TimeInterval(emptyInterval.first + 1, emptyInterval.last - 1),
                                 featurePositions, featureVelocities)]
                newObject.updatePositions()
        else:  # time intervals overlap
            newTimeInterval = TimeInterval.union(obj1.getTimeInterval(), obj2.getTimeInterval())
            newObject = MovingObject(newNum, newTimeInterval,
                                     nObjects=1)  # hypothesis is that it's the same object being reunited
            if hasattr(obj1, 'featureNumbers') and hasattr(obj2, 'featureNumbers'):
                newObject.featureNumbers = obj1.featureNumbers + obj2.featureNumbers
            if obj1.hasFeatures() and obj2.hasFeatures():
                newObject.features = obj1.getFeatures() + obj2.getFeatures()
                newObject.updatePositions()
            else:
                print('Cannot update object positions without features')
        # user type
        if obj1.getUserType() != obj2.getUserType():
            print('The two moving objects have different user types: obj1 {} obj2 {}'.format(
                userTypeNames[obj1.getUserType()], userTypeNames[obj2.getUserType()]))
        newObject.setUserType(obj1.getUserType())
        return newObject

    def getObjectInTimeInterval(self, inter):
        '''Returns a new object extracted from self,
        restricted to time interval inter'''
        intersection = TimeInterval.intersection(inter, self.getTimeInterval())
        if not intersection.empty():
            trajectoryInterval = TimeInterval(intersection.first - self.getFirstInstant(),
                                              intersection.last - self.getFirstInstant())
            obj = MovingObject(self.num, intersection, self.positions.getTrajectoryInInterval(trajectoryInterval),
                               self.geometry, self.userType, self.nObjects)
            if self.velocities is not None:
                obj.velocities = self.velocities.getTrajectoryInInterval(trajectoryInterval)
            return obj
        else:
            print('The object does not exist at {}'.format(inter))
            return None

    def getObjectsInMask(self, mask, homography=None, minLength=1):
        '''Returns new objects made of the positions in the mask
        mask is in the destination of the homography space'''
        if homography is not None:
            self.projectedPositions = self.positions.homographyProject(homography)
        else:
            self.projectedPositions = self.positions

        def inMask(positions, i, mask):
            p = positions[i]
            return mask[int(p.y), int(p.x)] != 0.

        # subTimeIntervals self.getFirstInstant()+i
        filteredIndices = [inMask(self.projectedPositions, i, mask) for i in range(int(self.length()))]
        # 'connected components' in subTimeIntervals
        l = 0
        intervalLabels = []
        prev = True
        for i in filteredIndices:
            if i:
                if not prev:  # new interval
                    l += 1
                intervalLabels.append(l)
            else:
                intervalLabels.append(-1)
            prev = i
        intervalLabels = array(intervalLabels)
        subObjects = []
        for l in set(intervalLabels):
            if l >= 0:
                if sum(intervalLabels == l) >= minLength:
                    times = [self.getFirstInstant() + i for i in range(len(intervalLabels)) if intervalLabels[i] == l]
                    subTimeInterval = TimeInterval(min(times), max(times))
                    subObjects.append(self.getObjectInTimeInterval(subTimeInterval))

        return subObjects

    def getPositions(self):
        return self.positions

    def getVelocities(self):
        return self.velocities

    def getUserType(self):
        return self.userType

    def computeCumulativeDistances(self):
        self.positions.computeCumulativeDistances()

    def getCurvilinearPositions(self):
        if hasattr(self, 'curvilinearPositions'):
            return self.curvilinearPositions
        else:
            return None

    def plotCurvilinearPositions(self, lane=None, options='', withOrigin=False, **kwargs):
        if hasattr(self, 'curvilinearPositions'):
            if lane is None:
                plot(list(self.getTimeInterval()), self.curvilinearPositions.positions[0], options, **kwargs)
                if withOrigin:
                    plot([self.getFirstInstant()], [self.curvilinearPositions.positions[0][0]], 'ro', **kwargs)
            else:
                instants = []
                coords = []
                for t, p in zip(self.getTimeInterval(), self.curvilinearPositions):
                    if p[2] == lane:
                        instants.append(t)
                        coords.append(p[0])
                    else:
                        instants.append(NaN)
                        coords.append(NaN)
                plot(instants, coords, options, **kwargs)
                if withOrigin and len(instants) > 0:
                    plot([instants[0]], [coords[0]], 'ro', **kwargs)
        else:
            print('Object {} has no curvilinear positions'.format(self.getNum()))

    def interpolateCurvilinearPositions(self, t):
        '''Linear interpolation of curvilinear positions, t being a float'''
        if hasattr(self, 'curvilinearPositions'):
            if self.existsAtInstant(t):
                i = int(floor(t))
                p1 = self.getCurvilinearPositionAtInstant(i)
                p2 = self.getCurvilinearPositionAtInstant(i + 1)
                alpha = t - float(i)
                if alpha < 0.5:
                    lane = p1[2]
                else:
                    lane = p2[2]
                return [(1 - alpha) * p1[0] + alpha * p2[0], (1 - alpha) * p1[1] + alpha * p2[1], lane]
            else:
                print('Object {} does not exist at {}'.format(self.getNum(), t))
        else:
            print('Object {} has no curvilinear positions'.format(self.getNum()))

    def setUserType(self, userType):
        self.userType = userType

    def getNObjects(self):
        return self.nObjects

    def setNObjects(self, nObjects):
        if nObjects is None or nObjects >= 1:
            self.nObjects = nObjects
        else:
            print('Number of objects represented by object {} must be greater or equal to 1 ({})'.format(self.getNum(),
                                                                                                         nObjects))
            self.nObjects = None

    def setFeatures(self, features, featuresOrdered=False):
        '''Sets the features in the features field based on featureNumbers
        if not all features are loaded from 0, one needs to renumber in a dict'''
        if featuresOrdered:
            tmp = features
        else:
            tmp = {f.getNum(): f for f in features}
        self.features = [tmp[i] for i in self.featureNumbers]

    def getFeatures(self):
        return self.features

    def hasFeatures(self):
        return (self.features is not None)

    def getFeature(self, i):
        if self.hasFeatures() and i < len(self.features):
            return self.features[i]
        else:
            return None

    def getNLongestFeatures(self, nFeatures=1):
        if self.features is None:
            return []
        else:
            tmp = utils.sortByLength(self.getFeatures(), reverse=True)
            return tmp[:min(len(tmp), nFeatures)]

    def getFeatureNumbersOverTime(self):
        '''Returns the number of features at each instant
        dict instant -> number of features'''
        if self.hasFeatures():
            featureNumbers = {}
            for t in self.getTimeInterval():
                n = 0
                for f in self.getFeatures():
                    if f.existsAtInstant(t):
                        n += 1
                featureNumbers[t] = n
            return featureNumbers
        else:
            print('Object {} has no features loaded.'.format(self.getNum()))
            return None

    def getSpeeds(self, nInstantsIgnoredAtEnds=0):
        speeds = self.getVelocities().norm()
        if nInstantsIgnoredAtEnds > 0:
            n = min(nInstantsIgnoredAtEnds, int(floor(self.length() / 2.)))
            return speeds[n:-n]
        else:
            return speeds

    def getAccelerations(self, window_length, polyorder, delta=1.0, axis=-1, mode='interp', cval=0.0, speeds=None,
                         nInstantsIgnoredAtEnds=0):
        '''Returns the 1-D acceleration from the 1-D speeds
        Caution about previously filtered data'''
        if speeds is None:
            speeds = self.getSpeeds(nInstantsIgnoredAtEnds)
        return savgol_filter(speeds, window_length, polyorder, 1, delta, axis, mode, cval)

    def getSpeedIndicator(self):
        from indicators import SeverityIndicator
        return SeverityIndicator('Speed', {t: self.getVelocityAtInstant(t).norm2() for t in self.getTimeInterval()})

    def getPositionAt(self, i):
        return self.positions[i]

    def getVelocityAt(self, i):
        return self.velocities[i]

    def getPositionAtInstant(self, i):
        return self.positions[i - self.getFirstInstant()]

    def getVelocityAtInstant(self, i):
        return self.velocities[i - self.getFirstInstant()]

    def getCurvilinearPositionAt(self, i):
        return self.curvilinearPositions[i]

    def getCurvilinearVelocityAt(self, i):
        return self.curvilinearVelocities[i]

    def getCurvilinearPositionAtInstant(self, i):
        return self.curvilinearPositions[i - self.getFirstInstant()]

    def getCurvilinearVelocityAtInstant(self, i):
        return self.curvilinearVelocities[i - self.getFirstInstant()]

    def getXCoordinates(self):
        return self.positions.getXCoordinates()

    def getYCoordinates(self):
        return self.positions.getYCoordinates()

    def plot(self, options='', withOrigin=False, timeStep=1, withFeatures=False, withIds=False, **kwargs):
        if withIds:
            objNum = self.getNum()
        else:
            objNum = None
        if withFeatures and self.hasFeatures():
            for f in self.getFeatures():
                f.positions.plot('r', True, timeStep, **kwargs)
            self.positions.plot('bx-', True, timeStep, objNum, **kwargs)
        else:
            self.positions.plot(options, withOrigin, timeStep, objNum, **kwargs)

    def plotOnWorldImage(self, nPixelsPerUnitDistance, options='', withOrigin=False, timeStep=1, withIds=False,
                         **kwargs):
        if withIds:
            self.positions.plotOnWorldImage(nPixelsPerUnitDistance, options, withOrigin, timeStep, self.getNum(),
                                            **kwargs)
        else:
            self.positions.plotOnWorldImage(nPixelsPerUnitDistance, options, withOrigin, timeStep, None, **kwargs)

    def play(self, videoFilename, homography=None, undistort=False, intrinsicCameraMatrix=None,
             distortionCoefficients=None, undistortedImageMultiplication=1.):
        cvutils.displayTrajectories(videoFilename, [self], homography=homography, firstFrameNum=self.getFirstInstant(),
                                    lastFrameNumArg=self.getLastInstant(), undistort=undistort,
                                    intrinsicCameraMatrix=intrinsicCameraMatrix,
                                    distortionCoefficients=distortionCoefficients,
                                    undistortedImageMultiplication=undistortedImageMultiplication)

    def speedDiagnostics(self, framerate=1., display=False, nInstantsIgnoredAtEnds=0):
        speeds = framerate * self.getSpeeds(nInstantsIgnoredAtEnds)
        coef = utils.linearRegression(list(range(len(speeds))), speeds)
        print('min/5th perc speed: {} / {}\nspeed diff: {}\nspeed stdev: {}\nregression: {}'.format(min(speeds),
                                                                                                    scoreatpercentile(
                                                                                                        speeds, 5),
                                                                                                    speeds[-2] - speeds[
                                                                                                        1], std(speeds),
                                                                                                    coef[0]))
        if display:
            from matplotlib.pyplot import figure, axis
            figure(1)
            self.plot()
            axis('equal')
            figure(2)
            plot(list(self.getTimeInterval()), speeds)
            figure(3)
            plot(list(self.getTimeInterval()), self.getAccelerations(9, 3, speeds=speeds))  # arbitrary parameter

    @staticmethod
    def minMaxDistance(obj1, obj2):
        '''Computes the min max distance used for feature grouping'''
        commonTimeInterval = obj1.commonTimeInterval(obj2)
        if not commonTimeInterval.empty():
            minDistance = (obj1.getPositionAtInstant(commonTimeInterval.first) - obj2.getPositionAtInstant(
                commonTimeInterval.first)).norm2()
            maxDistance = minDistance
            for t in list(commonTimeInterval)[1:]:
                d = (obj1.getPositionAtInstant(t) - obj2.getPositionAtInstant(t)).norm2()
                if d < minDistance:
                    minDistance = d
                elif d > maxDistance:
                    maxDistance = d
            return int(commonTimeInterval.length()), minDistance, maxDistance
        else:
            return int(commonTimeInterval.length()), None, None

    @staticmethod
    def distances(obj1, obj2, instant1, _instant2=None):
        '''Returns the distances between all features of the 2 objects
        at the same instant instant1
        or at instant1 and instant2'''
        if _instant2 is None:
            instant2 = instant1
        else:
            instant2 = _instant2
        positions1 = [f.getPositionAtInstant(instant1).astuple() for f in obj1.features if f.existsAtInstant(instant1)]
        positions2 = [f.getPositionAtInstant(instant2).astuple() for f in obj2.features if f.existsAtInstant(instant2)]
        return cdist(positions1, positions2, metric='euclidean')

    @staticmethod
    def minDistance(obj1, obj2, instant1, instant2=None):
        return MovingObject.distances(obj1, obj2, instant1, instant2).min()

    @staticmethod
    def maxDistance(obj1, obj2, instant, instant2=None):
        return MovingObject.distances(obj1, obj2, instant1, instant2).max()

    def maxSize(self):
        '''Returns the max distance between features
        at instant there are the most features'''
        if hasattr(self, 'features'):
            nFeatures = -1
            tMaxFeatures = 0
            for t in self.getTimeInterval():
                n = len([f for f in self.features if f.existsAtInstant(t)])
                if n > nFeatures:
                    nFeatures = n
                    tMaxFeatures = t
            return MovingObject.maxDistance(self, self, tMaxFeatures)
        else:
            print('Load features to compute a maximum size')
            return None

    def setRoutes(self, startRouteID, endRouteID):
        self.startRouteID = startRouteID
        self.endRouteID = endRouteID

    def getInstantsCrossingLane(self, p1, p2):
        '''Returns the instant(s)
        at which the object passes from one side of the segment to the other
        empty list if there is no crossing'''
        indices, intersections = self.positions.getIntersections(p1, p2)
        return [t + self.getFirstInstant() for t in indices]

    def computeTrajectorySimilarities(self, prototypes, lcss):
        'Computes the similarities to the prototypes using the LCSS'
        if not hasattr(self, 'prototypeSimilarities'):
            self.prototypeSimilarities = []
            for proto in prototypes:
                lcss.similarities(proto.getMovingObject().getPositions().asArray().T, self.getPositions().asArray().T)
                similarities = lcss.similarityTable[-1, :-1].astype(float)
                self.prototypeSimilarities.append(similarities / minimum(arange(1., len(similarities) + 1),
                                                                         proto.getMovingObject().length() * ones(
                                                                             len(similarities))))

    @staticmethod
    def computePET(obj1, obj2, collisionDistanceThreshold):
        '''Post-encroachment time based on distance threshold

        Returns the smallest time difference when the object positions are within collisionDistanceThreshold
        and the instants at which each object is passing through its corresponding position'''
        positions1 = [p.astuple() for p in obj1.getPositions()]
        positions2 = [p.astuple() for p in obj2.getPositions()]
        n1 = len(positions1)
        n2 = len(positions2)
        pets = zeros((n1, n2))
        for i, t1 in enumerate(obj1.getTimeInterval()):
            for j, t2 in enumerate(obj2.getTimeInterval()):
                pets[i, j] = abs(t1 - t2)
        distances = cdist(positions1, positions2, metric='euclidean')
        smallDistances = (distances <= collisionDistanceThreshold)
        if smallDistances.any():
            smallPets = pets[smallDistances]
            petIdx = smallPets.argmin()
            distanceIndices = argwhere(smallDistances)[petIdx]
            return smallPets[petIdx], obj1.getFirstInstant() + distanceIndices[0], obj2.getFirstInstant() + \
                   distanceIndices[1]
        else:
            return None, None, None

    def predictPosition(self, instant, nTimeSteps, externalAcceleration=Point(0, 0)):
        '''Predicts the position of object at instant+deltaT,
        at constant speed'''
        return predictPositionNoLimit(nTimeSteps, self.getPositionAtInstant(instant),
                                      self.getVelocityAtInstant(instant), externalAcceleration)

    def projectCurvilinear(self, alignments, halfWidth=3):
        self.curvilinearPositions = CurvilinearTrajectory.fromTrajectoryProjection(self.getPositions(), alignments,
                                                                                   halfWidth)

    def computeSmoothTrajectory(self, minCommonIntervalLength):
        '''Computes the trajectory as the mean of all features
        if a feature exists, its position is

        Warning work in progress
        TODO? not use the first/last 1-.. positions'''
        nFeatures = len(self.features)
        if nFeatures == 0:
            print('Empty object features\nCannot compute smooth trajectory')
        else:
            # compute the relative position vectors
            relativePositions = {}  # relativePositions[(i,j)] is the position of j relative to i
            for i in range(nFeatures):
                for j in range(i):
                    fi = self.features[i]
                    fj = self.features[j]
                    inter = fi.commonTimeInterval(fj)
                    if inter.length() >= minCommonIntervalLength:
                        xi = array(fi.getXCoordinates()[inter.first - fi.getFirstInstant():int(fi.length()) - (
                                    fi.getLastInstant() - inter.last)])
                        yi = array(fi.getYCoordinates()[inter.first - fi.getFirstInstant():int(fi.length()) - (
                                    fi.getLastInstant() - inter.last)])
                        xj = array(fj.getXCoordinates()[inter.first - fj.getFirstInstant():int(fj.length()) - (
                                    fj.getLastInstant() - inter.last)])
                        yj = array(fj.getYCoordinates()[inter.first - fj.getFirstInstant():int(fj.length()) - (
                                    fj.getLastInstant() - inter.last)])
                        relativePositions[(i, j)] = Point(median(xj - xi), median(yj - yi))
                        relativePositions[(j, i)] = -relativePositions[(i, j)]

    def computeBoundingPolygon(self, instant):
        '''Returns a bounding box for the feature positions at instant
        bounding box format is a list of points (4 in this case for a rectangle)

        TODO add method argument if using different methods/shapes'''
        if self.hasFeatures():
            positions = [f.getPositionAtInstant(instant) for f in self.getFeatures() if f.existsAtInstant(instant)]
            return Point.boundingRectangle(positions, self.getVelocityAtInstant(instant))
        else:
            print('Object {} has no features'.format(self.getNum()))
            return None

    ###
    # User Type Classification
    ###
    def classifyUserTypeSpeedMotorized(self, threshold, aggregationFunc=median, nInstantsIgnoredAtEnds=0):
        '''Classifies slow and fast road users
        slow: non-motorized -> pedestrians
        fast: motorized -> cars

        aggregationFunc can be any function that can be applied to a vector of speeds, including percentile:
        aggregationFunc = lambda x: percentile(x, percentileFactor) # where percentileFactor is 85 for 85th percentile'''
        speeds = self.getSpeeds(nInstantsIgnoredAtEnds)
        if aggregationFunc(speeds) >= threshold:
            self.setUserType(userType2Num['car'])
        else:
            self.setUserType(userType2Num['pedestrian'])

    def classifyUserTypeSpeed(self, speedProbabilities, aggregationFunc=median, nInstantsIgnoredAtEnds=0):
        '''Classifies road user per road user type
        speedProbabilities are functions return P(speed|class)
        in a dictionary indexed by user type names
        Returns probabilities for each class

        for simple threshold classification, simply pass non-overlapping indicator functions (membership)
        e.g. def indic(x):
        if abs(x-mu) < sigma:
        return 1
        else:
        return x'''
        if not hasattr(self, 'aggregatedSpeed'):
            self.aggregatedSpeed = aggregationFunc(self.getSpeeds(nInstantsIgnoredAtEnds))
        userTypeProbabilities = {}
        for userTypename in speedProbabilities:
            userTypeProbabilities[userType2Num[userTypename]] = speedProbabilities[userTypename](self.aggregatedSpeed)
        self.setUserType(utils.argmaxDict(userTypeProbabilities))
        return userTypeProbabilities

    def initClassifyUserTypeHoGSVM(self, aggregationFunc, pedBikeCarSVM, bikeCarSVM=None,
                                   pedBikeSpeedTreshold=float('Inf'), bikeCarSpeedThreshold=float('Inf'),
                                   nInstantsIgnoredAtEnds=0, homography=None, intrinsicCameraMatrix=None,
                                   distortionCoefficients=None):
        '''Initializes the data structures for classification

        TODO? compute speed for longest feature?'''
        self.aggregatedSpeed = aggregationFunc(self.getSpeeds(nInstantsIgnoredAtEnds))
        if self.aggregatedSpeed < pedBikeSpeedTreshold or bikeCarSVM is None:
            self.appearanceClassifier = pedBikeCarSVM
        elif self.aggregatedSpeed < bikeCarSpeedThreshold:
            self.appearanceClassifier = bikeCarSVM
        else:
            self.appearanceClassifier = carClassifier
        # project feature positions
        if self.hasFeatures():
            for f in self.getFeatures():
                pp = cvutils.worldToImageProject(f.getPositions().asArray(), intrinsicCameraMatrix,
                                                 distortionCoefficients, homography).tolist()
                f.positions = Trajectory(pp)
        self.userTypes = {}

    def classifyUserTypeHoGSVMAtInstant(self, img, instant, width, height, px, py, minNPixels, rescaleSize,
                                        orientations, pixelsPerCell, cellsPerBlock, blockNorm):
        '''Extracts the image box around the object
        (of square size max(width, height) of the box around the features,
        with an added px or py for width and height (around the box))
        computes HOG on this cropped image (with parameters rescaleSize, orientations, pixelsPerCell, cellsPerBlock)
        and applies the SVM model on it'''
        croppedImg = cvutils.imageBox(img, self, instant, width, height, px, py, minNPixels)
        if croppedImg is not None and len(croppedImg) > 0:
            hog = cvutils.HOG(croppedImg, rescaleSize, orientations, pixelsPerCell, cellsPerBlock, blockNorm)
            self.userTypes[instant] = self.appearanceClassifier.predict(hog.reshape(1, hog.size))
        else:
            self.userTypes[instant] = userType2Num['unknown']

    def classifyUserTypeHoGSVM(self, pedBikeCarSVM=None, width=0, height=0, homography=None, images=None,
                               bikeCarSVM=None, pedBikeSpeedTreshold=float('Inf'), bikeCarSpeedThreshold=float('Inf'),
                               minSpeedEquiprobable=-1, speedProbabilities=None, aggregationFunc=median,
                               maxPercentUnknown=0.5, nInstantsIgnoredAtEnds=0, px=0.2, py=0.2, minNPixels=800,
                               rescaleSize=(64, 64), orientations=9, pixelsPerCell=(8, 8), cellsPerBlock=(2, 2)):
        '''Agregates SVM detections in each image and returns probability
        (proportion of instants with classification in each category)

        images is a dictionary of images indexed by instant
        With default parameters, the general (ped-bike-car) classifier will be used

        Considered categories are the keys of speedProbabilities'''
        if not hasattr(self, 'aggregatedSpeed') or not hasattr(self, 'userTypes'):
            print('Initializing the data structures for classification by HoG-SVM')
            self.initClassifyUserTypeHoGSVM(aggregationFunc, pedBikeCarSVM, bikeCarSVM, pedBikeSpeedTreshold,
                                            bikeCarSpeedThreshold, nInstantsIgnoredAtEnds)

        if len(
                self.userTypes) != self.length() and images is not None:  # if classification has not been done previously
            for t in self.getTimeInterval():
                if t not in self.userTypes:
                    self.classifyUserTypeHoGSVMAtInstant(images[t], t, homography, width, height, px, py, minNPixels,
                                                         rescaleSize, orientations, pixelsPerCell, cellsPerBlock)
        # compute P(Speed|Class)
        if speedProbabilities is None or self.aggregatedSpeed < minSpeedEquiprobable:  # equiprobable information from speed
            userTypeProbabilities = {userType2Num['car']: 1., userType2Num['pedestrian']: 1.,
                                     userType2Num['bicycle']: 1.}
        else:
            userTypeProbabilities = {userType2Num[userTypename]: speedProbabilities[userTypename](self.aggregatedSpeed)
                                     for userTypename in speedProbabilities}
        # compute P(Class|Appearance)
        nInstantsUserType = {userTypeNum: 0 for userTypeNum in
                             userTypeProbabilities}  # number of instants the object is classified as userTypename
        nInstantsUserType[userType2Num['unknown']] = 0
        for t in self.userTypes:
            nInstantsUserType[self.userTypes[t]] += 1  # nInstantsUserType.get(self.userTypes[t], 0) + 1
        # result is P(Class|Appearance) x P(Speed|Class)
        if nInstantsUserType[userType2Num['unknown']] < maxPercentUnknown * self.length():  # if not too many unknowns
            for userTypeNum in userTypeProbabilities:
                userTypeProbabilities[userTypeNum] *= nInstantsUserType[userTypeNum]
        # class is the user type that maximizes usertype probabilities
        if nInstantsUserType[userType2Num['unknown']] >= maxPercentUnknown * self.length() and (
                speedProbabilities is None or self.aggregatedSpeed < minSpeedEquiprobable):  # if no speed information and too many unknowns
            self.setUserType(userType2Num['unknown'])
        else:
            self.setUserType(utils.argmaxDict(userTypeProbabilities))

    def classifyUserTypeArea(self, areas, homography):
        '''Classifies the object based on its location (projected to image space)
        areas is a dictionary of matrix of the size of the image space
        for different road users possible locations, indexed by road user type names

        TODO: areas could be a wrapper object with a contains method that would work for polygons and images (with wrapper class)
        skip frames at beginning/end?'''
        print('not implemented/tested yet')
        if not hasattr(self, projectedPositions):
            if homography is not None:
                self.projectedPositions = obj.positions.homographyProject(homography)
            else:
                self.projectedPositions = obj.positions
        possibleUserTypes = {userType: 0 for userType in range(len(userTypenames))}
        for p in self.projectedPositions:
            for userTypename in areas:
                if areas[userTypename][p.x, p.y] != 0:
                    possibleUserTypes[userType2Enum[userTypename]] += 1
        # what to do: threshold for most common type? self.setUserType()
        return possibleUserTypes

    @staticmethod
    def collisionCourseDotProduct(movingObject1, movingObject2, instant):
        'A positive result indicates that the road users are getting closer'
        deltap = movingObject1.getPositionAtInstant(instant) - movingObject2.getPositionAtInstant(instant)
        deltav = movingObject2.getVelocityAtInstant(instant) - movingObject1.getVelocityAtInstant(instant)
        return Point.dot(deltap, deltav)

    @staticmethod
    def collisionCourseCosine(movingObject1, movingObject2, instant):
        'A positive result indicates that the road users are getting closer'
        return Point.cosine(movingObject1.getPositionAtInstant(instant) - movingObject2.getPositionAtInstant(instant),
                            # deltap
                            movingObject2.getVelocityAtInstant(instant) - movingObject1.getVelocityAtInstant(
                                instant))  # deltav


class Prototype(object):
    'Class for a prototype'

    def __init__(self, filename, num, trajectoryType, nMatchings=None):
        self.filename = filename
        self.num = num
        self.trajectoryType = trajectoryType
        self.nMatchings = nMatchings
        self.movingObject = None

    def getFilename(self):
        return self.filename

    def getNum(self):
        return self.num

    def getTrajectoryType(self):
        return self.trajectoryType

    def getNMatchings(self):
        return self.nMatchings

    def getMovingObject(self):
        return self.movingObject

    def setMovingObject(self, o):
        self.movingObject = o

    def __str__(self):
        return '{} {} {}'.format(self.filename, self.num, self.trajectoryType)

    def __eq__(self, p2):
        return self.filename == p2.filename and self.num == p2.num and self.trajectoryType == p2.trajectoryType

    def __hash__(self):
        return hash((self.filename, self.num, self.trajectoryType))


##################
# Annotations
##################

class BBMovingObject(MovingObject):
    '''Class for a moving object represented as a bounding box
    used for series of ground truth annotations using bounding boxes
     and for the output of Urban Tracker http://www.jpjodoin.com/urbantracker/

    By default in image space

    Its center is the center of the box (generalize to other shapes?)
    (computed after projecting if homography available)
    '''

    def __init__(self, num=None, timeInterval=None, topLeftPositions=None, bottomRightPositions=None,
                 userType=userType2Num['unknown']):
        super(BBMovingObject, self).__init__(num, timeInterval, userType=userType)
        self.topLeftPositions = topLeftPositions.getPositions()
        self.bottomRightPositions = bottomRightPositions.getPositions()

    def computeCentroidTrajectory(self, homography=None):
        self.positions = self.topLeftPositions.add(self.bottomRightPositions).__mul__(0.5)
        if homography is not None:
            self.positions = self.positions.homographyProject(homography)

    def matches(self, obj, instant, matchingDistance):
        '''Indicates if the annotation matches obj (MovingObject)
        with threshold matchingDistance
        Returns distance if below matchingDistance, matchingDistance+1 otherwise
        (returns an actual value, otherwise munkres does not terminate)'''
        d = Point.distanceNorm2(self.getPositionAtInstant(instant), obj.getPositionAtInstant(instant))
        if d < matchingDistance:
            return d
        else:
            return matchingDistance + 1


def matchObjects(obj1, obj2, instant, matchingDistance):
    '''Indicates if obj matches obj2 with threshold matchingDistance
        Returns distance if below matchingDistance, matchingDistance+1 otherwise
    (returns an actual value, otherwise munkres does not terminate)'''
    d = Point.distanceNorm2(obj1.getPositionAtInstant(instant), obj2.getPositionAtInstant(instant))
    if d < matchingDistance:
        return d
    else:
        return matchingDistance + 1


# TODO class to have different matching methods, eg with something like matchObjects
def computeClearMOT(annotations, objects, matchingDistance, firstInstant, lastInstant, returnMatches=False,
                    debug=False):
    '''Computes the CLEAR MOT metrics

    Reference:
    Keni, Bernardin, and Stiefelhagen Rainer. "Evaluating multiple object tracking performance: the CLEAR MOT metrics." EURASIP Journal on Image and Video Processing 2008 (2008)

    objects and annotations are supposed to in the same space
    current implementation is BBMovingObject (bounding boxes)
    mathingDistance is threshold on matching between annotation and object

    TO: tracker output (objects)
    GT: ground truth (annotations)

    Output: returns motp, mota, mt, mme, fpt, gt
    mt number of missed GT.frames (sum of the number of GT not detected in each frame)
    mme number of mismatches
    fpt number of false alarm.frames (tracker objects without match in each frame)
    gt number of GT.frames

    if returnMatches is True, return as 2 new arguments the GT and TO matches
    matches is a dict
    matches[i] is the list of matches for GT/TO i
    the list of matches is a dict, indexed by time, for the TO/GT id matched at time t
    (an instant t not present in matches[i] at which GT/TO exists means a missed detection or false alarm)

    TODO: Should we use the distance as weights or just 1/0 if distance below matchingDistance?
    (add argument useDistanceForWeights = False)'''
    from munkres import Munkres

    munk = Munkres()
    dist = 0.  # total distance between GT and TO
    ct = 0  # number of associations between GT and tracker output in each frame
    gt = 0  # number of GT.frames
    mt = 0  # number of missed GT.frames (sum of the number of GT not detected in each frame)
    fpt = 0  # number of false alarm.frames (tracker objects without match in each frame)
    mme = 0  # number of mismatches
    matches = {}  # match[i] is the tracker track associated with GT i (using object references)
    if returnMatches:
        gtMatches = {a.getNum(): {} for a in annotations}
        toMatches = {o.getNum(): {} for o in objects}
    else:
        gtMatches = None
        toMatches = None
    for t in range(firstInstant, lastInstant + 1):
        previousMatches = matches.copy()
        # go through currently matched GT-TO and check if they are still matched withing matchingDistance
        toDelete = []
        for a in matches:
            if a.existsAtInstant(t) and matches[a].existsAtInstant(t):
                d = a.matches(matches[a], t, matchingDistance)
                if d < matchingDistance:
                    dist += d
                else:
                    toDelete.append(a)
            else:
                toDelete.append(a)
        for a in toDelete:
            del matches[a]

        # match all unmatched GT-TO
        matchedGTs = list(matches.keys())
        matchedTOs = list(matches.values())
        costs = []
        unmatchedGTs = [a for a in annotations if a.existsAtInstant(t) and a not in matchedGTs]
        unmatchedTOs = [o for o in objects if o.existsAtInstant(t) and o not in matchedTOs]
        nGTs = len(matchedGTs) + len(unmatchedGTs)
        nTOs = len(matchedTOs) + len(unmatchedTOs)
        if len(unmatchedTOs) > 0:
            for a in unmatchedGTs:
                costs.append([a.matches(o, t, matchingDistance) for o in unmatchedTOs])
        if len(costs) > 0:
            newMatches = munk.compute(costs)
            for k, v in newMatches:
                if costs[k][v] < matchingDistance:
                    matches[unmatchedGTs[k]] = unmatchedTOs[v]
                    dist += costs[k][v]
        if debug:
            print('{} '.format(t) + ', '.join(['{} {}'.format(k.getNum(), v.getNum()) for k, v in matches.items()]))
        if returnMatches:
            for a, o in matches.items():
                gtMatches[a.getNum()][t] = o.getNum()
                toMatches[o.getNum()][t] = a.getNum()

        # compute metrics elements
        ct += len(matches)
        mt += nGTs - len(matches)
        fpt += nTOs - len(matches)
        gt += nGTs
        # compute mismatches
        # for gt that do not appear in both frames, check if the corresponding to was matched to another gt in previous/next frame
        mismatches = []
        for a in matches:
            if a in previousMatches:
                if matches[a] != previousMatches[a]:
                    mismatches.append(a)
            elif matches[a] in list(previousMatches.values()):
                mismatches.append(matches[a])
        for a in previousMatches:
            if a not in matches and previousMatches[a] in list(matches.values()):
                mismatches.append(previousMatches[a])
        if debug:
            for mm in set(mismatches):
                print('{} {}'.format(type(mm), mm.getNum()))
        # some object mismatches may appear twice
        mme += len(set(mismatches))

    if ct > 0:
        motp = dist / ct
    else:
        motp = None
    if gt > 0:
        mota = 1. - float(mt + fpt + mme) / gt
    else:
        mota = None
    return motp, mota, mt, mme, fpt, gt, gtMatches, toMatches


def plotRoadUsers(objects, colors):
    '''Colors is a PlottingPropertyValues instance'''
    from matplotlib.pyplot import figure, axis
    figure()
    for obj in objects:
        obj.plot(colors.get(obj.userType))
    axis('equal')


if __name__ == "__main__":
    import doctest
    import unittest

    suite = doctest.DocFileSuite('tests/moving.txt')
    # suite = doctest.DocTestSuite()
    unittest.TextTestRunner().run(suite)
    # doctest.testmod()
    # doctest.testfile("example.txt")
    if shapelyAvailable:
        suite = doctest.DocFileSuite('tests/moving_shapely.txt')
        unittest.TextTestRunner().run(suite)
