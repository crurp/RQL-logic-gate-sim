"""
Unit tests for circuit_builder module.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src import circuit_builder


class TestCircuitBuilder(unittest.TestCase):
    """Test cases for circuit_builder module."""
    
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def test_validate_flux(self):
        """Test flux validation."""
        # Valid flux
        self.assertTrue(circuit_builder.validate_flux(0.5))
        self.assertTrue(circuit_builder.validate_flux(0.0))
        self.assertTrue(circuit_builder.validate_flux(1.0))
        
        # Invalid flux
        with self.assertRaises(ValueError):
            circuit_builder.validate_flux(1.5)
        with self.assertRaises(ValueError):
            circuit_builder.validate_flux(-0.1)
    
    def test_validate_energy(self):
        """Test energy validation."""
        # Valid energy
        self.assertTrue(circuit_builder.validate_energy(10.0))
        self.assertTrue(circuit_builder.validate_energy(0.1))
        
        # Invalid energy
        with self.assertRaises(ValueError):
            circuit_builder.validate_energy(-1.0)
        with self.assertRaises(ValueError):
            circuit_builder.validate_energy(0.0)
    
    def test_build_rql_inverter(self):
        """Test building RQL inverter."""
        try:
            circuit = circuit_builder.build_rql_inverter(
                Ej=10.0, Ec=0.2, flux=0.5
            )
            self.assertIsNotNone(circuit)
        except Exception as e:
            self.fail(f"build_rql_inverter raised {e}")
    
    def test_build_rql_inverter_invalid_params(self):
        """Test building RQL inverter with invalid parameters."""
        with self.assertRaises(ValueError):
            circuit_builder.build_rql_inverter(Ej=-10.0, Ec=0.2, flux=0.5)
        
        with self.assertRaises(ValueError):
            circuit_builder.build_rql_inverter(Ej=10.0, Ec=0.2, flux=1.5)


if __name__ == '__main__':
    unittest.main()

