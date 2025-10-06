"""
Pipeline principal de IASi que integra todos los módulos.
"""

from typing import Dict, Any, List
from .signals import SignalProcessor
from .index import SeismicIndex
from .alerts import AlertSystem


class IASiPipeline:
    """
    Pipeline completo de IASi que integra ingesta de datos,
    normalización, cálculo de índice y generación de alertas.
    """
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Inicializa el pipeline de IASi.
        
        Args:
            weights: Pesos personalizados para cada señal
        """
        self.signal_processor = SignalProcessor()
        self.seismic_index = SeismicIndex(weights)
        self.alert_system = AlertSystem()
    
    def ingest_data(self, data: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Ingesta datos de múltiples fuentes.
        
        Args:
            data: Diccionario con datos de cada señal
                  Formato: {
                      'A': {'value': float, 'min': float, 'max': float, 'metadata': dict},
                      'R': {...},
                      ...
                  }
        
        Returns:
            Señales procesadas y normalizadas
        """
        processed_signals = {}
        
        for signal_type, signal_data in data.items():
            if signal_type not in SignalProcessor.SIGNAL_TYPES:
                raise ValueError(f"Tipo de señal inválido: {signal_type}")
            
            value = signal_data.get('value')
            min_val = signal_data.get('min', 0.0)
            max_val = signal_data.get('max', 100.0)
            metadata = signal_data.get('metadata', {})
            
            processed = self.signal_processor.ingest_signal(
                signal_type, value, min_val, max_val, metadata
            )
            processed_signals[signal_type] = processed
        
        return processed_signals
    
    def process_and_alert(self, data: Dict[str, Dict[str, Any]], 
                         context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Procesa datos y genera alerta completa.
        
        Args:
            data: Datos de entrada de todas las señales
            context: Contexto adicional para la alerta
            
        Returns:
            Resultado completo del procesamiento
        """
        # 1. Ingestar y normalizar señales
        signals = self.ingest_data(data)
        
        # 2. Calcular índice de riesgo
        index_record = self.seismic_index.calculate_index(signals)
        
        # 3. Generar alerta
        alert = self.alert_system.generate_alert(index_record, context)
        
        # 4. Retornar resultado completo
        result = {
            'signals': signals,
            'index': index_record,
            'alert': alert
        }
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del pipeline.
        
        Returns:
            Estado completo del sistema
        """
        latest_signals = self.signal_processor.get_latest_signals()
        
        status = {
            'latest_signals': latest_signals,
            'total_signals_processed': sum(
                len(history) 
                for history in self.signal_processor.signal_history.values()
            ),
            'total_indices_calculated': len(self.seismic_index.index_history),
            'total_alerts_generated': len(self.alert_system.alerts),
            'current_weights': self.seismic_index.weights.copy(),
            'thresholds': self.seismic_index.THRESHOLDS.copy()
        }
        
        # Agregar último índice si existe
        if self.seismic_index.index_history:
            status['latest_index'] = self.seismic_index.index_history[-1]
        
        # Agregar última alerta si existe
        if self.alert_system.alerts:
            status['latest_alert'] = self.alert_system.alerts[-1]
        
        return status
    
    def generate_weekly_report(self) -> Dict[str, Any]:
        """
        Genera reporte semanal del sistema.
        
        Returns:
            Reporte semanal completo
        """
        return self.alert_system.generate_weekly_report()
    
    def get_trend_analysis(self, window: int = 7) -> Dict[str, Any]:
        """
        Obtiene análisis de tendencia del índice.
        
        Args:
            window: Ventana temporal para el análisis
            
        Returns:
            Análisis de tendencia
        """
        return self.seismic_index.get_trend_analysis(window)
