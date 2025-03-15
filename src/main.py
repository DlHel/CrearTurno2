import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    """Función principal que inicia la aplicación."""
    print("\n==== INICIANDO APLICACIÓN DE GESTIÓN DE TURNOS ====")
    
    # Crear la aplicación
    app = QApplication(sys.argv)
    
    # Establecer el estilo de la aplicación
    app.setStyle("Fusion")
    
    # Crear y mostrar la ventana principal
    window = MainWindow()
    window.show()
    
    print("Aplicación iniciada correctamente. Interfaz de usuario cargada.")
    
    # Ejecutar el bucle principal de la aplicación
    exit_code = app.exec()
    print("\n==== APLICACIÓN FINALIZADA ====")
    sys.exit(exit_code)

if __name__ == "__main__":
    main() 