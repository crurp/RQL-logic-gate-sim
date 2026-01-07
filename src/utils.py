"""
Utility Module for RQL Logic Gate Simulator.

This module provides helper functions for data visualization, error handling,
and parameter validation. Includes functions for plotting energy spectra,
anti-crossings, and handling simulation errors.
"""

import logging
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Tuple, List
import os


# Configure logging
logger = logging.getLogger(__name__)


def setup_logging(log_file='simulation_errors.log', level=logging.INFO):
    """
    Set up logging configuration for the simulator.
    
    Args:
        log_file (str): Path to log file. Default is 'simulation_errors.log'.
        level (int): Logging level. Default is logging.INFO.
    """
    try:
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Configure logging
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()  # Also log to console
            ]
        )
        
        print(f"Checkpoint: Logging configured to {log_file}")
        logger.info("Logging configured successfully")
        
    except Exception as e:
        print(f"Error setting up logging: {e}")
        # Fallback to basic logging
        logging.basicConfig(level=level)


def validate_parameters(params: dict, required_keys: List[str]) -> bool:
    """
    Validate that all required parameters are present and valid.
    
    Args:
        params (dict): Dictionary of parameters to validate.
        required_keys (list): List of required parameter keys.
        
    Returns:
        bool: True if all parameters are valid.
        
    Raises:
        ValueError: If required parameters are missing or invalid.
    """
    try:
        missing_keys = [key for key in required_keys if key not in params]
        if missing_keys:
            raise ValueError(f"Missing required parameters: {missing_keys}")
        
        for key in required_keys:
            value = params[key]
            if value is None:
                raise ValueError(f"Parameter {key} cannot be None")
            
            # Type-specific validation
            if 'flux' in key.lower():
                if not (0 <= float(value) <= 1):
                    raise ValueError(f"{key} must be between 0 and 1, got {value}")
            elif 'energy' in key.lower() or 'ej' in key.lower() or 'ec' in key.lower():
                if float(value) <= 0:
                    raise ValueError(f"{key} must be positive, got {value}")
        
        return True
        
    except Exception as e:
        logger.error(f"Parameter validation failed: {e}")
        raise


def plot_energy_spectrum(energies: np.ndarray, 
                        flux_values: Optional[np.ndarray] = None,
                        title: str = "Energy Spectrum",
                        xlabel: str = "Energy Level",
                        ylabel: str = "Energy (GHz)",
                        save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot energy spectrum of RQL gate.
    
    Args:
        energies (np.ndarray): Energy eigenvalues in GHz. Can be 1D (single set)
                               or 2D (multiple flux points).
        flux_values (np.ndarray, optional): Flux values for x-axis if 2D energies.
        title (str): Plot title. Default is "Energy Spectrum".
        xlabel (str): X-axis label. Default is "Energy Level".
        ylabel (str): Y-axis label. Default is "Energy (GHz)".
        save_path (str, optional): Path to save figure. If None, don't save.
        
    Returns:
        matplotlib.figure.Figure: Figure object.
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        energies = np.array(energies)
        
        if energies.ndim == 1:
            # Single set of energies
            ax.plot(range(len(energies)), energies, 'o-', linewidth=2, markersize=8)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            
        elif energies.ndim == 2:
            # Multiple flux points - plot energy vs flux
            if flux_values is None:
                flux_values = np.arange(energies.shape[0])
            
            for i in range(min(5, energies.shape[1])):  # Plot first 5 levels
                ax.plot(flux_values, energies[:, i], linewidth=2, 
                       label=f'Level {i}')
            
            ax.set_xlabel("Flux (Φ₀)")
            ax.set_ylabel("Energy (GHz)")
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        ax.set_title(title)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Checkpoint: Figure saved to {save_path}")
            logger.info(f"Figure saved to {save_path}")
        
        return fig
        
    except Exception as e:
        error_msg = f"Error plotting energy spectrum: {e}"
        print(f"Error at visualization: {error_msg}")
        logger.error(error_msg, exc_info=True)
        raise


def plot_flux_sweep(flux_values: np.ndarray,
                   energy_levels: np.ndarray,
                   title: str = "Energy vs Flux",
                   save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot flux sweep showing energy levels vs external flux.
    
    Args:
        flux_values (np.ndarray): Array of flux values in units of flux quantum.
        energy_levels (np.ndarray): 2D array (n_points, n_levels) of energies in GHz.
        title (str): Plot title. Default is "Energy vs Flux".
        save_path (str, optional): Path to save figure. If None, don't save.
        
    Returns:
        matplotlib.figure.Figure: Figure object.
    """
    try:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        n_levels = energy_levels.shape[1]
        colors = plt.cm.viridis(np.linspace(0, 1, n_levels))
        
        for i in range(n_levels):
            ax.plot(flux_values, energy_levels[:, i], 
                   linewidth=2, color=colors[i], label=f'Level {i}')
        
        ax.set_xlabel("Flux (Φ₀)", fontsize=12)
        ax.set_ylabel("Energy (GHz)", fontsize=12)
        ax.set_title(title, fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Checkpoint: Flux sweep plot saved to {save_path}")
            logger.info(f"Flux sweep plot saved to {save_path}")
        
        return fig
        
    except Exception as e:
        error_msg = f"Error plotting flux sweep: {e}"
        print(f"Error at visualization: {error_msg}")
        logger.error(error_msg, exc_info=True)
        raise


def plot_anti_crossing(flux_values: np.ndarray,
                      energy_levels: np.ndarray,
                      level1: int = 0,
                      level2: int = 1,
                      title: str = "Anti-Crossing",
                      save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot anti-crossing between two energy levels, indicating coupling.
    
    Args:
        flux_values (np.ndarray): Array of flux values.
        energy_levels (np.ndarray): 2D array of energy levels.
        level1 (int): First energy level index. Default is 0.
        level2 (int): Second energy level index. Default is 1.
        title (str): Plot title. Default is "Anti-Crossing".
        save_path (str, optional): Path to save figure. If None, don't save.
        
    Returns:
        matplotlib.figure.Figure: Figure object.
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if level2 >= energy_levels.shape[1]:
            raise ValueError(f"Level {level2} not available (max: {energy_levels.shape[1]-1})")
        
        ax.plot(flux_values, energy_levels[:, level1], 'b-', 
               linewidth=2, label=f'Level {level1}')
        ax.plot(flux_values, energy_levels[:, level2], 'r-', 
               linewidth=2, label=f'Level {level2}')
        
        # Highlight minimum gap
        gap = np.abs(energy_levels[:, level2] - energy_levels[:, level1])
        min_gap_idx = np.argmin(gap)
        min_gap = gap[min_gap_idx]
        min_gap_flux = flux_values[min_gap_idx]
        
        ax.axvline(min_gap_flux, color='g', linestyle='--', 
                  label=f'Min gap: {min_gap:.4f} GHz')
        ax.scatter([min_gap_flux], [energy_levels[min_gap_idx, level1]], 
                  color='g', s=100, zorder=5)
        ax.scatter([min_gap_flux], [energy_levels[min_gap_idx, level2]], 
                  color='g', s=100, zorder=5)
        
        ax.set_xlabel("Flux (Φ₀)", fontsize=12)
        ax.set_ylabel("Energy (GHz)", fontsize=12)
        ax.set_title(title, fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Checkpoint: Anti-crossing plot saved to {save_path}")
            logger.info(f"Anti-crossing plot saved to {save_path}")
        
        return fig
        
    except Exception as e:
        error_msg = f"Error plotting anti-crossing: {e}"
        print(f"Error at visualization: {error_msg}")
        logger.error(error_msg, exc_info=True)
        raise


def calculate_gate_metrics(energies: np.ndarray) -> dict:
    """
    Calculate key metrics for RQL gate performance.
    
    Args:
        energies (np.ndarray): Energy eigenvalues in GHz.
        
    Returns:
        dict: Dictionary containing metrics like ground state energy,
              transition frequency, anharmonicity, etc.
    """
    try:
        energies = np.array(energies)
        
        if len(energies) < 2:
            raise ValueError("Need at least 2 energy levels")
        
        metrics = {
            'ground_state_energy': float(energies[0]),
            'first_excited_energy': float(energies[1]) if len(energies) > 1 else None,
            'transition_frequency': float(energies[1] - energies[0]) if len(energies) > 1 else None,
        }
        
        if len(energies) >= 3:
            metrics['anharmonicity'] = float((energies[2] - energies[1]) - 
                                            (energies[1] - energies[0]))
        else:
            metrics['anharmonicity'] = None
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error calculating gate metrics: {e}")
        raise

