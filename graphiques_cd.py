stop_nInter10 = {1: 5.133333333333334, 2: 364.2}

stop_nInter20 = {1: 39.666666666666664, 2: 562.2}

stop_nInter50 = {1: 199.86666666666667, 2: 1135.8}

yield_nInter50 = {1: 199.8, 2: 1098.0}

yield_nInter20 = {1: 42.86666666666667, 2: 532.3333333333334}

yield_nInter10 = {1: 9.133333333333333, 2: 326.93333333333334}

sQuo_nInter10 = {1: 0.0, 2: 145.33333333333334}

sQuo_nInter20 = {1: 52.6, 2: 287.1333333333333}

sQuo_nInter50 = {1: 315.3333333333333, 2: 723.2666666666667}

import matplotlib.pyplot as plt

x = [10, 20, 50]
y_stop_1 = [5, 39, 199]
y_stop_2 = [364, 562, 1135]

y_yield_1 = [9, 42, 199]
y_yield_2 = [326, 532, 1098]

y_sQuo_1 = [0, 52, 315]
y_sQuo_2 = [145, 287, 723]

plt.plot(x, y_stop_1)
plt.plot(x, y_yield_1)
plt.plot(x, y_sQuo_1)

plt.legend(['stop sign', 'yield sign', 'status quo'])
plt.xlabel('interaction distance (m)')
plt.ylabel('nInter')
plt.savefig('rearEnd-nInter_variations.pdf')

plt.close()

plt.plot(x, y_stop_2)
plt.plot(x, y_yield_2)
plt.plot(x, y_sQuo_2)

plt.legend(['stop sign', 'yield sign', 'status quo'])
plt.xlabel('interaction distance (m)')
plt.ylabel('nInter')
plt.savefig('side-nInter_variations.pdf')

plt.legend(['stop sign', 'yield sign', 'status quo'])

plt.close()
