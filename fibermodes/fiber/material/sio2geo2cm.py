'''
Created on 2014-09-08

@author: cbrunet
'''

from .claussiusmossotti import ClaussiusMossotti
import numpy


class SiO2GeO2(ClaussiusMossotti):

    '''
    classdocs
    '''

    name = "Silica doped with Germania (Claussius-Mossotti version)"
    nparams = 1
    WLRANGE = (0.6e-6, 1.8e-6)
    XRANGE = 0.2

    A = numpy.array([0.2045154578, 0.06451676258, 0.1311583151])
    B = numpy.array([-0.1011783769, 0.1778934999, -0.1064179581])
    Z = numpy.array([0.06130807320e-6, 0.1108859848e-6, 8.964441861e-6])

    @classmethod
    def info(cls):
        return "Silica doped with Germania."

# Article (Sunak1989)
# Sunak, H. & Bastien, S.
# Refractive index and material dispersion interpolation of doped silica
# in the 0.6-1.8 mu m wavelength region
# Photonics Technology Letters, IEEE, 1989, 1, 142-145
