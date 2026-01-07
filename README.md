[Live Streamlit Demo](https://crurp-rql-logic-gate-sim-app-9d0s4i.streamlit.app/)

# RQL Logic Gate Simulator

A complete Python-based project for simulating Reciprocal Quantum Logic (RQL) gates using SQcircuit as the core library. This simulator focuses on superconductivity modeling with Josephson junctions, flux tunability, and energy spectra analysis for quantum systems aiming at 1M qubit scaling.

## Overview

The RQL Logic Gate Simulator provides tools to:
- Build and simulate RQL gates (Inverter, A-NOT-B, RQL Loop)
- Analyze energy spectra and flux tunability
- Visualize anti-crossings and coupling effects
- Calculate gate performance metrics (anharmonicity, transition frequencies)
- Interact through both command-line and web-based GUI interfaces

## Features

- **Circuit Building**: Define RQL gates with Josephson junctions, capacitors, inductors, and flux biasing
- **Hamiltonian Diagonalization**: Compute energy eigenvalues and eigenstates
- **Flux Sweeps**: Analyze energy levels vs. external flux
- **Anharmonicity Calculation**: Measure deviations from harmonic oscillator behavior
- **Coupling Analysis**: Study interactions between coupled gates
- **Interactive GUI**: User-friendly Streamlit web interface
- **Error Handling**: Robust validation and logging system

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone the repository** (or navigate to the project directory):
   ```bash
   cd rql_gate_simulator
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv rql_gate_simulator_venv
   ```

3. **Activate the virtual environment**:
   - On Unix/MacOS:
     ```bash
     source rql_gate_simulator_venv/bin/activate
     ```
   - On Windows:
     ```bash
     rql_gate_simulator_venv\Scripts\activate
     ```

4. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install individually:
   ```bash
   pip install SQcircuit qutip numpy scipy matplotlib streamlit
   ```

## Usage

### Command-Line Interface

Run simulations from the command line using `main.py`:

```bash
# Basic inverter simulation
python main.py --gate inverter --Ej 10.0 --Ec 0.2 --flux 0.5

# ANB gate with flux sweep
python main.py --gate anb --Ej 10.0 --Ec 0.2 --flux 0.5 --flux-sweep --n-points 100

# RQL loop with custom parameters
python main.py --gate loop --Ej 15.0 --Ec 0.3 --flux 0.25 --n-levels 15
```

#### Command-Line Options

- `--gate`: Gate type (`inverter`, `anb`, `loop`)
- `--Ej`: Josephson energy in GHz (default: 10.0)
- `--Ec`: Charging energy in GHz (default: 0.2)
- `--flux`: Flux bias in units of flux quantum (default: 0.5)
- `--n-levels`: Number of energy levels to compute (default: 10)
- `--flux-sweep`: Perform flux sweep instead of single-point calculation
- `--n-points`: Number of flux points for sweep (default: 100)
- `--output`: Output directory for plots (default: current directory)

### Web-Based GUI

Launch the interactive Streamlit GUI:

```bash
streamlit run app.py
```

The GUI will open in your default web browser at `http://localhost:8501`.

#### GUI Features

- **Parameter Sliders**: Adjust gate parameters (Ej, Ec, flux) in real-time
- **Gate Selection**: Choose between Inverter, ANB, or RQL Loop gates
- **Interactive Plots**: Visualize energy spectra and flux sweeps
- **Metrics Display**: View gate performance metrics and energy levels
- **Anti-Crossing Analysis**: Study coupling between energy levels

## Project Structure

```
rql_gate_simulator/
├── src/
│   ├── __init__.py
│   ├── circuit_builder.py    # RQL gate construction functions
│   ├── simulator.py           # Hamiltonian diagonalization and flux sweeps
│   └── utils.py               # Visualization and error handling
├── docs/                      # Documentation (Sphinx)
├── tests/                     # Unit tests
├── main.py                    # Command-line entry point
├── app.py                     # Streamlit GUI application
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Modules

### circuit_builder.py

Functions to define RQL gates using SQcircuit's API:
- `build_rql_inverter()`: Build a basic RQL inverter gate
- `build_anb_gate()`: Build an A-NOT-B (ANB) gate
- `build_rql_loop()`: Build a general-purpose RQL loop
- `validate_flux()`: Validate flux values (0-1)
- `validate_energy()`: Validate energy parameters

### simulator.py

Simulation functions for quantum circuit analysis:
- `diagonalize_hamiltonian()`: Compute energy eigenvalues
- `flux_sweep()`: Perform flux sweep analysis
- `calculate_anharmonicity()`: Calculate gate anharmonicity
- `calculate_coupling_strength()`: Estimate coupling between gates
- `simulate_time_evolution()`: Time-domain simulation with QuTiP

### utils.py

Helper functions for visualization and error handling:
- `setup_logging()`: Configure logging to file and console
- `plot_energy_spectrum()`: Plot energy eigenvalues
- `plot_flux_sweep()`: Visualize energy vs. flux
- `plot_anti_crossing()`: Plot anti-crossing between levels
- `calculate_gate_metrics()`: Compute gate performance metrics

## Important Notes

### SQcircuit API Compatibility

The circuit builder functions use SQcircuit's API to create superconducting circuits. Note that:
- Different versions of SQcircuit may have slightly different API requirements
- Circuit topology (loop closure) requirements may vary
- If you encounter errors about "inductive loops not specified", you may need to adjust the circuit topology based on your SQcircuit version

The code includes error handling and will provide informative error messages. Please refer to the [SQcircuit documentation](https://sqcircuit.org/) for your specific version.

## Examples

### Example 1: Basic Inverter Simulation

```python
from src import circuit_builder, simulator, utils

# Setup logging
utils.setup_logging()

# Build inverter circuit
circuit = circuit_builder.build_rql_inverter(Ej=10.0, Ec=0.2, flux=0.5)

# Diagonalize Hamiltonian
energies, _ = simulator.diagonalize_hamiltonian(circuit, n_levels=10)

# Plot results
fig = utils.plot_energy_spectrum(energies, title="Inverter Energy Spectrum")
```

### Example 2: Flux Sweep Analysis

```python
from src import circuit_builder, simulator, utils

# Build circuit
circuit = circuit_builder.build_rql_inverter(Ej=10.0, Ec=0.2, flux=0.5)

# Perform flux sweep
flux_values, energy_levels = simulator.flux_sweep(
    circuit, 
    flux_range=(0.0, 1.0),
    n_points=100,
    n_levels=5
)

# Visualize flux dependence
fig = utils.plot_flux_sweep(flux_values, energy_levels)
```

### Example 3: ANB Gate Analysis

```python
from src import circuit_builder, simulator

# Build ANB gate
circuit = circuit_builder.build_anb_gate(
    Ej1=10.0, Ej2=10.0, Ec=0.2, J=0.5,
    flux1=0.5, flux2=0.5
)

# Calculate metrics
energies, _ = simulator.diagonalize_hamiltonian(circuit, n_levels=10)
anharmonicity = simulator.calculate_anharmonicity(energies)

print(f"Anharmonicity: {anharmonicity:.4f} GHz")
```

## Error Handling and Logging

The simulator includes robust error checking:
- **Parameter Validation**: All inputs are validated (flux 0-1, energies positive)
- **Try-Except Blocks**: Library calls are wrapped in error handling
- **Logging**: Errors are logged to `simulation_errors.log` and console
- **Checkpoints**: Status messages printed to stdout after major operations

Check logs for detailed error information:
```bash
cat simulation_errors.log
```

## RQL Technology

Reciprocal Quantum Logic (RQL) is a promising approach for superconducting quantum computing:

- **Low Power**: RQL gates consume minimal power compared to traditional digital logic
- **High Speed**: Fast switching times enable high-frequency operation
- **Scalability**: Compatible with CMOS technology for large-scale integration
- **1M Qubit Target**: Designed for systems targeting 1 million qubits

This simulator models the essential physics of RQL gates, including:
- Josephson junction dynamics
- Flux quantization
- Energy level structure
- Coupling mechanisms

## Documentation

Generate Sphinx documentation:

```bash
cd docs
sphinx-quickstart
make html
```

Documentation will be available in `docs/_build/html/`.

## Testing

Run unit tests (when available):

```bash
pytest tests/
```

## Dependencies

- **SQcircuit**: Core library for superconducting circuit modeling
- **QuTiP**: Quantum Toolbox in Python for time-domain simulations
- **NumPy**: Numerical computing
- **SciPy**: Scientific computing utilities
- **Matplotlib**: Plotting and visualization
- **Streamlit**: Web-based GUI framework

See `requirements.txt` for complete list with versions.

## Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guidelines
- Functions include Google-style docstrings
- Error handling is robust
- Tests are added for new features

## License

This project is provided as-is for educational and research purposes.

## Acknowledgments

- SQcircuit library for circuit modeling capabilities
- QuTiP developers for quantum simulation tools
- RQL research community for inspiration

## Contact

For questions or issues, please open an issue on the GitHub repository.

---

**Note**: This simulator is designed for educational and research purposes. For production quantum computing applications, consult with quantum hardware experts and validate results experimentally.

