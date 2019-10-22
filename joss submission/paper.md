---
title: X-safety: A Python minimal simulation tool for traffic safety 
tags:
  - Python
  - traffic safety
  - road interactions
  - traffic conflicts
  - safety analysis
  - crossing 
  - traffic simulation
  - SMoS
  - surrogate measures of safety 
authors:
  - name: Lionel Nébot-Janvier
    orcid: 0000-0002-9918-4502
    affiliation: 1
  - name: Nicolas Saunier
    orcid: 0000-0003-0218-7932
    affiliation: 1

	
affiliations:
 - name: École Polytechnique de Montréal. Civil, Geological and Mining Engineering Department
   index: 1
date: 16 October 2019
bibliography: paper.bib
---

# Summary

Traffic collisions remain a global cause of death. Road traffic safety analysis most commonly relies on historical crash records and to make any change cities have to collect up to five years of crash data (@global-synergies). Such an approach is reactive to the extent that one must wait for long periods of time to collect sufficient data coming from crash reports to identify unsafe sites and implement solutions. This constitutes therefore an ethical issue as one needs to wait for accidents to occur to be able to prevent them. 

To circumvent this limitation surrogate measures of safety (SMoS) have been studied and developed over the last decades. SMoS are measures that rely on indicators obtained from direct traffic observation. SMoS make the study of road faster and more importantly it is a proactive approach that could be used to prevent accidents from happening. However, the relation of these indicators with road safety needs to be studied. In an empirical approach, Svensson studied the distribution of safety indicators on different sites (-@svensson1998method; -@svensson06estimating). We propose to investigate the distributions of interaction severity indicators via the  development of a  minimal microscopic traffic simulation tool under an open source license: X-safety.

This piece of software aims to provide a free and open source solution to study safety of road users’ interactions at crossings. X-safety can be used to realize simulation of traffic along a road intersection and compute safety indicators that will be lately studied.
We also provide a tutorial detailing the use of X-safety for simple use cases.



# X-Safety

``X-safety'' is a Python package that allows to represent road users moving in one dimension. It relies on a relatively simple car-following model developed by Newell (see -@ newell2002simplified; laval2008microscopic). Interactions at intersection are the result of a simple behavior model at traffic control devices based on gap acceptance theory for yield and stop signs. 
The program has been developed following the methodology adapted from the work of Gauthier (see @ gauthier2016calibration). It is to be noted that the positions and indicators of each users are updated at a regular step time that is defined by the user of X-Safety. 
In its first version, turning movements and lane changes are not allowed. 

In order to use X-safety the user needs to define the experimental setup: network, duration of simulation, number of replications, and models entry parameters.
For each replication, the program iterates the computation, and saves the measures of interest. 
These measures can then be compared for different type of facilities.  

X-safety also contains a collection of functions that can be used to perform operations on lists but also to load, save and modify YAML files. The implementation of X-Safety relies on Traffic Intelligence (see @st2015large
) that is a set of tools for transport data and video analysis. Traffic Intelligence provided a framework to represent users in the simulation system and their coordinates. 

The program makes several approximations which therefore limit its application:

- Users’ trajectories are predicted at constant speed. It implies that the temporal indicators that require motion prediction use the same hypothesis.
- Users are assumed to have an infinite acceleration capacity, which brings discontinuities into their trajectories and indicators. 
- Users are assumed to have no lateral movement. This reduces the range of possible positions that can be reached from an origin, and therefore trajectories and safety indicators might lack of representativity with real life behavior of road users in a traffic conflict event. 

``X-safety'' had been used previously to lead several case studies that are presented in ``An Open-Source Minimal Micro-Simulation Tool for1Safety Analysis’’ (Lionel Nébot Janvier and Nicolas Saunier, 2019). 



# Acknowledgements

The authors wish to acknowledge the financial support of the National Science and Engineering Council (NSERC) of Canada through the Discovery Acceleration Supplement grant no 507950.

# References

---
nocite: | 
  @laureshyn16appendix, @hyden87tct, @youngsimulation2014, @nebotsaunier2019
