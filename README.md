# Sistema de Gestión de Turnos

Sistema modular para la gestión de turnos laborales, desarrollado en Python con interfaz gráfica en PyQt6.

## Características Principales

- Creación y gestión de turnos laborales
- Búsqueda y edición de turnos existentes
- Gestión de horarios flexibles
- Consulta de turnos por funcionario
- Control de marcaje de asistencia

## Estructura del Proyecto

```
CrearTurno2/
├── src/
│   ├── database/
│   │   ├── oracle_connection.py
│   │   ├── mongo_connection.py
│   │   └── cache_manager.py
│   ├── models/
│   │   ├── turno.py
│   │   └── turno_detalle.py
│   ├── ui/
│   │   ├── main_window.py
│   │   ├── crear_turno/
│   │   ├── buscar_turno/
│   │   ├── horario_flexible/
│   │   └── consulta_turno/
│   └── utils/
│       ├── validators.py
│       └── sql_generator.py
├── requirements.txt
└── README.md
```

## Requisitos del Sistema

- Python 3.8 o superior
- Oracle Client 19c
- MongoDB

## Configuración de Base de Datos

### Oracle
- Conexión: `jdbc:oracle:thin:@//orauchp-cluster-scan.uchile.cl:1525/uchdb_prod.uchile.cl`
- Usuario: USR_MANTENCION (solo lectura)

### MongoDB
- Configuración pendiente

## Instalación

1. Clonar el repositorio
2. Crear un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```
3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Módulos Principales

### 1. Crear Turno
- Creación de turnos con detalle de jornada
- Asignación automática de IDs
- Validación de duplicados
- Generación de scripts SQL

### 2. Buscar y Editar Turno
- Búsqueda por ID o nombre
- Edición de detalles del turno
- Gestión de estados
- Exportación de scripts de actualización

### 3. Horario Flexible
- Gestión de horarios flexibles
- Configuración de parámetros

### 4. Consulta Turno Funcionario
- Visualización de turnos asignados
- Historial de turnos

### 5. Marcaje Asistencia
- Registro de asistencia
- Consulta de marcajes 