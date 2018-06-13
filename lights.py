import simpy
env=simpy.Environment()

def car(env):
    global light, liste
    liste=[]
    while True:
        light='green'
        print('light turned green at %d' % env.now)
        liste=liste+[[light,env.now]]
        t_green = 25
        yield env.timeout(t_green)

        light='red'
        print('light turned red at %d' % env.now)
        liste=liste+[[light,env.now]]
        t_red = 30
        yield env.timeout(t_red)

env.process(car(env))
env.run(until=120)
print(liste)
