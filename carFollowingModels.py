from trafficintelligence import moving

class Models(object):

    class Naive(object):

        @staticmethod
        def position(previousPosition, velocity, step):
            return previousPosition + velocity*step

        @staticmethod
        def speed(curvilinearPositionLeaderAt, curvilinearPositionFollowingAt, velocity, leaderVehicleLength, TIVmin):
            d = curvilinearPositionLeaderAt - (curvilinearPositionFollowingAt + velocity) - leaderVehicleLength
            TIV = d/velocity
            if TIV < TIVmin :
                speedValue = d/TIVmin
            if speedValue < 0 :
                speedValue = 0
            return speedValue

    class Newell(object):


        @staticmethod
        def position(previousPosition, desiredSpeed):
            return None

        @staticmethod
        def speed(curvilinearPositionLeader, curvilinearPositionFollowing, desiredSpeed):
            return None

        @staticmethod
        def acceleration():
            return None

    class IDM(object):

        @staticmethod
        def position(previousPosition, velocity, followingAcceleration, step):
            if velocity > 0:
                return previousPosition + step * velocity
            else :
                return previousPosition - 0.5*(velocity**2)/followingAcceleration

        @staticmethod
        def speed(followingVelocity, followingAcceleration, step):
            speedValue = max(0,followingVelocity + step*followingAcceleration)
            return speedValue

        @staticmethod
        def acceleration(s0, v ,T, delta_v, a, v, delta, v0, s):
            return a*(1-((v/v0)**delta)-(SStar(s0, v, T, delta_v, a, b)/s)**2)

        @staticmethod
        def SStar(s0, v, T, delta_v, a, b):
            return s0 + max(0,v*T + v*delta_v/(2*((a*b)**0.5)))
