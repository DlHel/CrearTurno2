from src.database.turno_dao import TurnoDAO
from src.models.turno import Turno, TurnoDetalleDiario
from datetime import time

# Crear instancia del DAO
dao = TurnoDAO()

# Crear dos turnos con el mismo ID para simular el problema
t1 = Turno()
t1.id_turno = 76
t1.nombre = 'Turno 1'
t1.vigencia = 'A'
t1.frecuencia = 'Diarios'
d1 = TurnoDetalleDiario(0, 76, 'Lunes', time(9, 0), 540)
d2 = TurnoDetalleDiario(0, 76, 'Martes', time(9, 0), 540)
t1.detalles = [d1, d2]

t2 = Turno()
t2.id_turno = 76  # Mismo ID que t1
t2.nombre = 'Turno 2'
t2.vigencia = 'A'
t2.frecuencia = 'Diarios'
d3 = TurnoDetalleDiario(0, 76, 'Miércoles', time(9, 0), 540)
d4 = TurnoDetalleDiario(0, 76, 'Jueves', time(9, 0), 540)
t2.detalles = [d3, d4]

turnos = [t1, t2]

# Obtener los últimos IDs
ultimo_id_turno = dao.obtener_ultimo_id_turno()
ultimo_id_detalle = dao.obtener_ultimo_id_detalle()

print(f"Último ID de turno: {ultimo_id_turno}")
print(f"Último ID de detalle: {ultimo_id_detalle}")

# Crear una copia de los turnos con IDs únicos
turnos_procesados = []

for i, turno_original in enumerate(turnos):
    turno = Turno()
    turno.id_turno = ultimo_id_turno + i
    turno.nombre = turno_original.nombre
    turno.vigencia = turno_original.vigencia
    turno.frecuencia = turno_original.frecuencia
    
    # Copiar los detalles con IDs correlativos
    for j, detalle_original in enumerate(turno_original.detalles):
        detalle = TurnoDetalleDiario(
            id_turno_detalle_diario=ultimo_id_detalle + j,
            id_turno=turno.id_turno,
            jornada=detalle_original.jornada,
            hora_ingreso=detalle_original.hora_ingreso,
            duracion=detalle_original.duracion
        )
        turno.detalles.append(detalle)
    
    turnos_procesados.append(turno)
    ultimo_id_detalle += len(turno.detalles)

# Generar script para cada turno
script = ''
for i, turno in enumerate(turnos_procesados):
    print(f"Generando SQL para turno {i+1}: ID={turno.id_turno}, Nombre={turno.nombre}")
    print(f"Detalles: {[d.id_turno_detalle_diario for d in turno.detalles]}")
    
    # Usar el método de TurnoDAO para generar el script
    turno_script = dao.generar_script_sql(turno)
    if turno_script:
        script += f"-- Turno {i+1}: {turno.nombre} (ID: {turno.id_turno})\n"
        script += turno_script + "\n\n"

print("\n=== SCRIPT SQL GENERADO ===\n")
print(script) 