# Documentación Técnica - IASi

## Índice

1. [Arquitectura del Sistema](#arquitectura-del-sistema)
2. [Módulos](#módulos)
3. [API Reference](#api-reference)
4. [Ejemplos de Uso](#ejemplos-de-uso)
5. [Configuración](#configuración)

## Arquitectura del Sistema

IASi sigue una arquitectura modular dividida en 4 componentes principales:

### 1. SignalProcessor (`iasi/signals.py`)
Responsable de:
- Ingesta de datos de 5 fuentes (A, R, D, M, S)
- Normalización de valores a escala [0,1]
- Mantenimiento del historial de señales
- Metadatos y trazabilidad

### 2. SeismicIndex (`iasi/index.py`)
Responsable de:
- Cálculo del índice probabilístico ponderado
- Clasificación de riesgo en 4 niveles
- Análisis de tendencias
- Validación de pesos

### 3. AlertSystem (`iasi/alerts.py`)
Responsable de:
- Generación de alertas individuales
- Reportes semanales consolidados
- Recomendaciones por nivel de riesgo
- Exportación en múltiples formatos

### 4. IASiPipeline (`iasi/pipeline.py`)
Orquestador que:
- Integra todos los módulos
- Provee API de alto nivel
- Gestiona el flujo completo de datos

## Módulos

### SignalProcessor

```python
from iasi.signals import SignalProcessor

processor = SignalProcessor()

# Ingestar señal
signal = processor.ingest_signal(
    signal_type='D',  # Deformación
    value=5.0,
    min_val=0.0,
    max_val=10.0,
    metadata={'satellite': 'Sentinel-1'}
)

# Obtener historial
history = processor.get_signal_history('D', limit=10)
```

### SeismicIndex

```python
from iasi.index import SeismicIndex

# Con pesos personalizados
custom_weights = {
    'A': 0.10,
    'R': 0.15,
    'D': 0.40,
    'M': 0.10,
    'S': 0.25
}

index_calc = SeismicIndex(weights=custom_weights)

# Calcular índice
index_record = index_calc.calculate_index(signals)

# Análisis de tendencia
trend = index_calc.get_trend_analysis(window=7)
```

### AlertSystem

```python
from iasi.alerts import AlertSystem

alert_sys = AlertSystem()

# Generar alerta
alert = alert_sys.generate_alert(index_record, context)

# Exportar
json_alert = alert_sys.export_alert(alert, format='json')
text_alert = alert_sys.export_alert(alert, format='text')

# Reporte semanal
weekly_report = alert_sys.generate_weekly_report()
```

## API Reference

### IASiPipeline

#### `__init__(weights=None)`
Inicializa el pipeline.

**Parámetros:**
- `weights` (dict, opcional): Pesos personalizados para cada señal

#### `process_and_alert(data, context=None)`
Procesa datos y genera alerta completa.

**Parámetros:**
- `data` (dict): Datos de las 5 señales
- `context` (dict, opcional): Contexto adicional

**Retorna:**
```python
{
    'signals': {...},  # Señales normalizadas
    'index': {...},    # Índice calculado
    'alert': {...}     # Alerta generada
}
```

**Ejemplo:**
```python
data = {
    'A': {'value': 50, 'min': 0, 'max': 100},
    'R': {'value': 300, 'min': 100, 'max': 500},
    'D': {'value': 5, 'min': 0, 'max': 10},
    'M': {'value': 50, 'min': 0, 'max': 100},
    'S': {'value': 2.5, 'min': 0, 'max': 5}
}

result = pipeline.process_and_alert(data)
```

#### `get_status()`
Obtiene estado completo del sistema.

**Retorna:**
```python
{
    'latest_signals': {...},
    'total_signals_processed': int,
    'total_indices_calculated': int,
    'total_alerts_generated': int,
    'current_weights': {...},
    'thresholds': {...},
    'latest_index': {...},
    'latest_alert': {...}
}
```

## Ejemplos de Uso

### Ejemplo 1: Procesamiento Básico

```python
from iasi import IASiPipeline

pipeline = IASiPipeline()

data = {
    'A': {'value': 65, 'min': 0, 'max': 100},
    'R': {'value': 350, 'min': 100, 'max': 500},
    'D': {'value': 7.5, 'min': 0, 'max': 10},
    'M': {'value': 55, 'min': 0, 'max': 100},
    'S': {'value': 3.2, 'min': 0, 'max': 5}
}

result = pipeline.process_and_alert(data)

print(f"Riesgo: {result['index']['risk_level']}")
print(f"Índice: {result['index']['index_value']:.4f}")
```

### Ejemplo 2: Pesos Personalizados

```python
custom_weights = {
    'A': 0.10,
    'R': 0.15,
    'D': 0.40,  # Mayor peso a deformación
    'M': 0.10,
    'S': 0.25   # Mayor peso a sensores
}

pipeline = IASiPipeline(weights=custom_weights)
result = pipeline.process_and_alert(data)
```

### Ejemplo 3: Reporte Semanal

```python
# Procesar datos de 7 días
for day in range(7):
    daily_data = get_daily_data(day)  # Tu función
    pipeline.process_and_alert(daily_data)

# Generar reporte
report = pipeline.generate_weekly_report()

print(f"Total alertas: {report['summary']['total_alerts']}")
print(f"Nivel predominante: {report['summary']['predominant_risk_level']}")
```

### Ejemplo 4: Análisis de Tendencia

```python
trend = pipeline.get_trend_analysis(window=7)

print(f"Tendencia: {trend['trend']}")  # CRECIENTE, DECRECIENTE, ESTABLE
print(f"Índice medio: {trend['mean_index']:.4f}")
```

## Configuración

### Tipos de Señales

| Código | Nombre | Descripción | Ejemplo de Rango |
|--------|--------|-------------|------------------|
| A | Animales | Comportamiento anómalo | 0-100 |
| R | Radón | Concentración de gas (Bq/m³) | 100-500 |
| D | Deformación | Deformación InSAR (mm/año) | 0-10 |
| M | Marino | Anomalías oceánicas | 0-100 |
| S | Sensores | Actividad sísmica (Richter) | 0-5 |

### Pesos por Defecto

```python
DEFAULT_WEIGHTS = {
    'A': 0.15,  # Animales: 15%
    'R': 0.20,  # Radón: 20%
    'D': 0.35,  # Deformación: 35% (mayor peso)
    'M': 0.15,  # Marino: 15%
    'S': 0.15   # Sensores: 15%
}
```

### Umbrales de Riesgo

```python
THRESHOLDS = {
    'BAJO': (0.0, 0.3),      # [0.0 - 0.3)
    'MEDIO': (0.3, 0.6),     # [0.3 - 0.6)
    'ALTO': (0.6, 0.8),      # [0.6 - 0.8)
    'CRÍTICO': (0.8, 1.0)    # [0.8 - 1.0]
}
```

### Formato de Metadatos

Los metadatos pueden incluir cualquier información adicional:

```python
metadata = {
    'location': 'Zona Andina Central',
    'satellite': 'Sentinel-1',
    'confidence': 'high',
    'station': 'EST-001',
    # ... cualquier otro campo
}
```

## Notas de Implementación

### Normalización

La normalización se realiza usando la fórmula:

```
normalized = (value - min) / (max - min)
```

Con clipping a [0, 1]:
- Valores < min → 0.0
- Valores > max → 1.0

### Cálculo del Índice

El índice se calcula como suma ponderada:

```
IASi = Σ(señal_normalizada_i × peso_i)
```

### Trazabilidad

Cada operación mantiene:
- Timestamp ISO 8601
- Valores crudos y normalizados
- Metadatos completos
- Contribución al índice

## Manejo de Errores

### Señales Faltantes

```python
# Lanza ValueError si falta alguna señal
try:
    result = pipeline.process_and_alert(incomplete_data)
except ValueError as e:
    print(f"Error: {e}")
```

### Tipo de Señal Inválido

```python
# Lanza ValueError si el tipo no es A, R, D, M, o S
try:
    processor.ingest_signal('X', 50, 0, 100)
except ValueError as e:
    print(f"Error: {e}")
```

### Pesos Inválidos

```python
# Lanza ValueError si los pesos no suman 1.0
try:
    pipeline = IASiPipeline(weights={'A': 0.5, 'R': 0.5})
except ValueError as e:
    print(f"Error: {e}")
```

## Tests

Ejecutar tests:

```bash
# Todos los tests
python -m unittest discover tests

# Test específico
python -m unittest tests.test_pipeline

# Con verbosidad
python -m unittest discover tests -v
```

## Dependencias

- Python 3.7+
- numpy >= 1.20.0

## Licencia

MIT License - Ver LICENSE para más detalles.
