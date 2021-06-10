from math import pi, degrees, atan, sin, cos, acos, sqrt, exp
from matplotlib import pyplot as plt
import numpy as np

# Rotor model using blade element momentum theory
class Rotor:
    # Inputs:
    #   blade: characteristic blade (from blade.py)
    #   nblades: number of blades
    def __init__(self, blade, nblades):
        self._blade = blade
        self._nblades = nblades
        self._rstrip = []
        self._chordstrip = []
        self._twiststrip = []
        self._dR = None
        self._inflow = []
        self._alpha = []
        self._cl = []
        self._cd = []
        self._dT = []
        self._dP = []
        self._thrust = None
        self._power = None
        self._CT = None
        self._CP = None

    # Computes chord and twist distributions at strip centers
    def discretize(self, nstrips):
        self._chordstrip = []
        self._twiststrip = []
        Ri = self._blade.innerRadius()
        Ro = self._blade.outerRadius()
        self._dR = (Ro-Ri) / nstrips
        for strip in range(nstrips):
            r = Ri + (float(strip)+0.5)*self._dR
            self._rstrip.append(r)
            self._chordstrip.append(self._blade.chord(r))
            self._twiststrip.append(self._blade.twist(r))

        # Initialize outputs
        self._inflow = nstrips*[0.]
        self._alpha = nstrips*[0.]
        self._cl = nstrips*[0.]
        self._cd = nstrips*[0.]
        self._dT = nstrips*[0.]
        self._dP = nstrips*[0.]

    # Calculates forces and power on rotor in hover or climbing flight
    # Inputs:
    #   rho: air density
    #   V: incoming axial air flow speed
    #   rpm: rotor speed
    #   theta0: collective pitch (degrees)
    #   maxiters: max iterations for inflow convergence
    #   tol: tolerance for inflow convergence
    #   relax: relaxation factor for converging inflow. Lower value gives slower
    #       but more reliable convergence.
    def calc(self, rho, V, rpm, theta0, maxiters=5000, tol=1e-12, relax=0.01):
        om = rpm*1./60.*2.*pi           # Rotational speed in rad/sec

        # Calculate outputs for each strip
        nstrips = len(self._rstrip)
        b = self._nblades
        Ro = self._blade.outerRadius()
        for strip in range(nstrips):

            # Iterate on local induced inflow vi
            r = self._rstrip[strip]
            vi = self._inflow[strip]
            inflow_err = 1e6
            iters = 0
            while inflow_err > tol and iters < maxiters:
                # Strip aerodynamics
                Ut = om*r
                Up = V + vi
                Usquare = Ut**2 + Up**2
                phi = atan(Up/Ut)
                alpha = theta0 + self._twiststrip[strip] - degrees(phi)
                cl = self._blade._airfoil.Cl(alpha)
                cd = self._blade._airfoil.Cd(alpha)
                Lp = 0.5*rho*Usquare*self._chordstrip[strip]*cl
                Dp = 0.5*rho*Usquare*self._chordstrip[strip]*cd

                # Prandtl tip loss factor (from Energy Procedia paper)
                if V+vi > 0.:
                    f = 0.5*b*(Ro-r)/(r*sin(phi))
                    Ft = 2./pi*acos(exp(-f))
                else:
                    Ft = 1.

                # Annular thrust and power
                dT = b*Ft*self._dR*(Lp*cos(phi) - Dp*sin(phi))
                dP = b*Ft*Ut*self._dR*(Dp*cos(phi) + Lp*sin(phi))

                # Inflow according to momentum theory
                ''' 4.*pi*rho*r*self._dR*(V*vim + vim**2) = dT '''
                a = 4.*pi*rho*r*self._dR
                arg = 0.25*V**2 + dT/a
                vim = -0.5*V + sqrt(max(arg, 0.))

                # Calculate error based on non-dimensional induced inflow and update
                inflow_err = sqrt((vim-vi)**2)/(om*Ro)
                vi = relax*vim + (1.-relax)*vi
                iters += 1

            # Warning if inflow didn't converge
            if inflow_err > tol:
                print("Warning: inflow did not converge for strip {:d}.".format(strip))

            # Store converged values
            self._inflow[strip] = vi
            self._alpha[strip] = alpha
            self._cl[strip] = cl
            self._cd[strip] = cd
            self._dT[strip] = dT
            self._dP[strip] = dP

            # Integrate
            A = pi*Ro**2.
            self._thrust = np.sum(self._dT)
            self._power = np.sum(self._dP)
            self._CT = self._thrust/(rho*A*(om*Ro)**2.)
            self._CP = self._power/(rho*A*(om*Ro)**3.)

    # Plots rotor data
    def plotInflow(self):
        plt.clf()
        plt.close()
        fig, ax = plt.subplots()
        ax.set_xlabel("r")
        ax.set_ylabel("Induced inflow")
        ax.plot(self._rstrip, self._inflow)
        ax.grid()
        plt.show()

    def plotAlpha(self):
        plt.clf()
        plt.close()
        fig, ax = plt.subplots()
        ax.set_xlabel("r")
        ax.set_ylabel("Angle of attack (deg)")
        ax.plot(self._rstrip, self._alpha)
        ax.grid()
        plt.show()

    def plotCl(self):
        plt.clf()
        plt.close()
        fig, ax = plt.subplots()
        ax.set_xlabel("r")
        ax.set_ylabel("Strip lift coefficient")
        ax.plot(self._rstrip, self._cl)
        ax.grid()
        plt.show()

    def plotCd(self):
        plt.clf()
        plt.close()
        fig, ax = plt.subplots()
        ax.set_xlabel("r")
        ax.set_ylabel("Strip drag coefficient")
        ax.plot(self._rstrip, self._cd)
        ax.grid()
        plt.show()

    def plotCT(self):
        plt.clf()
        plt.close()
        nondim = self._thrust/self._CT
        fig, ax = plt.subplots()
        ax.set_xlabel("r")
        ax.set_ylabel("Strip thrust coefficient")
        ax.plot(self._rstrip, np.array(self._dT)/nondim)
        ax.grid()
        plt.show()

    def plotCP(self):
        plt.clf()
        plt.close()
        nondim = self._power/self._CP
        fig, ax = plt.subplots()
        ax.set_xlabel("r")
        ax.set_ylabel("Strip power coefficient")
        ax.plot(self._rstrip, np.array(self._dP)/nondim)
        ax.grid()
        plt.show()
