"""
Ejemplo de uso del sistema IASi.
Demuestra cómo ingestar datos y generar alertas semanales.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from iasi import IASiPipeline
import random
from datetime import datetime, timedelta


def simulate_weekly_data():
    """Simula datos de una semana para demostración."""
    print("="*80)
    print("IASi - Índice de Anomalía Sísmica inteligente")
    print("Simulación de monitoreo semanal - Cordillera Andina")
    print("="*80)
    print()
    
    # Inicializar pipeline
    pipeline = IASiPipeline()
    
    # Simular datos de 7 días
    for day in range(7):
        print(f"\n{'='*80}")
        print(f"DÍA {day + 1} - {(datetime.now() - timedelta(days=6-day)).strftime('%Y-%m-%d')}")
        print(f"{'='*80}\n")
        
        # Generar datos simulados con tendencia creciente
        base_risk = 0.3 + (day * 0.08)  # Riesgo incrementa día a día
        
        data = {
            'A': {  # Animales
                'value': 40 + base_risk * 30 + random.uniform(-5, 5),
                'min': 0,
                'max': 100,
                'metadata': {
                    'location': 'Zona Andina Central',
                    'species_count': random.randint(5, 15),
                    'anomaly_type': 'comportamiento_inquieto'
                }
            },
            'R': {  # Radón
                'value': 150 + base_risk * 200 + random.uniform(-20, 20),
                'min': 100,
                'max': 500,
                'metadata': {
                    'unit': 'Bq/m³',
                    'station': 'Estación Monitoreo Radón #3',
                    'depth': '2m'
                }
            },
            'D': {  # Deformación InSAR
                'value': 2 + base_risk * 8 + random.uniform(-0.5, 0.5),
                'min': 0,
                'max': 10,
                'metadata': {
                    'unit': 'mm/año',
                    'satellite': 'Sentinel-1',
                    'processing': 'InSAR',
                    'confidence': 'high'
                }
            },
            'M': {  # Marino
                'value': 20 + base_risk * 40 + random.uniform(-3, 3),
                'min': 0,
                'max': 100,
                'metadata': {
                    'parameter': 'temperatura_anomalía',
                    'unit': '°C',
                    'buoy_id': 'BUOY-002'
                }
            },
            'S': {  # Sensores
                'value': 1.5 + base_risk * 4 + random.uniform(-0.2, 0.2),
                'min': 0,
                'max': 5,
                'metadata': {
                    'type': 'sismómetro',
                    'unit': 'Richter',
                    'network': 'Red Sísmica Nacional'
                }
            }
        }
        
        # Procesar y generar alerta
        context = {
            'region': 'Cordillera Andina',
            'day_of_week': day + 1,
            'coordinates': {'lat': -33.4489, 'lon': -70.6693}
        }
        
        result = pipeline.process_and_alert(data, context)
        
        # Mostrar resultados
        print("SEÑALES PROCESADAS:")
        for signal_type, signal_data in result['signals'].items():
            print(f"  [{signal_type}] {signal_data['type_name']}: "
                  f"Valor={signal_data['raw_value']:.2f} → "
                  f"Normalizado={signal_data['normalized_value']:.4f}")
        
        print(f"\nÍNDICE DE RIESGO: {result['index']['index_value']:.4f}")
        print(f"NIVEL: {result['index']['risk_level']}")
        print(f"\nINTERPRETACIÓN:")
        print(f"  {result['alert']['interpretation']}")
        
        print(f"\nRECOMENDACIONES PRINCIPALES:")
        for i, rec in enumerate(result['alert']['recommendations'][:3], 1):
            print(f"  {i}. {rec}")
    
    # Generar reporte semanal
    print("\n" + "="*80)
    print("REPORTE SEMANAL")
    print("="*80 + "\n")
    
    weekly_report = pipeline.generate_weekly_report()
    
    print(f"ID Reporte: {weekly_report['report_id']}")
    print(f"Período: Semana {weekly_report['period']['week_number']}/{weekly_report['period']['year']}")
    print(f"\nRESUMEN:")
    print(f"  Total de alertas: {weekly_report['summary']['total_alerts']}")
    print(f"  Nivel predominante: {weekly_report['summary']['predominant_risk_level']}")
    print(f"  Índice medio: {weekly_report['summary']['mean_index']:.4f}")
    print(f"  Índice máximo: {weekly_report['summary']['max_index']:.4f}")
    print(f"\nDISTRIBUCIÓN DE RIESGO:")
    for level, count in weekly_report['summary']['risk_distribution'].items():
        print(f"  {level}: {count} alertas")
    
    print(f"\nINTERPRETACIÓN SEMANAL:")
    print(f"  {weekly_report['interpretation']}")
    
    # Análisis de tendencia
    print("\n" + "="*80)
    print("ANÁLISIS DE TENDENCIA")
    print("="*80 + "\n")
    
    trend = pipeline.get_trend_analysis()
    print(f"Tendencia: {trend['trend']}")
    print(f"Índice medio (7 días): {trend['mean_index']:.4f}")
    print(f"Rango: [{trend['min_index']:.4f}, {trend['max_index']:.4f}]")
    print(f"Desviación estándar: {trend['std_dev']:.4f}")
    
    # Exportar última alerta en formato texto
    print("\n" + "="*80)
    print("EJEMPLO DE ALERTA EXPORTADA (FORMATO TEXTO)")
    print("="*80)
    
    last_alert = pipeline.alert_system.alerts[-1]
    alert_text = pipeline.alert_system.export_alert(last_alert, format='text')
    print(alert_text)


if __name__ == "__main__":
    simulate_weekly_data()
