"""
IASi (Índice de Anomalía Sísmica inteligente)
Prototipo para la Cordillera Andina que fusiona señales naturales y biológicas 
con observación satelital (InSAR) para emitir alertas semanales de riesgo sísmico.
"""

__version__ = "1.0.0"
__author__ = "IASi Team - SpaceApps NASA 2025"

from .pipeline import IASiPipeline
from .signals import SignalProcessor
from .index import SeismicIndex
from .alerts import AlertSystem

__all__ = [
    'IASiPipeline',
    'SignalProcessor',
    'SeismicIndex',
    'AlertSystem'
]
