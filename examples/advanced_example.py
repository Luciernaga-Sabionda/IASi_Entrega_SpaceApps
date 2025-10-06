"""
Ejemplo avanzado mostrando personalización de pesos y exportación.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from iasi import IASiPipeline
import json


def main():
    print("="*80)
    print("IASi - Ejemplo Avanzado")
    print("Personalización de pesos y exportación de alertas")
    print("="*80)
    print()
    
    # Inicializar pipeline con pesos personalizados
    # En este caso, damos más peso a los sensores directos
    custom_weights = {
        'A': 0.10,  # Animales: 10%
        'R': 0.15,  # Radón: 15%
        'D': 0.40,  # Deformación: 40% (mayor peso)
        'M': 0.10,  # Marino: 10%
        'S': 0.25   # Sensores: 25% (mayor peso)
    }
    
    print("Pesos personalizados:")
    for signal, weight in custom_weights.items():
        print(f"  {signal}: {weight*100:.0f}%")
    print()
    
    pipeline = IASiPipeline(weights=custom_weights)
    
    # Escenario: Alta deformación detectada por InSAR
    data = {
        'A': {'value': 45, 'min': 0, 'max': 100},      # Comportamiento normal
        'R': {'value': 250, 'min': 100, 'max': 500},   # Radón moderado
        'D': {'value': 9.2, 'min': 0, 'max': 10},      # Alta deformación!
        'M': {'value': 30, 'min': 0, 'max': 100},      # Marino normal
        'S': {'value': 4.1, 'min': 0, 'max': 5}        # Actividad sísmica elevada
    }
    
    context = {
        'region': 'Cordillera Andina - Zona Norte',
        'coordinates': {'lat': -18.5, 'lon': -69.3},
        'elevation': 4500,
        'observation_date': '2025-10-06'
    }
    
    # Procesar
    result = pipeline.process_and_alert(data, context)
    
    print("="*80)
    print("RESULTADO DEL PROCESAMIENTO")
    print("="*80)
    print(f"Índice: {result['index']['index_value']:.4f}")
    print(f"Nivel: {result['index']['risk_level']}")
    print()
    
    # Exportar en formato JSON
    print("="*80)
    print("ALERTA EXPORTADA (JSON)")
    print("="*80)
    alert_json = pipeline.alert_system.export_alert(result['alert'], format='json')
    print(alert_json)
    print()
    
    # Guardar en archivo
    output_file = '/tmp/iasi_alert.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(alert_json)
    print(f"✓ Alerta guardada en: {output_file}")
    print()
    
    # Exportar en formato texto
    print("="*80)
    print("ALERTA EXPORTADA (TEXTO)")
    print("="*80)
    alert_text = pipeline.alert_system.export_alert(result['alert'], format='text')
    print(alert_text)
    
    # Comparar con pesos por defecto
    print("="*80)
    print("COMPARACIÓN: ¿Qué pasaría con pesos por defecto?")
    print("="*80)
    
    pipeline_default = IASiPipeline()
    result_default = pipeline_default.process_and_alert(data, context)
    
    print(f"Con pesos personalizados: Índice = {result['index']['index_value']:.4f}, Nivel = {result['index']['risk_level']}")
    print(f"Con pesos por defecto:    Índice = {result_default['index']['index_value']:.4f}, Nivel = {result_default['index']['risk_level']}")
    print()
    print("Diferencia en contribuciones:")
    for signal_type in ['A', 'R', 'D', 'M', 'S']:
        contrib_custom = result['index']['signal_contributions'][signal_type]['contribution']
        contrib_default = result_default['index']['signal_contributions'][signal_type]['contribution']
        diff = contrib_custom - contrib_default
        print(f"  {signal_type}: {contrib_custom:.4f} vs {contrib_default:.4f} (diff: {diff:+.4f})")


if __name__ == "__main__":
    main()
