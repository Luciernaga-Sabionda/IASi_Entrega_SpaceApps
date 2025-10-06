"""
Módulo de procesamiento de señales para IASi.
Normaliza señales de diferentes fuentes a escala [0,1].
"""

from typing import Dict, Any, List
import numpy as np
from datetime import datetime


class SignalProcessor:
    """
    Procesa y normaliza señales de cinco fuentes clave:
    - A (Animales): Comportamiento animal anómalo
    - R (Radón): Niveles de gas radón
    - D (Deformación): Datos satelitales InSAR
    - M (Marino): Anomalías marinas
    - S (Sensores): Datos de sensores sísmicos
    """
    
    SIGNAL_TYPES = {
        'A': 'Animales',
        'R': 'Radón',
        'D': 'Deformación',
        'M': 'Marino',
        'S': 'Sensores'
    }
    
    def __init__(self):
        self.signal_history: Dict[str, List[Dict[str, Any]]] = {
            'A': [],
            'R': [],
            'D': [],
            'M': [],
            'S': []
        }
    
    def normalize_signal(self, value: float, min_val: float, max_val: float) -> float:
        """
        Normaliza un valor a escala [0,1].
        
        Args:
            value: Valor a normalizar
            min_val: Valor mínimo del rango
            max_val: Valor máximo del rango
            
        Returns:
            Valor normalizado entre 0 y 1
        """
        if max_val == min_val:
            return 0.5
        
        normalized = (value - min_val) / (max_val - min_val)
        return np.clip(normalized, 0.0, 1.0)
    
    def ingest_signal(self, signal_type: str, value: float, 
                      min_val: float = 0.0, max_val: float = 100.0,
                      metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Ingesta y normaliza una señal.
        
        Args:
            signal_type: Tipo de señal ('A', 'R', 'D', 'M', 'S')
            value: Valor crudo de la señal
            min_val: Valor mínimo del rango esperado
            max_val: Valor máximo del rango esperado
            metadata: Metadatos adicionales de la señal
            
        Returns:
            Diccionario con señal normalizada y trazabilidad
        """
        if signal_type not in self.SIGNAL_TYPES:
            raise ValueError(f"Tipo de señal inválido: {signal_type}. "
                           f"Debe ser uno de: {list(self.SIGNAL_TYPES.keys())}")
        
        normalized_value = self.normalize_signal(value, min_val, max_val)
        
        signal_data = {
            'type': signal_type,
            'type_name': self.SIGNAL_TYPES[signal_type],
            'raw_value': value,
            'normalized_value': normalized_value,
            'min_val': min_val,
            'max_val': max_val,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.signal_history[signal_type].append(signal_data)
        
        return signal_data
    
    def get_latest_signals(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene las últimas señales de cada tipo.
        
        Returns:
            Diccionario con las últimas señales de cada tipo
        """
        latest = {}
        for signal_type in self.SIGNAL_TYPES:
            if self.signal_history[signal_type]:
                latest[signal_type] = self.signal_history[signal_type][-1]
            else:
                latest[signal_type] = None
        
        return latest
    
    def get_signal_history(self, signal_type: str = None, 
                          limit: int = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Obtiene el historial de señales.
        
        Args:
            signal_type: Tipo de señal específico (opcional)
            limit: Número máximo de registros por tipo
            
        Returns:
            Historial de señales
        """
        if signal_type:
            if signal_type not in self.SIGNAL_TYPES:
                raise ValueError(f"Tipo de señal inválido: {signal_type}")
            history = {signal_type: self.signal_history[signal_type]}
        else:
            history = self.signal_history.copy()
        
        if limit:
            history = {k: v[-limit:] for k, v in history.items()}
        
        return history
