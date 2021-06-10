import sys
import numpy as np

class Airfoil:
    def __init__(self):
        self._alphas = None
        self._cls = None
        self._cds = None

    # Reads alpha, cl, cd from tables. If multiple tables are passed, interpolated values
    # will be averaged from all tables.
    def readTables(self, filenames):
        self._alphas = []
        self._cls = []
        self._cds = []
        for filename in filenames:
            try:
                f = open(filename)
            except IOError:
                sys.stderr.write("Unable to open airfoil table {:s}.\n".format(filename))
                sys.exit(1)
            alphas, cls, cds = self._readTable(f)
            f.close()
            self._alphas.append(alphas)
            self._cls.append(cls)
            self._cds.append(cds)

    def _readTable(self, f):
        alphas = []
        cls = []
        cds = []
        for line in f:
            if not line.startswith('#'):
                splitline = line.split()
                if len(splitline) != 3:
                    sys.stderr.write("Format error in airfoil table.\n")
                    f.close()
                    sys.exit(1)
                alphas.append(float(splitline[0]))
                cls.append(float(splitline[1]))
                cds.append(float(splitline[2]))
        return alphas, cls, cds

    # Reads Cl and Cd tables separately and interpolates to same alphas
    def readClCdTables(self, clfilename, cdfilename):
        alphascl = []
        alphascd = []
        cls = []
        cds = []
        try:
            fcl = open(clfilename)
        except IOError:
            sys.stderr.write("Unable to open airfoil Cl table {:s}.\n".format(clfilename))
            sys.exit(1)
        try:
            fcd = open(cdfilename)
        except IOError:
            sys.stderr.write("Unable to open airfoil Cd table {:s}.\n".format(cdfilename))
            sys.exit(1)

        # Read tables
        for line in fcl:
            if not line.startswith('#'):
                splitline = line.split()
                if len(splitline) != 2:
                    sys.stderr.write("Format error in Cl table.\n")
                    fcl.close()
                    sys.exit(1)
                alphascl.append(float(splitline[0]))
                cls.append(float(splitline[1]))
        fcl.close()

        for line in fcd:
            if not line.startswith('#'):
                splitline = line.split()
                if len(splitline) != 2:
                    sys.stderr.write("Format error in Cd table.\n")
                    fcd.close()
                    sys.exit(1)
                alphascd.append(float(splitline[0]))
                cds.append(float(splitline[1]))
        fcd.close()

        # Interpolate to the finer set of alphas
        if len(alphascl) > len(alphascd):
            self._alphas = [alphascl]
            self._cls = [cls]
            self._cds = [np.interp(alphascl, alphascd, cds)]
        else:
            self._alphas = [alphascd]
            self._cls = [np.interp(alphascd, alphascl, cls)]
            self._cds = [cds]

    # Interpolates lift coefficient from tables and returns averaged result
    def Cl(self, alpha):
        clvals = []
        ntables = len(self._alphas)
        for i in range(ntables):
            clvals.append(np.interp(alpha, self._alphas[i], self._cls[i]))
        return sum(clvals)/ntables

    # Interpolates drag coefficient from tables and returns averaged result
    def Cd(self, alpha):
        cdvals = []
        ntables = len(self._alphas)
        for i in range(ntables):
            cdvals.append(np.interp(alpha, self._alphas[i], self._cds[i]))
        return sum(cdvals)/ntables
