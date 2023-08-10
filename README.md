# Gravitational Wave Detector Zoo

**Artificial Scientific Discovery of interferometric Gravitational Wave Detectors**\
_Mario Krenn*, Yehonathan Drori*, Rana X. Adhikari_\
(* = equal contribution)

Here we present the technical details of solutions discovered by GWAlgo, and the
corresponding PyKat and Finesse files for reproducing the solutions.

<p align="center">
   <img src="https://github.com/artificial-scientist-lab/GWDetectorZoo/blob/main/strain.png" alt="Strain Sensitivity of four superior solutions" width="666px">
</p>
Details on these four superior solutions can be found at [Broadband](), [Cosmology](), [Supernova]() and [Neutron Star Post-Merger]().

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
* [Post-Merger, Quantum+Classical, Large](type0/README.md)
* [Narrow Post-Merger, Quantum+Classical, Large](type1/README.md)
* [Supernova, Quantum+Classical, Large](type2/README.md)
* [Primodial Black Holes, Quantum+Classical, Large](type3/README.md)
* [Broad Band, Quantum+Classical, Large](type4/README.md)
* [Broad Band, Quantum, Large](type5/README.md)
* [Narrow Post-Merger, Quantum, Large](type6/README.md)
* [Post-Merger, Quantum, Large](type8/README.md)
* [Primodial Black Holes, Quantum, Large](type9/README.md)
* [Broad Band, Quantum, Small](type10/README.md)
