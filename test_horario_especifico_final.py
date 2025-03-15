import cx_Oracle
from datetime import time

# Datos de conexión
host = "orauchp-cluster-scan.uchile.cl"
port = 1525
service_name = "uchdb_prod.uchile.cl"
username = "USR_MANTENCION"
password = "tiMfiayGvJOvvlo"

# Clase para representar un turno
class Turno:
    def __init__(self):
        self.id_turno = None
        self.nombre = ""
        self.vigencia = 1
        self.frecuencia = "Diarios"
        self.detalles = []

# Clase para representar un detalle de turno
class TurnoDetalleDiario:
    def __init__(self, id_turno_detalle_diario, id_turno, jornada, hora_ingreso, duracion):
        self.id_turno_detalle_diario = id_turno_detalle_diario
        self.id_turno = id_turno
        self.jornada = jornada
        self.hora_ingreso = hora_ingreso
        self.duracion = duracion
        self.hora_salida = None
        self.calcular_hora_salida()
    
    def calcular_hora_salida(self):
        """Calcula la hora de salida basada en la hora de ingreso y la duración en minutos."""
        if self.hora_ingreso and self.duracion:
            minutos_totales = self.hora_ingreso.hour * 60 + self.hora_ingreso.minute + self.duracion
            horas = minutos_totales // 60
            minutos = minutos_totales % 60
            self.hora_salida = time(hour=horas % 24, minute=minutos)

def buscar_turnos_similares(connection, turno):
    """
    Busca turnos con configuración exactamente igual al proporcionado.
    Compara solo día, hora de entrada y hora de salida.
    """
    print(f"Buscando turnos similares para turno ID={turno.id_turno}, Nombre={turno.nombre}")
    
    if not turno.detalles:
        print("No hay detalles en el turno a comparar")
        return []
    
    # Mostrar detalles del turno a comparar
    print("Detalles del turno a comparar:")
    for detalle in turno.detalles:
        print(f"  - {detalle.jornada}: {detalle.hora_ingreso} - Duración: {detalle.duracion} min - Salida: {detalle.hora_salida}")
    
    # Obtener todos los turnos de la base de datos
    print("Buscando turnos con configuración similar")
    query_todos_turnos = """
    SELECT t.ID_TURNO, t.NOMBRE, t.VIGENCIA, t.FRECUENCIA,
           tdd.ID_TURNO_DETALLE_DIARIO, tdd.JORNADA, tdd.HORA_INGRESO, tdd.DURACION
    FROM ASISTENCIAS.TURNO t
    JOIN ASISTENCIAS.TURNO_DETALLE_DIARIO tdd ON t.ID_TURNO = tdd.ID_TURNO
    ORDER BY t.ID_TURNO, tdd.JORNADA
    """
    
    cursor = connection.cursor()
    cursor.execute(query_todos_turnos)
    results_todos_turnos = cursor.fetchall()
    cursor.close()
    
    if not results_todos_turnos:
        print("No se encontraron turnos en la base de datos")
        return []
    
    print(f"Se encontraron {len(results_todos_turnos)} filas de resultados")
    
    # Agrupar resultados por turno
    turnos_agrupados = {}
    for row in results_todos_turnos:
        id_turno = row[0]
        nombre = row[1]
        jornada = row[5]
        hora_ingreso = row[6]
        duracion = row[7]
        
        if id_turno not in turnos_agrupados:
            turnos_agrupados[id_turno] = {
                'nombre': nombre,
                'detalles': []
            }
        
        # Calcular hora de salida
        minutos_totales = hora_ingreso.hour * 60 + hora_ingreso.minute + duracion
        horas_salida = minutos_totales // 60
        minutos_salida = minutos_totales % 60
        hora_salida = time(hour=horas_salida % 24, minute=minutos_salida)
        
        turnos_agrupados[id_turno]['detalles'].append({
            'jornada': jornada,
            'hora_ingreso': hora_ingreso,
            'duracion': duracion,
            'hora_salida': hora_salida
        })
    
    print(f"Se agruparon en {len(turnos_agrupados)} turnos distintos")
    
    # Preparar los detalles del turno a comparar
    detalles_turno = []
    for detalle in turno.detalles:
        detalles_turno.append({
            'jornada': detalle.jornada,
            'hora_ingreso': detalle.hora_ingreso,
            'duracion': detalle.duracion,
            'hora_salida': detalle.hora_salida
        })
    
    # Crear un conjunto con los días del turno a comparar
    dias_turno = {detalle['jornada'] for detalle in detalles_turno}
    print(f"Días del turno a comparar: {dias_turno}")
    
    # Resultados para coincidencias exactas
    coincidencias_exactas = []
    
    # Buscar coincidencias
    for id_turno, info in turnos_agrupados.items():
        nombre = info['nombre']
        detalles = info['detalles']
        
        # Crear un conjunto con los días del turno candidato
        dias_candidato = {detalle['jornada'] for detalle in detalles}
        
        # Si los conjuntos de días son diferentes, no hay coincidencia
        if dias_turno != dias_candidato:
            continue
        
        print(f"\nEvaluando turno ID={id_turno}, Nombre={nombre}")
        print(f"Días coinciden: {dias_turno} == {dias_candidato}")
        
        # Verificar coincidencia exacta
        es_coincidencia_exacta = True
        
        # Crear diccionarios para facilitar la comparación por día
        detalles_turno_dict = {detalle['jornada']: detalle for detalle in detalles_turno}
        detalles_candidato_dict = {detalle['jornada']: detalle for detalle in detalles}
        
        # Comparar cada día
        for dia in dias_turno:
            detalle_original = detalles_turno_dict[dia]
            detalle_comparar = detalles_candidato_dict[dia]
            
            # Convertimos a minutos para comparar hora de ingreso
            minutos_ingreso_orig = detalle_original['hora_ingreso'].hour * 60 + detalle_original['hora_ingreso'].minute
            minutos_ingreso_comp = detalle_comparar['hora_ingreso'].hour * 60 + detalle_comparar['hora_ingreso'].minute
            
            print(f"  Comparando {dia}:")
            print(f"    Hora ingreso original: {detalle_original['hora_ingreso']} ({minutos_ingreso_orig} min)")
            print(f"    Hora ingreso comparar: {detalle_comparar['hora_ingreso']} ({minutos_ingreso_comp} min)")
            
            # Para coincidencia exacta, las horas de ingreso deben ser idénticas
            if minutos_ingreso_orig != minutos_ingreso_comp:
                print(f"    ❌ Horas de ingreso diferentes")
                es_coincidencia_exacta = False
                break
            else:
                print(f"    ✓ Horas de ingreso iguales")
            
            # Convertimos a minutos para comparar hora de salida
            minutos_salida_orig = detalle_original['hora_salida'].hour * 60 + detalle_original['hora_salida'].minute
            minutos_salida_comp = detalle_comparar['hora_salida'].hour * 60 + detalle_comparar['hora_salida'].minute
            
            print(f"    Hora salida original: {detalle_original['hora_salida']} ({minutos_salida_orig} min)")
            print(f"    Hora salida comparar: {detalle_comparar['hora_salida']} ({minutos_salida_comp} min)")
            
            # Para coincidencia exacta, las horas de salida deben ser idénticas
            if minutos_salida_orig != minutos_salida_comp:
                print(f"    ❌ Horas de salida diferentes")
                es_coincidencia_exacta = False
                break
            else:
                print(f"    ✓ Horas de salida iguales")
        
        if es_coincidencia_exacta:
            print(f"✅ Encontrada coincidencia exacta con ID={id_turno}")
            coincidencias_exactas.append((id_turno, nombre, detalles))
    
    print(f"Filtrado completado. Se encontraron {len(coincidencias_exactas)} coincidencias exactas")
    return coincidencias_exactas

def main():
    try:
        # Crear DSN
        dsn = cx_Oracle.makedsn(
            host,
            port,
            service_name=service_name
        )
        
        # Conectar a la base de datos
        print("Conectando a la base de datos...")
        connection = cx_Oracle.connect(
            user=username,
            password=password,
            dsn=dsn
        )
        print("Conexión establecida correctamente")
        
        # Crear un turno de prueba con el horario específico
        turno = Turno()
        turno.id_turno = None  # No asignamos ID para buscar por configuración
        turno.nombre = "Turno de prueba - Lu-Ju 9:00-18:15, Vi 9:00-16:00"
        
        # Agregar detalles para Lunes a Jueves (9:00 a 18:15)
        for dia in ['Lunes', 'Martes', 'Miércoles', 'Jueves']:
            detalle = TurnoDetalleDiario(
                id_turno_detalle_diario=None,
                id_turno=None,
                jornada=dia,
                hora_ingreso=time(9, 0),  # 9:00 AM
                duracion=555  # 9 horas y 15 minutos (555 minutos)
            )
            turno.detalles.append(detalle)
        
        # Agregar detalle para Viernes (9:00 a 16:00)
        detalle_viernes = TurnoDetalleDiario(
            id_turno_detalle_diario=None,
            id_turno=None,
            jornada='Viernes',
            hora_ingreso=time(9, 0),  # 9:00 AM
            duracion=420  # 7 horas (420 minutos)
        )
        turno.detalles.append(detalle_viernes)
        
        print(f"Turno creado: ID={turno.id_turno}, Nombre={turno.nombre}")
        print(f"Detalles: {len(turno.detalles)} días")
        for d in turno.detalles:
            print(f"  - {d.jornada}: {d.hora_ingreso} - Duración: {d.duracion} min - Salida: {d.hora_salida}")
        
        # Buscar turnos similares
        print("\nBuscando turnos similares...")
        similares = buscar_turnos_similares(connection, turno)
        
        # Mostrar resultados
        print(f"\nSe encontraron {len(similares)} turnos similares:")
        for idx, (id_turno, nombre, detalles) in enumerate(similares):
            print(f"Turno similar #{idx+1}: ID={id_turno}, Nombre={nombre}")
            print(f"  Detalles: {len(detalles)} días")
            for detalle in detalles:
                print(f"    {detalle['jornada']}: {detalle['hora_ingreso']} - Duración: {detalle['duracion']} min - Salida: {detalle['hora_salida']}")
        
        # Cerrar conexión
        connection.close()
        print("\nConexión cerrada correctamente")
        
    except Exception as e:
        print(f"Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 