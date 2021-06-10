# ddwfttw_vehicle
Dead downwind faster than the wind vehicle simulation

This simulation is loosely based on the world-record-holding Blackbird vehicle.
Four forces act on the vehicle:
* Rotor thrust
* Drag due to transmission (the wheels power the rotor)
* Frame drag due to air flow over the vehicle
* Rolling resistance

I could not find detailed specifications for the vehicle, so I had to estimate most of the parameters. Available information included the rotor diameter and airfoil. The rotor is definitely note completely optimized, but I did spend some time tweaking it to try to get a positive net force over the largest speed range I could.

The main simulation script is sim.py. Python with matplotlib and numpy are required to run it. Note that the code is not at all optimized for speed.

The rotor model is based on blade element theory combined with momentum theory to iteratively calculate the correct induced flow through the disk. This model is strictly not valid when the vehicle is moving less than the wind speed, but the accuracy increases as it gets close to that state. Due to this limitation, the simulation starts off with the vehicle moving at half the wind speed instead of at rest.

With a tail wind of 10 mph the simulated vehicle eventually reaches 26.5 mph, which is pretty close to the record of 27.7 mph. Of course, this could be easily improved in the simulation by reducing the sources of drag or removing simulated inefficiencies, but I wanted it to be as realistic as possible.
