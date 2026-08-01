import math
import numpy as np
import matplotlib.pyplot as plt
import argparse

# Core Constants
c = 3e8  # Speed of light in m/s

def calculate_patch_dimensions(f, er, height):
    """Calculates physical dimensions of a rectangular microstrip patch antenna."""
    W = (c / (2 * f)) * math.sqrt(2 / (er + 1))
    W_h = W / height
    e_reff = ((er + 1) / 2) + ((er - 1) / 2) * (1 / math.sqrt(1 + 12 * (1 / W_h)))
    delta_L = 0.412 * height * ((e_reff + 0.3) * (W_h + 0.264)) / ((e_reff - 0.258) * (W_h + 0.8))
    L_eff = c / (2 * f * math.sqrt(e_reff))
    L = L_eff - (2 * delta_L)
    return W, L, e_reff

def calculate_array_factor(num_elements, spacing, freq, steer_angle_deg, bend_radius=0):
    """
    Calculates the 2D radiation pattern of a flat or conformal (curved) linear array.
    bend_radius: Radius of the cylinder in meters. 0 means perfectly flat.
    """
    lambda_0 = c / freq
    beta = 2 * np.pi / lambda_0
    steer_rad = np.radians(steer_angle_deg)
    
    # 360 degrees of observation points
    theta = np.linspace(-np.pi, np.pi, 720) 
    
    AF = np.zeros_like(theta, dtype=complex)
    
    for n in range(num_elements):
        # 1. Physical placement of element n
        # Center the array at n=0 for symmetry
        n_centered = n - (num_elements - 1) / 2
        arc_length = n_centered * spacing
        
        if bend_radius == 0:
            # Flat Array (lies on the X-axis)
            x_n = arc_length
            z_n = 0
            element_tilt = 0
        else:
            # Conformal Array (wrapped around a cylinder)
            # Element angle around the cylinder
            gamma_n = arc_length / bend_radius 
            x_n = bend_radius * np.sin(gamma_n)
            # Shifted so the center of the array touches z=0
            z_n = bend_radius * np.cos(gamma_n) - bend_radius 
            element_tilt = gamma_n
            
        # 2. Calculate phase excitation to steer the beam
        # We apply a phase shift (alpha) to compensate for spatial delays and curvature
        alpha_n = -beta * (x_n * np.sin(steer_rad) + z_n * np.cos(steer_rad))
        
        # 3. Element Factor (Patch antennas radiate mostly forward, modelled roughly as cos(theta))
        # For conformal arrays, each element points in a different direction!
        local_theta = theta - element_tilt
        element_factor = np.cos(local_theta)
        element_factor[np.abs(local_theta) > np.pi/2] = 0 # No backlobe radiation for ideal patch on ground plane
        
        # 4. Superposition: Add this element's wave to the total field
        phase_contribution = beta * (x_n * np.sin(theta) + z_n * np.cos(theta)) + alpha_n
        AF += element_factor * np.exp(1j * phase_contribution)

    # Normalize and convert to dB
    AF_mag = np.abs(AF)
    AF_norm = AF_mag / np.max(AF_mag)
    AF_dB = 20 * np.log10(AF_norm + 1e-10)
    AF_dB = np.clip(AF_dB, -40, 0)
    
    return theta, AF_dB

def plot_pattern(theta, AF_dB, title):
    """Plots the radiation pattern in polar coordinates."""
    plt.figure(figsize=(8, 6))
    ax = plt.subplot(111, projection='polar')
    ax.plot(theta, AF_dB, color='blue', linewidth=2)
    # Configure polar plot so 0 degrees (broadside) points UP
    ax.set_theta_zero_location("N") 
    ax.set_theta_direction(-1)      
    ax.set_ylim(-40, 0)             
    ax.set_yticks([-30, -20, -10, 0])
    ax.set_title(title, fontsize=12, pad=20)
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AeroArray-6G: Conformal Antenna Synthesis")
    parser.add_argument('-f', '--frequency', type=float, default=140.0, help="Frequency in GHz (default: 140)")
    parser.add_argument('-er', '--epsilon', type=float, default=3.0, help="Substrate permittivity (default: 3.0)")
    parser.add_argument('-th', '--thickness', type=float, default=0.1, help="Substrate thickness in mm (default: 0.1)")
    parser.add_argument('-n', '--elements', type=int, default=8, help="Number of elements (default: 8)")
    parser.add_argument('-s', '--steer', type=float, default=0.0, help="Beam steering angle in degrees (default: 0)")
    parser.add_argument('-r', '--radius', type=float, default=0.0, help="Conformal bending radius in mm. 0 = flat (default: 0)")
    
    args = parser.parse_args()

    f_r = args.frequency * 1e9
    lambda_0 = c / f_r
    h = args.thickness * 1e-3
    bend_radius_m = args.radius * 1e-3
    
    print("==================================================")
    print(f"   AeroArray-6G: Conformal Array Synthesis ({args.frequency} GHz)")
    print("==================================================")
    
    W, L, e_reff = calculate_patch_dimensions(f_r, args.epsilon, h)
    spacing = lambda_0 / 2 # Standard half-wavelength spacing
    
    print(f"\n--- Physical Dimensions ---")
    print(f"  Patch Width (W)          : {W*1000:.4f} mm")
    print(f"  Patch Length (L)         : {L*1000:.4f} mm")
    print(f"  Element Spacing (d)      : {spacing*1000:.4f} mm")
    
    print(f"\n--- Array Parameters ---")
    print(f"  Elements (N)             : {args.elements}")
    print(f"  Target Scan Angle        : {args.steer}°")
    
    if args.radius > 0:
        print(f"  Geometry                 : CONFORMAL (Cylindrical)")
        print(f"  Bending Radius (R)       : {args.radius} mm")
        title = f"{args.elements}-Element Conformal Array (R={args.radius}mm)\nSteered to {args.steer}° at {args.frequency} GHz"
    else:
        print(f"  Geometry                 : FLAT (Planar)")
        title = f"{args.elements}-Element Flat Array\nSteered to {args.steer}° at {args.frequency} GHz"
        
    print("\nGenerating Phase-Compensated Radiation Pattern...")
    theta, AF_dB = calculate_array_factor(args.elements, spacing, f_r, args.steer, bend_radius_m)
    plot_pattern(theta, AF_dB, title)