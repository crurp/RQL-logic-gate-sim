"""
Streamlit GUI Application for RQL Logic Gate Simulator.

This module provides an interactive web-based GUI for simulating RQL gates,
visualizing energy spectra, and analyzing gate performance metrics.
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add src directory to path
base_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(base_dir, 'src')
sys.path.insert(0, base_dir)
sys.path.insert(0, src_dir)

from src import circuit_builder
from src import simulator
from src import utils


# Page configuration
st.set_page_config(
    page_title="RQL Logic Gate Simulator",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Setup logging
utils.setup_logging()

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<div class="main-header">⚛️ RQL Logic Gate Simulator</div>', 
                unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar for parameters
    with st.sidebar:
        st.header("⚙️ Gate Parameters")
        
        # Gate type selection
        gate_type = st.selectbox(
            "Gate Type",
            ["Inverter", "A-NOT-B (ANB)", "RQL Loop"],
            index=0
        )
        
        st.subheader("Physical Parameters")
        
        # Josephson energy
        Ej = st.slider(
            "Josephson Energy (Ej) [GHz]",
            min_value=1.0,
            max_value=100.0,
            value=10.0,
            step=0.1,
            help="Josephson junction energy in GHz"
        )
        
        # Charging energy
        Ec = st.slider(
            "Charging Energy (Ec) [GHz]",
            min_value=0.01,
            max_value=10.0,
            value=0.2,
            step=0.01,
            help="Capacitive charging energy in GHz"
        )
        
        # Flux bias
        flux = st.slider(
            "Flux Bias (Φ) [Φ₀]",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.01,
            help="External flux bias in units of flux quantum"
        )
        
        # Additional parameters for ANB gate
        if gate_type == "A-NOT-B (ANB)":
            Ej2 = st.slider(
                "Josephson Energy 2 (Ej2) [GHz]",
                min_value=1.0,
                max_value=100.0,
                value=10.0,
                step=0.1
            )
            J = st.slider(
                "Coupling Strength (J) [GHz]",
                min_value=0.01,
                max_value=10.0,
                value=0.5,
                step=0.01
            )
            flux2 = st.slider(
                "Flux Bias 2 (Φ2) [Φ₀]",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.01
            )
        
        # Simulation parameters
        st.subheader("Simulation Parameters")
        
        n_levels = st.slider(
            "Number of Energy Levels",
            min_value=3,
            max_value=50,
            value=10,
            step=1
        )
        
        perform_flux_sweep = st.checkbox(
            "Perform Flux Sweep",
            value=False,
            help="Sweep flux from 0 to 1 and compute energy levels"
        )
        
        if perform_flux_sweep:
            n_points = st.slider(
                "Flux Points",
                min_value=10,
                max_value=200,
                value=100,
                step=10
            )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📊 Visualization")
        
        # Buttons for actions
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            build_button = st.button("🔧 Build Circuit", use_container_width=True)
        
        with col_btn2:
            simulate_button = st.button("⚡ Run Simulation", use_container_width=True)
        
        # Initialize session state
        if 'circuit' not in st.session_state:
            st.session_state.circuit = None
        if 'energies' not in st.session_state:
            st.session_state.energies = None
        if 'flux_sweep_data' not in st.session_state:
            st.session_state.flux_sweep_data = None
        
        # Build circuit
        if build_button:
            try:
                with st.spinner("Building circuit..."):
                    if gate_type == "Inverter":
                        st.session_state.circuit = circuit_builder.build_rql_inverter(
                            Ej=Ej, Ec=Ec, flux=flux
                        )
                    elif gate_type == "A-NOT-B (ANB)":
                        st.session_state.circuit = circuit_builder.build_anb_gate(
                            Ej1=Ej, Ej2=Ej2, Ec=Ec, J=J, flux1=flux, flux2=flux2
                        )
                    elif gate_type == "RQL Loop":
                        st.session_state.circuit = circuit_builder.build_rql_loop(
                            Ej=Ej, Ec=Ec, flux=flux
                        )
                    
                    st.success("✅ Circuit built successfully!")
                    st.session_state.energies = None
                    st.session_state.flux_sweep_data = None
                    
            except Exception as e:
                st.error(f"❌ Error building circuit: {e}")
        
        # Run simulation
        if simulate_button or st.session_state.circuit is not None:
            if st.session_state.circuit is None:
                st.warning("⚠️ Please build circuit first!")
            else:
                try:
                    with st.spinner("Running simulation..."):
                        if perform_flux_sweep:
                            flux_values, energy_levels = simulator.flux_sweep(
                                st.session_state.circuit,
                                flux_range=(0.0, 1.0),
                                n_points=n_points,
                                n_levels=n_levels
                            )
                            st.session_state.flux_sweep_data = (flux_values, energy_levels)
                            st.session_state.energies = None
                            
                            # Plot flux sweep
                            fig = utils.plot_flux_sweep(
                                flux_values,
                                energy_levels,
                                title=f"{gate_type} - Energy vs Flux"
                            )
                            st.pyplot(fig)
                            
                        else:
                            energies, _ = simulator.diagonalize_hamiltonian(
                                st.session_state.circuit,
                                n_levels=n_levels
                            )
                            st.session_state.energies = energies
                            st.session_state.flux_sweep_data = None
                            
                            # Plot energy spectrum
                            fig = utils.plot_energy_spectrum(
                                energies,
                                title=f"{gate_type} - Energy Spectrum"
                            )
                            st.pyplot(fig)
                        
                        st.success("✅ Simulation completed successfully!")
                        
                except Exception as e:
                    st.error(f"❌ Error running simulation: {e}")
                    st.exception(e)
        
        # Display existing results if available
        if st.session_state.flux_sweep_data is not None:
            flux_values, energy_levels = st.session_state.flux_sweep_data
            fig = utils.plot_flux_sweep(
                flux_values,
                energy_levels,
                title=f"{gate_type} - Energy vs Flux"
            )
            st.pyplot(fig)
        
        elif st.session_state.energies is not None:
            fig = utils.plot_energy_spectrum(
                st.session_state.energies,
                title=f"{gate_type} - Energy Spectrum"
            )
            st.pyplot(fig)
        
        # Anti-crossing plot option
        if st.session_state.flux_sweep_data is not None:
            st.subheader("🔀 Anti-Crossing Analysis")
            level1 = st.slider("First Level", 0, min(4, n_levels-1), 0)
            level2 = st.slider("Second Level", 1, min(5, n_levels-1), 1)
            
            if st.button("Plot Anti-Crossing"):
                try:
                    flux_values, energy_levels = st.session_state.flux_sweep_data
                    fig = utils.plot_anti_crossing(
                        flux_values,
                        energy_levels,
                        level1=level1,
                        level2=level2,
                        title=f"Anti-Crossing: Levels {level1} and {level2}"
                    )
                    st.pyplot(fig)
                except Exception as e:
                    st.error(f"Error plotting anti-crossing: {e}")
    
    with col2:
        st.header("📈 Metrics")
        
        # Display metrics
        if st.session_state.energies is not None:
            try:
                metrics = utils.calculate_gate_metrics(st.session_state.energies)
                
                st.metric(
                    "Ground State Energy",
                    f"{metrics['ground_state_energy']:.4f} GHz"
                )
                
                if metrics['transition_frequency']:
                    st.metric(
                        "Transition Frequency (0→1)",
                        f"{metrics['transition_frequency']:.4f} GHz"
                    )
                
                if metrics['anharmonicity']:
                    st.metric(
                        "Anharmonicity (α)",
                        f"{metrics['anharmonicity']:.4f} GHz"
                    )
                
                # Energy levels table
                st.subheader("Energy Levels")
                energy_data = {
                    'Level': list(range(min(10, len(st.session_state.energies)))),
                    'Energy (GHz)': [f"{E:.4f}" for E in st.session_state.energies[:10]]
                }
                import pandas as pd
                df = pd.DataFrame(energy_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
            except Exception as e:
                st.error(f"Error calculating metrics: {e}")
        
        elif st.session_state.flux_sweep_data is not None:
            flux_values, energy_levels = st.session_state.flux_sweep_data
            st.info("Flux sweep data available. Adjust parameters to see metrics.")
            
            # Show some statistics
            st.subheader("Statistics")
            min_energies = np.min(energy_levels, axis=0)
            max_energies = np.max(energy_levels, axis=0)
            
            for i in range(min(3, energy_levels.shape[1])):
                st.metric(
                    f"Level {i} Range",
                    f"{min_energies[i]:.4f} - {max_energies[i]:.4f} GHz"
                )
        
        else:
            st.info("👈 Build circuit and run simulation to see metrics")
        
        # Information section
        st.header("ℹ️ About")
        st.markdown("""
        **RQL Logic Gate Simulator**
        
        This tool simulates Reciprocal Quantum Logic (RQL) gates for
        superconducting quantum computing systems targeting 1M qubit scaling.
        
        **Features:**
        - Josephson junction modeling
        - Flux tunability analysis
        - Energy spectrum calculations
        - Anti-crossing visualization
        - Gate performance metrics
        """)
        
        # Technology info
        with st.expander("Learn about RQL"):
            st.markdown("""
            **Reciprocal Quantum Logic (RQL)** is a promising approach for
            scalable quantum computing using superconducting circuits.
            
            Key advantages:
            - Low power consumption
            - High operating speed
            - Compatibility with CMOS technology
            - Potential for massive qubit scaling
            
            The simulator uses SQcircuit library for circuit modeling and
            Hamiltonian diagonalization.
            """)


if __name__ == "__main__":
    main()

