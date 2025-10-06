"""
Sistema de alertas semanales de riesgo sísmico.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import json


class AlertSystem:
    """
    Sistema de alertas semanales que genera reportes 
    basados en el índice de riesgo sísmico.
    """
    
    def __init__(self):
        self.alerts: List[Dict[str, Any]] = []
    
    def generate_alert(self, index_record: Dict[str, Any], 
                      context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Genera una alerta basada en el índice de riesgo.
        
        Args:
            index_record: Registro del índice calculado
            context: Información contextual adicional
            
        Returns:
            Alerta generada con toda la información relevante
        """
        alert = {
            'alert_id': f"IASi-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'index_value': index_record['index_value'],
            'risk_level': index_record['risk_level'],
            'signal_contributions': index_record['signal_contributions'],
            'interpretation': self._get_risk_interpretation(index_record['risk_level']),
            'recommendations': self._get_recommendations(index_record['risk_level']),
            'context': context or {},
            'week_number': datetime.now().isocalendar()[1],
            'year': datetime.now().year
        }
        
        self.alerts.append(alert)
        
        return alert
    
    def _get_risk_interpretation(self, risk_level: str) -> str:
        """Obtiene la interpretación del nivel de riesgo."""
        interpretations = {
            'BAJO': 'Riesgo sísmico bajo. Condiciones normales en la región.',
            'MEDIO': 'Riesgo sísmico medio. Se detectan anomalías que requieren monitoreo continuo.',
            'ALTO': 'Riesgo sísmico alto. Múltiples señales indican actividad anómala. Activar protocolos de preparación.',
            'CRÍTICO': 'Riesgo sísmico crítico. Convergencia de señales de alerta. Emitir alerta inmediata a autoridades.'
        }
        return interpretations.get(risk_level, 'Nivel desconocido')
    
    def _get_recommendations(self, risk_level: str) -> List[str]:
        """Obtiene recomendaciones basadas en el nivel de riesgo."""
        recommendations = {
            'BAJO': [
                'Mantener monitoreo rutinario de todas las señales',
                'Revisar y actualizar planes de emergencia',
                'Continuar con calibración de sensores'
            ],
            'MEDIO': [
                'Incrementar frecuencia de monitoreo',
                'Alertar a equipos de respuesta rápida',
                'Verificar estado de infraestructura crítica',
                'Preparar comunicados preventivos'
            ],
            'ALTO': [
                'Activar protocolos de preparación',
                'Notificar a autoridades locales y regionales',
                'Intensificar monitoreo de señales críticas',
                'Preparar evacuaciones preventivas si es necesario',
                'Activar centros de operaciones de emergencia'
            ],
            'CRÍTICO': [
                'ALERTA INMEDIATA: Emitir comunicado urgente',
                'Activar todos los protocolos de emergencia',
                'Coordinar con autoridades nacionales',
                'Preparar evacuación de zonas de alto riesgo',
                'Activar cadena de comando de emergencia',
                'Mantener comunicación constante con población'
            ]
        }
        return recommendations.get(risk_level, ['Consultar con expertos'])
    
    def generate_weekly_report(self, week_alerts: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Genera reporte semanal consolidado.
        
        Args:
            week_alerts: Alertas de la semana (usa las últimas si no se especifica)
            
        Returns:
            Reporte semanal completo
        """
        if week_alerts is None:
            # Obtener alertas de la última semana
            week_ago = datetime.now() - timedelta(days=7)
            week_alerts = [
                alert for alert in self.alerts
                if datetime.fromisoformat(alert['timestamp']) >= week_ago
            ]
        
        if not week_alerts:
            return {
                'status': 'NO_DATA',
                'message': 'No hay alertas para generar reporte semanal'
            }
        
        # Analizar alertas de la semana
        risk_levels = [alert['risk_level'] for alert in week_alerts]
        index_values = [alert['index_value'] for alert in week_alerts]
        
        # Determinar nivel de riesgo predominante
        risk_counts = {level: risk_levels.count(level) for level in set(risk_levels)}
        predominant_risk = max(risk_counts, key=risk_counts.get)
        
        # Calcular estadísticas
        import numpy as np
        mean_index = float(np.mean(index_values))
        max_index = float(np.max(index_values))
        min_index = float(np.min(index_values))
        
        report = {
            'report_id': f"IASi-Weekly-{datetime.now().strftime('%Y-W%W')}",
            'period': {
                'start': week_alerts[0]['timestamp'],
                'end': week_alerts[-1]['timestamp'],
                'week_number': datetime.now().isocalendar()[1],
                'year': datetime.now().year
            },
            'summary': {
                'total_alerts': len(week_alerts),
                'predominant_risk_level': predominant_risk,
                'risk_distribution': risk_counts,
                'mean_index': mean_index,
                'max_index': max_index,
                'min_index': min_index
            },
            'alerts': week_alerts,
            'interpretation': self._get_weekly_interpretation(predominant_risk, risk_counts),
            'recommendations': self._get_recommendations(predominant_risk),
            'generated_at': datetime.now().isoformat()
        }
        
        return report
    
    def _get_weekly_interpretation(self, predominant_risk: str, 
                                   risk_counts: Dict[str, int]) -> str:
        """Genera interpretación del reporte semanal."""
        total = sum(risk_counts.values())
        distribution = ', '.join([
            f"{level}: {count} ({count/total*100:.1f}%)"
            for level, count in sorted(risk_counts.items())
        ])
        
        return (f"Durante la semana se registró un nivel de riesgo predominante {predominant_risk}. "
                f"Distribución de alertas: {distribution}.")
    
    def export_alert(self, alert: Dict[str, Any], format: str = 'json') -> str:
        """
        Exporta una alerta en el formato especificado.
        
        Args:
            alert: Alerta a exportar
            format: Formato de exportación ('json', 'text')
            
        Returns:
            Alerta en formato solicitado
        """
        if format == 'json':
            return json.dumps(alert, indent=2, ensure_ascii=False)
        
        elif format == 'text':
            text = f"""
{'='*80}
ALERTA IASi - Índice de Anomalía Sísmica inteligente
{'='*80}
ID: {alert['alert_id']}
Fecha: {alert['timestamp']}
Semana: {alert['week_number']}/{alert['year']}

ÍNDICE DE RIESGO: {alert['index_value']:.4f}
NIVEL: {alert['risk_level']}

INTERPRETACIÓN:
{alert['interpretation']}

CONTRIBUCIÓN POR SEÑAL:
"""
            for signal_type, contrib in alert['signal_contributions'].items():
                text += f"  - {signal_type}: {contrib['normalized_value']:.4f} (peso: {contrib['weight']:.2f}, contribución: {contrib['contribution']:.4f})\n"
            
            text += f"\nRECOMENDACIONES:\n"
            for i, rec in enumerate(alert['recommendations'], 1):
                text += f"  {i}. {rec}\n"
            
            text += f"\n{'='*80}\n"
            
            return text
        
        else:
            raise ValueError(f"Formato no soportado: {format}")
    
    def get_alerts(self, limit: int = None, risk_level: str = None) -> List[Dict[str, Any]]:
        """
        Obtiene alertas con filtros opcionales.
        
        Args:
            limit: Número máximo de alertas
            risk_level: Filtrar por nivel de riesgo
            
        Returns:
            Lista de alertas
        """
        alerts = self.alerts.copy()
        
        if risk_level:
            alerts = [a for a in alerts if a['risk_level'] == risk_level]
        
        if limit:
            alerts = alerts[-limit:]
        
        return alerts
