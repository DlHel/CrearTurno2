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

def obtener_turno_por_id(connection, id_turno):
    """Obtiene un turno de la base de datos por su ID."""
    print(f"Buscando turno con ID={id_turno}")
    
    query = """
    SELECT t.ID_TURNO, t.NOMBRE, t.VIGENCIA, t.FRECUENCIA,
           tdd.ID_TURNO_DETALLE_DIARIO, tdd.JORNADA, tdd.HORA_INGRESO, tdd.DURACION
    FROM ASISTENCIAS.TURNO t
    JOIN ASISTENCIAS.TURNO_DETALLE_DIARIO tdd ON t.ID_TURNO = tdd.ID_TURNO
    WHERE t.ID_TURNO = :id_turno
    ORDER BY tdd.JORNADA
    """
    
    cursor = connection.cursor()
    cursor.execute(query, id_turno=id_turno)
    results = cursor.fetchall()
    cursor.close()
    
    if not results:
        print(f"No se encontró turno con ID={id_turno}")
        return None
    
    turno = Turno()
    turno.id_turno = id_turno
    turno.nombre = results[0][1]
    turno.vigencia = results[0][2]
    turno.frecuencia = results[0][3]
    
    print(f"Turno encontrado: ID={turno.id_turno}, Nombre={turno.nombre}")
    print(f"Detalles: {len(results)} días")
    
    for row in results:
        id_detalle = row[4]
        jornada = row[5]
        hora_ingreso = row[6]
        duracion = row[7]
        
        detalle = TurnoDetalleDiario(
            id_turno_detalle_diario=id_detalle,
            id_turno=id_turno,
            jornada=jornada,
            hora_ingreso=hora_ingreso,
            duracion=duracion
        )
        
        turno.detalles.append(detalle)
        print(f"  {jornada}: {hora_ingreso} - Duración: {duracion} min - Salida: {detalle.hora_salida}")
    
    return turno

def crear_turno_especifico():
    """Crea un turno con el horario específico: Lu-Ju 9:00-18:15, Vi 9:00-16:00."""
    turno = Turno()
    turno.id_turno = None  # No asignamos ID para buscar por configuración
    turno.nombre = "Turno de prueba - Lu-Ju 9:00-18:15, Vi 9:00-16:00"
    
    # Mapeo de días en minúsculas a mayúsculas para coincidir con la base de datos
    dias_mapping = {
        'lunes': 'LUNES',
        'martes': 'MARTES',
        'miércoles': 'MIERCOLES',  # Nota: sin tilde en la base de datos
        'jueves': 'JUEVES',
        'viernes': 'VIERNES'
    }
    
    # Agregar detalles para Lunes a Jueves (9:00 a 18:15)
    for dia in ['lunes', 'martes', 'miércoles', 'jueves']:
        detalle = TurnoDetalleDiario(
            id_turno_detalle_diario=None,
            id_turno=None,
            jornada=dias_mapping[dia],  # Usar el nombre en mayúsculas
            hora_ingreso=time(9, 0),  # 9:00 AM
            duracion=555  # 9 horas y 15 minutos (555 minutos)
        )
        turno.detalles.append(detalle)
    
    # Agregar detalle para Viernes (9:00 a 16:00)
    detalle_viernes = TurnoDetalleDiario(
        id_turno_detalle_diario=None,
        id_turno=None,
        jornada=dias_mapping['viernes'],  # Usar el nombre en mayúsculas
        hora_ingreso=time(9, 0),  # 9:00 AM
        duracion=420  # 7 horas (420 minutos)
    )
    turno.detalles.append(detalle_viernes)
    
    return turno

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
        
        # Obtener el turno ID=1 de la base de datos
        print("\n--- VERIFICANDO TURNO ID=1 ---")
        turno_original = obtener_turno_por_id(connection, 1)
        
        if not turno_original:
            print("No se encontró el turno ID=1")
        else:
            # Crear un turno de prueba con el horario específico
            print("\n--- CREANDO TURNO DE PRUEBA ---")
            turno_prueba = crear_turno_especifico()
            
            print(f"Turno de prueba creado: ID={turno_prueba.id_turno}, Nombre={turno_prueba.nombre}")
            print(f"Detalles: {len(turno_prueba.detalles)} días")
            for d in turno_prueba.detalles:
                print(f"  - {d.jornada}: {d.hora_ingreso} - Duración: {d.duracion} min - Salida: {d.hora_salida}")
            
            # Buscar turnos similares
            print("\n--- BUSCANDO TURNOS SIMILARES ---")
            similares = buscar_turnos_similares(connection, turno_prueba)
            
            # Mostrar resultados
            print(f"\nSe encontraron {len(similares)} turnos similares:")
            for idx, (id_turno, nombre, detalles) in enumerate(similares):
                print(f"Turno similar #{idx+1}: ID={id_turno}, Nombre={nombre}")
                print(f"  Detalles: {len(detalles)} días")
                for detalle in detalles:
                    print(f"    {detalle['jornada']}: {detalle['hora_ingreso']} - Duración: {detalle['duracion']} min - Salida: {detalle['hora_salida']}")
            
            # Verificar si el turno ID=1 está entre las coincidencias
            ids_encontrados = [id_turno for id_turno, _, _ in similares]
            if 1 in ids_encontrados:
                print("\n✅ CONFIRMADO: El turno ID=1 coincide exactamente con el horario especificado.")
            else:
                print("\n❌ ERROR: El turno ID=1 NO coincide con el horario especificado.")
                
                # Verificar manualmente si el turno ID=1 tiene el horario especificado
                print("\n--- VERIFICACIÓN MANUAL DEL TURNO ID=1 ---")
                print("Comparando horarios del turno ID=1 con el horario especificado:")
                
                # Crear un diccionario para facilitar la comparación
                detalles_turno1 = {detalle.jornada: detalle for detalle in turno_original.detalles}
                detalles_prueba = {detalle.jornada: detalle for detalle in turno_prueba.detalles}
                
                # Verificar si los días coinciden
                dias_turno1 = set(detalles_turno1.keys())
                dias_prueba = set(detalles_prueba.keys())
                
                if dias_turno1 == dias_prueba:
                    print(f"✓ Los días coinciden: {dias_turno1} == {dias_prueba}")
                    
                    # Verificar cada día
                    coincidencia_total = True
                    for dia in dias_prueba:
                        detalle1 = detalles_turno1.get(dia)
                        detalle_prueba = detalles_prueba.get(dia)
                        
                        if not detalle1 or not detalle_prueba:
                            print(f"❌ Falta detalle para el día {dia}")
                            coincidencia_total = False
                            continue
                        
                        # Comparar hora de ingreso
                        ingreso1 = detalle1.hora_ingreso
                        ingreso_prueba = detalle_prueba.hora_ingreso
                        
                        if ingreso1.hour == ingreso_prueba.hour and ingreso1.minute == ingreso_prueba.minute:
                            print(f"✓ {dia}: Hora de ingreso coincide: {ingreso1} == {ingreso_prueba}")
                        else:
                            print(f"❌ {dia}: Hora de ingreso diferente: {ingreso1} != {ingreso_prueba}")
                            coincidencia_total = False
                        
                        # Comparar duración
                        if detalle1.duracion == detalle_prueba.duracion:
                            print(f"✓ {dia}: Duración coincide: {detalle1.duracion} == {detalle_prueba.duracion}")
                        else:
                            print(f"❌ {dia}: Duración diferente: {detalle1.duracion} != {detalle_prueba.duracion}")
                            coincidencia_total = False
                        
                        # Comparar hora de salida
                        salida1 = detalle1.hora_salida
                        salida_prueba = detalle_prueba.hora_salida
                        
                        if salida1.hour == salida_prueba.hour and salida1.minute == salida_prueba.minute:
                            print(f"✓ {dia}: Hora de salida coincide: {salida1} == {salida_prueba}")
                        else:
                            print(f"❌ {dia}: Hora de salida diferente: {salida1} != {salida_prueba}")
                            coincidencia_total = False
                    
                    if coincidencia_total:
                        print("\n✅ VERIFICACIÓN MANUAL: El turno ID=1 SÍ coincide exactamente con el horario especificado.")
                        print("El problema puede estar en la comparación automática.")
                    else:
                        print("\n❌ VERIFICACIÓN MANUAL: El turno ID=1 NO coincide exactamente con el horario especificado.")
                else:
                    print(f"❌ Los días no coinciden: {dias_turno1} != {dias_prueba}")
        
        # Cerrar conexión
        connection.close()
        print("\nConexión cerrada correctamente")
        
    except Exception as e:
        print(f"Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 