import sys
from math import pi

class Vehicle:
    # Vehicle parameters:
    #   wheel_radius: wheel radius
    #   gear_ratio: ratio of wheel rpm to prop rpm
    #   gear_efficiency: transmission efficiency
    #   CDf: drag coefficient for air flowing over the vehicle from front to back
    #   CDb: drag coefficient for air flowing over the vehicle from back to front
    #   Crr: coefficient of rolling resistance
    #   A: projected frontal area (sq ft)
    #   m: total vehicle mass (slug)
    #   rotor: rotor (from rotor.py)
    def __init__(self, wheel_radius, gear_ratio, gear_efficiency, CDf, CDb, Crr, A, m,
                 rotor):
        self._rw = wheel_radius
        self._trans = gear_ratio
        self._eta_trans = gear_efficiency
        self._CDf = CDf
        self._CDb = CDb
        self._Crr = Crr
        self._A = A
        self._m = m
        self._rotor = rotor
        self._Vvehicle = None
        self._Fdrag_aero = None
        self._Fdrag_rotor = None
        self._Frr = None

    # Set vehicle speed (positive direction is downwind)
    def setSpeed(self, Vvehicle):
        self._Vvehicle = Vvehicle

    # Computes forces given wind speed, air density, collective pitch,
    # and gravitational acceleration
    def computeForces(self, Vwind, rho, theta0, g):
        if self._Vvehicle is None:
            sys.stderr.write("Vehicle speed must be set first.\n")
            sys.exit(1)

        # Wheel rotational speed
        wheel_rps = self._Vvehicle/(2.*pi*self._rw)
        wheel_rpm = wheel_rps*60.

        # Rotor speed
        rotor_rpm = wheel_rpm/self._trans

        # Relative wind from front
        vrel = self._Vvehicle-Vwind

        # Rotor forces
        if rotor_rpm > 0.:
            self._rotor.calc(rho, vrel, rotor_rpm, theta0)
        else:
            print("Rotor speed is less than or equal to 0. Zeroing torque and power.")
            self._rotor._thrust = 0.
            self._rotor._power = 0.

        # Aerodynamic drag force
        if vrel < 0.:
            # Direction is positive if relative wind is from behind
            self._Fdrag_aero = self._CDb*0.5*rho*vrel**2*self._A
        else:
            # Direction is negative if relative wind is from behind
            self._Fdrag_aero = -self._CDf*0.5*rho*vrel**2*self._A

        # Drag force on wheels needed to turn the rotor (negative since pulling back)
        if rotor_rpm > 0.:
            rotor_om = rotor_rpm*1./60.*2.*pi
            rotor_torque = self._rotor._power/rotor_om
            wheel_torque = rotor_torque/(self._trans*self._eta_trans)
            self._Fdrag_rotor = -wheel_torque/self._rw
        else:
            self._Fdrag_rotor = 0.

        # Rolling resistance (negative since pulling back)
        self._Frr = -self._Crr*self._m*g

        # Return force breakdown
        return {"rotor_thrust": self._rotor._thrust, "aero_drag": self._Fdrag_aero,
                "rotor_drag": self._Fdrag_rotor, "rolling": self._Frr}
