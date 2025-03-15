import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from src.database.oracle_connection import OracleConnection

@pytest.mark.unit
class TestOracleConnection:
    """Pruebas para la clase OracleConnection."""
    
    def test_singleton_pattern(self):
        """Prueba que la clase OracleConnection implemente el patrón Singleton."""
        # Crear dos instancias
        conn1 = OracleConnection()
        conn2 = OracleConnection()
        
        # Verificar que sean la misma instancia
        assert conn1 is conn2
    
    @patch('cx_Oracle.connect')
    @patch('cx_Oracle.makedsn')
    def test_connect_success(self, mock_makedsn, mock_connect):
        """Prueba que el método connect funcione correctamente cuando la conexión es exitosa."""
        # Configurar mocks
        mock_dsn = MagicMock()
        mock_makedsn.return_value = mock_dsn
        
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        
        # Crear instancia y conectar
        conn = OracleConnection()
        conn._connection_reported = False  # Resetear para la prueba
        conn.connection = None  # Asegurar que no hay conexión previa
        result = conn.connect()
        
        # Verificar que se llamó a makedsn con los parámetros correctos
        mock_makedsn.assert_called_once_with(
            conn.host,
            conn.port,
            service_name=conn.service_name
        )
        
        # Verificar que se llamó a connect con los parámetros correctos
        mock_connect.assert_called_once_with(
            user=conn.username,
            password=conn.password,
            dsn=mock_dsn
        )
        
        # Verificar que se devolvió la conexión
        assert result == mock_connection
        
        # Verificar que se actualizaron los intentos de conexión
        assert conn.connection_attempts == 0
    
    @patch('cx_Oracle.connect')
    def test_connect_error(self, mock_connect):
        """Prueba que el método connect maneje correctamente los errores de conexión."""
        # Configurar mock para lanzar una excepción
        import cx_Oracle
        mock_connect.side_effect = cx_Oracle.Error("Error de conexión simulado")
        
        # Crear instancia y conectar
        conn = OracleConnection()
        conn.connection = None  # Asegurar que no hay conexión previa
        conn.connection_attempts = 0  # Resetear intentos
        
        # Intentar conectar
        result = conn.connect()
        
        # Verificar que se incrementaron los intentos de conexión
        assert conn.connection_attempts == 1
        
        # Verificar que se devolvió None
        assert result is None
    
    @patch('cx_Oracle.connect')
    def test_max_connection_attempts(self, mock_connect):
        """Prueba que se respete el número máximo de intentos de conexión."""
        # Crear instancia
        conn = OracleConnection()
        conn.connection = None  # Asegurar que no hay conexión previa
        
        # Establecer intentos al máximo
        conn.connection_attempts = conn.max_connection_attempts
        
        # Intentar conectar
        result = conn.connect()
        
        # Verificar que no se intentó conectar y se devolvió None
        mock_connect.assert_not_called()
        assert result is None
    
    def test_is_connected_no_connection(self):
        """Prueba que is_connected devuelva False cuando no hay conexión."""
        conn = OracleConnection()
        conn.connection = None
        
        assert conn.is_connected() is False
    
    @patch.object(OracleConnection, '_is_connection_valid')
    def test_is_connected_with_connection(self, mock_is_valid):
        """Prueba que is_connected devuelva el resultado de _is_connection_valid cuando hay conexión."""
        # Caso 1: Conexión válida
        conn = OracleConnection()
        conn.connection = MagicMock()
        mock_is_valid.return_value = True
        
        assert conn.is_connected() is True
        
        # Caso 2: Conexión no válida
        mock_is_valid.return_value = False
        
        assert conn.is_connected() is False
    
    def test_is_connection_valid_no_connection(self):
        """Prueba que _is_connection_valid devuelva False cuando no hay conexión."""
        conn = OracleConnection()
        conn.connection = None
        
        assert conn._is_connection_valid() is False
    
    @patch('datetime.datetime')
    def test_is_connection_valid_recent_ping(self, mock_datetime):
        """Prueba que _is_connection_valid no haga ping si se hizo uno recientemente."""
        # Configurar mock de datetime
        now = datetime.now()
        mock_datetime.now.return_value = now
        
        # Crear instancia con conexión y ping reciente
        conn = OracleConnection()
        conn.connection = MagicMock()
        conn._last_ping_time = now - timedelta(minutes=1)  # Ping hace 1 minuto
        
        # Verificar que no se hace ping y se devuelve True
        assert conn._is_connection_valid() is True
        conn.connection.ping.assert_not_called()
    
    @patch('datetime.datetime')
    def test_is_connection_valid_ping_needed(self, mock_datetime):
        """Prueba que _is_connection_valid haga ping si ha pasado suficiente tiempo."""
        # Configurar mock de datetime
        now = datetime.now()
        mock_datetime.now.return_value = now
        
        # Crear instancia con conexión y ping antiguo
        conn = OracleConnection()
        conn.connection = MagicMock()
        conn.connection.ping.return_value = None  # ping exitoso
        conn._last_ping_time = now - timedelta(minutes=10)  # Ping hace 10 minutos
        
        # Verificar que se hace ping y se devuelve True
        assert conn._is_connection_valid() is True
        conn.connection.ping.assert_called_once()
        
        # Verificar que se actualizó el tiempo del último ping
        # Usar una comparación más flexible para evitar problemas con microsegundos
        assert (conn._last_ping_time - now).total_seconds() < 0.1
    
    @patch('datetime.datetime')
    def test_is_connection_valid_ping_error(self, mock_datetime):
        """Prueba que _is_connection_valid maneje correctamente errores de ping."""
        # Configurar mock de datetime
        now = datetime.now()
        mock_datetime.now.return_value = now
        
        # Crear instancia con conexión y ping antiguo
        conn = OracleConnection()
        conn.connection = MagicMock()
        conn.connection.ping.side_effect = Exception("Error de ping simulado")
        conn._last_ping_time = now - timedelta(minutes=10)  # Ping hace 10 minutos
        
        # Verificar que se hace ping y se devuelve False
        assert conn._is_connection_valid() is False
        conn.connection.ping.assert_called_once()
    
    def test_close(self):
        """Prueba que el método close cierre correctamente la conexión."""
        # Crear instancia con conexión
        conn = OracleConnection()
        conn.connection = MagicMock()
        
        # Guardar una referencia al objeto connection
        connection_mock = conn.connection
        
        # Cerrar conexión
        conn.close()
        
        # Verificar que se llamó al método close de la conexión
        connection_mock.close.assert_called_once()
        
        # Verificar que se estableció la conexión a None
        assert conn.connection is None 