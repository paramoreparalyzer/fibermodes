'''
Created on 2014-09-08

@author: cbrunet
'''

from .material import Material, sellmeier
from .silica import Silica
from .germania import Germania
from scipy.optimize import brentq
import numpy


class SiO2GeO2(Material):

    '''
    classdocs
    '''

    name = "Silica doped with Germania"
    nparams = 1
    WLRANGE = (0.6e-6, 1.8e-6)
    XRANGE = 1

    B = numpy.array(Silica.B)
    Bp = numpy.array(Germania.B) - B
    C = numpy.array(Silica.C)
    Cp = numpy.array(Germania.C) - C

    @classmethod
    def n(cls, wl, x):
        cls._testRange(wl)
        cls._testConcentration(x)
        return sellmeier(wl, cls.B + x * cls.Bp, cls.C + x * cls.C)

    @classmethod
    def info(cls):
        return "Silica doped with Germania."

    @classmethod
    def xFromN(cls, wl, n):
        nSi = Silica.n(wl)
        nGe = Germania.n(wl)
        assert nSi <= n <= nGe

        return brentq(lambda x: cls.n(wl, x)-n, 0, cls.XRANGE)

# J. W. Fleming, “Dispersion in geo2–sio2 glasses,” Appl. Opt.,
# vol. 23, no. 24, pp. 4486–4493, Dec 1984. [Online]. Available:
# http://ao.osa.org/abstract.cfm?URI=ao-23-24-4486

# Article (Sunak1989)
# Sunak, H. & Bastien, S.
# Refractive index and material dispersion interpolation of doped silica
# in the 0.6-1.8 mu m wavelength region
# Photonics Technology Letters, IEEE, 1989, 1, 142-145
