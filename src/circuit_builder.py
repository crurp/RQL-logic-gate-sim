"""
Circuit Builder Module for RQL Logic Gate Simulator.

This module provides functions to define RQL (Reciprocal Quantum Logic) gates
using SQcircuit's API. It includes functionality to build superconducting
circuits with Josephson junctions, capacitors, inductors, and flux biasing.
"""

import logging
import numpy as np
try:
    import SQcircuit as sq
except ImportError as e:
    logging.error(f"Failed to import SQcircuit: {e}")
    raise


# Configure logging
logger = logging.getLogger(__name__)


def validate_flux(flux):
    """
    Validate that flux value is within acceptable range (0 to 1).
    
    Args:
        flux (float): Flux value in units of flux quantum.
        
    Returns:
        bool: True if valid, False otherwise.
        
    Raises:
        ValueError: If flux is outside valid range.
    """
    try:
        flux = float(flux)
        if not (0 <= flux <= 1):
            raise ValueError(f"Flux must be between 0 and 1, got {flux}")
        return True
    except (TypeError, ValueError) as e:
        logger.error(f"Invalid flux value: {e}")
        raise


def validate_energy(energy, name="Energy"):
    """
    Validate that energy value is positive and reasonable.
    
    Args:
        energy (float): Energy value in GHz.
        name (str): Name of the parameter for error messages.
        
    Returns:
        bool: True if valid, False otherwise.
        
    Raises:
        ValueError: If energy is negative or invalid.
    """
    try:
        energy = float(energy)
        if energy <= 0:
            raise ValueError(f"{name} must be positive, got {energy}")
        if energy > 1000:  # Reasonable upper limit for GHz
            logger.warning(f"{name} value {energy} GHz seems unusually high")
        return True
    except (TypeError, ValueError) as e:
        logger.error(f"Invalid {name} value: {e}")
        raise


def build_rql_inverter(Ej=10.0, Ec=0.2, flux=0.5, ng=0.0):
    """
    Build a basic RQL inverter gate circuit.
    
    An RQL inverter consists of a superconducting loop with a Josephson
    junction, capacitor, and flux biasing. This function creates a simple
    single-junction circuit for demonstration.
    
    Args:
        Ej (float): Josephson energy in GHz. Default is 10.0 GHz.
        Ec (float): Charging energy in GHz. Default is 0.2 GHz.
        flux (float): External flux bias in units of flux quantum (0-1).
                      Default is 0.5.
        ng (float): Gate charge offset. Default is 0.0.
        
    Returns:
        SQcircuit.Circuit: Configured circuit object for the inverter.
        
    Raises:
        ValueError: If input parameters are invalid.
    """
    try:
        print(f"Checkpoint: Building RQL inverter with Ej={Ej} GHz, Ec={Ec} GHz, flux={flux}")
        logger.info(f"Building RQL inverter: Ej={Ej} GHz, Ec={Ec} GHz, flux={flux}")
        
        # Validate inputs
        validate_energy(Ej, "Ej")
        validate_energy(Ec, "Ec")
        validate_flux(flux)
        
        # Create a simple single-loop circuit with Josephson junction
        # This represents a basic RQL inverter gate
        # For SQcircuit, we need to ensure loops are properly closed
        loop1 = sq.Loop(value=flux)
        
        # Josephson junction with energy Ej (in GHz)
        # Try without unit parameter first, as SQcircuit version may vary
        try:
            JJ = sq.Junction(value=Ej, loops=[loop1], unit="GHz")
            C = sq.Capacitor(value=1/(2*Ec), unit="GHz")
        except TypeError:
            # Fallback if unit parameter not supported
            JJ = sq.Junction(value=Ej, loops=[loop1])
            C = sq.Capacitor(value=1/(2*Ec))
        
        # Create circuit elements dictionary
        # Elements connect nodes (0, 1) where 0 is ground
        # For a simple loop, we connect 0->1 and need to close the loop
        elements = {
            (0, 1): [JJ, C],
        }
        
        # Build the circuit
        # SQcircuit may require explicit loop closure or different topology
        try:
            cr = sq.Circuit(elements)
            cr.set_trunc_nums([50])  # Set truncation for charge basis
        except ValueError as e:
            # If basic topology fails, try alternative approach
            logger.warning(f"Standard topology failed: {e}, trying alternative")
            # Alternative: use a simple LC oscillator model
            # This is a fallback that should work with SQcircuit
            raise ValueError(
                f"Circuit topology may need adjustment for SQcircuit version. "
                f"Original error: {e}. "
                f"Please check SQcircuit documentation for proper loop closure."
            )
        
        # Set gate charge
        if ng != 0:
            cr.set_trunc_nums([50])  # Truncation for charge basis
            cr.set_charge_offset([ng])
        
        print("Checkpoint: Circuit built successfully")
        logger.info("RQL inverter circuit built successfully")
        
        return cr
        
    except Exception as e:
        error_msg = f"Error building RQL inverter: {e}"
        print(f"Error at circuit building: {error_msg}")
        logger.error(error_msg, exc_info=True)
        raise


def build_anb_gate(Ej1=10.0, Ej2=10.0, Ec=0.2, J=0.5, flux1=0.5, flux2=0.5):
    """
    Build an A-NOT-B (ANB) RQL gate circuit.
    
    The ANB gate consists of two coupled superconducting loops with
    Josephson junctions. This is a more complex gate that demonstrates
    RQL logic functionality.
    
    Args:
        Ej1 (float): Josephson energy of first junction in GHz.
                     Default is 10.0 GHz.
        Ej2 (float): Josephson energy of second junction in GHz.
                     Default is 10.0 GHz.
        Ec (float): Charging energy in GHz. Default is 0.2 GHz.
        J (float): Coupling strength between loops in GHz.
                   Default is 0.5 GHz.
        flux1 (float): External flux bias for first loop (0-1).
                       Default is 0.5.
        flux2 (float): External flux bias for second loop (0-1).
                       Default is 0.5.
        
    Returns:
        SQcircuit.Circuit: Configured circuit object for the ANB gate.
        
    Raises:
        ValueError: If input parameters are invalid.
    """
    try:
        print(f"Checkpoint: Building ANB gate with Ej1={Ej1}, Ej2={Ej2}, J={J} GHz")
        logger.info(f"Building ANB gate: Ej1={Ej1}, Ej2={Ej2}, J={J} GHz")
        
        # Validate inputs
        validate_energy(Ej1, "Ej1")
        validate_energy(Ej2, "Ej2")
        validate_energy(Ec, "Ec")
        validate_flux(flux1)
        validate_flux(flux2)
        
        # Create two flux loops
        loop1 = sq.Loop(value=flux1)
        loop2 = sq.Loop(value=flux2)
        
        # Josephson junctions (in GHz)
        JJ1 = sq.Junction(value=Ej1, loops=[loop1], unit="GHz")
        JJ2 = sq.Junction(value=Ej2, loops=[loop2], unit="GHz")
        
        # Coupling junction between loops
        JJ_coupling = sq.Junction(value=J, loops=[loop1, loop2], unit="GHz")
        
        # Capacitors (in GHz^-1)
        C1 = sq.Capacitor(value=1/(2*Ec), unit="GHz")
        C2 = sq.Capacitor(value=1/(2*Ec), unit="GHz")
        
        # Create circuit with three nodes
        # Node 0: ground, Node 1: first loop, Node 2: second loop
        elements = {
            (0, 1): [JJ1, C1],
            (0, 2): [JJ2, C2],
            (1, 2): [JJ_coupling],
        }
        
        # Build the circuit
        cr = sq.Circuit(elements)
        cr.set_trunc_nums([50, 50])  # Set truncation for two nodes
        
        print("Checkpoint: ANB gate circuit built successfully")
        logger.info("ANB gate circuit built successfully")
        
        return cr
        
    except Exception as e:
        error_msg = f"Error building ANB gate: {e}"
        print(f"Error at circuit building: {error_msg}")
        logger.error(error_msg, exc_info=True)
        raise


def build_rql_loop(Ej=10.0, Ec=0.2, El=0.1, flux=0.5):
    """
    Build a basic RQL superconducting loop with Josephson junction.
    
    This function creates a general-purpose RQL loop circuit that can be
    used as a building block for more complex gates.
    
    Args:
        Ej (float): Josephson energy in GHz. Default is 10.0 GHz.
        Ec (float): Charging energy in GHz. Default is 0.2 GHz.
        El (float): Inductive energy in GHz. Default is 0.1 GHz.
        flux (float): External flux bias in units of flux quantum (0-1).
                      Default is 0.5.
        
    Returns:
        SQcircuit.Circuit: Configured circuit object.
        
    Raises:
        ValueError: If input parameters are invalid.
    """
    try:
        print(f"Checkpoint: Building RQL loop with Ej={Ej}, Ec={Ec}, El={El} GHz")
        logger.info(f"Building RQL loop: Ej={Ej}, Ec={Ec}, El={El} GHz")
        
        # Validate inputs
        validate_energy(Ej, "Ej")
        validate_energy(Ec, "Ec")
        validate_energy(El, "El")
        validate_flux(flux)
        
        # Create flux loop
        loop = sq.Loop(value=flux)
        
        # Circuit elements (in GHz or GHz^-1)
        JJ = sq.Junction(value=Ej, loops=[loop], unit="GHz")
        C = sq.Capacitor(value=1/(2*Ec), unit="GHz")
        L = sq.Inductor(value=1/El, loops=[loop], unit="GHz")
        
        # Build circuit
        elements = {
            (0, 1): [JJ, C, L],
        }
        
        cr = sq.Circuit(elements)
        cr.set_trunc_nums([50])  # Set truncation for charge basis
        
        print("Checkpoint: RQL loop circuit built successfully")
        logger.info("RQL loop circuit built successfully")
        
        return cr
        
    except Exception as e:
        error_msg = f"Error building RQL loop: {e}"
        print(f"Error at circuit building: {error_msg}")
        logger.error(error_msg, exc_info=True)
        raise

