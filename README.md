# IASi - Índice de Anomalía Sísmica inteligente

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**Entrega SpaceApps NASA 2025**

## 📋 Descripción

IASi (Índice de Anomalía Sísmica inteligente) es un prototipo desarrollado para la Cordillera Andina que fusiona señales naturales y biológicas con observación satelital (InSAR) para emitir alertas semanales de riesgo sísmico.

El sistema integra datos de **cinco fuentes clave**:
- **A (Animales)**: Comportamiento animal anómalo
- **R (Radón)**: Niveles de gas radón en el suelo
- **D (Deformación)**: Datos satelitales InSAR de deformación terrestre
- **M (Marino)**: Anomalías marinas (temperatura, nivel del mar)
- **S (Sensores)**: Datos de sensores sísmicos

### 🎯 Características Principales

- **Normalización automática**: Todas las señales se normalizan a escala [0,1]
- **Índice probabilístico**: Integración ponderada de señales con umbrales auditables
- **Trazabilidad completa**: Cada señal y cálculo mantiene su historial y metadatos
- **Alertas semanales**: Sistema automático de generación de alertas con niveles de riesgo
- **Análisis de tendencias**: Detección de patrones y tendencias en el tiempo

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    IASi Pipeline                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Ingesta de Datos (5 fuentes)                          │
│     ├── A: Animales                                        │
│     ├── R: Radón                                           │
│     ├── D: Deformación (InSAR)                            │
│     ├── M: Marino                                          │
│     └── S: Sensores                                        │
│                         ↓                                   │
│  2. Normalización [0,1]                                    │
│     └── SignalProcessor                                    │
│                         ↓                                   │
│  3. Cálculo de Índice Probabilístico                      │
│     └── SeismicIndex (con pesos: A=0.15, R=0.20,         │
│         D=0.35, M=0.15, S=0.15)                          │
│                         ↓                                   │
│  4. Clasificación de Riesgo                               │
│     ├── BAJO     [0.0 - 0.3)                             │
│     ├── MEDIO    [0.3 - 0.6)                             │
│     ├── ALTO     [0.6 - 0.8)                             │
│     └── CRÍTICO  [0.8 - 1.0]                             │
│                         ↓                                   │
│  5. Generación de Alertas                                 │
│     └── AlertSystem (reportes semanales)                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Instalación

### Requisitos

- Python 3.7 o superior
- pip

### Pasos

1. Clonar el repositorio:
```bash
git clone https://github.com/Luciernaga-Sabionda/IASi_Entrega_SpaceApps.git
cd IASi_Entrega_SpaceApps
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## 💻 Uso

### Ejemplo Básico

```python
from iasi import IASiPipeline

# Inicializar el pipeline
pipeline = IASiPipeline()

# Datos de entrada de las 5 señales
data = {
    'A': {'value': 50, 'min': 0, 'max': 100},      # Animales
    'R': {'value': 300, 'min': 100, 'max': 500},   # Radón (Bq/m³)
    'D': {'value': 5, 'min': 0, 'max': 10},        # Deformación (mm/año)
    'M': {'value': 50, 'min': 0, 'max': 100},      # Marino
    'S': {'value': 2.5, 'min': 0, 'max': 5}        # Sensores (Richter)
}

# Procesar y generar alerta
result = pipeline.process_and_alert(data)

print(f"Índice de riesgo: {result['index']['index_value']:.4f}")
print(f"Nivel: {result['index']['risk_level']}")
print(f"Recomendaciones: {result['alert']['recommendations']}")
```

### Ejecutar Ejemplo Completo

```bash
python examples/example_usage.py
```

Este ejemplo simula una semana de monitoreo con datos sintéticos y genera:
- Procesamiento diario de señales
- Cálculo de índice de riesgo
- Alertas diarias
- Reporte semanal consolidado
- Análisis de tendencias

### Salida Esperada

```
================================================================================
IASi - Índice de Anomalía Sísmica inteligente
Simulación de monitoreo semanal - Cordillera Andina
================================================================================

DÍA 1 - 2025-01-01
SEÑALES PROCESADAS:
  [A] Animales: Valor=45.23 → Normalizado=0.4523
  [R] Radón: Valor=250.15 → Normalizado=0.3754
  [D] Deformación: Valor=3.45 → Normalizado=0.3450
  [M] Marino: Valor=35.20 → Normalizado=0.3520
  [S] Sensores: Valor=1.85 → Normalizado=0.3700

ÍNDICE DE RIESGO: 0.3712
NIVEL: MEDIO

RECOMENDACIONES PRINCIPALES:
  1. Incrementar frecuencia de monitoreo
  2. Alertar a equipos de respuesta rápida
  3. Verificar estado de infraestructura crítica
```

## 📊 Estructura del Proyecto

```
IASi_Entrega_SpaceApps/
├── iasi/                      # Paquete principal
│   ├── __init__.py           # Inicialización del paquete
│   ├── pipeline.py           # Pipeline principal
│   ├── signals.py            # Procesamiento de señales
│   ├── index.py              # Cálculo de índice sísmico
│   └── alerts.py             # Sistema de alertas
├── examples/                  # Ejemplos de uso
│   └── example_usage.py      # Ejemplo completo
├── tests/                     # Tests unitarios
│   ├── test_signals.py       # Tests de señales
│   ├── test_index.py         # Tests de índice
│   └── test_pipeline.py      # Tests de pipeline
├── requirements.txt           # Dependencias
└── README.md                 # Este archivo
```

## 🧪 Tests

Ejecutar los tests:

```bash
# Todos los tests
python -m unittest discover tests

# Test específico
python -m unittest tests.test_pipeline
```

## 📈 Metodología

### Normalización de Señales

Cada señal se normaliza usando:

```
normalized_value = (value - min_val) / (max_val - min_val)
```

Con clipping a [0, 1].

### Cálculo del Índice

El índice probabilístico se calcula como:

```
IASi = Σ(señal_normalizada_i × peso_i)
```

Pesos por defecto:
- Deformación (D): 35% (mayor peso por precisión satelital)
- Radón (R): 20%
- Animales (A): 15%
- Marino (M): 15%
- Sensores (S): 15%

### Umbrales de Riesgo

| Nivel | Rango | Interpretación |
|-------|-------|----------------|
| BAJO | [0.0 - 0.3) | Condiciones normales |
| MEDIO | [0.3 - 0.6) | Monitoreo continuo recomendado |
| ALTO | [0.6 - 0.8) | Activar protocolos de preparación |
| CRÍTICO | [0.8 - 1.0] | Emitir alerta inmediata |

## 🔍 Trazabilidad

Cada señal y cálculo mantiene:
- Timestamp de ingesta
- Valor crudo y normalizado
- Metadatos de origen
- Contribución al índice final

Ejemplo de registro:
```json
{
  "type": "D",
  "type_name": "Deformación",
  "raw_value": 5.0,
  "normalized_value": 0.5,
  "min_val": 0.0,
  "max_val": 10.0,
  "timestamp": "2025-01-01T12:00:00",
  "metadata": {
    "satellite": "Sentinel-1",
    "processing": "InSAR"
  }
}
```

## 🌍 Aplicación en la Cordillera Andina

El sistema está diseñado específicamente para:
- Monitoreo continuo de zonas sísmicamente activas
- Integración de múltiples fuentes de datos
- Alertas tempranas basadas en convergencia de señales
- Soporte a decisiones de autoridades locales

## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

## 👥 Autores
- ROXANA ANDREA SALAZAR MARIN,
- GREIMAR JOSE SALAZAR MARIN,
- JHON ALEXANDRE MENESES OSPINA,
**IASi Team - SpaceApps NASA 2025**

## 🙏 Agradecimientos
- Carolina Parada Veliz Directora de Magíster de la Univ. de Concepciòn, Chile
- NASA SpaceApps Challenge 2025
- Comunidad científica de monitoreo sísmico
- Servicios geológicos de la región Andina

---

**Nota**: Este es un prototipo de investigación. Para uso en producción, se requiere validación con datos reales y calibración con expertos en sismología.
