import math

import matplotlib.pyplot as plt
import numpy as np

import toolkit

baseCaseResults = toolkit.loadYaml('sorties/sensitivity-analysis/base case/base-case-results.yml')

baseCaseRearEndMeanTTCmin = np.mean(baseCaseResults["minTTCs"][1])
baseCaseSideTTCmin = np.mean(baseCaseResults["minTTCs"][2])
baseCaseMeanPET = np.mean(baseCaseResults["PETs"])

baseCaseMeanSideInter10 = baseCaseResults["nInter10"][2]
baseCaseMeanSideInter20 = baseCaseResults["nInter20"][2]
baseCaseMeanSideInter50 = baseCaseResults["nInter50"][2]

baseCaseMeanRearInter10 = baseCaseResults["nInter10"][1]
baseCaseMeanRearInter20 = baseCaseResults["nInter20"][1]
baseCaseMeanRearInter50 = baseCaseResults["nInter50"][1]

def getSensivities(parameter):
    results = {"-40": {"minTTCs": toolkit.loadYaml('sorties/sensitivity-analysis/{}/-40%/sa-minTTCs-{}-0.4.yml'.format(parameter, parameter)),
                        "PETs": toolkit.loadYaml('sorties/sensitivity-analysis/{}/-40%/sa-PETs-{}-0.4.yml'.format(parameter, parameter)),
                        "nInter10": toolkit.loadYaml('sorties/sensitivity-analysis/{}/-40%/sa-nInter10{}--0.4.yml'.format(parameter, parameter)),
                        "nInter20": toolkit.loadYaml('sorties/sensitivity-analysis/{}/-40%/sa-nInter20{}--0.4.yml'.format(parameter, parameter)),
                        "nInter50": toolkit.loadYaml('sorties/sensitivity-analysis/{}/-40%/sa-nInter50{}--0.4.yml'.format(parameter, parameter)),
                       "sidenInter10": toolkit.loadYaml('sorties/sensitivity-analysis/{}/-40%/sa-side-nInter10-{}--0.4.yml'.format(parameter, parameter)),
                       "sidenInter20": toolkit.loadYaml('sorties/sensitivity-analysis/{}/-40%/sa-side-nInter20-{}--0.4.yml'.format(parameter, parameter)),
                       "sidenInter50": toolkit.loadYaml('sorties/sensitivity-analysis/{}/-40%/sa-side-nInter50-{}--0.4.yml'.format(parameter, parameter)),
                       "rearEndnInter10": toolkit.loadYaml('sorties/sensitivity-analysis/{}/-40%/sa-rearEnd-nInter10-{}--0.4.yml'.format(parameter, parameter)),
                       "rearEndnInter20": toolkit.loadYaml('sorties/sensitivity-analysis/{}/-40%/sa-rearEnd-nInter20-{}--0.4.yml'.format(parameter, parameter)),
                       "rearEndnInter50": toolkit.loadYaml('sorties/sensitivity-analysis/{}/-40%/sa-rearEnd-nInter50-{}--0.4.yml'.format(parameter, parameter))

                       },

                 "+40": {"minTTCs": toolkit.loadYaml('sorties/sensitivity-analysis/{}/+40%/sa-minTTCs-{}0.4.yml'.format(parameter, parameter)),
                        "PETs": toolkit.loadYaml('sorties/sensitivity-analysis/{}/+40%/sa-PETs-{}0.4.yml'.format(parameter, parameter)),
                        "nInter10":toolkit.loadYaml('sorties/sensitivity-analysis/{}/+40%/sa-nInter10{}-0.4.yml'.format(parameter, parameter)),
                        "nInter20":toolkit.loadYaml('sorties/sensitivity-analysis/{}/+40%/sa-nInter20{}-0.4.yml'.format(parameter, parameter)),
                        "nInter50":toolkit.loadYaml('sorties/sensitivity-analysis/{}/+40%/sa-nInter50{}-0.4.yml'.format(parameter, parameter)),
               "sidenInter10": toolkit.loadYaml('sorties/sensitivity-analysis/{}/+40%/sa-side-nInter10-{}-0.4.yml'.format(parameter, parameter)),
               "sidenInter20": toolkit.loadYaml('sorties/sensitivity-analysis/{}/+40%/sa-side-nInter20-{}-0.4.yml'.format(parameter, parameter)),
               "sidenInter50": toolkit.loadYaml('sorties/sensitivity-analysis/{}/+40%/sa-side-nInter50-{}-0.4.yml'.format(parameter, parameter)),
               "rearEndnInter10": toolkit.loadYaml('sorties/sensitivity-analysis/{}/+40%/sa-rearEnd-nInter10-{}-0.4.yml'.format(parameter, parameter)),
               "rearEndnInter20": toolkit.loadYaml('sorties/sensitivity-analysis/{}/+40%/sa-rearEnd-nInter20-{}-0.4.yml'.format(parameter, parameter)),
               "rearEndnInter50": toolkit.loadYaml('sorties/sensitivity-analysis/{}/+40%/sa-rearEnd-nInter50-{}-0.4.yml'.format(parameter, parameter))}
               }

    rearEndMeanTTCmin = {"-40": np.mean(results['-40']["minTTCs"][1]), "+40": np.mean(results['+40']["minTTCs"][1])}
    sideMeanTTCmin = {"-40": np.mean(results['-40']["minTTCs"][2]), "+40": np.mean(results['+40']["minTTCs"][2])}
    meanPET = {"-40": np.mean(results['-40']["PETs"]), "+40": np.mean(results['+40']["PETs"])}

    meanSideInter10 = {"-40": np.mean(results["-40"]["sidenInter10"]['{}'.format(parameter)][-.4]), "+40": np.mean(results["+40"]["sidenInter10"]['{}'.format(parameter)][.4])}
    meanSideInter20 = {"-40": np.mean(results["-40"]["sidenInter20"]['{}'.format(parameter)][-.4]), "+40": np.mean(results["+40"]["sidenInter20"]['{}'.format(parameter)][.4])}
    meanSideInter50 = {"-40": np.mean(results["-40"]["sidenInter50"]['{}'.format(parameter)][-.4]), "+40": np.mean(results["+40"]["sidenInter50"]['{}'.format(parameter)][.4])}

    meanRearInter10 = {"-40": np.mean(results["-40"]["rearEndnInter10"]['{}'.format(parameter)][-.4]), "+40": np.mean(results["+40"]["rearEndnInter10"]['{}'.format(parameter)][.4])}
    meanRearInter20 = {"-40": np.mean(results["-40"]["rearEndnInter20"]['{}'.format(parameter)][-.4]), "+40": np.mean(results["+40"]["rearEndnInter20"]['{}'.format(parameter)][.4])}
    meanRearInter50 = {"-40": np.mean(results["-40"]["rearEndnInter50"]['{}'.format(parameter)][-.4]), "+40": np.mean(results["+40"]["rearEndnInter50"]['{}'.format(parameter)][.4])}

    rearEndTTCSensitivity = {"-40":((100 * (baseCaseRearEndMeanTTCmin - rearEndMeanTTCmin["-40"])) / baseCaseRearEndMeanTTCmin), "+40":((100 * (baseCaseRearEndMeanTTCmin - rearEndMeanTTCmin["+40"])) / baseCaseRearEndMeanTTCmin)}
    sideTTCSensitivity = {"-40":((100 * (baseCaseSideTTCmin - sideMeanTTCmin["-40"])) / baseCaseSideTTCmin), "+40":((100 * (baseCaseSideTTCmin - sideMeanTTCmin["+40"])) / baseCaseSideTTCmin)}
    petsSensitivity = {"-40":((100 * (baseCaseMeanPET - meanPET["-40"])) / baseCaseMeanPET), "+40":((100 * (baseCaseMeanPET - meanPET["+40"])) / baseCaseMeanPET)}

    sidenInter10Sensitivity = {"-40":((100 * (baseCaseMeanSideInter10 - meanSideInter10["-40"])) / baseCaseMeanSideInter10)/.4, "+40":((100 * (baseCaseMeanSideInter10 - meanSideInter10["+40"])) / baseCaseMeanSideInter10)/.4}
    sidenInter20Sensitivity = {"-40":((100 * (baseCaseMeanSideInter20 - meanSideInter20["-40"])) / baseCaseMeanSideInter20)/.4, "+40":((100 * (baseCaseMeanSideInter20 - meanSideInter20["+40"])) / baseCaseMeanSideInter20)/.4}
    sidenInter50Sensitivity = {"-40":((100 * (baseCaseMeanSideInter50 - meanSideInter50["-40"])) / baseCaseMeanSideInter50)/.4, "+40":((100 * (baseCaseMeanSideInter50 - meanSideInter50["+40"])) / baseCaseMeanSideInter50)/.4}


    rearInter10Sensitivity = {"-40":((100 * ((baseCaseMeanRearInter10 - meanRearInter10["-40"])) / baseCaseMeanRearInter10))/.4, "+40":((100 * (baseCaseMeanRearInter10 - meanRearInter10["+40"])) / baseCaseMeanRearInter10)/.4}
    rearInter20Sensitivity = {"-40":((100 * ((baseCaseMeanRearInter20 - meanRearInter20["-40"])) / baseCaseMeanRearInter20))/.4, "+40":((100 * (baseCaseMeanSideInter20 - meanRearInter20["+40"])) / baseCaseMeanSideInter20)/.4}
    rearInter50Sensitivity = {"-40":((100 * ((baseCaseMeanRearInter50 - meanRearInter50["-40"])) / baseCaseMeanRearInter50))/.4, "+40":((100 * (baseCaseMeanSideInter50 - meanRearInter50["+40"])) / baseCaseMeanSideInter50)/.4}

    sensitivities = {"rearTTCmin": rearEndTTCSensitivity,
                      "sideTTCmin": sideTTCSensitivity,
                      "PETs": petsSensitivity,
                      "rearnInter10": rearInter10Sensitivity,
                      "rearnInter20": rearInter20Sensitivity,
                      "rearnInter50": rearInter50Sensitivity,
                      "sidenInter10": sidenInter10Sensitivity,
                      "sidenInter20": sidenInter20Sensitivity,
                      "sidenInter50": sidenInter50Sensitivity,
                      }
    toolkit.saveYaml('{}Sensitivities.yml'.format(parameter), sensitivities)

    plus40 = []
    moins40 = []
    for truc in sensitivities:
        moins40.append(sensitivities[truc]['-40'])
    for truc in sensitivities:
        plus40.append(sensitivities[truc]['+40'])
    inf = [x for x in moins40 if ((math.isnan(x) == False) and float('inf') != abs(x))]
    sup = [x for x in plus40 if ((math.isnan(x) == False) and float('inf') != abs(x))]
    return inf, sup

# display
#dn

x = ['rear-end $\overline{TTC}_{min}$', 'side $\overline{TTC}_{min}$', '$\overline{PET}$', 'rear end $\overline{nInter}_{20}$', 'rear end $\overline{nInter}_{50}$', 'side $\overline{nInter}_{10}$', 'side $\overline{nInter}_{20}$', 'side $\overline{nInter}_{50}$']
param= 'speed'
moins40 = getSensivities(param)[0]
plus40 = getSensivities(param)[1]


fig = plt.figure()
ax = plt.subplot(111)
ax.barh(x, moins40, color='None', align='edge', height=.8, edgecolor='b', label=r"$\mu_{v_{f}}$-40%")
ax.barh(x, plus40, color='None', align='edge', height=.8, edgecolor='r', label=r"$\mu_{v_{f}}$+40%")
plt.legend()
x_pos = [i+.4 for i in range(0, len(x))]
plt.yticks(x_pos, x)
plt.xlabel('Variation percentage (%)')
plt.tight_layout()
plt.plot([0,0], [0,len(x)], color='black')
plt.savefig('sa-speed.pdf')
plt.close('all')


x = ['rear-end $\overline{TTC}_{min}$', 'side $\overline{TTC}_{min}$', '$\overline{PET}$', 'rear end $\overline{nInter}_{20}$', 'rear end $\overline{nInter}_{50}$', 'side $\overline{nInter}_{10}$', 'side $\overline{nInter}_{20}$', 'side $\overline{nInter}_{50}$']
param= 'dn'
moins40 = getSensivities(param)[0]
plus40 = getSensivities(param)[1]


fig = plt.figure()
ax = plt.subplot(111)
ax.barh(x, moins40, color='None', align='edge', height=.8, edgecolor='b', label=r"$\mu_{d}$-40%")
ax.barh(x, plus40, color='None', align='edge', height=.8, edgecolor='r', label=r"$\mu_{d}$+40%")
plt.legend()
x_pos = [i+.4 for i in range(0, len(x))]
plt.yticks(x_pos, x)
plt.xlabel('Variation percentage (%)')
plt.tight_layout()
plt.plot([0,0], [0,len(x)], color='black')
plt.savefig('sa-delta.pdf')
plt.close('all')

param= 'headway'
moins40 = getSensivities(param)[0]
plus40 = getSensivities(param)[1]


fig = plt.figure()
ax = plt.subplot(111)
ax.barh(x, moins40, color='None', align='edge', height=.8, edgecolor='b', label=r"$1/\lambda}$-40%")
ax.barh(x, plus40, color='None', align='edge', height=.8, edgecolor='r', label=r"$1/\lambda}$+40%")
plt.legend()
x_pos = [i+.4 for i in range(0, len(x))]
plt.yticks(x_pos, x)
plt.xlabel('Variation percentage (%)')
plt.tight_layout()
plt.plot([0,0], [0,len(x)], color='black')
plt.savefig('sa-headway.pdf')
plt.close('all')

param= 'tau'
moins40 = getSensivities(param)[0]
plus40 = getSensivities(param)[1]


fig = plt.figure()
ax = plt.subplot(111)
ax.barh(x, moins40, color='None', align='edge', height=.8, edgecolor='b', label=r"$\mu_{\tau}$-40%")
ax.barh(x, plus40, color='None', align='edge', height=.8, edgecolor='r', label=r"$\mu_{\tau}$+40%")
plt.legend()
x_pos = [i+.4 for i in range(0, len(x))]
plt.yticks(x_pos, x)
plt.xlabel('Variation percentage (%)')
plt.tight_layout()
plt.plot([0,0], [0,len(x)], color='black')
plt.savefig('sa-tau.pdf')
plt.close('all')

param= 'length'
moins40 = getSensivities(param)[0]
plus40 = getSensivities(param)[1]


fig = plt.figure()
ax = plt.subplot(111)
ax.barh(x, moins40, color='None', align='edge', height=.8, edgecolor='b', label=r"$\mu_{l}$-40%")
ax.barh(x, plus40, color='None', align='edge', height=.8, edgecolor='r', label=r"$\mu_{l}$+40%")
plt.legend()
x_pos = [i+.4 for i in range(0, len(x))]
plt.yticks(x_pos, x)
plt.xlabel('Variation percentage (%)')
plt.tight_layout()
plt.plot([0,0], [0,len(x)], color='black')
plt.savefig('sa-length.pdf')
plt.close('all')
