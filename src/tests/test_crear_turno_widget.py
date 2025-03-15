import unittest
from unittest.mock import MagicMock, patch
from datetime import time
import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox

# Agregar el directorio raíz al path para poder importar los módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.crear_turno.crear_turno_widget import CrearTurnoWidget
from models.turno import Turno, TurnoDetalleDiario

class TestCrearTurnoWidget(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Crear una instancia de QApplication para las pruebas
        cls.app = QApplication([])
    
    def setUp(self):
        # Crear mocks para las dependencias
        self.turno_dao_mock = MagicMock()
        
        # Crear una instancia de CrearTurnoWidget con el mock
        with patch('ui.crear_turno.crear_turno_widget.TurnoDAO', return_value=self.turno_dao_mock):
            self.widget = CrearTurnoWidget()
        
        # Configurar el widget con datos de prueba
        self.widget.id_turno_label.setText("76")
        self.widget.nombre_custom_edit.setText("76-44 Lu a Vi")
        self.widget.btn_activo.setChecked(True)
        
        # Crear detalles de prueba
        self.widget.detalles = [
            {
                'dia': 'Lunes',
                'hora_ingreso': '09:00',
                'hora_salida': '18:15',
                'duracion_minutos': 555,
                'id': 359
            },
            {
                'dia': 'Martes',
                'hora_ingreso': '09:00',
                'hora_salida': '18:15',
                'duracion_minutos': 555,
                'id': 360
            },
            {
                'dia': 'Miércoles',
                'hora_ingreso': '09:00',
                'hora_salida': '18:15',
                'duracion_minutos': 555,
                'id': 361
            },
            {
                'dia': 'Jueves',
                'hora_ingreso': '09:00',
                'hora_salida': '18:15',
                'duracion_minutos': 555,
                'id': 362
            },
            {
                'dia': 'Viernes',
                'hora_ingreso': '09:00',
                'hora_salida': '16:00',
                'duracion_minutos': 420,
                'id': 363
            }
        ]
        
        # Mock para la función validar_turno
        self.widget.validar_turno = MagicMock(return_value=True)
        
        # Mock para la función actualizar_tabla_detalles
        self.widget.actualizar_tabla_detalles = MagicMock()
        
        # Mock para la función _generar_nombre_turno
        self.widget._generar_nombre_turno = MagicMock(return_value="76-44 Lu a Vi")
        
        # Mock para la función inicializar_nuevo_turno
        self.widget.inicializar_nuevo_turno = MagicMock()
        
        # Mock para la función generar_script_sql
        self.widget.generar_script_sql = MagicMock()
    
    def test_guardar_turno_turno_existente(self):
        """Prueba que guardar_turno detecte un turno existente y muestre la alerta correspondiente."""
        # Configurar el mock para buscar_turnos_similares para que devuelva un turno existente
        turnos_similares = [
            (76, "76-44 Lu a Vi", [
                {
                    'jornada': 'Lunes',
                    'hora_ingreso': time(9, 0),
                    'hora_salida': time(18, 15)
                },
                {
                    'jornada': 'Martes',
                    'hora_ingreso': time(9, 0),
                    'hora_salida': time(18, 15)
                },
                {
                    'jornada': 'Miércoles',
                    'hora_ingreso': time(9, 0),
                    'hora_salida': time(18, 15)
                },
                {
                    'jornada': 'Jueves',
                    'hora_ingreso': time(9, 0),
                    'hora_salida': time(18, 15)
                },
                {
                    'jornada': 'Viernes',
                    'hora_ingreso': time(9, 0),
                    'hora_salida': time(16, 0)
                }
            ])
        ]
        self.turno_dao_mock.buscar_turnos_similares.return_value = turnos_similares
        
        # Mock para QMessageBox.question para simular que el usuario hace clic en "No"
        with patch('PyQt6.QtWidgets.QMessageBox.question', return_value=QMessageBox.StandardButton.No) as mock_question:
            # Ejecutar la función a probar
            self.widget.guardar_turno()
            
            # Verificar que se llamó a buscar_turnos_similares
            self.turno_dao_mock.buscar_turnos_similares.assert_called_once()
            
            # Verificar que se mostró el mensaje de alerta
            mock_question.assert_called_once()
            
            # Verificar que el mensaje contiene la información del turno existente
            args, kwargs = mock_question.call_args
            self.assertIn("¡ATENCIÓN! Turno ya existe en la base de datos", args[1])  # Título
            self.assertIn("El turno con ID 76 ya existe en la base de datos", args[2])  # Mensaje
            
            # Verificar que no se llamó a guardar_turno en el DAO
            self.turno_dao_mock.guardar_turno.assert_not_called()
    
    def test_guardar_turno_turno_existente_continuar(self):
        """Prueba que guardar_turno continúe si el usuario decide continuar a pesar de la duplicidad."""
        # Configurar el mock para buscar_turnos_similares para que devuelva un turno existente
        turnos_similares = [
            (76, "76-44 Lu a Vi", [
                {
                    'jornada': 'Lunes',
                    'hora_ingreso': time(9, 0),
                    'hora_salida': time(18, 15)
                },
                # ... otros detalles
            ])
        ]
        self.turno_dao_mock.buscar_turnos_similares.return_value = turnos_similares
        
        # Mock para QMessageBox.question para simular que el usuario hace clic en "Sí"
        with patch('PyQt6.QtWidgets.QMessageBox.question', return_value=QMessageBox.StandardButton.Yes) as mock_question:
            # Ejecutar la función a probar
            self.widget.guardar_turno()
            
            # Verificar que se llamó a buscar_turnos_similares
            self.turno_dao_mock.buscar_turnos_similares.assert_called_once()
            
            # Verificar que se mostró el mensaje de alerta
            mock_question.assert_called()
            
            # Verificar que se llamó a guardar_turno en el DAO
            self.turno_dao_mock.guardar_turno.assert_called_once()
    
    def test_guardar_turno_turno_nuevo(self):
        """Prueba que guardar_turno no muestre alerta si el turno no existe."""
        # Configurar el mock para buscar_turnos_similares para que no devuelva turnos
        self.turno_dao_mock.buscar_turnos_similares.return_value = []
        
        # Ejecutar la función a probar
        self.widget.guardar_turno()
        
        # Verificar que se llamó a buscar_turnos_similares
        self.turno_dao_mock.buscar_turnos_similares.assert_called_once()
        
        # Verificar que se llamó a guardar_turno en el DAO
        self.turno_dao_mock.guardar_turno.assert_called_once()
    
    def test_guardar_turno_turno_exactamente_igual(self):
        """Prueba que guardar_turno muestre alerta si encuentra un turno exactamente igual."""
        # Configurar el mock para buscar_turnos_similares para que devuelva un turno exactamente igual
        turnos_similares = [
            (77, "77-44 Lu a Vi", [
                {
                    'jornada': 'Lunes',
                    'hora_ingreso': time(9, 0),
                    'hora_salida': time(18, 15)
                },
                # ... otros detalles
            ])
        ]
        self.turno_dao_mock.buscar_turnos_similares.return_value = turnos_similares
        
        # Mock para QMessageBox.question para simular que el usuario hace clic en "No"
        with patch('PyQt6.QtWidgets.QMessageBox.question', return_value=QMessageBox.StandardButton.No) as mock_question:
            # Ejecutar la función a probar
            self.widget.guardar_turno()
            
            # Verificar que se llamó a buscar_turnos_similares
            self.turno_dao_mock.buscar_turnos_similares.assert_called_once()
            
            # Verificar que se mostró el mensaje de alerta
            mock_question.assert_called_once()
            
            # Verificar que el mensaje contiene la información del turno exactamente igual
            args, kwargs = mock_question.call_args
            self.assertIn("Turnos Exactamente Iguales Encontrados", args[1])  # Título
            self.assertIn("Se encontraron 1 turnos exactamente iguales", args[2])  # Mensaje
            
            # Verificar que no se llamó a guardar_turno en el DAO
            self.turno_dao_mock.guardar_turno.assert_not_called()

if __name__ == '__main__':
    unittest.main() 