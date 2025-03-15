import pytest
from unittest.mock import patch, MagicMock
import sys
from src.main import main

@pytest.mark.unit
class TestMain:
    """Pruebas para la función principal."""
    
    @patch('src.main.QApplication')
    @patch('src.main.MainWindow')
    @patch('src.main.OracleConnection')
    def test_main_success(self, mock_oracle_connection, mock_main_window, mock_qapp):
        """Prueba que la función main funcione correctamente cuando la conexión es exitosa."""
        # Configurar mocks
        mock_conn_instance = mock_oracle_connection.return_value
        mock_conn_instance.is_connected.return_value = True
        
        mock_app_instance = mock_qapp.return_value
        mock_app_instance.exec.return_value = 0
        
        mock_window_instance = mock_main_window.return_value
        
        # Ejecutar la función main
        result = main()
        
        # Verificar que se creó la aplicación
        mock_qapp.assert_called_once_with(sys.argv)
        
        # Verificar que se estableció la conexión
        mock_conn_instance.connect.assert_called_once()
        
        # Verificar que se creó y mostró la ventana principal
        mock_main_window.assert_called_once()
        mock_window_instance.show.assert_called_once()
        
        # Verificar que se ejecutó la aplicación
        mock_app_instance.exec.assert_called_once()
        
        # Verificar que se cerró la conexión
        mock_conn_instance.close.assert_called_once()
        
        # Verificar que se devolvió el código de salida correcto
        assert result == 0
    
    @patch('src.main.QMessageBox')
    @patch('src.main.QApplication')
    @patch('src.main.OracleConnection')
    def test_main_connection_error(self, mock_oracle_connection, mock_qapp, mock_message_box):
        """Prueba que la función main maneje correctamente los errores de conexión."""
        # Configurar mocks
        mock_conn_instance = mock_oracle_connection.return_value
        mock_conn_instance.is_connected.return_value = False
        
        # Ejecutar la función main
        result = main()
        
        # Verificar que se creó la aplicación
        mock_qapp.assert_called_once_with(sys.argv)
        
        # Verificar que se estableció la conexión
        mock_conn_instance.connect.assert_called_once()
        
        # Verificar que se mostró un mensaje de error
        mock_message_box.critical.assert_called_once()
        
        # Verificar que no se ejecutó la aplicación
        mock_app_instance = mock_qapp.return_value
        mock_app_instance.exec.assert_not_called()
        
        # Verificar que se devolvió el código de error
        assert result == 1
    
    @patch('src.main.QMessageBox')
    @patch('src.main.QApplication')
    @patch('src.main.OracleConnection')
    def test_main_connection_exception(self, mock_oracle_connection, mock_qapp, mock_message_box):
        """Prueba que la función main maneje correctamente las excepciones durante la conexión."""
        # Configurar mocks
        mock_conn_instance = mock_oracle_connection.return_value
        mock_conn_instance.connect.side_effect = Exception("Error de conexión simulado")
        
        # Ejecutar la función main
        result = main()
        
        # Verificar que se creó la aplicación
        mock_qapp.assert_called_once_with(sys.argv)
        
        # Verificar que se intentó establecer la conexión
        mock_conn_instance.connect.assert_called_once()
        
        # Verificar que se mostró un mensaje de error
        mock_message_box.critical.assert_called_once()
        
        # Verificar que no se ejecutó la aplicación
        mock_app_instance = mock_qapp.return_value
        mock_app_instance.exec.assert_not_called()
        
        # Verificar que se devolvió el código de error
        assert result == 1 