import cx_Oracle
from datetime import time

# Datos de conexión
host = "orauchp-cluster-scan.uchile.cl"
port = 1525
service_name = "uchdb_prod.uchile.cl"
username = "USR_MANTENCION"
password = "tiMfiayGvJOvvlo"

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
        
        # Consultar los turnos existentes
        query = """
        SELECT t.ID_TURNO, t.NOMBRE, t.VIGENCIA, t.FRECUENCIA,
               tdd.ID_TURNO_DETALLE_DIARIO, tdd.JORNADA, tdd.HORA_INGRESO, tdd.DURACION
        FROM ASISTENCIAS.TURNO t
        JOIN ASISTENCIAS.TURNO_DETALLE_DIARIO tdd ON t.ID_TURNO = tdd.ID_TURNO
        WHERE t.ID_TURNO IN (
            SELECT DISTINCT ID_TURNO 
            FROM ASISTENCIAS.TURNO_DETALLE_DIARIO 
            WHERE JORNADA = 'Lunes'
        )
        ORDER BY t.ID_TURNO, tdd.JORNADA
        """
        
        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        
        if not results:
            print("No se encontraron turnos en la base de datos")
            return
        
        print(f"Se encontraron {len(results)} filas de resultados")
        
        # Agrupar resultados por turno
        turnos_agrupados = {}
        for row in results:
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
        
        print(f"Se encontraron {len(turnos_agrupados)} turnos distintos con día Lunes")
        
        # Mostrar los primeros 10 turnos con sus detalles
        print("\nPrimeros 10 turnos:")
        for idx, (id_turno, info) in enumerate(list(turnos_agrupados.items())[:10]):
            nombre = info['nombre']
            detalles = info['detalles']
            
            print(f"Turno #{idx+1}: ID={id_turno}, Nombre={nombre}")
            print(f"  Detalles: {len(detalles)} días")
            
            # Filtrar solo los detalles del lunes
            detalles_lunes = [d for d in detalles if d['jornada'] == 'Lunes']
            
            for detalle in detalles_lunes:
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