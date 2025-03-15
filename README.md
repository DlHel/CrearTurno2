# Sistema de Gestión de Turnos
**Versión 1.2**

Sistema para la gestión de turnos de funcionarios que incluye diversas funcionalidades para crear, editar, consultar y gestionar turnos, así como el marcaje de asistencia.

## Características Principales

### Módulo Crear Turno
- Creación de turnos nuevos con validación de datos
- Implementación de turnos consecutivos
- Generación optimizada de nombres de turno
- Exportación de scripts SQL
- Detección mejorada de turnos duplicados

### Módulo Buscar y Editar Turno
- Búsqueda avanzada de turnos por diversos criterios
- Edición de turnos existentes
- Generación de scripts de actualización SQL
- Visualización mejorada de cambios realizados

### Módulo Horario Flexible
- Consulta de horarios flexibles por organismo y funcionario
- Filtros por fecha y estado
- Tabla de resultados con formato mejorado
- Visualización detallada de horarios por días

### Módulo Consulta Turno Funcionario
- Consulta de turnos asignados por organismo y funcionario
- Filtros de búsqueda avanzados
- Visualización detallada de información de turnos
- Tabla de resultados optimizada

### Módulo Marcaje Asistencia
- Registro de marcajes de entrada y salida
- Consulta de marcajes por RUT
- Validación de datos de funcionarios
- Generación de scripts SQL para persistencia

## Requisitos
- Python 3.8+
- PyQt6
- Oracle Database (cx_Oracle)
- Dependencias especificadas en requirements.txt

## Instalación

1. Clonar el repositorio:
```
git clone https://github.com/tu-usuario/sistema-turnos.git
cd sistema-turnos
```

2. Crear y activar entorno virtual:
```
python -m venv .venv
# En Windows
.venv\Scripts\activate
# En Linux/Mac
source .venv/bin/activate
```

3. Instalar dependencias:
```
pip install -r requirements.txt
```

4. Configurar la conexión a la base de datos en `src/database/oracle_connection.py`

## Ejecución
```
cd src
python main.py
```

## Estructura del Proyecto

```
src/
├── database/          # Módulos de conexión a base de datos
├── models/            # Modelos de datos
├── ui/                # Interfaces de usuario
│   ├── crear_turno/   # Módulo para crear turnos
│   ├── buscar_turno/  # Módulo para buscar y editar turnos
│   ├── horario_flexible/ # Módulo para horarios flexibles
│   ├── consulta_turno/ # Módulo para consulta de turnos por funcionario
│   ├── marcaje_asistencia/ # Módulo para registro de asistencia
│   └── main_window.py # Ventana principal de la aplicación
├── utils/             # Utilidades y helpers
└── main.py            # Punto de entrada de la aplicación
```

## Uso
1. Inicie la aplicación ejecutando `python main.py` desde el directorio `src`
2. Navegue entre los diferentes módulos usando las pestañas de la interfaz
3. Cada módulo tiene su propia documentación de ayuda contextual

## Mejoras en la Versión 1.2
- Implementación completa del módulo "Horario Flexible"
- Integración del módulo "Consulta Turno Funcionario"
- Desarrollo del módulo "Marcaje Asistencia"
- Correcciones en la detección de turnos duplicados
- Optimización en la generación de scripts SQL
- Mejoras en la interfaz de usuario y experiencia de usuario
- Validaciones adicionales en la entrada de datos

## Próximas Características Planificadas
- Exportación de datos a formatos Excel y PDF
- Integración con sistema de correo electrónico para notificaciones
- Interfaz de administración avanzada
- Módulo de reportes estadísticos

## Licencia
Uso interno - Todos los derechos reservados 