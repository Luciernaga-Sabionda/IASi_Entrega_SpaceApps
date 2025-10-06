"""
Tests para el pipeline completo de IASi.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from iasi import IASiPipeline


class TestIASiPipeline(unittest.TestCase):
    
    def setUp(self):
        self.pipeline = IASiPipeline()
    
    def test_full_pipeline(self):
        """Test del pipeline completo."""
        # Datos de entrada
        data = {
            'A': {'value': 50, 'min': 0, 'max': 100},
            'R': {'value': 300, 'min': 100, 'max': 500},
            'D': {'value': 5, 'min': 0, 'max': 10},
            'M': {'value': 50, 'min': 0, 'max': 100},
            'S': {'value': 2.5, 'min': 0, 'max': 5}
        }
        
        # Procesar
        result = self.pipeline.process_and_alert(data)
        
        # Verificar estructura del resultado
        self.assertIn('signals', result)
        self.assertIn('index', result)
        self.assertIn('alert', result)
        
        # Verificar señales
        self.assertEqual(len(result['signals']), 5)
        
        # Verificar índice
        self.assertIn('index_value', result['index'])
        self.assertIn('risk_level', result['index'])
        
        # Verificar alerta
        self.assertIn('alert_id', result['alert'])
        self.assertIn('recommendations', result['alert'])
    
    def test_status(self):
        """Test de obtención de estado."""
        # Procesar algunos datos
        data = {
            'A': {'value': 50, 'min': 0, 'max': 100},
            'R': {'value': 300, 'min': 100, 'max': 500},
            'D': {'value': 5, 'min': 0, 'max': 10},
            'M': {'value': 50, 'min': 0, 'max': 100},
            'S': {'value': 2.5, 'min': 0, 'max': 5}
        }
        self.pipeline.process_and_alert(data)
        
        # Obtener estado
        status = self.pipeline.get_status()
        
        # Verificar estructura
        self.assertIn('latest_signals', status)
        self.assertIn('total_signals_processed', status)
        self.assertIn('total_indices_calculated', status)
        self.assertIn('total_alerts_generated', status)
        self.assertIn('latest_index', status)
        self.assertIn('latest_alert', status)
        
        # Verificar valores
        self.assertEqual(status['total_signals_processed'], 5)
        self.assertEqual(status['total_indices_calculated'], 1)
        self.assertEqual(status['total_alerts_generated'], 1)
    
    def test_weekly_report(self):
        """Test de generación de reporte semanal."""
        # Generar múltiples alertas
        for i in range(5):
            data = {
                'A': {'value': 50 + i * 5, 'min': 0, 'max': 100},
                'R': {'value': 300 + i * 10, 'min': 100, 'max': 500},
                'D': {'value': 5 + i * 0.5, 'min': 0, 'max': 10},
                'M': {'value': 50 + i * 5, 'min': 0, 'max': 100},
                'S': {'value': 2.5 + i * 0.2, 'min': 0, 'max': 5}
            }
            self.pipeline.process_and_alert(data)
        
        # Generar reporte
        report = self.pipeline.generate_weekly_report()
        
        # Verificar estructura
        self.assertIn('report_id', report)
        self.assertIn('summary', report)
        self.assertIn('alerts', report)
        
        # Verificar resumen
        self.assertEqual(report['summary']['total_alerts'], 5)
        self.assertIn('predominant_risk_level', report['summary'])


if __name__ == '__main__':
    unittest.main()
