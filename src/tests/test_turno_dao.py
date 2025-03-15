import unittest
from unittest.mock import MagicMock, patch
from datetime import time
import sys
import os

# Agregar el directorio raíz al path para poder importar los módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.turno_dao import TurnoDAO
from models.turno import Turno, TurnoDetalleDiario

class TestTurnoDAO(unittest.TestCase):
    
    def setUp(self):
        # Crear un mock para la conexión a la base de datos
        self.db_mock = MagicMock()
        
        # Crear una instancia de TurnoDAO con el mock
        with patch('database.turno_dao.OracleConnection', return_value=self.db_mock):
            self.turno_dao = TurnoDAO()
        
        # Configurar el mock para que _verificar_conexion no haga nada
        self.turno_dao._verificar_conexion = MagicMock()
        
        # Crear un turno de prueba
        self.turno_test = Turno()
        self.turno_test.id_turno = 76
        self.turno_test.nombre = "76-44 Lu a Vi"
        self.turno_test.vigencia = "A"
        self.turno_test.frecuencia = "Diarios"
        
        # Agregar detalles al turno
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        horas_ingreso = [time(9, 0) for _ in range(5)]
        duraciones = [555, 555, 555, 555, 420]
        
        for i, dia in enumerate(dias):
            detalle = TurnoDetalleDiario(
                id_turno_detalle_diario=359 + i,
                id_turno=76,
                jornada=dia,
                hora_ingreso=horas_ingreso[i],
                duracion=duraciones[i]
            )
            self.turno_test.detalles.append(detalle)
    
    def test_buscar_turnos_similares_turno_existente_por_id(self):
        """Prueba que buscar_turnos_similares detecte un turno existente por ID."""
        # Configurar el mock para devolver datos que coincidan con el turno de prueba
        resultados_mock = [
            (76, "76-44 Lu a Vi", "A", "Diarios", 359, "Lunes", MagicMock(hour=9, minute=0), 555),
            (76, "76-44 Lu a Vi", "A", "Diarios", 360, "Martes", MagicMock(hour=9, minute=0), 555),
            (76, "76-44 Lu a Vi", "A", "Diarios", 361, "Miércoles", MagicMock(hour=9, minute=0), 555),
            (76, "76-44 Lu a Vi", "A", "Diarios", 362, "Jueves", MagicMock(hour=9, minute=0), 555),
            (76, "76-44 Lu a Vi", "A", "Diarios", 363, "Viernes", MagicMock(hour=9, minute=0), 420)
        ]
        
        self.db_mock.execute_query.return_value = resultados_mock
        
        # Ejecutar la función a probar
        turnos_similares = self.turno_dao.buscar_turnos_similares(self.turno_test)
        
        # Verificar que se encontró el turno
        self.assertEqual(len(turnos_similares), 1)
        self.assertEqual(turnos_similares[0][0], 76)  # ID del turno
        self.assertEqual(turnos_similares[0][1], "76-44 Lu a Vi")  # Nombre del turno
        
        # Verificar que se llamó a execute_query con los parámetros correctos
        self.db_mock.execute_query.assert_called_with(
            unittest.mock.ANY,  # No verificamos la consulta exacta
            {"id_turno": 76}
        )
    
    def test_buscar_turnos_similares_turno_existente_por_jornada(self):
        """Prueba que buscar_turnos_similares detecte un turno existente por jornada similar."""
        # Configurar el mock para devolver None en la búsqueda por ID
        # y luego datos que coincidan con el turno de prueba en la búsqueda por jornada
        self.db_mock.execute_query.side_effect = [
            [],  # Resultado para la búsqueda por ID exacto
            [],  # Resultado para la búsqueda por ID en el nombre
            [
                (77, "77-44 Lu a Vi", "A", "Diarios", 370, "Lunes", MagicMock(hour=9, minute=0), 555),
                (77, "77-44 Lu a Vi", "A", "Diarios", 371, "Martes", MagicMock(hour=9, minute=0), 555),
                (77, "77-44 Lu a Vi", "A", "Diarios", 372, "Miércoles", MagicMock(hour=9, minute=0), 555),
                (77, "77-44 Lu a Vi", "A", "Diarios", 373, "Jueves", MagicMock(hour=9, minute=0), 555),
                (77, "77-44 Lu a Vi", "A", "Diarios", 374, "Viernes", MagicMock(hour=9, minute=0), 420)
            ]
        ]
        
        # Ejecutar la función a probar
        turnos_similares = self.turno_dao.buscar_turnos_similares(self.turno_test)
        
        # Verificar que se encontró el turno
        self.assertEqual(len(turnos_similares), 1)
        self.assertEqual(turnos_similares[0][0], 77)  # ID del turno
        self.assertEqual(turnos_similares[0][1], "77-44 Lu a Vi")  # Nombre del turno
    
    def test_generar_script_sql_turno_existente(self):
        """Prueba que generar_script_sql genere un script de actualización para un turno existente."""
        # Configurar el mock para indicar que el turno existe
        self.db_mock.execute_query.side_effect = [
            [(1,)],  # Resultado para la consulta COUNT(*) - turno existe
            [  # Resultado para la consulta de detalles existentes
                (359, "Lunes"),
                (360, "Martes"),
                (361, "Miércoles"),
                (362, "Jueves"),
                (363, "Viernes")
            ]
        ]
        
        # Ejecutar la función a probar
        script = self.turno_dao.generar_script_sql(self.turno_test)
        
        # Verificar que el script contiene una actualización en lugar de una inserción
        self.assertIn("UPDATE ASISTENCIAS.TURNO", script)
        self.assertIn("WHERE ID_TURNO = 76", script)
        
        # Verificar que el script elimina los detalles existentes
        self.assertIn("DELETE FROM ASISTENCIAS.TURNO_DETALLE_DIARIO", script)
        self.assertIn("WHERE ID_TURNO = 76", script)
        
        # Verificar que el script inserta los nuevos detalles
        self.assertIn("INSERT INTO ASISTENCIAS.TURNO_DETALLE_DIARIO", script)
        
        # Verificar que se llamó a execute_query con los parámetros correctos
        self.db_mock.execute_query.assert_any_call(
            unittest.mock.ANY,  # No verificamos la consulta exacta
            {"id_turno": 76}
        )
    
    def test_generar_script_sql_turno_nuevo(self):
        """Prueba que generar_script_sql genere un script de inserción para un turno nuevo."""
        # Configurar el mock para indicar que el turno no existe
        self.db_mock.execute_query.side_effect = [
            [(0,)]  # Resultado para la consulta COUNT(*) - turno no existe
        ]
        
        # Ejecutar la función a probar
        script = self.turno_dao.generar_script_sql(self.turno_test)
        
        # Verificar que el script contiene una inserción en lugar de una actualización
        self.assertIn("INSERT INTO ASISTENCIAS.TURNO", script)
        self.assertIn("VALUES (76, '76-44 Lu a Vi', 'A', 'Diarios')", script)
        
        # Verificar que el script no elimina detalles existentes
        self.assertNotIn("DELETE FROM ASISTENCIAS.TURNO_DETALLE_DIARIO", script)
        
        # Verificar que el script inserta los nuevos detalles
        self.assertIn("INSERT INTO ASISTENCIAS.TURNO_DETALLE_DIARIO", script)
        
        # Verificar que se llamó a execute_query con los parámetros correctos
        self.db_mock.execute_query.assert_called_with(
            unittest.mock.ANY,  # No verificamos la consulta exacta
            {"id_turno": 76}
        )

if __name__ == '__main__':
    unittest.main() 