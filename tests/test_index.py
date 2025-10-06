"""
Tests para el módulo de índice sísmico.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from iasi.index import SeismicIndex
from iasi.signals import SignalProcessor


class TestSeismicIndex(unittest.TestCase):
    
    def setUp(self):
        self.index = SeismicIndex()
        self.processor = SignalProcessor()
    
    def test_default_weights(self):
        """Test que los pesos por defecto suman 1.0."""
        total = sum(self.index.weights.values())
        self.assertAlmostEqual(total, 1.0, places=2)
    
    def test_calculate_index(self):
        """Test de cálculo de índice."""
        # Crear señales de prueba
        signals = {
            'A': self.processor.ingest_signal('A', 50, 0, 100),
            'R': self.processor.ingest_signal('R', 300, 100, 500),
            'D': self.processor.ingest_signal('D', 5, 0, 10),
            'M': self.processor.ingest_signal('M', 50, 0, 100),
            'S': self.processor.ingest_signal('S', 2.5, 0, 5)
        }
        
        # Calcular índice
        index_record = self.index.calculate_index(signals)
        
        # Verificar estructura
        self.assertIn('index_value', index_record)
        self.assertIn('risk_level', index_record)
        self.assertIn('signal_contributions', index_record)
        
        # Verificar que el índice está en rango [0,1]
        self.assertGreaterEqual(index_record['index_value'], 0.0)
        self.assertLessEqual(index_record['index_value'], 1.0)
    
    def test_risk_classification(self):
        """Test de clasificación de riesgo."""
        # Test riesgo BAJO
        signals = {
            'A': {'normalized_value': 0.1},
            'R': {'normalized_value': 0.1},
            'D': {'normalized_value': 0.1},
            'M': {'normalized_value': 0.1},
            'S': {'normalized_value': 0.1}
        }
        index_record = self.index.calculate_index(signals)
        self.assertEqual(index_record['risk_level'], 'BAJO')
        
        # Test riesgo CRÍTICO
        signals = {
            'A': {'normalized_value': 0.9},
            'R': {'normalized_value': 0.9},
            'D': {'normalized_value': 0.9},
            'M': {'normalized_value': 0.9},
            'S': {'normalized_value': 0.9}
        }
        index_record = self.index.calculate_index(signals)
        self.assertEqual(index_record['risk_level'], 'CRÍTICO')
    
    def test_missing_signals(self):
        """Test con señales faltantes."""
        signals = {
            'A': {'normalized_value': 0.5},
            'R': {'normalized_value': 0.5}
            # Faltan D, M, S
        }
        
        with self.assertRaises(ValueError):
            self.index.calculate_index(signals)
    
    def test_trend_analysis(self):
        """Test de análisis de tendencia."""
        # Agregar múltiples índices
        for i in range(10):
            signals = {
                'A': {'normalized_value': 0.1 + i * 0.05},
                'R': {'normalized_value': 0.1 + i * 0.05},
                'D': {'normalized_value': 0.1 + i * 0.05},
                'M': {'normalized_value': 0.1 + i * 0.05},
                'S': {'normalized_value': 0.1 + i * 0.05}
            }
            self.index.calculate_index(signals)
        
        # Analizar tendencia
        trend = self.index.get_trend_analysis(window=7)
        
        self.assertIn('trend', trend)
        self.assertIn('mean_index', trend)
        self.assertEqual(trend['trend'], 'CRECIENTE')


if __name__ == '__main__':
    unittest.main()
