import os
from rotor import Rotor
from blade import Blade
from airfoil import Airfoil
from matplotlib import pyplot as plt

# Simulation of rotor from NACA-TN-626
if __name__ == "__main__":
    # Load NACA 0015 airfoil data
    foil = Airfoil()
    foil.readTables([os.path.join("airfoil_tables", "naca0015.table1"),
                     os.path.join("airfoil_tables", "naca0015.table2")])

    # Blade
    radial = [1.5, 5., 30.]
    chord = [0.75, 2., 2.]
    twist = [0., 0., 0.]
    blade = Blade(radial, chord, twist, foil)
    blade.plotChord()

    # Set up rotor
    nblades = 5
    nstrips = 100
    rotor = Rotor(blade, nblades)
    rotor.discretize(nstrips)

    # Air density, convert from kg/m^3 to snail/in^3
    kg2slug = 0.06852177
    m2in = 1./0.0254
    slug2snail = 1./12.
    in2ft = 1./12.
    rho = 1.225*kg2slug/(m2in**3)*slug2snail

    # Solve
    V = 0.
    rpm = 960.
    theta0 = [float(i)*0.5 for i in range(25)]
    theta0[0] = 0.1
    CT = []
    CP = []
    for th in theta0:
        print("theta: {:0.1f}".format(th))
        rotor.calc(rho, V, rpm, th)
        CT.append(rotor._CT)
        CP.append(rotor._CP)

    # From Table IV in NACA-TN-262. Note that the numbers from the table have been
    # halved since their convention for CT and CP is double the one used here.
    tn262_theta0 = [0., 2., 4., 6., 8., 10., 12.]
    tn262_ct = [0, 0.0005905, 0.00181, 0.00347, 0.005515, 0.00774, 0.01]
    tn262_cp = [0.000119, 0.000135, 0.000198, 0.00034, 0.000543, 0.0008175, 0.00114]

    # Plot
    fig, ax = plt.subplots()
    ax.set_xlabel("Collective pitch (deg)")
    ax.set_ylabel("Thrust coefficient")
    ax.plot(theta0, CT)
    ax.plot(tn262_theta0, tn262_ct, 'o')
    ax.grid()
    ax.legend(["Blade element model", "NACA-TN-262"])
    fig.savefig("validation_ct.png", bbox_inches="tight")

    plt.clf()
    plt.close()
    fig, ax = plt.subplots()
    ax.set_xlabel("Collective pitch (deg)")
    ax.set_ylabel("Power coefficient")
    ax.plot(theta0, CP)
    ax.plot(tn262_theta0, tn262_cp, 'o')
    ax.grid()
    ax.legend(["Blade element model", "NACA-TN-262"])
    fig.savefig("validation_cp.png", bbox_inches="tight")
