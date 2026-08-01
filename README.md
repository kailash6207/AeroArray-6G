AeroArray-6G: Conformal Array Synthesis (sub-THz)

A Python-based toolkit for calculating and synthesizing the dimensions and radiation patterns of millimeter-wave (mmWave) and sub-terahertz microstrip antenna arrays. This project is specifically designed to tackle the hardware challenges of 6G UAV and V2X applications, including electronic beam steering and conformal (curved) geometries.

Features

Microstrip Transmission Line Calculator: Precisely calculates Patch Width ($W$) and Length ($L$) for high-frequency microstrip antennas, accounting for fringing fields on ultra-thin substrates (like LCP).

Vector-based Array Factor Synthesis: Calculates the radiation pattern using discrete summation, allowing for arbitrary placement of elements in 2D space.

Realistic Element Factors: Incorporates directional element radiation patterns ($\cos(\theta)$), preventing unrealistic isotropic assumptions.

Phase-Controlled Beam Steering: Calculates the necessary progressive phase shifts to steer the main beam to a target angle ($\theta_0$).

Conformal Phase Compensation: Maps the linear array onto a cylindrical surface (representing a drone fuselage or car chassis) and computes the exact phase-weighting required to focus a beam from a curved surface.

Requirements

Python 3.x

NumPy

Matplotlib

Install dependencies:

pip install numpy matplotlib


Usage and Parameters

You can run the script via the command line to simulate various physical and electrical states.

Basic Flat Array (Default):

python antenna_calculator.py 


Beam Steering (Tracking a target at 30 degrees):

python antenna_calculator.py --steer 30


Conformal Array (Wrapped around a 15mm drone arm, steered to -15 degrees):

python antenna_calculator.py --elements 12 --radius 15 --steer -15


Full CLI Arguments:

-f, --frequency: Target frequency in GHz (default: 140.0)

-er, --epsilon: Substrate relative permittivity (default: 3.0 for LCP)

-th, --thickness: Substrate thickness in millimeters (default: 0.1)

-n, --elements: Number of elements in the linear array (default: 8)

-s, --steer: Target beam steering angle in degrees (default: 0)

-r, --radius: Conformal bending radius in mm. Set to 0 for a flat array (default: 0).

Why Conformal Phase Compensation Matters

When wrapping a standard array around a cylinder, elements point in different directions and sit at different depths relative to the wavefront. Without compensation, the main beam broadens significantly and loses peak gain (directivity). This script automatically projects the coordinates $(X_n, Z_n)$ of each element and applies a phase shift $\alpha_n$ to theoretically reconstruct a focused beam, proving the mathematical viability of the array before 3D EM simulation in CST/HFSS.

License

MIT License