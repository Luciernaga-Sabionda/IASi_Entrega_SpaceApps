"""
Ejemplo simple de uso básico del sistema IASi.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from iasi import IASiPipeline


def main():
    print("="*80)
    print("IASi - Índice de Anomalía Sísmica inteligente")
    print("Ejemplo básico de procesamiento")
    print("="*80)
    print()
    
    # Inicializar el pipeline
    pipeline = IASiPipeline()
    
    # Datos de ejemplo de las 5 señales
    data = {
        'A': {  # Animales - Comportamiento anómalo
            'value': 65,
            'min': 0,
            'max': 100,
            'metadata': {
                'location': 'Zona Andina Central',
                'species_count': 12,
                'anomaly_type': 'comportamiento_inquieto'
            }
        },
        'R': {  # Radón - Concentración de gas
            'value': 350,
            'min': 100,
            'max': 500,
            'metadata': {
                'unit': 'Bq/m³',
                'station': 'Estación Monitoreo Radón #3',
                'depth': '2m'
            }
        },
        'D': {  # Deformación - Datos InSAR
            'value': 7.5,
            'min': 0,
            'max': 10,
            'metadata': {
                'unit': 'mm/año',
                'satellite': 'Sentinel-1',
                'processing': 'InSAR',
                'confidence': 'high'
            }
        },
        'M': {  # Marino - Anomalías oceánicas
            'value': 55,
            'min': 0,
            'max': 100,
            'metadata': {
                'parameter': 'temperatura_anomalía',
                'unit': '°C',
                'buoy_id': 'BUOY-002'
            }
        },
        'S': {  # Sensores - Sismómetros
            'value': 3.2,
            'min': 0,
            'max': 5,
            'metadata': {
                'type': 'sismómetro',
                'unit': 'Richter',
                'network': 'Red Sísmica Nacional'
            }
        }
    }
    
    # Contexto regional
    context = {
        'region': 'Cordillera Andina',
        'coordinates': {'lat': -33.4489, 'lon': -70.6693},
        'population_nearby': 50000
    }
    
    # Procesar datos y generar alerta
    result = pipeline.process_and_alert(data, context)
    
    # Mostrar resultados detallados
    print("1. SEÑALES PROCESADAS")
    print("-" * 80)
    for signal_type in ['A', 'R', 'D', 'M', 'S']:
        signal = result['signals'][signal_type]
        print(f"\n[{signal_type}] {signal['type_name']}")
        print(f"  Valor crudo: {signal['raw_value']:.2f} [{signal['min_val']:.0f}-{signal['max_val']:.0f}]")
        print(f"  Normalizado: {signal['normalized_value']:.4f}")
        if signal['metadata']:
            print(f"  Metadata: {signal['metadata']}")
    
    print("\n" + "="*80)
    print("2. ÍNDICE DE RIESGO CALCULADO")
    print("-" * 80)
    index = result['index']
    print(f"\nÍndice: {index['index_value']:.4f}")
    print(f"Nivel de Riesgo: {index['risk_level']}")
    
    print("\nContribución por señal:")
    for signal_type, contrib in index['signal_contributions'].items():
        print(f"  {signal_type}: {contrib['normalized_value']:.4f} × {contrib['weight']:.2f} = {contrib['contribution']:.4f}")
    
    print("\n" + "="*80)
    print("3. ALERTA GENERADA")
    print("-" * 80)
    alert = result['alert']
    print(f"\nID: {alert['alert_id']}")
    print(f"Fecha: {alert['timestamp']}")
    print(f"Semana: {alert['week_number']}/{alert['year']}")
    
    print(f"\nInterpretación:")
    print(f"  {alert['interpretation']}")
    
    print(f"\nRecomendaciones:")
    for i, rec in enumerate(alert['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    print("\n" + "="*80)
    print("4. ESTADO DEL SISTEMA")
    print("-" * 80)
    status = pipeline.get_status()
    print(f"\nSeñales procesadas: {status['total_signals_processed']}")
    print(f"Índices calculados: {status['total_indices_calculated']}")
    print(f"Alertas generadas: {status['total_alerts_generated']}")
    
    print("\nPesos configurados:")
    for signal_type, weight in status['current_weights'].items():
        print(f"  {signal_type}: {weight:.2f}")
    
    print("\nUmbrales de riesgo:")
    for level, (min_val, max_val) in status['thresholds'].items():
        print(f"  {level}: [{min_val:.1f} - {max_val:.1f})")
    
    print("\n" + "="*80)
    print("✓ Procesamiento completado exitosamente")
    print("="*80)


if __name__ == "__main__":
    main()
