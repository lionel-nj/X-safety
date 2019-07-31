import matplotlib.pyplot as plt
import numpy as np

import toolkit

zones = [1000, 5000, 10000]
results = {}
for zone in zones:
    results[zone] = {}
    intermed = toolkit.loadYaml('sorties/zone analysis/{}/zone{}-results.yml'.format(zone, zone))
    for val in intermed:
        results[zone][val] = intermed[val][zone]

# raw graphs
# ttc cdf
for zone in results:
    sideTTCs = toolkit.flatten(results[zone]['TTCs'][2].values())
    sideTTCs_x = np.sort(sideTTCs)
    sideTTCs_y = np.arange(len(sideTTCs))/15# / float(len(sideTTCs))
    plt.plot(sideTTCs_x, sideTTCs_y)
    plt.xlabel('side Time to Collision (s)')
    plt.ylabel('Number of observations')
    plt.legend(['$1000\ m^{2}$', '$5000\ m^{2}$', '$10000\ m^{2}$'])
plt.close()

#pets cdf
for zone in results:
    PETs = toolkit.flatten(results[zone]['PETS'].values())
    PETs_x = np.sort(PETs)
    PETs_y = np.arange(len(PETs))/15# / float(len(PETs))
    plt.plot(PETs_x, PETs_y)
    plt.xlabel('Post Encroachment Time (s)')
    plt.ylabel('Number of observations')
    plt.legend(['$1000\ m^{2}$', '$5000\ m^{2}$', '$10000\ m^{2}$'])
plt.close()

#nInter cdf
#rear end
for zone in results:
    minDistance = toolkit.flatten(results[zone]['minDistances'][1].values())
    minDistance_x = np.sort(minDistance)
    minDistance_y = np.arange(len(minDistance)) / 15
    plt.plot(minDistance_x, minDistance_y)
    plt.xlabel('rear end minimum distance of interactions (s)')
    plt.ylabel('Number of observations')
    plt.legend(['$1000\ m^{2}$', '$5000\ m^{2}$', '$10000\ m^{2}$'])
plt.close()

#side
for zone in results:
    minDistance = toolkit.flatten(results[zone]['minDistances'][2].values())
    minDistance_x = np.sort(minDistance)
    minDistance_y = np.arange(len(minDistance)) / 15
    plt.plot(minDistance_x, minDistance_y)
    plt.xlabel('rear end minimum distance of interactions (s)')
    plt.ylabel('Number of observations')
    plt.legend(['$1000\ m^{2}$', '$5000\ m^{2}$', '$10000\ m^{2}$'])
plt.close()

# normed graphs

# ttc cdf
for zone in results:
    sideTTCs = toolkit.flatten(results[zone]['TTCs'][2].values())
    sideTTCs_x = np.sort(sideTTCs)
    sideTTCs_y = 100*np.arange(len(sideTTCs))/15/ float(len(sideTTCs))
    plt.plot(sideTTCs_x, sideTTCs_y)
    plt.xlabel('side Time to Collision (s)')
    plt.ylabel('Number of observations')
    plt.legend(['$1000\ m^{2}$', '$5000\ m^{2}$', '$10000\ m^{2}$'])
plt.close()

#pets cdf
for zone in results:
    PETs = toolkit.flatten(results[zone]['PETS'].values())
    PETs_x = np.sort(PETs)
    PETs_y = 100*np.arange(len(PETs))/15/ float(len(PETs))
    plt.plot(PETs_x, PETs_y)
    plt.xlabel('Post Encroachment Time (s)')
    plt.ylabel('Number of observations')
    plt.legend(['$1000\ m^{2}$', '$5000\ m^{2}$', '$10000\ m^{2}$'])
plt.close()

#nInter cdf
#rear end
for zone in results:
    minDistance = toolkit.flatten(results[zone]['minDistances'][1].values())
    minDistance_x = np.sort(minDistance)
    minDistance_y = 100*np.arange(len(minDistance)) / 15 /float(len(minDistance))
    plt.plot(minDistance_x, minDistance_y)
    plt.xlabel('rear end minimum distance of interactions (s)')
    plt.ylabel('Number of observations')
    plt.legend(['$1000\ m^{2}$', '$5000\ m^{2}$', '$10000\ m^{2}$'])
plt.close()

#side

for zone in results:
    minDistance = toolkit.flatten(results[zone]['minDistances'][2].values())
    minDistance_x = np.sort(minDistance)
    minDistance_y = 100*np.arange(len(minDistance)) / 15 /float(len(minDistance))
    plt.plot(minDistance_x, minDistance_y)
    plt.xlabel('rear end minimum distance of interactions (s)')
    plt.ylabel('Number of observations')
    plt.legend(['$1000\ m^{2}$', '$5000\ m^{2}$', '$10000\ m^{2}$'])
plt.close()

# pdf
# ttc side
#raw
for zone in results:
    zone_histogram, zone_bin_centers = np.histogram(toolkit.flatten(results[zone]['TTCs'][2].values()))
    zone_bin_centers = 0.5*(zone_bin_centers[1:] + zone_bin_centers[:-1])
    zone_histogram2 = np.array([k for k in range(len(zone_histogram))])
    for k in range(0, len(zone_histogram)):
        zone_histogram2[k] = zone_histogram[k] / len(toolkit.flatten(results[zone]['TTCs'][2].values()))
    plt.plot(zone_bin_centers, zone_histogram)

plt.xlabel('Side Time to Collision (s)')
plt.ylabel('Number of observations')
plt.legend(['$1000\ m^{2}$', '$5000\ m^{2}$', '$10000\ m^{2}$'])
plt.close()

#pet
for zone in results:
    zone_histogram, zone_bin_centers = np.histogram(toolkit.flatten(results[zone]['PETS'].values()))
    zone_bin_centers = 0.5*(zone_bin_centers[1:] + zone_bin_centers[:-1])
    zone_histogram2 = np.array([k for k in range(len(zone_histogram))])
    for k in range(0, len(zone_histogram)):
        zone_histogram2[k] = zone_histogram[k] / len(toolkit.flatten(results[zone]['PETS'].values()))
    plt.plot(zone_bin_centers, zone_histogram)

plt.xlabel('Post Encroachment Time (s)')
plt.ylabel('Number of observations')
plt.legend(['$1000\ m^{2}$', '$5000\ m^{2}$', '$10000\ m^{2}$'])
plt.close()

#nInter
#rear end
for zone in results:
    zone_histogram, zone_bin_centers = np.histogram(toolkit.flatten(results[zone]['minDistances'][1].values()))
    zone_bin_centers = 0.5*(zone_bin_centers[1:] + zone_bin_centers[:-1])
    zone_histogram2 = np.array([k for k in range(len(zone_histogram))])
    for k in range(0, len(zone_histogram)):
        zone_histogram2[k] = zone_histogram[k] / len(toolkit.flatten(results[zone]['minDistances'][1].values()))
    plt.plot(zone_bin_centers, zone_histogram)

plt.xlabel('Post Encroachment Time (s)')
plt.ylabel('Number of observations')
plt.legend(['$1000\ m^{2}$', '$5000\ m^{2}$', '$10000\ m^{2}$'])
plt.close()

#side
for zone in results:
    zone_histogram, zone_bin_centers = np.histogram(toolkit.flatten(results[zone]['minDistances'][2].values()))
    zone_bin_centers = 0.5*(zone_bin_centers[1:] + zone_bin_centers[:-1])
    zone_histogram2 = np.array([k for k in range(len(zone_histogram))])
    for k in range(0, len(zone_histogram)):
        zone_histogram2[k] = zone_histogram[k] / len(toolkit.flatten(results[zone]['minDistances'][2].values()))
    plt.plot(zone_bin_centers, zone_histogram)

plt.xlabel('Post Encroachment Time (s)')
plt.ylabel('Number of observations')
plt.legend(['$1000\ m^{2}$', '$5000\ m^{2}$', '$10000\ m^{2}$'])
plt.close()
