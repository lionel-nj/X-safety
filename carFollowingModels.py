from trafficintelligence import moving

class Models(object):

    class Naive(object):

        @staticmethod
        def position(previousPosition, velocity, step):
            return previousPosition + velocity*step

        @staticmethod
        def speed(curvilinearPositionLeader, curvilinearPositionFollowing, desiredSpeed, TIVmin):
            d = curvilinearPositionLeader - curvilinearPositionFollowing

            TIV = d/desiredSpeed

            if TIV > TIVmin :
                speedValue = desiredSpeed
            else :
                speedValue = d/TIVmin

            return speedValue

        def acceleration(previousSpeed, velocity, step):
            return (velocity - previousSpeed)/step

    class Newell(object):

        @staticmethod
        def position(previousPosition, desiredSpeed, step):
            return previousPosition + step*desiredSpeed

        @staticmethod
        def speed(curvilinearPositionLeader, curvilinearPositionFollowing, desiredSpeed):
            return None

        @staticmethod
        def acceleration():
            return None

    class IDM(object):

        @staticmethod
        def position(previousPosition, velocity, followingAcceleration, step):
            if velocity != 0:
                return previousPosition + step * velocity + 0.5*followingAcceleration*(step**2)
            else :
                return previousPosition
            # else :
            #     return previousPosition


        @staticmethod
        def speed(followingVelocity, followingAcceleration, step):
            speedValue = followingVelocity + step*followingAcceleration
            return max(0,speedValue)

        @staticmethod
        def acceleration(s0, v ,T, delta_v, a, b, delta, v0, s):
            return a*(1-((v/v0)**delta)-(Models.IDM.SStar(s0, v, T, delta_v, a, b)/s)**2)

        @staticmethod
        def SStar(s0, v, T, delta_v, a, b):
            if s0 + v*T + v*delta_v/(2*((a*b)**0.5)) > s0:
                return s0 + v*T + v*delta_v/(2*((a*b)**0.5))
            else:
                return s0
