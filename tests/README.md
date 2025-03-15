# Pruebas del Sistema de Gestión de Turnos

Este directorio contiene las pruebas automatizadas para el Sistema de Gestión de Turnos.

## Estructura

```
tests/
├── database/       # Pruebas para los módulos de base de datos
├── models/         # Pruebas para los modelos de datos
├── ui/             # Pruebas para los componentes de la interfaz de usuario
├── utils/          # Pruebas para las utilidades
└── test_main.py    # Pruebas para el módulo principal
```

## Tipos de Pruebas

- **Pruebas Unitarias**: Prueban componentes individuales de forma aislada.
- **Pruebas de Interfaz de Usuario**: Prueban los componentes de la interfaz gráfica.
- **Pruebas de Integración**: Prueban la interacción entre diferentes componentes.

## Ejecución de Pruebas

### Requisitos Previos

Asegúrese de tener instaladas todas las dependencias de desarrollo:

```bash
pip install -r requirements.txt
```

### Ejecutar Todas las Pruebas

```bash
python run_tests.py
```

### Ejecutar Solo Pruebas Unitarias

```bash
python run_tests.py --unit
```

### Ejecutar Solo Pruebas de Interfaz de Usuario

```bash
python run_tests.py --ui
```

### Ejecutar Solo Pruebas de Integración

```bash
python run_tests.py --integration
```

### Generar Informe de Cobertura

```bash
python run_tests.py --cov
```

El informe de cobertura se generará en HTML en el directorio `htmlcov/`.

## Convenciones de Nomenclatura

- Los archivos de prueba deben comenzar con `test_`.
- Las clases de prueba deben comenzar con `Test`.
- Los métodos de prueba deben comenzar con `test_`.
- Utilice marcadores para categorizar las pruebas: `@pytest.mark.unit`, `@pytest.mark.ui`, `@pytest.mark.integration`.

## Buenas Prácticas

1. **Aislamiento**: Cada prueba debe ser independiente y no depender del estado de otras pruebas.
2. **Fixtures**: Utilice fixtures de pytest para configurar el estado inicial de las pruebas.
3. **Mocks**: Utilice mocks para simular componentes externos como la base de datos.
4. **Aserciones Claras**: Cada prueba debe tener aserciones claras y específicas.
5. **Documentación**: Documente el propósito de cada prueba con docstrings.

## Solución de Problemas

### Errores Comunes

- **ImportError**: Asegúrese de que el directorio raíz del proyecto esté en el PYTHONPATH.
- **Errores de Qt**: Para pruebas de UI, asegúrese de que QApplication se inicialice correctamente.
- **Errores de Base de Datos**: Utilice mocks para evitar conexiones reales a la base de datos durante las pruebas. 