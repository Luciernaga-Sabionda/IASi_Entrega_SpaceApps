"""
Módulo de índice sísmico probabilístico con umbrales auditables.
"""

from typing import Dict, Any, List
import numpy as np
from datetime import datetime


class SeismicIndex:
    """
    Calcula el índice probabilístico de riesgo sísmico 
    integrando múltiples señales normalizadas.
    """
    
    # Umbrales auditables para clasificación de riesgo
    THRESHOLDS = {
        'BAJO': (0.0, 0.3),
        'MEDIO': (0.3, 0.6),
        'ALTO': (0.6, 0.8),
        'CRÍTICO': (0.8, 1.0)
    }
    
    # Pesos por defecto para cada señal (suman 1.0)
    DEFAULT_WEIGHTS = {
        'A': 0.15,  # Animales
        'R': 0.20,  # Radón
        'D': 0.35,  # Deformación (InSAR tiene mayor peso)
        'M': 0.15,  # Marino
        'S': 0.15   # Sensores
    }
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Inicializa el calculador de índice sísmico.
        
        Args:
            weights: Pesos personalizados para cada señal (deben sumar 1.0)
        """
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self._validate_weights()
        self.index_history: List[Dict[str, Any]] = []
    
    def _validate_weights(self):
        """Valida que los pesos sean correctos."""
        total = sum(self.weights.values())
        if not np.isclose(total, 1.0, atol=0.01):
            raise ValueError(f"Los pesos deben sumar 1.0, suma actual: {total}")
        
        expected_keys = set(self.DEFAULT_WEIGHTS.keys())
        actual_keys = set(self.weights.keys())
        if expected_keys != actual_keys:
            raise ValueError(f"Los pesos deben incluir todas las señales: {expected_keys}")
    
    def calculate_index(self, signals: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcula el índice probabilístico de riesgo sísmico.
        
        Args:
            signals: Diccionario con señales normalizadas de cada tipo
            
        Returns:
            Diccionario con el índice calculado y trazabilidad
        """
        # Validar que todas las señales estén presentes
        missing_signals = []
        for signal_type in self.DEFAULT_WEIGHTS.keys():
            if signal_type not in signals or signals[signal_type] is None:
                missing_signals.append(signal_type)
        
        if missing_signals:
            raise ValueError(f"Señales faltantes: {missing_signals}")
        
        # Calcular índice ponderado
        index_value = 0.0
        signal_contributions = {}
        
        for signal_type, weight in self.weights.items():
            normalized_value = signals[signal_type]['normalized_value']
            contribution = normalized_value * weight
            index_value += contribution
            
            signal_contributions[signal_type] = {
                'normalized_value': normalized_value,
                'weight': weight,
                'contribution': contribution
            }
        
        # Determinar nivel de riesgo
        risk_level = self._classify_risk(index_value)
        
        # Crear registro con trazabilidad completa
        index_record = {
            'index_value': float(index_value),
            'risk_level': risk_level,
            'timestamp': datetime.now().isoformat(),
            'signal_contributions': signal_contributions,
            'weights_used': self.weights.copy(),
            'thresholds': self.THRESHOLDS.copy()
        }
        
        self.index_history.append(index_record)
        
        return index_record
    
    def _classify_risk(self, index_value: float) -> str:
        """
        Clasifica el nivel de riesgo basado en umbrales.
        
        Args:
            index_value: Valor del índice (0-1)
            
        Returns:
            Nivel de riesgo ('BAJO', 'MEDIO', 'ALTO', 'CRÍTICO')
        """
        for risk_level, (min_val, max_val) in self.THRESHOLDS.items():
            if min_val <= index_value < max_val:
                return risk_level
        
        # Si es exactamente 1.0
        if index_value >= self.THRESHOLDS['CRÍTICO'][0]:
            return 'CRÍTICO'
        
        return 'BAJO'
    
    def get_risk_interpretation(self, risk_level: str) -> str:
        """
        Obtiene la interpretación del nivel de riesgo.
        
        Args:
            risk_level: Nivel de riesgo
            
        Returns:
            Descripción del nivel de riesgo
        """
        interpretations = {
            'BAJO': 'Riesgo sísmico bajo. Condiciones normales.',
            'MEDIO': 'Riesgo sísmico medio. Monitoreo continuo recomendado.',
            'ALTO': 'Riesgo sísmico alto. Activar protocolos de preparación.',
            'CRÍTICO': 'Riesgo sísmico crítico. Emitir alerta inmediata.'
        }
        return interpretations.get(risk_level, 'Nivel desconocido')
    
    def get_index_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de índices calculados.
        
        Args:
            limit: Número máximo de registros
            
        Returns:
            Historial de índices
        """
        if limit:
            return self.index_history[-limit:]
        return self.index_history.copy()
    
    def get_trend_analysis(self, window: int = 7) -> Dict[str, Any]:
        """
        Analiza tendencia del índice en una ventana temporal.
        
        Args:
            window: Número de registros a analizar
            
        Returns:
            Análisis de tendencia
        """
        if len(self.index_history) < 2:
            return {
                'trend': 'INSUFICIENTE',
                'message': 'Datos insuficientes para análisis de tendencia'
            }
        
        recent_indices = [
            record['index_value'] 
            for record in self.index_history[-window:]
        ]
        
        # Calcular tendencia simple
        if len(recent_indices) >= 2:
            slope = np.polyfit(range(len(recent_indices)), recent_indices, 1)[0]
            
            if slope > 0.05:
                trend = 'CRECIENTE'
            elif slope < -0.05:
                trend = 'DECRECIENTE'
            else:
                trend = 'ESTABLE'
        else:
            trend = 'ESTABLE'
        
        return {
            'trend': trend,
            'window_size': len(recent_indices),
            'mean_index': float(np.mean(recent_indices)),
            'std_dev': float(np.std(recent_indices)),
            'min_index': float(np.min(recent_indices)),
            'max_index': float(np.max(recent_indices))
        }
