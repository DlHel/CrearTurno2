import cx_Oracle
from typing import Optional, Dict, Any, Union
import os
from datetime import datetime, timedelta
import time

class OracleConnection:
    _instance = None
    _cache: Dict[str, Any] = {}
    _cache_timestamp: Dict[str, datetime] = {}
    CACHE_DURATION = timedelta(minutes=10)  # Reducir a 10 minutos para evitar datos desactualizados
    # Bandera para rastrear si la conexión ya ha sido informada como exitosa
    _connection_reported = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OracleConnection, cls).__new__(cls)
            cls._instance.connection = None
            cls._instance.host = "orauchp-cluster-scan.uchile.cl"
            cls._instance.port = 1525
            cls._instance.service_name = "uchdb_prod.uchile.cl"
            cls._instance.username = "USR_MANTENCION"
            cls._instance.password = "tiMfiayGvJOvvlo"
            cls._instance.connection_attempts = 0
            cls._instance.max_connection_attempts = 3
            cls._instance._last_ping_time = datetime.now() - timedelta(minutes=20)  # Inicializar con un valor pasado
            cls._instance._ping_interval = timedelta(minutes=5)  # Verificar ping cada 5 minutos
        return cls._instance
    
    def _initialize_cache(self):
        """Inicializa el caché con consultas comunes que se usan frecuentemente."""
        # Inicializar las estructuras de caché, pero no precargar consultas aún
        self._cache = {}
        self._cache_timestamp = {}

    def _is_connection_valid(self) -> bool:
        """Verifica si la conexión es válida sin llamar a ping() con demasiada frecuencia."""
        # Si no hay conexión, no es válida
        if not self.connection:
            return False
            
        # Si ha pasado suficiente tiempo desde el último ping, verificar nuevamente
        current_time = datetime.now()
        if current_time - self._last_ping_time > self._ping_interval:
            try:
                is_valid = self.connection.ping() is None  # ping() devuelve None si la conexión está viva
                self._last_ping_time = current_time
                return is_valid
            except:
                return False
                
        # Si el ping reciente fue exitoso, la conexión todavía es válida
        return True

    def connect(self) -> Optional[cx_Oracle.Connection]:
        """Establece la conexión con la base de datos Oracle."""
        try:
            if not self._is_connection_valid():
                # Limitar intentos de conexión
                if self.connection_attempts >= self.max_connection_attempts:
                    print("Máximo número de intentos de conexión alcanzado")
                    return None
                    
                self.connection_attempts += 1
                
                # Si había una conexión previa, intentar cerrarla primero
                if self.connection:
                    try:
                        self.connection.close()
                    except:
                        pass  # Ignorar errores al cerrar
                
                dsn = cx_Oracle.makedsn(
                    self.host,
                    self.port,
                    service_name=self.service_name
                )
                self.connection = cx_Oracle.connect(
                    user=self.username,
                    password=self.password,
                    dsn=dsn
                )
                
                # Solo reportar la conexión exitosa la primera vez
                if not self._connection_reported:
                    print("Conexión establecida exitosamente")
                    self._connection_reported = True
                
                self.connection_attempts = 0  # Resetear intentos si hay éxito
                self._last_ping_time = datetime.now()  # Actualizar tiempo del último ping
                
                # Precargar consultas comunes después de establecer conexión exitosa
                self._prefetch_common_queries()
            return self.connection
        except cx_Oracle.Error as error:
            print(f"Error al conectar a Oracle: {error}")
            return None

    def execute_query(self, query: str, params: Union[tuple, dict] = None, cache_key: str = None, retry_count: int = 1) -> Optional[list]:
        """
        Ejecuta una consulta SQL con caché opcional.
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta (opcional), puede ser tupla o diccionario
            cache_key: Clave para almacenar en caché (opcional)
            retry_count: Número de reintentos en caso de error
        
        Returns:
            Lista de resultados o None si hay error
        """
        # Generar clave de caché basada en la consulta y parámetros si no se proporciona
        if not cache_key and query:
            cache_key = f"{query}_{str(params)}"
            
        # Verificar caché si existe una clave
        if cache_key and cache_key in self._cache:
            cache_time = self._cache_timestamp.get(cache_key)
            if cache_time and datetime.now() - cache_time < self.CACHE_DURATION:
                return self._cache[cache_key]

        try:
            connection = self.connect()
            if not connection:
                return None

            cursor = connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            results = cursor.fetchall()
            
            # Almacenar en caché siempre que tengamos una clave
            if cache_key:
                self._cache[cache_key] = results
                self._cache_timestamp[cache_key] = datetime.now()

            return results

        except cx_Oracle.Error as error:
            print(f"Error al ejecutar la consulta: {error}")
            # Reintentar la consulta si es posible
            if retry_count > 0:
                time.sleep(1)  # Esperar antes de reintentar
                self._connection_reported = False  # Permitir reporte de reconexión
                return self.execute_query(query, params, cache_key, retry_count - 1)
            return None
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def _prefetch_common_queries(self):
        """Precarga consultas comunes en el caché durante la inicialización."""
        try:
            # Solo ejecutar si la conexión está establecida
            if not self.connection:
                return
                
            # Obtener último ID de turnos
            self.execute_query(
                "SELECT NVL(MAX(ID_TURNO), 0) + 1 FROM ASISTENCIAS.TURNO",
                cache_key="ultimo_id_turno"
            )
            
            # Obtener último ID de detalles
            self.execute_query(
                "SELECT NVL(MAX(ID_TURNO_DETALLE_DIARIO), 0) + 1 FROM ASISTENCIAS.TURNO_DETALLE_DIARIO",
                cache_key="ultimo_id_detalle"
            )
        except Exception as e:
            print(f"Error al precargar consultas comunes: {e}")

    def close(self):
        """Cierra la conexión con la base de datos."""
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
                self._connection_reported = False  # Resetear bandera al cerrar
                print("Conexión cerrada exitosamente")
            except cx_Oracle.Error as error:
                print(f"Error al cerrar la conexión: {error}")

    def clear_cache(self):
        """Limpia la caché de consultas."""
        self._cache.clear()
        self._cache_timestamp.clear()
        
    def refresh_cache(self):
        """Actualiza las consultas en caché."""
        self.clear_cache()
        self._prefetch_common_queries()
        
    def get_cached_value(self, cache_key: str, default=None):
        """Obtiene un valor del caché si existe, o devuelve un valor predeterminado."""
        if cache_key in self._cache:
            cache_time = self._cache_timestamp.get(cache_key)
            if cache_time and datetime.now() - cache_time < self.CACHE_DURATION:
                return self._cache[cache_key]
        return default

    def __del__(self):
        """Destructor que asegura el cierre de la conexión."""
        self.close() 