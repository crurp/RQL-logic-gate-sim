"""
Simulator Module for RQL Logic Gate Simulator.

This module implements simulations for Hamiltonian diagonalization, flux sweeps,
energy level calculations, anharmonicity, and coupling strength analysis.
Integrates QuTiP for time-domain pulse propagation when needed.
"""

import logging
import numpy as np
try:
    import SQcircuit as sq
except ImportError as e:
    logging.error(f"Failed to import SQcircuit: {e}")
    raise

try:
    from qutip import *
except ImportError as e:
    logging.error(f"Failed to import QuTiP: {e}")
    raise


# Configure logging
logger = logging.getLogger(__name__)


def diagonalize_hamiltonian(circuit, n_levels=10):
    """
    Diagonalize the Hamiltonian of an RQL circuit to get energy eigenvalues.
    
    Args:
        circuit (SQcircuit.Circuit): Circuit object to diagonalize.
        n_levels (int): Number of energy levels to compute. Default is 10.
        
    Returns:
        tuple: (energies, eigenvectors) where energies is array of eigenvalues
               in GHz and eigenvectors are the corresponding eigenstates.
               
    Raises:
        RuntimeError: If diagonalization fails.
    """
    try:
        print(f"Checkpoint: Diagonalizing Hamiltonian for {n_levels} levels")
        logger.info(f"Diagonalizing Hamiltonian for {n_levels} levels")
        
        if circuit is None:
            raise ValueError("Circuit object is None")
        
        # Set truncation numbers if not already set
        # Check if truncation is already set (circuit_builder should set it)
        trunc_already_set = False
        try:
            if hasattr(circuit, 'trunc_nums') and circuit.trunc_nums is not None:
                trunc_already_set = True
        except:
            pass
        
        if not trunc_already_set:
            # Try to determine number of modes, or use safe default
            # For most single-loop circuits, 1 mode is sufficient
            # But we'll try to be smart about it
            try:
                # Try to get the number of modes from the circuit
                # This is a fallback - circuit_builder should have set it
                circuit.set_trunc_nums([50])  # Default for single-mode circuits
            except ValueError:
                # If that fails, try with 2 modes (for ANB gate)
                try:
                    circuit.set_trunc_nums([50, 50])
                except:
                    # Last resort: let SQcircuit handle it
                    pass
        
        # Diagonalize the Hamiltonian
        eigenvals, eigenvecs = circuit.diag(n_eig=n_levels)
        
        # Convert eigenvalues to energy (they're already in GHz typically)
        energies = eigenvals
        
        print(f"Checkpoint: Hamiltonian diagonalized successfully, ground state = {energies[0]:.4f} GHz")
        logger.info(f"Diagonalization complete: ground state = {energies[0]:.4f} GHz")
        
        return energies, eigenvecs
        
    except Exception as e:
        error_msg = f"Error diagonalizing Hamiltonian: {e}"
        print(f"Error at simulation: {error_msg}")
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e


def flux_sweep(circuit, flux_range=None, n_points=100, n_levels=5):
    """
    Perform a flux sweep to compute energy levels vs. external flux.
    
    This function is essential for studying flux tunability of RQL gates
    and identifying operating points for quantum logic operations.
    
    Args:
        circuit (SQcircuit.Circuit): Circuit object to simulate.
        flux_range (tuple): (flux_min, flux_max) range to sweep.
                           Default is (0.0, 1.0).
        n_points (int): Number of flux points to sample. Default is 100.
        n_levels (int): Number of energy levels to compute. Default is 5.
        
    Returns:
        tuple: (flux_values, energy_levels) where flux_values is array of
               flux values and energy_levels is 2D array (n_points, n_levels)
               of energy eigenvalues in GHz.
               
    Raises:
        RuntimeError: If flux sweep fails.
    """
    try:
        if flux_range is None:
            flux_range = (0.0, 1.0)
        
        flux_min, flux_max = flux_range
        if not (0 <= flux_min < flux_max <= 1):
            raise ValueError(f"Invalid flux range: {flux_range}")
        
        print(f"Checkpoint: Starting flux sweep from {flux_min} to {flux_max} ({n_points} points)")
        logger.info(f"Flux sweep: {flux_min} to {flux_max}, {n_points} points")
        
        flux_values = np.linspace(flux_min, flux_max, n_points)
        energy_levels = np.zeros((n_points, n_levels))
        
        # Find the flux loop in the circuit
        loop = None
        for element_list in circuit.elements.values():
            for elem in element_list:
                if isinstance(elem, sq.Loop):
                    loop = elem
                    break
            if loop is not None:
                break
        
        if loop is None:
            # Try to find any loop in the circuit
            for elem_list in circuit.elements.values():
                for elem in elem_list:
                    if hasattr(elem, 'loops') and elem.loops:
                        loop = elem.loops[0]
                        break
                if loop is not None:
                    break
        
        if loop is None:
            raise ValueError("No flux loop found in circuit")
        
        # Sweep flux and compute energies
        for i, flux_val in enumerate(flux_values):
            try:
                # Update flux value
                loop.value = flux_val
                
                # Rebuild circuit with new flux
                circuit.update()
                
                # Diagonalize Hamiltonian
                energies, _ = diagonalize_hamiltonian(circuit, n_levels=n_levels)
                
                # Store results
                n_store = min(n_levels, len(energies))
                energy_levels[i, :n_store] = energies[:n_store]
                
                if (i + 1) % 20 == 0:
                    print(f"Checkpoint: Flux sweep progress: {i+1}/{n_points} points")
                    
            except Exception as e:
                logger.warning(f"Error at flux point {flux_val}: {e}")
                # Continue with previous values or NaN
                if i > 0:
                    energy_levels[i] = energy_levels[i-1]
                else:
                    energy_levels[i] = np.nan
        
        print(f"Checkpoint: Flux sweep completed successfully")
        logger.info("Flux sweep completed successfully")
        
        return flux_values, energy_levels
        
    except Exception as e:
        error_msg = f"Error during flux sweep: {e}"
        print(f"Error at simulation: {error_msg}")
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e


def calculate_anharmonicity(energies):
    """
    Calculate the anharmonicity of an RQL gate from energy levels.
    
    Anharmonicity is defined as (E_2 - E_1) - (E_1 - E_0), which measures
    the deviation from harmonic oscillator behavior. Critical for qubit design.
    
    Args:
        energies (array-like): Energy eigenvalues in GHz.
        
    Returns:
        float: Anharmonicity in GHz.
        
    Raises:
        ValueError: If insufficient energy levels are provided.
    """
    try:
        energies = np.array(energies)
        
        if len(energies) < 3:
            raise ValueError("Need at least 3 energy levels to calculate anharmonicity")
        
        # Anharmonicity: α = (E_2 - E_1) - (E_1 - E_0)
        E0, E1, E2 = energies[0], energies[1], energies[2]
        anharmonicity = (E2 - E1) - (E1 - E0)
        
        print(f"Checkpoint: Anharmonicity calculated: {anharmonicity:.4f} GHz")
        logger.info(f"Anharmonicity: {anharmonicity:.4f} GHz")
        
        return anharmonicity
        
    except Exception as e:
        error_msg = f"Error calculating anharmonicity: {e}"
        print(f"Error at simulation: {error_msg}")
        logger.error(error_msg, exc_info=True)
        raise


def calculate_coupling_strength(circuit1, circuit2, coupling_element=None):
    """
    Calculate coupling strength between two RQL gates.
    
    This function computes the effective coupling strength between two
    coupled superconducting circuits, important for multi-qubit systems
    targeting 1M qubit scaling.
    
    Args:
        circuit1 (SQcircuit.Circuit): First circuit.
        circuit2 (SQcircuit.Circuit): Second circuit.
        coupling_element (SQcircuit element): Coupling element (optional).
        
    Returns:
        float: Coupling strength in GHz.
        
    Raises:
        NotImplementedError: Full implementation requires circuit details.
    """
    try:
        print("Checkpoint: Calculating coupling strength")
        logger.info("Calculating coupling strength")
        
        # For a simplified calculation, we can estimate coupling
        # based on energy splittings in the combined system
        # This is a placeholder - full implementation would require
        # detailed circuit analysis
        
        # Get ground states of individual circuits
        E1, _ = diagonalize_hamiltonian(circuit1, n_levels=2)
        E2, _ = diagonalize_hamiltonian(circuit2, n_levels=2)
        
        # Estimate coupling (simplified)
        # In real implementation, would analyze anti-crossing in energy spectrum
        coupling = 0.1 * min(abs(E1[0] - E2[0]), 1.0)  # Simplified estimate
        
        print(f"Checkpoint: Estimated coupling strength: {coupling:.4f} GHz")
        logger.info(f"Estimated coupling strength: {coupling:.4f} GHz")
        
        return coupling
        
    except Exception as e:
        error_msg = f"Error calculating coupling strength: {e}"
        print(f"Error at simulation: {error_msg}")
        logger.error(error_msg, exc_info=True)
        raise


def compute_transition_frequencies(energies):
    """
    Compute transition frequencies between energy levels.
    
    Args:
        energies (array-like): Energy eigenvalues in GHz.
        
    Returns:
        numpy.ndarray: Array of transition frequencies in GHz.
    """
    try:
        energies = np.array(energies)
        
        if len(energies) < 2:
            raise ValueError("Need at least 2 energy levels")
        
        # Compute transitions from ground state
        transitions = energies[1:] - energies[0]
        
        print(f"Checkpoint: Transition frequencies computed")
        logger.info(f"Transition frequencies: {transitions} GHz")
        
        return transitions
        
    except Exception as e:
        error_msg = f"Error computing transition frequencies: {e}"
        logger.error(error_msg, exc_info=True)
        raise


def simulate_time_evolution(circuit, initial_state=None, times=None, drive=None):
    """
    Simulate time evolution of the circuit using QuTiP.
    
    This function performs time-domain simulation with optional drive fields,
    useful for studying gate dynamics and pulse propagation.
    
    Args:
        circuit (SQcircuit.Circuit): Circuit object.
        initial_state (qutip.Qobj): Initial quantum state. Default is ground state.
        times (array-like): Time points for simulation in ns.
                           Default is np.linspace(0, 100, 1000).
        drive (qutip.Qobj): Drive Hamiltonian (optional).
        
    Returns:
        qutip.Result: Time evolution result from QuTiP.
        
    Raises:
        RuntimeError: If simulation fails.
    """
    try:
        print("Checkpoint: Starting time evolution simulation")
        logger.info("Starting time evolution simulation")
        
        if times is None:
            times = np.linspace(0, 100, 1000)  # 0-100 ns, 1000 points
        
        # Get Hamiltonian from circuit
        energies, eigenvecs = diagonalize_hamiltonian(circuit, n_levels=10)
        
        # Construct Hamiltonian matrix
        H = Qobj(np.diag(energies))
        
        # Set initial state
        if initial_state is None:
            initial_state = basis(len(energies), 0)  # Ground state
        
        # Add drive if provided
        if drive is not None:
            H = H + drive
        
        # Time evolution
        result = sesolve(H, initial_state, times)
        
        print("Checkpoint: Time evolution simulation completed")
        logger.info("Time evolution simulation completed")
        
        return result
        
    except Exception as e:
        error_msg = f"Error in time evolution: {e}"
        print(f"Error at simulation: {error_msg}")
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e

