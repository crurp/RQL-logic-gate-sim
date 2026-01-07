"""
Main Entry Point for RQL Logic Gate Simulator.

This script provides a command-line interface for running RQL gate simulations.
It demonstrates basic usage of the circuit builder and simulator modules.
"""

import sys
import os
import argparse

# Add src directory to path
base_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(base_dir, 'src')
sys.path.insert(0, base_dir)
sys.path.insert(0, src_dir)

from src import circuit_builder
from src import simulator
from src import utils


def main():
    """
    Main function to run RQL gate simulations from command line.
    """
    parser = argparse.ArgumentParser(
        description='RQL Logic Gate Simulator - Command Line Interface'
    )
    parser.add_argument(
        '--gate', 
        type=str, 
        choices=['inverter', 'anb', 'loop'],
        default='inverter',
        help='Type of RQL gate to simulate (default: inverter)'
    )
    parser.add_argument(
        '--Ej', 
        type=float, 
        default=10.0,
        help='Josephson energy in GHz (default: 10.0)'
    )
    parser.add_argument(
        '--Ec', 
        type=float, 
        default=0.2,
        help='Charging energy in GHz (default: 0.2)'
    )
    parser.add_argument(
        '--flux', 
        type=float, 
        default=0.5,
        help='Flux bias in units of flux quantum (default: 0.5)'
    )
    parser.add_argument(
        '--n-levels', 
        type=int, 
        default=10,
        help='Number of energy levels to compute (default: 10)'
    )
    parser.add_argument(
        '--flux-sweep', 
        action='store_true',
        help='Perform flux sweep instead of single-point calculation'
    )
    parser.add_argument(
        '--n-points', 
        type=int, 
        default=100,
        help='Number of flux points for sweep (default: 100)'
    )
    parser.add_argument(
        '--output', 
        type=str, 
        default=None,
        help='Output directory for plots (default: current directory)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    utils.setup_logging()
    
    print("=" * 60)
    print("RQL Logic Gate Simulator")
    print("=" * 60)
    print(f"Gate type: {args.gate}")
    print(f"Ej = {args.Ej} GHz")
    print(f"Ec = {args.Ec} GHz")
    print(f"Flux = {args.flux} Φ₀")
    print("=" * 60)
    
    try:
        # Build circuit
        print("\n[1/3] Building circuit...")
        if args.gate == 'inverter':
            circuit = circuit_builder.build_rql_inverter(
                Ej=args.Ej, Ec=args.Ec, flux=args.flux
            )
        elif args.gate == 'anb':
            circuit = circuit_builder.build_anb_gate(
                Ej1=args.Ej, Ej2=args.Ej, Ec=args.Ec, flux1=args.flux, flux2=args.flux
            )
        elif args.gate == 'loop':
            circuit = circuit_builder.build_rql_loop(
                Ej=args.Ej, Ec=args.Ec, flux=args.flux
            )
        
        print("Checkpoint: Circuit built successfully")
        
        # Run simulation
        if args.flux_sweep:
            print("\n[2/3] Performing flux sweep...")
            flux_values, energy_levels = simulator.flux_sweep(
                circuit, 
                flux_range=(0.0, 1.0),
                n_points=args.n_points,
                n_levels=args.n_levels
            )
            
            print("Checkpoint: Flux sweep completed successfully")
            
            # Plot results
            print("\n[3/3] Plotting results...")
            fig = utils.plot_flux_sweep(
                flux_values, 
                energy_levels,
                title=f"{args.gate.upper()} Gate - Energy vs Flux"
            )
            
            if args.output:
                os.makedirs(args.output, exist_ok=True)
                save_path = os.path.join(args.output, f"{args.gate}_flux_sweep.png")
            else:
                save_path = f"{args.gate}_flux_sweep.png"
            
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Checkpoint: Results saved to {save_path}")
            
        else:
            print("\n[2/3] Diagonalizing Hamiltonian...")
            energies, _ = simulator.diagonalize_hamiltonian(
                circuit, 
                n_levels=args.n_levels
            )
            
            print("Checkpoint: Hamiltonian diagonalized successfully")
            print(f"\nEnergy Levels ({args.n_levels} levels):")
            for i, E in enumerate(energies[:min(10, len(energies))]):
                print(f"  Level {i}: {E:.4f} GHz")
            
            # Calculate metrics
            print("\n[3/3] Calculating gate metrics...")
            metrics = utils.calculate_gate_metrics(energies)
            
            print("\nGate Metrics:")
            print(f"  Ground state energy: {metrics['ground_state_energy']:.4f} GHz")
            if metrics['transition_frequency']:
                print(f"  Transition frequency: {metrics['transition_frequency']:.4f} GHz")
            if metrics['anharmonicity']:
                print(f"  Anharmonicity: {metrics['anharmonicity']:.4f} GHz")
            
            # Plot spectrum
            fig = utils.plot_energy_spectrum(
                energies,
                title=f"{args.gate.upper()} Gate - Energy Spectrum"
            )
            
            if args.output:
                os.makedirs(args.output, exist_ok=True)
                save_path = os.path.join(args.output, f"{args.gate}_spectrum.png")
            else:
                save_path = f"{args.gate}_spectrum.png"
            
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Checkpoint: Results saved to {save_path}")
        
        print("\n" + "=" * 60)
        print("Simulation completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError: {e}")
        print("Check simulation_errors.log for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()

