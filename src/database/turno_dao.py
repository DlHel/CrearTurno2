from typing import Optional, List, Tuple, Dict, Any
from datetime import time
import cx_Oracle
from .oracle_connection import OracleConnection
from src.models.turno import Turno, TurnoDetalleDiario

class TurnoDAOError(Exception):
    """Excepción base para errores del DAO."""
    pass

class ConexionError(TurnoDAOError):
    """Error de conexión a la base de datos."""
    pass

class ConsultaError(TurnoDAOError):
    """Error al ejecutar una consulta."""
    pass

class TurnoDAO:
    def __init__(self):
        self.db = OracleConnection()
        self._verificar_conexion()

    def _verificar_conexion(self) -> None:
        """
        Verifica que la conexión a la base de datos esté disponible.
        
        Raises:
            ConexionError: Si no se puede establecer la conexión
        """
        try:
            if not self.db.connect():
                raise ConexionError("No se pudo establecer la conexión con la base de datos")
        except cx_Oracle.Error as e:
            raise ConexionError(f"Error de conexión: {str(e)}")

    def obtener_ultimo_id_turno(self) -> int:
        """
        Obtiene el último ID de turno de la base de datos.
        
        Returns:
            int: El último ID + 1
            
        Raises:
            ConsultaError: Si hay un error al ejecutar la consulta
        """
        try:
            self._verificar_conexion()
            
            query = """
                SELECT NVL(MAX(ID_TURNO), 0) + 1
                FROM ASISTENCIAS.TURNO
            """
            result = self.db.execute_query(query, cache_key="ultimo_id_turno")
            
            if not result:
                raise ConsultaError("No se pudo obtener el último ID de turno")
                
            return result[0][0]
            
        except cx_Oracle.Error as e:
            raise ConsultaError(f"Error al obtener último ID de turno: {str(e)}")

    def obtener_ultimo_id_detalle(self) -> int:
        """
        Obtiene el último ID de detalle de turno de la base de datos.
        
        Returns:
            int: El último ID + 1
            
        Raises:
            ConsultaError: Si hay un error al ejecutar la consulta
        """
        try:
            self._verificar_conexion()
            
            query = """
                SELECT NVL(MAX(ID_TURNO_DETALLE_DIARIO), 0) + 1
                FROM ASISTENCIAS.TURNO_DETALLE_DIARIO
            """
            result = self.db.execute_query(query, cache_key="ultimo_id_detalle")
            
            if not result:
                raise ConsultaError("No se pudo obtener el último ID de detalle")
                
            return result[0][0]
            
        except cx_Oracle.Error as e:
            raise ConsultaError(f"Error al obtener último ID de detalle: {str(e)}")

    def buscar_turnos_similares(self, turno: Turno) -> List[Tuple[int, str, List[dict]]]:
        """
        Busca turnos con configuración similar al proporcionado.
        Compara la jornada completa, incluyendo los mismos días con horarios y duraciones similares.
        
        La búsqueda incluye varios niveles de coincidencia:
        1. Coincidencia exacta (mismos días, horas y duraciones)
        2. Coincidencia cercana (mismos días, horas similares)
        3. Coincidencia en estructura (misma cantidad de días, misma distribución)
        4. Coincidencia por ID en el nombre (si el nombre contiene un ID como '77-44')
        
        Args:
            turno: El turno a comparar
            
        Returns:
            Lista de tuplas (id_turno, nombre, detalles) de turnos similares
            
        Raises:
            ConsultaError: Si hay un error al ejecutar la consulta
        """
        try:
            self._verificar_conexion()
            
            if not turno.detalles:
                return []

            # Buscar primero por ID en el nombre, si existe
            turnos_coincidentes_por_id = []
            try:
                # Extraer posible ID del nombre
                id_buscado = None
                nombre_partes = turno.nombre.split('-')
                if len(nombre_partes) > 0 and nombre_partes[0].isdigit():
                    id_buscado = int(nombre_partes[0])
                
                if id_buscado:
                    query_id = """
                    SELECT t.ID_TURNO, t.NOMBRE, t.VIGENCIA, t.FRECUENCIA,
                           tdd.ID_TURNO_DETALLE_DIARIO, tdd.JORNADA, tdd.HORA_INGRESO, tdd.DURACION
                    FROM ASISTENCIAS.TURNO t
                    JOIN ASISTENCIAS.TURNO_DETALLE_DIARIO tdd ON t.ID_TURNO = tdd.ID_TURNO
                    WHERE t.ID_TURNO = :id_buscado
                    ORDER BY tdd.JORNADA
                    """
                    results_id = self.db.execute_query(query_id, {"id_buscado": id_buscado})
                    
                    if results_id:
                        turnos_agrupados = self._agrupar_resultados_turnos(results_id)
                        turnos_coincidentes_por_id = [(
                            id_turno,
                            info['nombre'],
                            self._convertir_detalles_para_comparacion(info['detalles'])
                        ) for id_turno, info in turnos_agrupados.items()]
            
            except Exception as e:
                print(f"Error al buscar por ID: {str(e)}")
            
            # Construir lista de días y sus horarios para comparar
            dias_turno = sorted([detalle.jornada for detalle in turno.detalles])
            
            # Consulta principal para buscar turnos con días similares
            placeholders = ', '.join([f":dia{i}" for i in range(len(dias_turno))])
            query = f"""
            SELECT t.ID_TURNO, t.NOMBRE, t.VIGENCIA, t.FRECUENCIA,
                   tdd.ID_TURNO_DETALLE_DIARIO, tdd.JORNADA, tdd.HORA_INGRESO, tdd.DURACION
            FROM ASISTENCIAS.TURNO t
            JOIN ASISTENCIAS.TURNO_DETALLE_DIARIO tdd ON t.ID_TURNO = tdd.ID_TURNO
            WHERE t.ID_TURNO IN (
                SELECT t.ID_TURNO 
                FROM ASISTENCIAS.TURNO t
                JOIN ASISTENCIAS.TURNO_DETALLE_DIARIO tdd ON t.ID_TURNO = tdd.ID_TURNO
                WHERE tdd.JORNADA IN ({placeholders})
                GROUP BY t.ID_TURNO
                HAVING COUNT(DISTINCT tdd.JORNADA) = :total_dias
            )
            ORDER BY t.ID_TURNO, tdd.JORNADA
            """
            
            params = {f"dia{i}": dia for i, dia in enumerate(dias_turno)}
            params["total_dias"] = len(dias_turno)
            
            results = self.db.execute_query(query, params)
            
            if not results:
                return turnos_coincidentes_por_id
            
            # Agrupar resultados por turno
            turnos_agrupados = self._agrupar_resultados_turnos(results)
            
            # Convertir a lista de tuplas (id, nombre, detalles)
            turnos_para_comparar = [(
                id_turno,
                info['nombre'],
                self._convertir_detalles_para_comparacion(info['detalles'])
            ) for id_turno, info in turnos_agrupados.items()]
            
            # Filtrar por similitud exacta en días y horarios
            turnos_coincidentes = self._filtrar_turnos_similares(turno, turnos_para_comparar)
            
            # Combinar con coincidencias por ID y eliminar duplicados
            todas_coincidencias = turnos_coincidentes + [t for t in turnos_coincidentes_por_id if t not in turnos_coincidentes]
            
            return todas_coincidencias
            
        except cx_Oracle.Error as e:
            raise ConsultaError(f"Error al buscar turnos similares: {str(e)}")

    def _agrupar_resultados_turnos(self, results: List[Tuple]) -> Dict[int, Dict[str, Any]]:
        """
        Agrupa los resultados de una consulta por ID de turno.
        
        Args:
            results: Resultados de la consulta
            
        Returns:
            Diccionario de turnos agrupados por ID
        """
        turnos_agrupados = {}
        for row in results:
            id_turno, nombre, vigencia, frecuencia, id_detalle, jornada, hora_ingreso, duracion = row
            
            if id_turno not in turnos_agrupados:
                turnos_agrupados[id_turno] = {
                    'nombre': nombre,
                    'vigencia': vigencia,
                    'frecuencia': frecuencia,
                    'detalles': []
                }
            
            # Convertir la hora Oracle a objeto time de Python
            hora = time(
                hour=hora_ingreso.hour if hasattr(hora_ingreso, 'hour') else hora_ingreso.hour(),
                minute=hora_ingreso.minute if hasattr(hora_ingreso, 'minute') else hora_ingreso.minute()
            )
            
            turnos_agrupados[id_turno]['detalles'].append({
                'id_turno_detalle_diario': id_detalle,
                'jornada': jornada,
                'hora_ingreso': hora,
                'duracion': duracion
            })
        
        return turnos_agrupados

    def _convertir_detalles_para_comparacion(self, detalles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convierte los detalles a un formato adecuado para comparación.
        
        Args:
            detalles: Lista de detalles
            
        Returns:
            Lista de detalles formateados para comparación
        """
        detalles_formateados = []
        
        for detalle in detalles:
            # Calcular hora de salida
            hora_ingreso = detalle['hora_ingreso']
            duracion = detalle['duracion']
            
            minutos_totales = hora_ingreso.hour * 60 + hora_ingreso.minute + duracion
            horas_salida = minutos_totales // 60
            minutos_salida = minutos_totales % 60
            hora_salida = time(hour=horas_salida % 24, minute=minutos_salida)
            
            detalles_formateados.append({
                'jornada': detalle['jornada'],
                'hora_ingreso': hora_ingreso,
                'hora_salida': hora_salida,
                'duracion': duracion
            })
        
        # Ordenar por jornada para facilitar la comparación
        dias_semana = {
            "Lunes": 1, "Martes": 2, "Miércoles": 3, 
            "Jueves": 4, "Viernes": 5, "Sábado": 6, "Domingo": 7
        }
        
        return sorted(detalles_formateados, key=lambda x: dias_semana.get(x['jornada'], 99))

    def _filtrar_turnos_similares(self, turno: Turno, turnos_para_comparar: List[Tuple[int, str, List[dict]]]) -> List[Tuple[int, str, List[dict]]]:
        """
        Filtra los turnos que son realmente similares al turno proporcionado.
        
        Args:
            turno: Turno a comparar
            turnos_para_comparar: Lista de turnos candidatos
            
        Returns:
            Lista de turnos similares
        """
        # Preparar los detalles del turno a comparar
        detalles_turno = []
        for detalle in turno.detalles:
            detalles_turno.append({
                'jornada': detalle.jornada,
                'hora_ingreso': detalle.hora_ingreso,
                'hora_salida': detalle.hora_salida or time(0, 0),  # Valor por defecto si es None
                'duracion': detalle.duracion
            })
        
        # Ordenar por jornada
        dias_semana = {
            "Lunes": 1, "Martes": 2, "Miércoles": 3, 
            "Jueves": 4, "Viernes": 5, "Sábado": 6, "Domingo": 7
        }
        detalles_turno = sorted(detalles_turno, key=lambda x: dias_semana.get(x['jornada'], 99))
        
        turnos_coincidentes = []
        
        for id_turno, nombre, detalles in turnos_para_comparar:
            # Si el número de detalles es diferente, no hay coincidencia exacta
            if len(detalles) != len(detalles_turno):
                continue
            
            es_coincidencia = True
            
            # Comparar cada día con su correspondiente
            for i, detalle_original in enumerate(detalles_turno):
                if i >= len(detalles):  # Protección contra índices fuera de rango
                    es_coincidencia = False
                    break
                    
                detalle_comparar = detalles[i]
                
                # Verificar si el día es el mismo
                if detalle_original['jornada'] != detalle_comparar['jornada']:
                    es_coincidencia = False
                    break
                
                # Verificar si las horas y duraciones son similares
                # Convertimos a minutos para comparar con una tolerancia
                minutos_ingreso_orig = detalle_original['hora_ingreso'].hour * 60 + detalle_original['hora_ingreso'].minute
                minutos_ingreso_comp = detalle_comparar['hora_ingreso'].hour * 60 + detalle_comparar['hora_ingreso'].minute
                
                # Permitir diferencia de 5 minutos para considerar similar
                if abs(minutos_ingreso_orig - minutos_ingreso_comp) > 5:
                    es_coincidencia = False
                    break
                
                # Verificar si la duración es similar (tolerancia de 10 minutos)
                if abs(detalle_original['duracion'] - detalle_comparar['duracion']) > 10:
                    es_coincidencia = False
                    break
            
            if es_coincidencia:
                turnos_coincidentes.append((id_turno, nombre, detalles))
        
        return turnos_coincidentes

    def asignar_ids(self, turno: Turno) -> None:
        """
        Asigna IDs al turno y sus detalles.
        
        Args:
            turno: El turno al que se asignarán los IDs
            
        Raises:
            ConsultaError: Si hay un error al obtener los IDs
        """
        try:
            # Siempre obtener un nuevo ID para el turno
            nuevo_id_turno = self.obtener_ultimo_id_turno()
            turno.id_turno = nuevo_id_turno
            
            # Obtener ID para el primer detalle
            id_detalle = self.obtener_ultimo_id_detalle()
            
            # Asignar IDs a cada detalle
            for detalle in turno.detalles:
                detalle.id_turno_detalle_diario = id_detalle
                detalle.id_turno = turno.id_turno
                id_detalle += 1
                    
        except (ConexionError, ConsultaError) as e:
            raise ConsultaError(f"Error al asignar IDs: {str(e)}")
            
    def buscar_por_id(self, id_turno: int) -> Optional[Turno]:
        """
        Busca un turno por su ID.
        
        Args:
            id_turno: ID del turno a buscar
            
        Returns:
            Turno encontrado o None si no existe
            
        Raises:
            ConsultaError: Si hay un error al ejecutar la consulta
        """
        try:
            self._verificar_conexion()
            
            query = """
            SELECT t.ID_TURNO, t.NOMBRE, t.VIGENCIA, t.FRECUENCIA,
                   tdd.ID_TURNO_DETALLE_DIARIO, tdd.JORNADA, 
                   tdd.HORA_INGRESO, tdd.DURACION
            FROM ASISTENCIAS.TURNO t
            JOIN ASISTENCIAS.TURNO_DETALLE_DIARIO tdd ON t.ID_TURNO = tdd.ID_TURNO
            WHERE t.ID_TURNO = :id_turno
            ORDER BY tdd.JORNADA
            """
            
            results = self.db.execute_query(query, params={'id_turno': id_turno})
            
            if not results:
                return None
                
            # Crear turno
            turno = Turno()
            turno.id_turno = results[0][0]
            turno.nombre = results[0][1]
            turno.vigencia = results[0][2]
            turno.frecuencia = results[0][3]
            
            # Agregar detalles
            for row in results:
                detalle = TurnoDetalleDiario(
                    id_turno_detalle_diario=row[4],
                    id_turno=turno.id_turno,
                    jornada=row[5],
                    hora_ingreso=time(row[6].hour, row[6].minute),
                    duracion=row[7]
                )
                detalle.calcular_hora_salida()
                turno.agregar_detalle(detalle)
                
            return turno
            
        except cx_Oracle.Error as e:
            raise ConsultaError(f"Error al buscar turno por ID: {str(e)}")
            
    def buscar_por_nombre(self, nombre: str) -> List[Turno]:
        """
        Busca turnos que contengan el texto en el nombre.
        
        Args:
            nombre: Texto a buscar en el nombre
            
        Returns:
            Lista de turnos encontrados
            
        Raises:
            ConsultaError: Si hay un error al ejecutar la consulta
        """
        try:
            self._verificar_conexion()
            
            query = """
            SELECT t.ID_TURNO, t.NOMBRE, t.VIGENCIA, t.FRECUENCIA,
                   tdd.ID_TURNO_DETALLE_DIARIO, tdd.JORNADA, 
                   tdd.HORA_INGRESO, tdd.DURACION
            FROM ASISTENCIAS.TURNO t
            JOIN ASISTENCIAS.TURNO_DETALLE_DIARIO tdd ON t.ID_TURNO = tdd.ID_TURNO
            WHERE UPPER(t.NOMBRE) LIKE UPPER('%' || :nombre || '%')
            ORDER BY t.ID_TURNO, tdd.JORNADA
            """
            
            results = self.db.execute_query(query, params={'nombre': nombre})
            
            if not results:
                return []
                
            # Procesar resultados
            turnos_dict = {}
            
            for row in results:
                id_turno = row[0]
                
                # Si el turno no existe en el diccionario, crearlo
                if id_turno not in turnos_dict:
                    turno = Turno()
                    turno.id_turno = id_turno
                    turno.nombre = row[1]
                    turno.vigencia = row[2]
                    turno.frecuencia = row[3]
                    turnos_dict[id_turno] = turno
                
                # Agregar detalle al turno
                turno = turnos_dict[id_turno]
                detalle = TurnoDetalleDiario(
                    id_turno_detalle_diario=row[4],
                    id_turno=turno.id_turno,
                    jornada=row[5],
                    hora_ingreso=time(row[6].hour, row[6].minute),
                    duracion=row[7]
                )
                detalle.calcular_hora_salida()
                turno.agregar_detalle(detalle)
                
            return list(turnos_dict.values())
            
        except cx_Oracle.Error as e:
            raise ConsultaError(f"Error al buscar turnos por nombre: {str(e)}")
            
    def guardar_script(self, script: str, path: str) -> bool:
        """
        Guarda un script SQL en un archivo.
        
        Args:
            script: Script SQL a guardar
            path: Ruta del archivo
            
        Returns:
            True si se guardó correctamente, False en caso de error
        """
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(script)
            return True
        except Exception as e:
            print(f"Error al guardar script: {str(e)}")
            return False
            
    def actualizar_vigencia(self, id_turno: int, vigencia: int) -> bool:
        """
        Actualiza la vigencia de un turno.
        
        Args:
            id_turno: ID del turno
            vigencia: Nueva vigencia (0 = Inactivo, 1 = Activo)
            
        Returns:
            True si se actualizó correctamente, False en caso de error
        """
        try:
            self._verificar_conexion()
            
            query = """
            UPDATE ASISTENCIAS.TURNO
            SET VIGENCIA = :vigencia
            WHERE ID_TURNO = :id_turno
            """
            
            self.db.execute_query(query, params={'vigencia': vigencia, 'id_turno': id_turno})
            return True
            
        except Exception as e:
            print(f"Error al actualizar vigencia: {str(e)}")
            return False

    def guardar_turno(self, turno: Turno) -> None:
        """
        Guarda un turno y sus detalles en la lista de turnos creados.
        Debido a restricciones de permisos, no se inserta directamente en la base de datos.
        
        Args:
            turno: El turno a guardar
        """
        try:
            print(f"Guardando turno: ID={turno.id_turno}, Nombre={turno.nombre}")
            
            # Verificar que todos los detalles tengan IDs asignados
            for detalle in turno.detalles:
                if detalle.id_turno_detalle_diario == 0:
                    self.asignar_ids(turno)
                    break
            
            # Generar script SQL para referencia
            script = self.generar_script_sql(turno)
            print(f"Script SQL generado para el turno {turno.id_turno}:")
            print(script)
            
            # Aquí se podría guardar el script en un archivo si es necesario
            
        except Exception as e:
            print(f"Error al guardar turno: {str(e)}")
            raise ConsultaError(f"Error al guardar turno: {str(e)}")

    def generar_script_sql(self, turno: Turno) -> str:
        """
        Genera un script SQL para insertar o actualizar un turno y sus detalles.
        
        Args:
            turno: El turno para el que generar el script
            
        Returns:
            String con el script SQL
        """
        try:
            script = ""
            
            # Asegurar que el turno tenga un ID válido
            if turno.id_turno <= 0:
                turno.id_turno = self.obtener_ultimo_id_turno()
            
            # Asegurar que los detalles tengan IDs válidos y correlativos
            if any(detalle.id_turno_detalle_diario <= 0 for detalle in turno.detalles):
                id_detalle_base = self.obtener_ultimo_id_detalle()
                for i, detalle in enumerate(turno.detalles):
                    detalle.id_turno_detalle_diario = id_detalle_base + i
                    detalle.id_turno = turno.id_turno
            
            # INSERT/UPDATE para la tabla TURNO
            script += f"-- Turno: {turno.nombre} (ID: {turno.id_turno})\n"
            script += f"INSERT INTO ASISTENCIAS.TURNO (ID_TURNO, NOMBRE, VIGENCIA, FRECUENCIA) VALUES ({turno.id_turno}, '{turno.nombre}', '{turno.vigencia}', '{turno.frecuencia}');\n"
            script += f"-- En caso de que ya exista, usar UPDATE:\n"
            script += f"-- UPDATE ASISTENCIAS.TURNO SET NOMBRE = '{turno.nombre}', VIGENCIA = '{turno.vigencia}', FRECUENCIA = '{turno.frecuencia}' WHERE ID_TURNO = {turno.id_turno};\n\n"
            
            # INSERTs para los detalles
            script += f"-- Detalles del turno {turno.id_turno}:\n"
            script += f"-- Si es una actualización, primero eliminar los detalles existentes:\n"
            script += f"-- DELETE FROM ASISTENCIAS.TURNO_DETALLE_DIARIO WHERE ID_TURNO = {turno.id_turno};\n\n"
            
            for detalle in turno.detalles:
                script += f"INSERT INTO ASISTENCIAS.TURNO_DETALLE_DIARIO (ID_TURNO_DETALLE_DIARIO, ID_TURNO, JORNADA, HORA_INGRESO, DURACION) VALUES ({detalle.id_turno_detalle_diario}, {turno.id_turno}, '{detalle.jornada}', TO_DATE('2025-01-01 {detalle.hora_ingreso.strftime('%H:%M')}:00', 'YYYY-MM-DD HH24:MI:SS'), {detalle.duracion});\n"
            
            return script
        except Exception as e:
            print(f"Error al generar script SQL en TurnoDAO: {str(e)}")
            import traceback
            traceback.print_exc()
            return None 