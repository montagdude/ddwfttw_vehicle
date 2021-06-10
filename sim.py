#!/usr/bin/env python
# Direct downwind faster than the wind vehicle simulation
#
import os
from math import pi
import numpy as np
from matplotlib import pyplot as plt
from airfoil import Airfoil
from blade import Blade
from rotor import Rotor
from vehicle import Vehicle
from rk4 import RK4

ddwfttw_vehicle = None
Vwind = None
rho = None
g = None
v_schedule = None
collective_schedule = None

# Equation of motion
# Inputs:
#   t: time
#   x: np.array([position, velocity])
#   (global) ddwfttw_vehicle
#   (global) Vwind
#   (global) rho: air density
#   (global) g: acceleration due to gravity
#   (global) v_schedule: vehicle speeds for interpolating collective
#   (global) collective_schedule: collective pitch at the speeds in v_schedule
# Returns:
#   xdot: np.array([velocity, acceleration])
def motion(t, x):
    global ddwfttw_vehicle
    global Vwind
    global rho
    global g
    global v_schedule
    global collective_schedule

    # Set vehicle velocity
    ddwfttw_vehicle.setSpeed(x[1])

    # Get collective pitch from schedule
    theta0 = np.interp(x[1], v_schedule, collective_schedule)
    forces = ddwfttw_vehicle.computeForces(Vwind, rho, theta0, g)
    f = sum(forces.values())

    # Equations of motion
    xdot = np.zeros((2))
    xdot[0] = x[1]
    xdot[1] = f/ddwfttw_vehicle._m

    return xdot

if __name__ == "__main__":
    # Conversion factors
    lbm2slug = 1./32.174
    mph2fps = 5280./3600.
    kg2slug = 0.06852177
    m2in = 1./0.0254
    in2ft = 1./12.

    # Vehicle parameters:
    #   wheel_radius: wheel radius (ft)
    #   gear_ratio: ratio of wheel rpm to prop rpm
    #   gear_efficiency: transmission efficiency
    #   CDf: drag coefficient for air flowing over the vehicle from front to back
    #   CDb: drag coefficient for air flowing over the vehicle from back to front
    #   Crr: coefficient of rolling resistance
    #   A: projected frontal area (sq ft)
    #   m: total vehicle mass (slug)
    wheel_radius = 1.25
    gear_ratio = 1.5
    gear_efficiency = 0.85
    CDf = 0.3
    CDb = 0.4
    Crr = 0.01
    A = 20.
    m = 650.*lbm2slug

    # Wind speed (ft/sec) (positive tailwind)
    Vwind = 10.*mph2fps

    # Air density (slug/ft^3)
    rho = 1.225*kg2slug/(m2in**3)/(in2ft**3)

    # Acceleration due to gravity
    g = 32.174

    # NACA 0012 airfoil
    airfoil = Airfoil()
    airfoil.readClCdTables(os.path.join("airfoil_tables","naca6412.cltable"),
                           os.path.join("airfoil_tables","naca6412.cdtable"))

    # Rotor blade parameters
    radial = [1., 2.5, 3.5, 8.75]   # Radial stations (ft)
    chord = [0.2, 1.1, 1.2, 0.3]  # Chord (ft)
    twist = [26., 18., 16., 8.0]      # Twist (deg)
    blade = Blade(radial, chord, twist, airfoil)
    blade.plotChord()
    blade.plotTwist()

    # Rotor
    rotor = Rotor(blade, 2)
    rotor.discretize(100)

    # collective schedule based on vehicle speed
    v_schedule = np.array([0.5, 0.8, 1.0, 1.5, 2.0, 2.2, 2.5, 2.6])*Vwind
    collective_schedule = np.array([0., 2., 4., 6., 8., 9., 9., 9.])

    # Vehicle
    ddwfttw_vehicle = Vehicle(wheel_radius, gear_ratio, gear_efficiency, CDf, CDb, Crr, A, m,
                              rotor)
    initial_speed = 0.5*Vwind       # Initial condition. Start rolling at half the wind
                                    # speed since rotor model loses accuracy below V.

    # Initialize some arrays for plotting later
    time = []
    position = []
    speed = []
    theta0 = []
    thrust = []
    fdrag_aero = []
    fdrag_rotor = []
    frolling_resistance = []

    # Run the DDWFTTW simulation and store some things to plot later
    maxsteps = 1000
    dt = 0.5
    initial_condition = np.array([0.0, initial_speed])
    integrator = RK4(motion, 0.0, initial_condition, dt)
    for i in range(maxsteps):
        integrator.step()
        time.append(integrator.t)
        position.append(integrator.y[0])
        speed.append(integrator.y[1]/mph2fps)
        theta0.append(np.interp(integrator.y[1], v_schedule, collective_schedule))
        thrust.append(ddwfttw_vehicle._rotor._thrust)
        fdrag_aero.append(ddwfttw_vehicle._Fdrag_aero)
        fdrag_rotor.append(ddwfttw_vehicle._Fdrag_rotor)
        frolling_resistance.append(ddwfttw_vehicle._Frr)
        print("Time step {:d}, time = {:.1f}, speed = {:.2f} mph"\
              .format(i+1, integrator.t, integrator.y[1]/mph2fps))

        # Kick out early if net force becomes <= 0. That means we can't go any faster.
        net = thrust[i] + fdrag_aero[i] + fdrag_rotor[i] + frolling_resistance[i]
        if net <= 0.:
            print("Max speed reached!")
            break

    # Plot
    fig, ax = plt.subplots(figsize=(10,6))
    ax.set_xlabel("Time (sec)")
    ax.set_ylabel("Position (ft)")
    ax.plot(time, position)
    ax.grid()
    fig.savefig("position.png", bbox_inches="tight")

    plt.clf()
    plt.close()
    fig, ax = plt.subplots(figsize=(10,6))
    ax.set_xlabel("Time (sec)")
    ax.set_ylabel("Speed (mph)")
    ax.plot([time[0], time[-1]], [Vwind/mph2fps, Vwind/mph2fps])
    ax.plot(time, speed)
    ax.grid()
    ax.legend(["Wind", "Vehicle"])
    fig.savefig("speed.png", bbox_inches="tight")

    plt.clf()
    plt.close()
    fig, ax = plt.subplots(figsize=(10,6))
    ax.set_xlabel("Time (sec)")
    ax.set_ylabel("Collective pitch (deg)")
    ax.plot(time, theta0)
    ax.grid()
    fig.savefig("collective.png", bbox_inches="tight")

    plt.clf()
    plt.close()
    fig, ax = plt.subplots(figsize=(10,6))
    ax.set_xlabel("Time (sec)")
    ax.set_ylabel("Vehicle forces (lbf)")
    ax.plot(time, thrust)
    ax.plot(time, fdrag_aero)
    ax.plot(time, fdrag_rotor)
    ax.plot(time, frolling_resistance)
    ax.grid()
    ax.legend(["Rotor thrust", "Frame drag", "Drag to spin rotor", "Rolling resistance"])
    fig.savefig("forces.png", bbox_inches="tight")
