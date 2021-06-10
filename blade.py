from matplotlib import pyplot as plt
import numpy as np
from airfoil import Airfoil
from copy import copy

class Blade:
    # Inputs:
    #   radial:  list of radial stations (dimensional, in ascending order)
    #   chord:   list of chord at each radial station
    #   twist:   list of twist at each radial station
    #   airfoil: blade airfoil (assumed the same everywhere)
    def __init__(self, radial, chord, twist, airfoil):
        self._radial = radial
        self._chord = chord
        self._twist = twist
        self._airfoil = airfoil

    # Returns inner radius
    def innerRadius(self):
        return self._radial[0]

    # Returns outer radius
    def outerRadius(self):
        return self._radial[-1]

    # Interpolates chord at given radial location
    def chord(self, r):
        return np.interp(r, self._radial, self._chord)

    # Interpolates twist at given radial location
    def twist(self, r):
        return np.interp(r, self._radial, self._twist)

    # Plots chord distribution
    def plotChord(self):
        xLE = [0.0]
        xTE = []
        for i in range(len(self._radial)):
            if i > 0:
                xLE.append(xLE[i-1] + 0.5*(self._chord[i]-self._chord[i-1]))
            xTE.append(xLE[i] - self._chord[i])
        xLoop = copy(xLE)
        xLoop.extend(xTE[::-1])
        xLoop.append(xLE[0])
        rLoop = copy(self._radial)
        rLoop.extend(self._radial[::-1])
        rLoop.append(self._radial[0])

        fig, ax = plt.subplots()
        ax.set_title("Blade geometry")
        ax.set_xlabel("Radial location")
        ax.set_ylabel("Chord")
        ax.plot(rLoop, xLoop)
        ax.set_aspect('equal','datalim')
        fig.savefig("chord.png", bbox_inches="tight")

    # Plots twist distribution
    def plotTwist(self):
        fig, ax = plt.subplots()
        ax.set_title("Blade twist")
        ax.set_xlabel("Radial location")
        ax.set_ylabel("Twist (deg)")
        ax.plot(self._radial, self._twist)
        fig.savefig("twist.png", bbox_inches="tight")
