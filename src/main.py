import sys
import os

# Añadir el directorio raíz al path para que las importaciones funcionen correctamente
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QMainWindow, QSplashScreen, QMessageBox
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, QTimer

from ui.main_window import MainWindow
from database.oracle_connection import OracleConnection

def main():
    """Función principal que inicia la aplicación."""
    print("\n==== INICIANDO APLICACIÓN DE GESTIÓN DE TURNOS v1.2 ====")
    print("Características principales:")
    print("- Creación y edición de turnos")
    print("- Búsqueda optimizada de turnos en base de datos")
    print("- Detección y gestión de turnos duplicados")
    print("- Generación de scripts SQL")
    
    app = QApplication(sys.argv)
    
    # Establecer conexión a la base de datos
    try:
        conn = OracleConnection()  # Usar el constructor directamente, ya que implementa singleton internamente
        conn.connect()  # Llamar al método connect explícitamente
        if conn.is_connected():
            print("Conexión establecida exitosamente")
        else:
            print("No se pudo establecer la conexión")
            QMessageBox.critical(
                None, 
                "Error de Conexión", 
                "No se pudo establecer la conexión con la base de datos.\nLa aplicación se cerrará."
            )
            return 1
    except Exception as e:
        print(f"Error al conectar: {str(e)}")
        QMessageBox.critical(
            None, 
            "Error de Conexión", 
            f"Error al conectar con la base de datos: {str(e)}\nLa aplicación se cerrará."
        )
        return 1
    
    # Crear y mostrar la ventana principal
    main_window = MainWindow()
    main_window.show()
    
    print("Aplicación iniciada correctamente. Interfaz de usuario cargada.")
    
    # Ejecutar el bucle principal de la aplicación
    ret = app.exec()
    
    # Cerrar la conexión de la base de datos al finalizar
    conn.close()
    
    print("\n==== APLICACIÓN FINALIZADA ====")
    print(f"Código de salida: {ret}")
    
    return ret

if __name__ == "__main__":
    sys.exit(main()) 