from typing import Optional, List, Tuple, Dict, Any
from datetime import time
import cx_Oracle
from .oracle_connection import OracleConnection
from models.turno import Turno, TurnoDetalleDiario

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
            print("DEBUG: Verificando conexión a la base de datos...")
            if not self.db.connect():
                print("DEBUG: No se pudo establecer la conexión con la base de datos")
                raise ConexionError("No se pudo establecer la conexión con la base de datos")
            print("DEBUG: Conexión a la base de datos verificada correctamente")
        except cx_Oracle.Error as e:
            print(f"DEBUG: Error de conexión a la base de datos: {str(e)}")
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
        Busca turnos con configuración exactamente igual al proporcionado.
        Compara solo día, hora de entrada y hora de salida.
        
        La búsqueda incluye dos niveles de coincidencia:
        1. Coincidencia exacta por ID (si el turno tiene un ID que ya existe en la BD)
        2. Coincidencia exacta (mismos días, horas de entrada y salida exactamente iguales)
        
        Args:
            turno: El turno a comparar
            
        Returns:
            Lista de tuplas (id_turno, nombre, detalles) de turnos exactamente iguales
        """
        try:
            print("DEBUG: Iniciando búsqueda de turnos similares")
            self._verificar_conexion()
            
            if not turno.detalles:
                print("DEBUG: No hay detalles en el turno a comparar")
                return []
            
            print(f"DEBUG: Buscando turnos similares para turno ID={turno.id_turno}, Nombre={turno.nombre}")
            print(f"DEBUG: Detalles del turno a comparar:")
            for detalle in turno.detalles:
                print(f"DEBUG:   - {detalle.jornada}: {detalle.hora_ingreso} - Duración: {detalle.duracion} min")
            
            # Verificar primero si existe un turno con el mismo ID
            if turno.id_turno is not None and turno.id_turno > 0:
                print(f"DEBUG: Verificando si existe un turno con ID={turno.id_turno}")
                query_id = """
                SELECT t.ID_TURNO, t.NOMBRE, t.VIGENCIA, t.FRECUENCIA,
                       tdd.ID_TURNO_DETALLE_DIARIO, tdd.JORNADA, tdd.HORA_INGRESO, tdd.DURACION
                FROM ASISTENCIAS.TURNO t
                JOIN ASISTENCIAS.TURNO_DETALLE_DIARIO tdd ON t.ID_TURNO = tdd.ID_TURNO
                WHERE t.ID_TURNO = :id_turno
                ORDER BY tdd.JORNADA
                """
                
                results_id = self.db.execute_query(query_id, {"id_turno": turno.id_turno})
                
                if results_id:
                    print(f"DEBUG: Se encontró un turno con ID={turno.id_turno}")
                    # Procesar resultados
                    turnos_agrupados = self._agrupar_resultados_turnos(results_id)
                    
                    if turnos_agrupados:
                        id_turno = list(turnos_agrupados.keys())[0]
                        info = turnos_agrupados[id_turno]
                        
                        # Convertir a formato para comparación
                        turno_existente = (
                            id_turno,
                            info['nombre'],
                            self._convertir_detalles_para_comparacion(info['detalles'])
                        )
                        
                        # Devolver solo este turno si existe
                        return [turno_existente]
            
            # Si no se encontró un turno con el mismo ID, buscar turnos similares
            print("DEBUG: Buscando turnos con configuración similar")
            
            # Obtener todos los turnos de la base de datos
            query_todos_turnos = """
            SELECT t.ID_TURNO, t.NOMBRE, t.VIGENCIA, t.FRECUENCIA,
                   tdd.ID_TURNO_DETALLE_DIARIO, tdd.JORNADA, tdd.HORA_INGRESO, tdd.DURACION
            FROM ASISTENCIAS.TURNO t
            JOIN ASISTENCIAS.TURNO_DETALLE_DIARIO tdd ON t.ID_TURNO = tdd.ID_TURNO
            ORDER BY t.ID_TURNO, tdd.JORNADA
            """
            
            print("DEBUG: Ejecutando consulta para obtener todos los turnos")
            results_todos_turnos = self.db.execute_query(query_todos_turnos)
            
            if not results_todos_turnos:
                print("DEBUG: No se encontraron turnos en la base de datos")
                return []
            
            print(f"DEBUG: Se encontraron {len(results_todos_turnos)} filas de resultados")
            
            # Agrupar resultados por turno
            turnos_agrupados = self._agrupar_resultados_turnos(results_todos_turnos)
            print(f"DEBUG: Se agruparon en {len(turnos_agrupados)} turnos distintos")
            
            # Convertir a lista de tuplas (id, nombre, detalles)
            turnos_para_comparar = [(
                id_turno,
                info['nombre'],
                self._convertir_detalles_para_comparacion(info['detalles'])
            ) for id_turno, info in turnos_agrupados.items()]
            
            # Filtrar por coincidencia exacta en días, horas de entrada y salida
            turnos_coincidentes = self._filtrar_turnos_similares(turno, turnos_para_comparar)
            
            print(f"DEBUG: Después de filtrar, se encontraron {len(turnos_coincidentes)} turnos coincidentes")
            
            return turnos_coincidentes
            
        except Exception as e:
            print(f"ERROR al buscar turnos similares: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    def _agrupar_resultados_turnos(self, results):
        """
        Agrupa los resultados de la consulta por turno.
        
        Args:
            results: Resultados de la consulta
            
        Returns:
            Diccionario con los turnos agrupados
        """
        turnos_agrupados = {}
        
        for row in results:
            id_turno = row[0]
            nombre = row[1]
            vigencia = row[2]
            frecuencia = row[3]
            id_detalle = row[4]
            jornada = row[5]
            hora_ingreso = row[6]
            duracion = row[7]
            
            if id_turno not in turnos_agrupados:
                turnos_agrupados[id_turno] = {
                    'nombre': nombre,
                    'vigencia': vigencia,
                    'frecuencia': frecuencia,
                    'detalles': []
                }
            
            turnos_agrupados[id_turno]['detalles'].append({
                'id_turno_detalle_diario': id_detalle,
                'jornada': jornada,
                'hora_ingreso': hora_ingreso,
                'duracion': duracion
            })
        
        return turnos_agrupados

    def _convertir_detalles_para_comparacion(self, detalles):
        """
        Convierte los detalles a un formato adecuado para la comparación.
        Solo incluye día, hora de entrada y hora de salida.
        
        Args:
            detalles: Lista de detalles del turno
            
        Returns:
            Lista de detalles convertidos
        """
        detalles_convertidos = []
        
        for detalle in detalles:
            hora_ingreso = detalle['hora_ingreso']
            duracion = detalle['duracion']
            
            # Calcular hora de salida a partir de la duración en minutos
            minutos_totales = hora_ingreso.hour * 60 + hora_ingreso.minute + duracion
            horas_salida = minutos_totales // 60
            minutos_salida = minutos_totales % 60
            hora_salida = time(hour=horas_salida % 24, minute=minutos_salida)
            
            # Normalizar el nombre del día (convertir a mayúsculas)
            jornada_normalizada = detalle['jornada'].upper()
            # Corregir "MIÉRCOLES" a "MIERCOLES" (sin tilde) para coincidir con la BD
            if jornada_normalizada == "MIÉRCOLES":
                jornada_normalizada = "MIERCOLES"
            elif jornada_normalizada == "SÁBADO":
                jornada_normalizada = "SABADO"
            
            detalles_convertidos.append({
                'jornada': jornada_normalizada,
                'hora_ingreso': hora_ingreso,
                'hora_salida': hora_salida
            })
        
        # Ordenar por jornada
        dias_semana = {
            "LUNES": 1, "MARTES": 2, "MIERCOLES": 3, 
            "JUEVES": 4, "VIERNES": 5, "SABADO": 6, "DOMINGO": 7
        }
        detalles_convertidos = sorted(detalles_convertidos, key=lambda x: dias_semana.get(x['jornada'], 99))
        
        return detalles_convertidos

    def _filtrar_turnos_similares(self, turno: Turno, turnos_para_comparar: List[Tuple[int, str, List[dict]]]) -> List[Tuple[int, str, List[dict]]]:
        """
        Filtra los turnos que son exactamente iguales al turno proporcionado.
        Solo compara día, hora de entrada y hora de salida.
        
        Args:
            turno: Turno a comparar
            turnos_para_comparar: Lista de turnos candidatos
            
        Returns:
            Lista de turnos exactamente iguales
        """
        print(f"DEBUG: Iniciando filtrado de turnos similares. Turno a comparar ID={turno.id_turno}")
        print(f"DEBUG: Hay {len(turnos_para_comparar)} turnos candidatos para comparar")
        
        # Preparar los detalles del turno a comparar
        detalles_turno = []
        for detalle in turno.detalles:
            # Calcular hora de salida si no está definida
            hora_salida = None
            if hasattr(detalle, 'hora_salida') and detalle.hora_salida:
                hora_salida = detalle.hora_salida
            else:
                minutos_totales = detalle.hora_ingreso.hour * 60 + detalle.hora_ingreso.minute + detalle.duracion
                horas_salida = minutos_totales // 60
                minutos_salida = minutos_totales % 60
                hora_salida = time(hour=horas_salida % 24, minute=minutos_salida)
                
            # Normalizar el nombre del día (convertir a mayúsculas)
            jornada_normalizada = detalle.jornada.upper()
            # Corregir "MIÉRCOLES" a "MIERCOLES" (sin tilde) para coincidir con la BD
            if jornada_normalizada == "MIÉRCOLES":
                jornada_normalizada = "MIERCOLES"
                
            detalles_turno.append({
                'jornada': jornada_normalizada,
                'hora_ingreso': detalle.hora_ingreso,
                'hora_salida': hora_salida
            })
        
        # Ordenar por jornada
        dias_semana = {
            "LUNES": 1, "MARTES": 2, "MIERCOLES": 3, 
            "JUEVES": 4, "VIERNES": 5, "SABADO": 6, "DOMINGO": 7
        }
        detalles_turno = sorted(detalles_turno, key=lambda x: dias_semana.get(x['jornada'], 99))
        
        # Resultados para coincidencias exactas
        coincidencias_exactas = []
        
        # Crear un conjunto con los días del turno a comparar
        dias_turno = {detalle['jornada'] for detalle in detalles_turno}
        print(f"DEBUG: Días del turno a comparar: {dias_turno}")
        
        # Verificar coincidencia exacta por ID primero
        for id_turno, nombre, detalles in turnos_para_comparar:
            if turno.id_turno is not None and id_turno == turno.id_turno:
                print(f"DEBUG: Encontrado turno con el mismo ID={id_turno}")
                coincidencias_exactas.insert(0, (id_turno, nombre, detalles))
                # No salimos del bucle para seguir buscando otras coincidencias exactas
        
        # Luego buscar otras coincidencias exactas
        for id_turno, nombre, detalles in turnos_para_comparar:
            # Saltar si ya encontramos este turno por ID
            if turno.id_turno is not None and id_turno == turno.id_turno:
                continue
                
            print(f"DEBUG: Comparando con turno ID={id_turno}, Nombre={nombre}")
            
            # Normalizar los nombres de los días en el turno candidato
            detalles_normalizados = []
            for detalle in detalles:
                jornada_normalizada = detalle['jornada'].upper()
                if jornada_normalizada == "MIÉRCOLES":
                    jornada_normalizada = "MIERCOLES"
                
                detalles_normalizados.append({
                    'jornada': jornada_normalizada,
                    'hora_ingreso': detalle['hora_ingreso'],
                    'hora_salida': detalle['hora_salida']
                })
            
            # Crear un conjunto con los días del turno candidato (normalizados)
            dias_candidato = {detalle['jornada'] for detalle in detalles_normalizados}
            
            # Si los conjuntos de días son diferentes, no hay coincidencia
            if dias_turno != dias_candidato:
                print(f"DEBUG: Los días no coinciden, saltando turno ID={id_turno}")
                continue
            
            print(f"DEBUG: Días coinciden: {dias_turno} == {dias_candidato}")
            
            # Verificar coincidencia exacta
            es_coincidencia_exacta = True
            
            # Crear diccionarios para facilitar la comparación por día
            detalles_turno_dict = {detalle['jornada']: detalle for detalle in detalles_turno}
            detalles_candidato_dict = {detalle['jornada']: detalle for detalle in detalles_normalizados}
            
            # Comparar cada día
            for dia in dias_turno:
                detalle_original = detalles_turno_dict[dia]
                detalle_comparar = detalles_candidato_dict[dia]
                
                # Convertimos a minutos para comparar hora de ingreso
                minutos_ingreso_orig = detalle_original['hora_ingreso'].hour * 60 + detalle_original['hora_ingreso'].minute
                minutos_ingreso_comp = detalle_comparar['hora_ingreso'].hour * 60 + detalle_comparar['hora_ingreso'].minute
                
                print(f"DEBUG: Comparando día {dia}:")
                print(f"DEBUG:   Hora ingreso original: {detalle_original['hora_ingreso']} ({minutos_ingreso_orig} min)")
                print(f"DEBUG:   Hora ingreso comparar: {detalle_comparar['hora_ingreso']} ({minutos_ingreso_comp} min)")
                
                # Para coincidencia exacta, las horas de ingreso deben ser idénticas
                if minutos_ingreso_orig != minutos_ingreso_comp:
                    print(f"DEBUG:   ❌ Las horas de ingreso no coinciden para el día {dia}")
                    es_coincidencia_exacta = False
                    break
                else:
                    print(f"DEBUG:   ✓ Horas de ingreso iguales")
                
                # Convertimos a minutos para comparar hora de salida
                minutos_salida_orig = detalle_original['hora_salida'].hour * 60 + detalle_original['hora_salida'].minute
                minutos_salida_comp = detalle_comparar['hora_salida'].hour * 60 + detalle_comparar['hora_salida'].minute
                
                print(f"DEBUG:   Hora salida original: {detalle_original['hora_salida']} ({minutos_salida_orig} min)")
                print(f"DEBUG:   Hora salida comparar: {detalle_comparar['hora_salida']} ({minutos_salida_comp} min)")
                
                # Para coincidencia exacta, las horas de salida deben ser idénticas
                if minutos_salida_orig != minutos_salida_comp:
                    print(f"DEBUG:   ❌ Las horas de salida no coinciden para el día {dia}")
                    es_coincidencia_exacta = False
                    break
                else:
                    print(f"DEBUG:   ✓ Horas de salida iguales")
            
            if es_coincidencia_exacta:
                print(f"DEBUG: ✅ Encontrada coincidencia exacta con ID={id_turno}")
                coincidencias_exactas.append((id_turno, nombre, detalles))
        
        print(f"DEBUG: Filtrado completado. Se encontraron {len(coincidencias_exactas)} coincidencias exactas")
        return coincidencias_exactas

    def asignar_ids(self, turno: Turno) -> None:
        """
        Asigna IDs al turno y sus detalles.
        
        Args:
            turno: El turno al que se asignarán los IDs
            
        Raises:
            ConsultaError: Si hay un error al obtener los IDs
        """
        try:
            # Solo asignar un nuevo ID si el turno no tiene uno válido
            if turno.id_turno <= 0:
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
            turno: El turno a insertar o actualizar.
            
        Returns:
            str: El script SQL generado.
        """
        try:
            script = []
            
            # Verificar si el turno ya existe en la base de datos
            turno_existe = False
            if turno.id_turno > 0:
                query = """
                SELECT COUNT(*) FROM ASISTENCIAS.TURNO 
                WHERE ID_TURNO = :id_turno
                """
                result = self.db.execute_query(query, {"id_turno": turno.id_turno})
                count = result[0][0] if result else 0
                turno_existe = count > 0
            
            # Generar script para el turno principal
            if turno_existe:
                # Script para actualizar un turno existente
                script.append(f"-- Actualización del turno existente con ID {turno.id_turno}")
                script.append(f"""
UPDATE ASISTENCIAS.TURNO
SET NOMBRE = '{turno.nombre}',
    VIGENCIA = {turno.vigencia},
    FRECUENCIA = '{turno.frecuencia}'
WHERE ID_TURNO = {turno.id_turno};
""")
            else:
                # Script para insertar un nuevo turno
                script.append(f"-- Inserción de un nuevo turno con ID {turno.id_turno}")
                script.append(f"""
INSERT INTO ASISTENCIAS.TURNO (ID_TURNO, NOMBRE, VIGENCIA, FRECUENCIA)
VALUES ({turno.id_turno}, '{turno.nombre}', {turno.vigencia}, '{turno.frecuencia}');
""")
            
            # Verificar si existen detalles para este turno
            detalles_existentes = {}
            if turno_existe:
                query = """
                SELECT ID_TURNO_DETALLE_DIARIO, JORNADA
                FROM ASISTENCIAS.TURNO_DETALLE_DIARIO
                WHERE ID_TURNO = :id_turno
                """
                result = self.db.execute_query(query, {"id_turno": turno.id_turno})
                if result:
                    detalles_existentes = {row[0]: row[1] for row in result}
                
                if detalles_existentes:
                    script.append(f"\n-- Eliminación de detalles existentes para el turno {turno.id_turno}")
                    script.append(f"""
DELETE FROM ASISTENCIAS.TURNO_DETALLE_DIARIO
WHERE ID_TURNO = {turno.id_turno};
""")
            
            # Generar script para los detalles del turno
            if turno.detalles:
                script.append(f"\n-- Inserción de detalles para el turno {turno.id_turno}")
                for detalle in turno.detalles:
                    hora_ingreso_str = detalle.hora_ingreso.strftime("%H:%M:%S")
                    script.append(f"""
INSERT INTO ASISTENCIAS.TURNO_DETALLE_DIARIO (ID_TURNO_DETALLE_DIARIO, ID_TURNO, JORNADA, HORA_INGRESO, DURACION)
VALUES ({detalle.id_turno_detalle_diario}, {detalle.id_turno}, '{detalle.jornada}', TO_DATE('2025-01-01 {hora_ingreso_str}', 'YYYY-MM-DD HH24:MI:SS'), {detalle.duracion});
""")
            
            script.append("COMMIT;")
            
            return "\n".join(script)
        except Exception as e:
            print(f"Error al generar script SQL: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"-- Error al generar script SQL: {str(e)}" 