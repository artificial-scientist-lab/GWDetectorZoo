# Gravitational Wave Detector Zoo

**Artificial Scientific Discovery of interferometric Gravitational Wave Detectors**\
_Mario Krenn*, Yehonathan Drori*, Rana X. Adhikari_\
(* = equal contribution)

Here we present the technical details of solutions discovered by GWAlgo, and the
corresponding PyKat and Finesse files for reproducing the solutions.

<p align="center">
   <img src="strain.png" alt="Strain Sensitivity of four superior solutions" width="1000px">
</p>

Details on these four superior solutions can be found at
[Broadband](type5/sol00),
[Cosmology](type9/sol00),
[Supernova](type2/sol00) and
[Neutron Star Post-Merger](type8/sol00).


## Solutions types
We have solutions for various frequency regimes, with different noise sources, and different geometric constraints. We sort them by the following properties:

**Frequency ranges**
* *Post-Merger*: 800Hz-3000Hz
* *Narrow Post-Merger*: 2700-3000Hz
* *Supernova*: 200-1000Hz
* *Primodial Black Holes*: 10-30Hz
* *Broadband*: 20-5000Hz

**Noise sources**
* *Quantum*: Laser frequency noise, laser intensity noise, quantum noise
* *Quantum+Classical*: Laser frequency noise, laser intensity noise, quantum noise, thermal noise, seismic noise

**Geometry constraints**
* *Large*: UIFO diameters constraint to 4 kilometres
* *Small*: Two 4 kilometer arms, and a 400x400 meter GW transducer


## Solutions
* **Post-Merger, Quantum+Classical, Large**
   * [Solution 0](type0/sol00)
* **Narrow Post-Merger, Quantum+Classical, Large**
   * [Solution 0](type1/sol00)
   * [Solution 1](type1/sol01)
   * [Solution 2](type1/sol02)
   * [Solution 3](type1/sol03)     
* **Supernova, Quantum+Classical, Large**
   * [Solution 0](type2/sol00)
   * [Solution 1](type2/sol01)
   * [Solution 2](type2/sol02)
* **Primodial Black Holes, Quantum+Classical, Large**
   * [Solution 0](type3/sol00)
   * [Solution 1](type3/sol01)
   * [Solution 2](type3/sol02) 
* **Broad Band, Quantum+Classical, Large**
   * [Solution 0](type4/sol00)
* **Broad Band, Quantum, Large**
   * [Solution 0](type5/sol00)
   * [Solution 1](type5/sol01)
* **Narrow Post-Merger, Quantum, Large**
* * ...
* **Post-Merger, Quantum, Large**
* * ...
* **Primodial Black Holes, Quantum, Large**
* * ...
* **Broad Band, Quantum, Small**
   * [Solution 0](type10/sol00)
   * [Solution 1](type10/sol01)
   * [Solution 2](type10/sol02)
   * [Solution 3](type10/sol03)   
