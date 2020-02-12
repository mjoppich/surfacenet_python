# surfacenet_python
![GitHub](https://img.shields.io/github/license/mjoppich/surfacenet_python) ![python](https://img.shields.io/badge/python-3.5%20%7C%203.6%20%7C%203.7-blue) 

SurfaceNets implementation in python3 // Volumetric Data to STL

The SurfaceNet algorithm is translated from 

[the JavaScript code provided by Mikola Lysenko](https://github.com/mikolalysenko/mikolalysenko.github.com/blob/master/Isosurface/js/surfacenets.js) .

This python class allows to transform any volumetric data into a polygonal representation, e.g. STL.
A 3D numpy array serves as input, such that, for instance, NRRD files can easily be converted.


I hope this implementation helps someone. If you are using this implementation in your scientific work, please cite the current Zenodo release.