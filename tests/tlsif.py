'''
Created on 2014-05-06

@author: cbrunet
'''
import unittest

from fibermodes import fixedFiber, Wavelength, Mode


class TestTLSIF(unittest.TestCase):

    def _compareModes(self, modes, sols):
        self.assertEqual(len(modes), len(sols))

        for i in range(len(sols)):
            self.assertAlmostEqual(modes[i].neff, sols[i][1])
            self.assertEqual(str(modes[i]), sols[i][0])

    def testCase2LP(self):
        """Annular-core fiber."""
        wl = Wavelength(1550e-9)
        fiber = fixedFiber(wl, [4e-6, 10e-6], [1.4444, 1.4489, 1.4444])

        sols = [('LP(0,1)', 1.4472296),
                ('LP(1,1)', 1.4465947),
                ('LP(2,1)', 1.4452985)]
        lpmodes = fiber.lpModes(delta=1e-3)
        self._compareModes(lpmodes, sols)

    def testCase2Vector(self):
        """Annular-core fiber."""
        wl = Wavelength(1550e-9)
        fiber = fixedFiber(wl, [4e-6, 10e-6], [1.4444, 1.4489, 1.4444])

        sols = [('HE(1,1)', 1.4472267686),
                ('TE(0,1)', 1.4465947086),
                ('HE(2,1)', 1.446591650399142),
                ('TM(0,1)', 1.446587672894224),
                ('EH(1,1)', 1.445296246037881),
                ('HE(3,1)', 1.4452944761507711)]
        lpmodes = fiber.lpModes(delta=1e-3)
        vmodes = fiber.vModes(lpmodes, delta=1e-4)
        self._compareModes(vmodes, sols)

    def _testFiberCutoff(self, rho, n, cutoffs, places=7):
        wl = Wavelength(1550e-9)
        fiber = fixedFiber(wl, rho, n)

        for mode, (co, comin) in cutoffs.items():
            self.assertAlmostEqual(fiber.cutoffV0(mode, comin), co,
                                   places=places,
                                   msg=str(mode))

    def testLPCutoffA(self):
        rho = [4e-6, 6e-6]
        n = [1.47, 1.43, 1.44]
        cutoffs = {
            Mode('LP', 1, 1): (4.034844259728652, 2),
            Mode('LP', 2, 1): (6.1486114063146005, 2),
            Mode('LP', 3, 1): (8.07126756792508, 2),
            Mode('LP', 4, 1): (9.911798124561814, 2),
            Mode('LP', 0, 2): (6.568180843774973, 2),
            Mode('LP', 1, 2): (8.922361377477307, 4.2),
            Mode('LP', 2, 2): (11.06585974653044, 6.2),
        }

        self._testFiberCutoff(rho, n, cutoffs)

    def testVCutoffA(self):
        rho = [4e-6, 6e-6]
        n = [1.47, 1.43, 1.44]
        cutoffs = {
            Mode('TE', 0, 1): (4.034844259728651, 2),
            Mode('HE', 2, 1): (4.071976253449693, 2),
            Mode('TM', 0, 1): (4.058192997221014, 2),
            Mode('EH', 1, 1): (6.158255614959294, 2),
            Mode('HE', 3, 1): (6.189815896708511, 2),
            Mode('EH', 2, 1): (8.080052963422796, 2),
            Mode('HE', 4, 1): (8.115131183786337, 2),
            Mode('EH', 3, 1): (9.91993372343631, 2),
            Mode('HE', 5, 1): (9.957649725258843, 2),
            Mode('HE', 1, 2): (6.589429513136826, 2),
            Mode('TE', 0, 2): (8.922361377477312, 5),
            Mode('HE', 2, 2): (8.948985568829624, 5),
            Mode('TM', 0, 2): (8.953573638542046, 5),
            Mode('EH', 1, 2): (11.078160141775095, 7),
            Mode('HE', 3, 2): (11.09621953195914, 7),
        }

        self._testFiberCutoff(rho, n, cutoffs)

    def testLPCutoffB(self):
        rho = [4e-6, 6e-6]
        n = [1.47, 1.45, 1.44]
        cutoffs = {
            Mode('LP', 1, 1): (3.1226096356321893, 2),
            Mode('LP', 2, 1): (5.096112984974791, 2),
            Mode('LP', 3, 1): (6.968066798210773, 2),
            Mode('LP', 4, 1): (8.8012241922413, 2),
            Mode('LP', 5, 1): (10.61168894514904, 2),
            Mode('LP', 0, 2): (4.676313597977374, 2),
            Mode('LP', 1, 2): (6.809117963058563, 3.2),
            Mode('LP', 2, 2): (8.743801177466404, 5.2),
            Mode('LP', 3, 2): (10.598944233713851, 7),
            Mode('LP', 0, 3): (8.047306845386878, 5),
            Mode('LP', 1, 3): (9.953012983126248, 7),
        }

        self._testFiberCutoff(rho, n, cutoffs)

    def testVCutoffB(self):
        rho = [4e-6, 6e-6]
        n = [1.47, 1.45, 1.44]
        cutoffs = {
            Mode('TM', 0, 1): (3.111217543593232, 2),
            Mode('TE', 0, 1): (3.122609635632189, 2),
            Mode('HE', 2, 1): (3.1400200936070846, 2),
            Mode('EH', 1, 1): (4.669304720761619, 2),
            Mode('HE', 1, 2): (5.088131872468638, 2),
            Mode('HE', 3, 1): (5.118129406153233, 2),
            Mode('TM', 0, 2): (6.7934897736915065, 4),
            Mode('HE', 2, 2): (6.80880538983052, 4),
            Mode('TE', 0, 2): (6.809117963058563, 4),
            Mode('EH', 2, 1): (6.958505239863098, 2),
            Mode('HE', 4, 1): (6.993124138822584, 2),
            Mode('EH', 1, 2): (8.049518101191492, 5),
            Mode('HE', 1, 3): (8.735885113376382, 6),
            Mode('HE', 3, 2): (8.747374022674864, 6),
            Mode('EH', 3, 1): (8.790776475777257, 2),
            Mode('HE', 5, 1): (8.828714775284547, 2),
            Mode('TE', 0, 3): (9.95301298312625, 7),
            Mode('HE', 2, 3): (9.962177458632713, 7),
            Mode('TM', 0, 3): (9.962228554278012, 7),
            Mode('EH', 2, 2): (10.591251538701066, 7),
            Mode('EH', 4, 1): (10.600825077678442, 2),
            Mode('HE', 4, 2): (10.605263286689778, 7),
            Mode('HE', 6, 1): (10.64128881198123, 2),
        }

        self._testFiberCutoff(rho, n, cutoffs)

    def testLPCutoffC(self):
        rho = [4e-6, 6e-6]
        n = [1.43, 1.47, 1.44]
        cutoffs = {
            Mode('LP', 1, 1): (3.010347467577181, 2),
            Mode('LP', 2, 1): (4.404178238529268, 2),
            Mode('LP', 3, 1): (5.631998448700369, 2),
            Mode('LP', 4, 1): (6.7965518925242865, 2),
            Mode('LP', 5, 1): (7.93118037952865, 2),
            Mode('LP', 6, 1): (9.050134813376669, 2),
            Mode('LP', 7, 1): (10.160295215952916, 2),
            Mode('LP', 0, 2): (10.813986300277824, 2),
        }

        self._testFiberCutoff(rho, n, cutoffs)

    def testVCutoffC(self):
        rho = [4e-6, 6e-6]
        n = [1.43, 1.47, 1.44]
        cutoffs = {
            Mode('TE', 0, 1): (3.0103474675771804, 2),
            Mode('TM', 0, 1): (3.0732744029480012, 2),
            Mode('TE', 0, 2): (11.215674035379953, 5),
            Mode('TM', 0, 2): (11.29528661745687, 5),
            Mode('EH', 1, 1): (4.43599929326006, 2),
            Mode('EH', 2, 1): (5.660787662502081, 2),
            Mode('EH', 3, 1): (6.821606789237238, 2),
            Mode('EH', 4, 1): (7.952484494712328, 2),
            Mode('EH', 5, 1): (9.067961694568465, 2),
            Mode('EH', 6, 1): (10.175030484705225, 2),
            Mode('HE', 2, 1): (3.0406851062929734, 2),
            Mode('HE', 3, 1): (4.438962073092406, 2),
            Mode('HE', 4, 1): (5.668294434394004, 2),
            Mode('HE', 5, 1): (6.833174601202006, 2),
            Mode('HE', 6, 1): (7.967602949136493, 2),
            Mode('HE', 7, 1): (9.086138896920177, 2),
            Mode('HE', 8, 1): (10.195817896822504, 2),
            Mode('HE', 1, 2): (10.844609209283163, 2),
            Mode('HE', 2, 2): (11.249595259175186, 6),
            Mode('EH', 1, 2): (11.843142062848772, 5),
            Mode('HE', 3, 2): (11.832900895486063, 7),
            Mode('EH', 2, 2): (12.538738658782329, 6),
            Mode('HE', 4, 2): (12.528230836249172, 8),
        }

        self._testFiberCutoff(rho, n, cutoffs)

    def testLPCutoffD(self):
        rho = [4e-6, 6e-6]
        n = [1.45, 1.47, 1.44]
        cutoffs = {
            Mode('LP', 1, 1): (2.702968459636167, 2),
            Mode('LP', 2, 1): (4.150583195855695, 2),
            Mode('LP', 3, 1): (5.430106475704322, 2),
            Mode('LP', 4, 1): (6.636532360901636, 2),
            Mode('LP', 5, 1): (7.804416891196523, 2),
            Mode('LP', 6, 1): (8.949785986163985, 2),
            Mode('LP', 7, 1): (10.080981852288588, 2),
            Mode('LP', 0, 2): (5.640393617621346, 2),
            Mode('LP', 1, 2): (8.008821133207624, 3),
            Mode('LP', 2, 2): (9.679408185385487, 5),
            Mode('LP', 3, 2): (10.97034948328025, 6),
            Mode('LP', 0, 3): (9.684508718046876, 6),
        }

        self._testFiberCutoff(rho, n, cutoffs)

    def testVCutoffD(self):
        rho = [4e-6, 6e-6]
        n = [1.45, 1.47, 1.44]
        cutoffs = {
            Mode('TE', 0, 1): (2.7029684596361676, 2),
            Mode('TM', 0, 1): (2.727734813318786, 2),
            Mode('TE', 0, 2): (8.008821133207624, 3),
            Mode('TM', 0, 2): (7.993329888241878, 3),
            Mode('EH', 1, 1): (4.1655157193520465, 2),
            Mode('EH', 2, 1): (5.445008118664826, 2),
            Mode('EH', 3, 1): (6.650249935726423, 2),
            Mode('EH', 4, 1): (7.816502257699482, 2),
            Mode('EH', 5, 1): (8.960139011974638, 2),
            Mode('EH', 6, 1): (10.089675701100248, 2),
            Mode('EH', 1, 2): (9.680599063398324, 5),
            Mode('EH', 2, 2): (10.98222290317733, 6),
            Mode('HE', 1, 2): (5.634608766525469, 2),
            Mode('HE', 2, 1): (2.7228694802366005, 2),
            Mode('HE', 3, 1): (4.176283860563018, 2),
            Mode('HE', 4, 1): (5.458819017982079, 2),
            Mode('HE', 5, 1): (6.666904206459127, 2),
            Mode('HE', 6, 1): (7.835721155652211, 2),
            Mode('HE', 7, 1): (8.981619572965892, 2),
            Mode('HE', 8, 1): (10.113121418012547, 2),
            Mode('HE', 1, 2): (5.634608766525465, 2),
            Mode('HE', 2, 2): (8.003273407163517, 3),
            Mode('HE', 3, 2): (9.681017840406332, 5),
            Mode('HE', 4, 2): (10.980585429648642, 6),
            Mode('HE', 1, 3): (9.686653009072776, 6),
        }

        self._testFiberCutoff(rho, n, cutoffs)

    def testLPCutoffE(self):
        rho = [4e-6, 6e-6]
        n = [1.44, 1.47, 1.44]
        cutoffs = {
            Mode('LP', 1, 1): (2.85904035776636975, 2),
            Mode('LP', 2, 1): (4.2866039225676404, 2),
            Mode('LP', 3, 1): (5.540915061306307, 2),
            Mode('LP', 4, 1): (6.725406031775626, 2),
            Mode('LP', 5, 1): (7.8752953434136135, 2),
            Mode('LP', 6, 1): (9.006117838838101, 2),
            Mode('LP', 7, 1): (10.125608397188888, 2),
            Mode('LP', 0, 2): (9.482807865823602, 2),
            Mode('LP', 1, 2): (10.27844425627377, 3),
        }

        self._testFiberCutoff(rho, n, cutoffs)

    def testVCutoffE(self):
        rho = [4e-6, 6e-6]
        n = [1.44, 1.47, 1.44]
        cutoffs = {
            Mode('TE', 0, 1): (2.859040357765955, 2),
            Mode('HE', 2, 1): (2.8832370027681815, 2),
            Mode('TM', 0, 1): (2.9017337070631224, 2),
            Mode('EH', 1, 1): (4.310052598194367, 2),
            Mode('HE', 3, 1): (4.316477364814478, 2),
            Mode('EH', 2, 1): (5.563044551409131, 2),
            Mode('HE', 4, 1): (5.573271721659564, 2),
            Mode('EH', 3, 1): (6.745115477350213, 2),
            Mode('HE', 5, 1): (6.758852822325253, 2),
            Mode('EH', 4, 1): (7.892295201926296, 2),
            Mode('HE', 6, 1): (7.9091525519850805, 2),
            Mode('EH', 5, 1): (9.020476094070924, 2),
            Mode('HE', 7, 1): (9.040050082529529, 2),
            Mode('EH', 6, 1): (10.137550450462196, 2),
            Mode('HE', 8, 1): (10.159460454232093, 2),
            Mode('HE', 1, 2): (9.482807865823602, 2),
            Mode('TE', 0, 2): (10.278444256273769, 3),
            Mode('HE', 2, 2): (10.289797328577112, 3),
            Mode('TM', 0, 2): (10.310990340988402, 3),
        }

        self._testFiberCutoff(rho, n, cutoffs)

    def testCutoffTableIII(self):
        """Values from cutoff acticle, Table III."""
        n = (1.444, 1.474, 1.444)
        b = 10e-6

        rho = (0.25*b, b)
        cutoffs = {
            Mode('TE', 0, 1): (2.4161, 2),
            Mode('HE', 2, 1): (2.4336, 2),
            Mode('TM', 0, 1): (2.4257, 2),
            # Mode('EH', 1, 1): (3.8330, 2),
            Mode('HE', 3, 1): (3.8561, 2),
            Mode('HE', 1, 2): (4.4475, 2),
            # Mode('EH', 2, 1): (5.1359, 2),
            Mode('HE', 4, 1): (5.1603, 2),
            Mode('TE', 0, 2): (5.7336, 3),
            Mode('HE', 2, 2): (5.7418, 3),
            Mode('TM', 0, 2): (5.7610, 3),
        }
        self._testFiberCutoff(rho, n, cutoffs, 4)

        rho = (0.5*b, b)
        cutoffs = {
            Mode('TE', 0, 1): (2.5544, 2),
            Mode('HE', 2, 1): (2.5742, 2),
            Mode('TM', 0, 1): (2.5822, 2),
            # Mode('EH', 1, 1): (3.9294, 2),
            Mode('HE', 3, 1): (3.9648, 2),
            Mode('HE', 1, 2): (6.3932, 2),
            # Mode('EH', 2, 1): (5.1976, 2),
            Mode('HE', 4, 1): (5.2316, 2),
            Mode('TE', 0, 2): (7.3236, 3),
            Mode('HE', 2, 2): (7.3337, 3),
            Mode('TM', 0, 2): (7.3583, 3),
        }
        self._testFiberCutoff(rho, n, cutoffs, 4)

        rho = (0.75*b, b)
        cutoffs = {
            Mode('TE', 0, 1): (3.1663, 2),
            Mode('HE', 2, 1): (3.1943, 2),
            Mode('TM', 0, 1): (3.2188, 2),
            # Mode('EH', 1, 1): (4.6458, 2),
            Mode('HE', 3, 1): (4.7123, 2),
            Mode('HE', 1, 2): (12.6056, 2),
            # Mode('EH', 2, 1): (5.9360, 2),
            Mode('HE', 4, 1): (6.0074, 2),
            Mode('TE', 0, 2): (13.3513, 4),
            Mode('HE', 2, 2): (13.3631, 4),
            Mode('TM', 0, 2): (13.3822, 4),
        }
        self._testFiberCutoff(rho, n, cutoffs, 4)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testSSIF']
    unittest.main()
