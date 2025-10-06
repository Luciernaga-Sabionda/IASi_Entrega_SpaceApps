"""
Tests para el módulo de procesamiento de señales.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from iasi.signals import SignalProcessor


class TestSignalProcessor(unittest.TestCase):
    
    def setUp(self):
        self.processor = SignalProcessor()
    
    def test_normalize_signal(self):
        """Test de normalización de señales."""
        # Test normalización básica
        result = self.processor.normalize_signal(50, 0, 100)
        self.assertEqual(result, 0.5)
        
        # Test límites
        result = self.processor.normalize_signal(0, 0, 100)
        self.assertEqual(result, 0.0)
        
        result = self.processor.normalize_signal(100, 0, 100)
        self.assertEqual(result, 1.0)
        
        # Test clipping
        result = self.processor.normalize_signal(150, 0, 100)
        self.assertEqual(result, 1.0)
        
        result = self.processor.normalize_signal(-50, 0, 100)
        self.assertEqual(result, 0.0)
    
    def test_ingest_signal(self):
        """Test de ingesta de señales."""
        # Ingestar señal de animales
        signal = self.processor.ingest_signal('A', 75, 0, 100)
        
        self.assertEqual(signal['type'], 'A')
        self.assertEqual(signal['type_name'], 'Animales')
        self.assertEqual(signal['raw_value'], 75)
        self.assertEqual(signal['normalized_value'], 0.75)
        self.assertIn('timestamp', signal)
    
    def test_invalid_signal_type(self):
        """Test con tipo de señal inválido."""
        with self.assertRaises(ValueError):
            self.processor.ingest_signal('X', 50, 0, 100)
    
    def test_signal_history(self):
        """Test de historial de señales."""
        # Ingestar varias señales
        self.processor.ingest_signal('A', 50, 0, 100)
        self.processor.ingest_signal('A', 60, 0, 100)
        self.processor.ingest_signal('R', 200, 100, 500)
        
        # Verificar historial
        history = self.processor.get_signal_history('A')
        self.assertEqual(len(history['A']), 2)
        
        # Verificar últimas señales
        latest = self.processor.get_latest_signals()
        self.assertIsNotNone(latest['A'])
        self.assertIsNotNone(latest['R'])
        self.assertIsNone(latest['D'])


if __name__ == '__main__':
    unittest.main()
