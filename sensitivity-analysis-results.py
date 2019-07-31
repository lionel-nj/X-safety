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
                       "rearEndnInter50": toolkit.loadYaml('sorties/sensitivity-analysis/{}/-40%/sa-rearEnd-nInter50-{}--0.4.yml'.format(parameter, parameter)),

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

    sidenInter10Sensitivity = {"-40":((100 * (baseCaseMeanSideInter10 - meanSideInter10["-40"])) / baseCaseMeanSideInter10), "+40":((100 * (baseCaseMeanSideInter10 - meanSideInter10["+40"])) / baseCaseMeanSideInter10)}
    sidenInter20Sensitivity = {"-40":((100 * (baseCaseMeanSideInter20 - meanSideInter20["-40"])) / baseCaseMeanSideInter20), "+40":((100 * (baseCaseMeanSideInter20 - meanSideInter20["+40"])) / baseCaseMeanSideInter20)}
    sidenInter50Sensitivity = {"-40":((100 * (baseCaseMeanSideInter50 - meanSideInter50["-40"])) / baseCaseMeanSideInter50), "+40":((100 * (baseCaseMeanSideInter50 - meanSideInter50["+40"])) / baseCaseMeanSideInter50)}


    rearInter10Sensitivity = {"-40":((100 * (baseCaseMeanRearInter10 - meanRearInter10["-40"])) / baseCaseMeanRearInter10), "+40":((100 * (baseCaseMeanRearInter10 - meanRearInter10["+40"])) / baseCaseMeanRearInter10)}
    rearInter20Sensitivity = {"-40":((100 * (baseCaseMeanRearInter20 - meanRearInter20["-40"])) / baseCaseMeanRearInter20), "+40":((100 * (baseCaseMeanSideInter20 - meanRearInter20["+40"])) / baseCaseMeanSideInter20)}
    rearInter50Sensitivity = {"-40":((100 * (baseCaseMeanRearInter50 - meanRearInter50["-40"])) / baseCaseMeanRearInter50), "+40":((100 * (baseCaseMeanSideInter50 - meanRearInter50["+40"])) / baseCaseMeanSideInter50)}

    sensitivities = {"rearTTCmin": rearEndTTCSensitivity,
                      "sideTTCmin": sideTTCSensitivity,
                      "PETs": petsSensitivity,
                      "sidenInter10": sidenInter10Sensitivity,
                      "sidenInter20": sidenInter20Sensitivity,
                      "sidenInter50": sidenInter50Sensitivity,
                      "rearnInter10": rearInter10Sensitivity,
                      "rearnInter20": rearInter20Sensitivity,
                      "rearnInter50": rearInter50Sensitivity,
                      }
    toolkit.saveYaml('{}Sensitivities.yml'.format(parameter), sensitivities)
    return sensitivities

# display
#dn
x = ['$mean\ rear-end\ TTC_{min }$', '$mean\ side\ TTC_{min }$', '$mean\ PET$', '$mean\ rear\ end\ nInter_{20}$', '$mean\ rear\ end\ nInter_{50}$', '$mean\ side\ nInter_{10}$', '$mean\ side\ nInter_{20}$', '$mean\ side\ nInter_{50}$']
moins40 = [8.871447130463679,
 -50.5025453212924,
 30.04446040498593,
 -9.78403755868545,
 -13.352025524509338,
 -12.3140874075204,
 -317.1632896305125,
 0.0]
plus40 = [-4.943886355590759,
 38.45468085191765,
 -11.437758546844718,
 15.248826291079808,
 11.379677076283466,
 12.436122340019834,
 91.16310548196849,
 54.39707116162002]

fig = plt.figure()
ax = plt.subplot(111)
ax.barh(x, moins40, color='None', align='edge', height=.8, edgecolor='b')
# for i, v in enumerate(moins40):
#     ax.text(v + 3, i + .25, str(v)[0:4], color='black', fontweight='bold')
ax.barh(x, plus40, color='None', align='edge', height=.8, edgecolor='r')
# for i, v in enumerate(plus40):
#     ax.text(v + 3, i + .25, str(v)[0:4], color='black', fontweight='bold')
plt.legend(['$\ tau-40\%$', '$\ tau+40\%$'])

# plt.legend(['$vehicle\ length\ -\ 40\%$', '$vehicle\ length\ +\ 40\%$'])
# ax.set_yticklabels(x, va='top', minor=False)
x_pos = [i+.4 for i in range(0, len(x))]
plt.yticks(x_pos, x)
plt.xlabel('Variation percentage (%)')
# plt.set_ytickslabel("a=center")
plt.tight_layout()
plt.plot([0,0], [0,len(x)], color='black')
plt.savefig('sa-tau.pdf')
plt.close('all')

plus40 = []
moins40 = []
for truc in dn:
    moins40.append(dn[truc]['-40'])
for truc in dn:
    plus40.append(dn[truc]['+40'])

moins40
plus40