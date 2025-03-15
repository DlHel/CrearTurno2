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
    
    def is_connected(self) -> bool:
        """Verifica si hay una conexión activa a la base de datos."""
        return self.connection is not None and self._is_connection_valid()
    
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
                print("DEBUG: Conexión no válida, intentando conectar...")
                # Limitar intentos de conexión
                if self.connection_attempts >= self.max_connection_attempts:
                    print("DEBUG: Máximo número de intentos de conexión alcanzado")
                    return None
                    
                self.connection_attempts += 1
                print(f"DEBUG: Intento de conexión #{self.connection_attempts}")
                
                # Si había una conexión previa, intentar cerrarla primero
                if self.connection:
                    try:
                        print("DEBUG: Cerrando conexión previa...")
                        self.connection.close()
                    except Exception as e:
                        print(f"DEBUG: Error al cerrar conexión previa: {str(e)}")
                
                print(f"DEBUG: Conectando a {self.host}:{self.port}/{self.service_name} con usuario {self.username}")
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
                    print("DEBUG: Conexión establecida exitosamente")
                    self._connection_reported = True
                
                self.connection_attempts = 0  # Resetear intentos si hay éxito
                self._last_ping_time = datetime.now()  # Actualizar tiempo del último ping
                print("DEBUG: Conexión establecida y validada")
                
                # Precargar consultas comunes después de establecer conexión exitosa
                self._prefetch_common_queries()
            else:
                print("DEBUG: Usando conexión existente")
                
            return self.connection
        except cx_Oracle.Error as error:
            print(f"DEBUG: Error al conectar a Oracle: {error}")
            return None

    def execute_query(self, query: str, params: Union[tuple, dict] = None, cache_key: str = None, retry_count: int = 1) -> Optional[list]:
        """
        Ejecuta una consulta SQL y devuelve los resultados.
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta (opcional)
            cache_key: Clave para almacenar en caché los resultados (opcional)
            retry_count: Número de intentos de reconexión en caso de error
            
        Returns:
            Lista de resultados o None si hay un error
        """
        # Si hay una clave de caché y los resultados están en caché y no han expirado, devolverlos
        if cache_key and cache_key in self._cache and cache_key in self._cache_timestamp:
            if datetime.now() - self._cache_timestamp[cache_key] < self.CACHE_DURATION:
                print(f"DEBUG: Usando resultados en caché para la clave '{cache_key}'")
                return self._cache[cache_key]
        
        # Verificar si hay conexión, si no, intentar conectar
        if not self.is_connected():
            print("DEBUG: No hay conexión activa, intentando conectar...")
            if not self.connect():
                print("DEBUG: No se pudo establecer conexión a la base de datos")
                return None
        
        try:
            print(f"DEBUG: Ejecutando consulta: {query[:100]}...")
            if params:
                print(f"DEBUG: Con parámetros: {params}")
            
            cursor = self.connection.cursor()
            cursor.execute(query, params or {})
            results = cursor.fetchall()
            cursor.close()
            
            print(f"DEBUG: Consulta ejecutada con éxito. Filas obtenidas: {len(results)}")
            
            # Si hay una clave de caché, almacenar los resultados
            if cache_key:
                self._cache[cache_key] = results
                self._cache_timestamp[cache_key] = datetime.now()
                print(f"DEBUG: Resultados almacenados en caché con la clave '{cache_key}'")
            
            return results
            
        except cx_Oracle.Error as e:
            print(f"DEBUG: Error al ejecutar consulta: {str(e)}")
            
            # Si es un error de conexión y hay intentos restantes, intentar reconectar
            if retry_count > 0:
                print(f"DEBUG: Intentando reconectar ({retry_count} intentos restantes)...")
                time.sleep(1)  # Esperar un segundo antes de reintentar
                self.connection = None  # Forzar reconexión
                if self.connect():
                    print("DEBUG: Reconexión exitosa, reintentando consulta...")
                    return self.execute_query(query, params, cache_key, retry_count - 1)
            
            print("DEBUG: No se pudo ejecutar la consulta después de los reintentos")
            return None

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

    def get_connection(self) -> Optional[cx_Oracle.Connection]:
        """
        Obtiene la conexión actual a la base de datos, estableciéndola si no existe.
        
        Returns:
            Objeto de conexión a Oracle o None si no se puede establecer
        """
        return self.connect()

    def __del__(self):
        """Destructor que asegura el cierre de la conexión."""
        self.close() 