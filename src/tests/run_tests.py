import unittest
import sys
import os

# Agregar el directorio raíz al path para poder importar los módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar las pruebas
from test_turno_dao import TestTurnoDAO
from test_crear_turno_widget import TestCrearTurnoWidget

if __name__ == '__main__':
    # Crear un test suite con todas las pruebas
    test_suite = unittest.TestSuite()
    
    # Agregar las pruebas de TurnoDAO
    test_suite.addTest(unittest.makeSuite(TestTurnoDAO))
    
    # Agregar las pruebas de CrearTurnoWidget
    test_suite.addTest(unittest.makeSuite(TestCrearTurnoWidget))
    
    # Ejecutar las pruebas
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Salir con código de error si alguna prueba falló
    sys.exit(not result.wasSuccessful()) 