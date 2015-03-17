"""Simulator module."""

from ..wavelength import Wavelength
from ..fiber.factory import Factory
from ..mode import Family, Mode
from fibermodes import constants
from itertools import product, count
from functools import reduce
from operator import mul
import numpy
import shelve
from distutils.version import StrictVersion
from copy import deepcopy


class Simulator(object):

    __version__ = "1.0.0"

    """Simulator class."""

    def __init__(self, delta=1e-6, epsilon=1e-12, cladding=False):
        """Constructor."""
        self._wl = None  # list of wavelengths
        self._f = None  # fiber factory
        self._matparams = None  # list of material parameters
        self._r = None  # list of layer radii

        self._constraints = {}  # list of constraints

        self._modes = {}  # found modes (fiber: {mode: smode})
        self._cutoffs = {}  # found cutoffs (fiber: {mode: cutoff})

        self._delta = delta
        self._epsilon = epsilon
        self._nmax = None
        self._cladding = cladding

    def setWavelength(self, wl):
        """Set the wavelengths used for the simulation.

        :param wl: wavelength as float (in meters),
                   or :class:`~fibermodes.wavelength.Wavelength` object,
                   or iterable returning either floats
                   or :class:`~fibermodes.wavelength.Wavelength` object.

        """
        self._wl = list(wl) if hasattr(wl, '__iter__') else [wl]
        for i, w in enumerate(self._wl):
            if not isinstance(w, Wavelength):
                self._wl[i] = Wavelength(w)

    def setMaterials(self, *args):
        """Set the materials used for the simulation.

        Unlike other simulation parameters, fiber materials must be fixed
        for the simulation. However, materials parameters can be swept.

        """
        self._f = Factory(args)

    def setMaterialsParams(self, *args):
        """Set the parameters used in the simulation, for each materials.

        """
        self._matparams = list()
        for params in args:  # for each layer
            self._matparams.append([list(p) if hasattr(p, '__iter__') else [p]
                                    for p in params])

    def setMaterialParam(self, layer, pnum, pval):
        if self._matparams is None:
            self._matparams = []
        self._matparams += [[]] * max(0, layer - len(self._matparams) + 1)
        self._matparams[layer] += [0] * max(
            0, pnum - len(self._matparams[layer]) + 1)
        self._matparams[layer][pnum] = (list(pval)
                                        if hasattr(pval, '__iter__')
                                        else [pval])

    def setRadius(self, layer, r):
        """Set the radius of layer to r"""
        if self._r is None:
            self._r = []
        self._r += [0] * max(0, layer - len(self._r) + 1)
        self._r[layer] = list(r) if hasattr(r, '__iter__') else [r]

    def setRadiusFct(self, layer, fct, *args):
        self.setRadius(layer, ((fct,) + args,))

    def setRadii(self, *args):
        """Set the radii of each layer used for the simulation.

        """
        self._r = list(list(r) if hasattr(r, '__iter__') else [r]
                       for r in args)

    def setV0Param(self, rna):
        """Set parameter for normalizing V0.

        :param rna: :math:`r \sqrt{n^2 - n_{cl}^2}`

        """
        self._f._rna = rna

    def addConstraint(self, name, cmp, *args):
        """Add constraint on parameters.

        :param name: Unique name for the constraint
        :param cmp: A comparison function. Take len(args) arguments.
                    Return ``True`` if arguments are accepted.
        :param args: Each arg is a tuple (pname, [arg1], [arg2]). See
                     :func:`getParam` for details.
        """
        self._constraints[name] = (cmp, args)

    def delConstraint(self, name):
        """Delete constraint on parameters.

        :param name: Unique name of the constraint
        """
        del self._constraints[name]

    def _testConstraints(self, fiber):
        """Return True if parameters are accepted.

        """
        for cmp, args in self._constraints.values():
            p = [fiber.get(pname, *pargs) for pname, *pargs in args]
            if not(cmp(*p)):
                break
        else:
            return True
        return False

    def setDelta(self, delta):
        self._delta = delta

    def setEpsilon(self, epsilon):
        self._epsilon = epsilon

    def setNMax(self, nmax):
        self._nmax = nmax

    def setCladdingModes(self, cladding):
        self._cladding = cladding

    def save(self, filename):
        """Save the current state of the simulator.

        :param filename: file name (string)

        """
        with shelve.open(filename) as db:
            db['version'] = self.__version__
            db['wavelength'] = self._wl
            db['factory'] = self._f
            db['matparams'] = self._matparams
            db['radii'] = self._r
            db['constraints'] = self._constraints
            db['lpModes'] = self._lpModes
            db['vModes'] = self._vModes

    def read(self, filename):
        """Restore from a file the current state of the simulator.

        If db version is lowwer than current version,
        the database is automatically upgraded to current version.

        :param filename: file name (string)

        """
        with shelve.open(filename) as db:
            try:
                if (StrictVersion(db['version']) <
                        StrictVersion(self.__version__)):
                    self._convert(db)
            except KeyError:
                raise FileNotFoundError()
            self._f = db['factory']
            self._wl = db['wavelength']
            self._matparams = db['matparams']
            self._r = db['radii']
            self._constraints = db['constraints']
            self._lpModes = db['lpModes']
            self._vModes = db['vModes']

    def _convert(self, db):
        """Convert db to current version."""
        pass

    def _iterator(self, wavelengths, matparam, radii, skipAsNone=False):
        if None in (self._wl, self._r, self._matparams):
            return
        params = [[0]*(self._f[i].nparams+1) for i in range(self._f.nlayers)]
        for flatparam in product(*(x for y in matparam for x in y)):
            k = 0
            for i in range(self._f.nlayers):
                for j in range(self._f[i].nparams):
                    params[i][j+1] = flatparam[k]  # params[0] is radius
                    k += 1
            for wl in wavelengths:
                for r in product(*radii):
                    for i in range(self._f.nlayers-1):  # skip last layer
                        params[i][0] = r[i]
                    fiber = self._f(wl, *params)
                    if fiber and self._testConstraints(fiber):
                        yield fiber
                    elif skipAsNone:
                        yield None

    def __iter__(self):
        """Generator of each possible fiber, within simulation parameters."""
        yield from self._iterator(self._wl, self._matparams, self._r)

    def __len__(self):
        """Number of different fibers generated by simulation parameters."""
        if None in (self._wl, self._r, self._matparams):
            return 0
        if not self._constraints:
            return self.__length_hint__()
        else:
            return sum(1 for _ in self)

    def __length_hint__(self):
        return len(self._wl) * reduce(mul, (len(r) for r in self._r)) * \
            reduce(mul, (len(p) for x in self._matparams for p in x))

    def getDimensions(self):
        dims = []
        if len(self._wl) > 1:
            dims.append(('wavelength',))
        for i, r in enumerate(self._r):
            if len(r) > 1:
                dims.append(('radius', i))
        for i, mp in enumerate(self._matparams):
            for j, p in enumerate(mp):
                if len(p) > 1:
                    dims.append(('material', i, j))
        return dims

    def shape(self):
        return tuple(len(self._getParameter(p)) for p in self.getDimensions())

    def _getParameter(self, dim):
        if dim[0] == 'wavelength':
            return self._wl
        elif dim[0] == 'radius':
            return self._r[dim[1]]
        elif dim[0] == 'material':
            return self._matparams[dim[1]][dim[2]]
        else:
            raise TypeError("Wrong parameter type {}".format(dim))

    def getParameters(self, dims=None):
        if dims is None:
            dims = self.getDimensions()
        return [self._getParameter(dim) for dim in dims]

    def _findNeighbors(self, fiber):
        fmin = []
        fmax = []

        # Parameters of current fiber
        wl = self._wl[0] if len(self._wl) == 1 else fiber._wl
        params = []
        if len(self._r) < len(self._f):
            self._r.append([0])
        for i in range(len(self._f)):
            lparam = [self._r[i][0] if len(self._r[i]) == 1 else fiber._r[i]]
            for j in range(len(self._matparams[i])):
                lparam.append(self._matparams[i][j][0]
                              if len(self._matparams[i][j]) == 1
                              else fiber._params[i][j])
            params.append(lparam)

        # Find neighbors
        for d in self.getDimensions():
            if d[0] == 'wavelength':
                i = self._wl.index(fiber._wl)
                if i > 0:
                    fmin.append(self._f(self._wl[i-1], *params))
                if i < len(self._wl)-1:
                    fmax.append(self._f(self._wl[i+1], *params))

            elif d[0] == 'radius':
                i = self._r[d[1]].index(fiber._r[d[1]])
                p = deepcopy(params)
                if i > 0:
                    p[d[1]][0] = self._r[d[1]][i-1]
                    f1 = self._f(wl, *p)
                else:
                    f1 = None
                if i < len(self._r[d[1]])-1:
                    p[d[1]][0] = self._r[d[1]][i+1]
                    f2 = self._f(wl, *p)
                else:
                    f2 = None
                # TODO: order fibers
                if f1:
                    fmin.append(f1)
                if f2:
                    fmax.append(f2)

            # TODO: mat params

        return fmin, fmax

    def _findBoundaries(self, fiber, mode):
        nmin = fiber._n.min() if self._cladding else fiber._n[-1]
        nmax = fiber._n.max()

        # Modes with lower index
        pm = None
        if mode.family in (Family.TE, Family.TM, Family.LP) and mode.m > 1:
            pm = self.getMode(fiber, Mode(mode.family, mode.nu, mode.m-1))
        elif mode.family == Family.EH:
            pm = self.getMode(fiber, Mode(Family.HE, mode.nu, mode.m))
        elif mode.family == Family.HE and mode.m > 1:
            pm = self.getMode(fiber, Mode(Family.EH, mode.nu, mode.m-1))
        if pm is not None:
            nmax = pm.neff - self._epsilon

        # Modes with lower nu
        if mode.nu > 1 and fiber in self._modes:
            pm = Mode(mode.family, mode.nu-1, mode.m)
            if pm in self._modes[fiber] and self._modes[fiber][pm] is not None:
                if self._modes[fiber][pm].neff < nmax:
                    nmax = self._modes[fiber][pm].neff - self._epsilon

        # if nmax > nmin:
        #     # Hint from found LP modes
        #     # if mode.family != Family.LP and fiber in self._modes:
        #     #     lpm = mode.lpEq()
        #     #     if lpm in self._modes[fiber] and self._modes[fiber] is not None:
        #     #         nmid = self._modes[fiber][lpm].neff

        #     fmin, fmax = self._findNeighbors(fiber)
        #     for f in fmin:
        #         if f in self._modes:
        #             m = self._modes[f].get(mode)
        #             if m and nmax > m.neff > nmin:
        #                 nmin = m.neff
        #     for f in fmax:
        #         if f in self._modes:
        #             m = self._modes[f].get(mode)
        #             if m and nmin < m.neff < nmax:
        #                 nmax = m.neff
        #     assert nmin < nmax

        return nmin, nmax

    def _solveForMode(self, fiber, mode):
        # Ensure we found mode with previous index
        pm = None
        if mode.family in (Family.TE, Family.TM, Family.LP) and mode.m > 1:
            pm = Mode(mode.family, mode.nu, mode.m-1)
        elif mode.family == Family.EH:
            pm = Mode(Family.HE, mode.nu, mode.m)
        elif mode.family == Family.HE and mode.m > 1:
            pm = Mode(Family.EH, mode.nu, mode.m-1)
        if pm is not None and self.getMode(fiber, pm) is None:
            return None

        smode = None
        nmin, nmax = self._findBoundaries(fiber, mode)
        if nmax > nmin:
            for delta in (self._delta, self._delta / 2):
                try:
                    smode = fiber.solve(mode, nmin, nmax, delta, self._epsilon)
                    break
                except OverflowError:
                    pass
        return smode

    def getCutoffV0(self, fiber, mode):
        if str(mode) in ("HE(1,1)", "LP(0,1)"):
            return 0

        fwl0 = fiber._fwl0()
        if fwl0 not in self._modes:
            self._modes[fwl0] = {}
        if mode in self._modes[fwl0]:
            cutoff = self._modes[fwl0][mode]
        else:
            c2 = 1
            if mode.m > 1:
                if str(mode) in ("HE(1,2)", "LP(0,2)"):
                    m2 = Mode("TE", 0, 1)
                else:
                    m2 = Mode(mode.family, mode.nu, mode.m - 1)
                c2 = self.getCutoffV0(fiber, m2)
            if c2:
                try:
                    cutoff = fiber.cutoffV0(mode, c2)
                except NotImplementedError:
                    cutoff = 0
            else:
                cutoff = 0
            self._modes[fwl0][mode] = cutoff
        return cutoff

    def getMode(self, fiber, mode):
        # Test for already solved modes
        if fiber not in self._modes:
            self._modes[fiber] = {}
        if mode in self._modes[fiber]:
            return self._modes[fiber][mode]

        # Test for cutoff
        cutoff = self.getCutoffV0(fiber, mode)
        if not cutoff or cutoff < fiber.V0:
            smode = self._solveForMode(fiber, mode)
        else:
            smode = None

        self._modes[fiber][mode] = smode
        return smode

    def getWavelength(self):
        dims = self.getDimensions()
        shape = self.shape()
        if len(dims) > 0 and dims[0][0] == 'wavelength':
            wl = numpy.empty(shape)
            wl.fill(self._wl[0])
        else:
            wl = numpy.tile(numpy.array(self._wl, ndmin=len(shape)), shape[1:])

        return wl

    def getV0(self):
        V0 = numpy.fromiter((f.V0 for f in iter(self)),
                            numpy.float,
                            self.__length_hint__())
        return V0.reshape(self.shape())

        s = self.shape()
        n1 = numpy.fromiter((max(f._n) for f in iter(self)),
                            numpy.float,
                            self.__length_hint__())
        ncl = numpy.fromiter((f._n[-1] for f in iter(self)),
                             numpy.float,
                             self.__length_hint__())
        na = numpy.sqrt(numpy.square(n1) - numpy.square(ncl)).reshape(s)

        rho = numpy.fromiter((f._r[-1] for f in iter(self)),
                             numpy.float,
                             self.__length_hint__()).reshape(s)

        return 2 * numpy.pi / self.getWavelength() * rho * na

    def getIndex(self, layer):
        n = numpy.fromiter((f['index', layer] for f in iter(self)),
                           numpy.float,
                           self.__length_hint__())
        return n.reshape(self.shape())

    def _getModeAttr(self, fiber, mode, attr, default=None):
        smode = self.getMode(fiber, mode)
        return getattr(smode, attr) if smode else default

    def _getModesAttr(self, mode, attr):
        """Generic function to fetch list of ``attr`` from solved modes.

        """
        a = numpy.fromiter((self._getModeAttr(fiber, mode, attr, 0)
                            for fiber in iter(self)),
                           numpy.float,
                           self.__length_hint__())
        a = a.reshape(self.shape())
        return numpy.ma.masked_less_equal(a, 0)

    def getNeff(self, mode):
        """Return list of effective indices for given mode.

        When the mode does not exist for a given set of parameters,
        the value is masked in the returned array.

        :param: :class:`~fibermodes.mode.Mode`
        :rtype: :class:`numpy.ma.core.MaskedArray`

        """
        return self._getModesAttr(mode, 'neff')

    def getBnorm(self, mode):
        """Return list of normalized propagation constants for given mode.

        When the mode does not exist for a given set of parameters,
        the value is masked in the returned array.

        :param: :class:`~fibermodes.mode.Mode`
        :rtype: :class:`numpy.ma.core.MaskedArray`

        """
        return self._getModesAttr(mode, 'bnorm')

    def _get5points(self, mode):
        wl = numpy.array(self._wl)
        neff = numpy.empty((5, len(self)))
        neff[2, :] = self.getNeff(mode).ravel()

        # if wl.size == 1 or (wl.size > 1 and wl[1] - wl[0] > 1e-8):
        h = 1e-9
        for i in (-2, -1, 1, 2):
            self._wl = wl + i * h
            neff[i+2, :] = self.getNeff(mode).ravel()
        self._wl = wl

        return neff, h

    def _calcBeta(self, mode):
        neff, h = self._get5points(mode)
        neff0 = neff[2, :]
        neff1 = (neff[0, :] - 8 * neff[1, :] +
                 8 * neff[3, :] - neff[4, :]) / (12 * h)
        neff2 = (-neff[0, :] + 16 * neff[1, :] - 30 * neff[2, :] +
                 16 * neff[3, :] - neff[4, :]) / (12 * h**2)
        neff3 = (-neff[0, :] + 2 * neff[1, :] - 2 * neff[3, :] +
                 neff[4, :]) / (2 * h**3)
        wl = self.getWavelength().ravel()
        beta0 = neff0 * constants.tpi / wl
        beta1 = (neff0 - wl * neff1) / constants.c
        beta2 = wl**3 / (constants.tpi * constants.c**2) * neff2
        beta3 = (-wl**4 / (4 * constants.pi**2 * constants.c**3) *
                 (wl * neff3 + neff2))
        for i, fiber in enumerate(iter(self)):
            if (self._modes[fiber][mode] and
                    self._modes[fiber][mode]._beta is None):
                self._modes[fiber][mode]._beta = [beta0[i], beta1[i],
                                                  beta2[i], beta3[i]]

    BETALIM = [None, (0, 1e-8), (-1e-24, 1e-24), (-1e-38, 1e-38)]

    def getBeta(self, mode, order=0):
        """Return list of propagation constants for given mode.

        When the mode does not exist for a given set of parameters,
        the value is masked in the returned array.

        :param: :class:`~fibermodes.mode.Mode`
        :rtype: :class:`numpy.ma.core.MaskedArray`

        """
        beta = numpy.empty(len(self))
        for i, fiber in enumerate(iter(self)):
            sm = self.getMode(fiber, mode)
            if sm:
                if sm.beta(order) is None:
                    self._calcBeta(mode)
                beta[i] = self._modes[fiber][mode]._beta[order]
            else:
                beta[i] = numpy.NaN
        beta = beta.reshape(self.shape(), order='F')
        if order == 0:
            return numpy.ma.masked_invalid(beta)
        else:
            return numpy.ma.masked_outside(beta,
                                           self.BETALIM[order][0],
                                           self.BETALIM[order][1])

    def getNg(self, mode):
        return self.getBeta(mode, 1) * constants.c

    def getD(self, mode):
        """Dispersion (ps / (nm km))

        """
        w2 = numpy.square(self.getWavelength())
        D = (-(constants.tpi * constants.c / w2) *
             self.getBeta(mode, 2)) * 1e6
        return D

    def getS(self, mode):
        """Dispersion slope (ps / nm^2 km)

        """
        w2 = numpy.square(self.getWavelength())
        S = ((constants.tpi * constants.c / w2)**2 *
             self.getBeta(mode, 3)) * 1e-3
        return S

    def findLPModes(self, ellmax=None, mmax=None):
        modes = set()
        wl = min(self._wl)
        fibers = list(self._iterator([wl], self._matparams, self._r))

        for ell in count(0):
            if ellmax is not None and ell > ellmax:
                break
            for m in count(1):
                if mmax and m > mmax:
                    break
                mode = Mode(Family.LP, ell, m)
                for fiber in fibers:
                    if self.getMode(fiber, mode) is not None:
                        modes.add(mode)
                        break
                    else:
                        mmax = m - 1
                        if m == 1:
                            ellmax = 0
                        break
        return sorted(modes)

    def findVModes(self, numax=None, mmax=None):
        modes = set()
        wl = min(self._wl)
        fibers = list(self._iterator([wl], self._matparams, self._r))

        # TE and TM modes
        for family in (Family.TE, Family.TM):
            for m in count(1):
                if mmax and m > mmax:
                    break
                mode = Mode(family, 0, m)
                for fiber in fibers:
                    if self.getMode(fiber, mode) is not None:
                        modes.add(mode)
                        break  # go to next "m"
                else:
                    break  # go to next "family"

        # HE and EH modes
        for nu in count(1):
            if numax and nu > numax:
                break
            for m in count(1):
                if mmax and m > mmax:
                    break
                if nu > 2:
                    mode = Mode(Family.EH, nu-2, m)
                    for fiber in fibers:
                        if self.getMode(fiber, mode) is not None:
                            modes.add(mode)
                            break  # go to "HE"
                    else:
                        mmax = m - 1
                        if m == 1:
                            numax = 1  # To exit from "nu" iterator
                        break  # go to next "nu"

                mode = Mode(Family.HE, nu, m)
                for fiber in fibers:
                    if self.getMode(fiber, mode) is not None:
                        modes.add(mode)
                        break  # go to next "m"
                else:
                    mmax = m - 1
                    if m == 1:
                        numax = 1  # To exit from "nu" iterator
                    break  # go to next "nu"

        return sorted(modes)
