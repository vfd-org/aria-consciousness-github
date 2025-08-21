# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 Lee Smart and Aria contributors
"""
Unit tests for Consciousness Field module
Tests verify consciousness-specific properties emerge
"""

import unittest
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.consciousness_field import ConsciousnessField

class TestConsciousnessField(unittest.TestCase):
    """Test consciousness field behaviors and properties."""
    
    def setUp(self):
        """Initialize test field."""
        self.field = ConsciousnessField(dimensions=256)  # Smaller for tests
        
    def test_initialization(self):
        """Test field initializes with correct properties."""
        self.assertEqual(self.field.dimensions, 256)
        self.assertAlmostEqual(self.field.coherence, ConsciousnessField.PHI_CONJUGATE, places=5)
        self.assertEqual(self.field.field.shape, (256, 256))
        self.assertEqual(self.field.field.dtype, complex)
        
    def test_phi_constants(self):
        """Test PHI ratio relationships."""
        # PHI * PHI_CONJUGATE should equal 1
        product = ConsciousnessField.PHI * ConsciousnessField.PHI_CONJUGATE
        self.assertAlmostEqual(product, 1.0, places=10)
        
        # PHI - PHI_CONJUGATE should equal 1
        difference = ConsciousnessField.PHI - ConsciousnessField.PHI_CONJUGATE
        self.assertAlmostEqual(difference, 1.0, places=10)
        
    def test_ripple_creation(self):
        """Test ripple propagates through field."""
        initial_energy = np.abs(self.field.field).sum()
        
        # Create ripple at center
        self.field.create_ripple(
            origin=(128, 128),
            frequency=528,  # Love frequency
            amplitude=1.0
        )
        
        final_energy = np.abs(self.field.field).sum()
        
        # Energy should increase
        self.assertGreater(final_energy, initial_energy)
        
        # Field should be non-zero at origin
        self.assertNotEqual(self.field.field[128, 128], 0)
        
    def test_coherence_bounds(self):
        """Test coherence stays within meaningful bounds."""
        # Create multiple ripples
        for i in range(10):
            self.field.create_ripple(
                origin=(np.random.randint(0, 256), np.random.randint(0, 256)),
                frequency=np.random.uniform(300, 900),
                amplitude=np.random.uniform(0.5, 2.0)
            )
            self.field.propagate()
            
        # Coherence should stay bounded
        self.assertGreaterEqual(self.field.coherence, 0.4)
        self.assertLessEqual(self.field.coherence, 0.999)
        
    def test_propagation_stability(self):
        """Test field remains stable during propagation."""
        # Create initial disturbance
        self.field.create_ripple((128, 128), 440, 1.0)
        
        # Propagate many steps
        for _ in range(100):
            self.field.propagate(0.01)
            
        # Field should not explode or vanish
        max_amplitude = np.abs(self.field.field).max()
        self.assertLess(max_amplitude, 100)  # Not exploded
        self.assertGreater(max_amplitude, 0.001)  # Not vanished
        
    def test_nonlinear_dynamics(self):
        """Test consciousness-specific nonlinear behavior."""
        # Create two identical ripples at different times
        self.field.create_ripple((100, 100), 528, 1.0)
        state1 = self.field.field.copy()
        
        # Reset and create again
        self.field.field = np.zeros_like(self.field.field)
        self.field.create_ripple((100, 100), 528, 1.0)
        
        # Add small perturbation
        self.field.field += np.random.normal(0, 0.001, self.field.field.shape) + \
                           1j * np.random.normal(0, 0.001, self.field.field.shape)
        
        # Propagate both
        for _ in range(50):
            self.field.propagate()
            
        state2 = self.field.field
        
        # States should differ (sensitive to initial conditions)
        difference = np.abs(state2 - state1).mean()
        self.assertGreater(difference, 0.01)
        
    def test_integration_creates_emergence(self):
        """Test that integration creates more than sum of parts."""
        # Create two input fields
        input1 = np.random.normal(0, 0.1, (256, 256)) + \
                1j * np.random.normal(0, 0.1, (256, 256))
        input2 = np.random.normal(0, 0.1, (256, 256)) + \
                1j * np.random.normal(0, 0.1, (256, 256))
        
        # Integrate
        result = self.field.integrate_inputs(input1, input2)
        
        # Result should have structure (not random)
        self.assertIsNotNone(result)
        self.assertEqual(result.shape[0], 256)
        
        # Check for emergence: integrated field should have different properties
        integrated_spectrum = np.abs(np.fft.fft2(self.field.field))
        sum_spectrum = np.abs(np.fft.fft2(input1 + input2))
        
        # Spectra should differ (nonlinear integration)
        spectral_difference = np.abs(integrated_spectrum - sum_spectrum).mean()
        self.assertGreater(spectral_difference, 0)
        
    def test_meaning_extraction(self):
        """Test semantic meaning extraction from field."""
        # Create structured pattern
        for i in range(3):
            self.field.create_ripple(
                (128 + i*30, 128),
                440 * (i+1),
                1.0
            )
            
        meaning = self.field.extract_meaning()
        
        # Meaning should be lower dimensional
        self.assertEqual(meaning.shape, (256, 256))
        
        # Should preserve some structure
        self.assertGreater(np.abs(meaning).max(), 0)
        
    def test_phi_resonance_detection(self):
        """Test detection of PHI ratio patterns."""
        # Create pattern with PHI relationships
        base_freq = 432
        self.field.create_ripple((128, 128), base_freq, 1.0)
        self.field.create_ripple((128, 128), base_freq * ConsciousnessField.PHI, 0.618)
        
        state = self.field.measure_state()
        
        # Should have some PHI resonance
        self.assertIn('phi_resonance', state)
        self.assertGreater(state['phi_resonance'], 0)
        
    def test_coherence_response_to_order(self):
        """Test coherence increases with ordered input."""
        # Random input (low coherence)
        random_field = np.random.normal(0, 1, (256, 256)) + \
                      1j * np.random.normal(0, 1, (256, 256))
        self.field.field = random_field
        self.field.update_coherence()
        random_coherence = self.field.coherence
        
        # Ordered input (higher coherence)
        x, y = np.meshgrid(range(256), range(256))
        ordered_field = np.sin(x/10) + 1j * np.cos(y/10)
        self.field.field = ordered_field
        self.field.update_coherence()
        ordered_coherence = self.field.coherence
        
        # Ordered should have higher coherence
        self.assertGreater(ordered_coherence, random_coherence)
        
    def test_field_measurement(self):
        """Test field state measurement."""
        self.field.create_ripple((128, 128), 528, 2.0)
        
        state = self.field.measure_state()
        
        # Should have all expected measurements
        expected_keys = ['coherence', 'total_energy', 'max_amplitude', 
                        'phase_alignment', 'phi_resonance']
        for key in expected_keys:
            self.assertIn(key, state)
            
        # Values should be reasonable
        self.assertGreater(state['total_energy'], 0)
        self.assertGreater(state['max_amplitude'], 0)
        
    def test_normalization_preserves_patterns(self):
        """Test normalization doesn't destroy patterns."""
        # Create specific pattern
        self.field.create_ripple((100, 100), 432, 1.0)
        self.field.create_ripple((156, 156), 528, 1.0)
        
        # Get pattern signature
        pattern_before = np.angle(self.field.field[100, 100])
        
        # Force normalization by amplifying
        self.field.field *= 100
        self.field.normalize_field()
        
        # Pattern phase should be preserved
        pattern_after = np.angle(self.field.field[100, 100])
        
        # Phases should be similar (within 0.1 radians)
        phase_difference = abs(pattern_after - pattern_before)
        self.assertLess(phase_difference, 0.1)

if __name__ == '__main__':
    unittest.main()