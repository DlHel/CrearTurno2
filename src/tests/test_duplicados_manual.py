import sys
import os
from datetime import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import QTimer, QTime

# Agregar el directorio raíz al path para poder importar los módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.crear_turno.crear_turno_widget import CrearTurnoWidget
from models.turno import Turno, TurnoDetalleDiario
from database.turno_dao import TurnoDAO

class TestDuplicadosWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test de Detección de Turnos Duplicados")
        self.setGeometry(100, 100, 800, 800)
        
        # Crear widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Crear layout
        layout = QVBoxLayout(central_widget)
        
        # Crear widget de CrearTurno
        self.crear_turno_widget = CrearTurnoWidget()
        layout.addWidget(self.crear_turno_widget)
        
        # Crear botones de prueba
        self.btn_cargar_turno_existente = QPushButton("Cargar Turno Existente (ID 76)")
        self.btn_cargar_turno_existente.clicked.connect(self.cargar_turno_existente)
        layout.addWidget(self.btn_cargar_turno_existente)
        
        self.btn_guardar = QPushButton("Guardar Turno (Debería Detectar Duplicado)")
        self.btn_guardar.clicked.connect(self.guardar_turno)
        layout.addWidget(self.btn_guardar)
        
        # Crear etiqueta para mostrar resultados
        self.lbl_resultado = QLabel("Resultado: ")
        layout.addWidget(self.lbl_resultado)
        
        # Inicializar DAO
        self.turno_dao = TurnoDAO()
        
        # Configurar temporizador para cargar automáticamente el turno existente
        QTimer.singleShot(500, self.cargar_turno_existente)
    
    def cargar_turno_existente(self):
        """Carga un turno existente en la interfaz para simular que el usuario lo está creando."""
        try:
            # Limpiar la interfaz
            self.crear_turno_widget.inicializar_nuevo_turno(limpiar_tabla=True)
            
            # Configurar el ID del turno
            self.crear_turno_widget.id_turno_label.setText("76")
            
            # Configurar el nombre del turno
            self.crear_turno_widget.nombre_custom_edit.setText("76-44 Lu a Vi")
            
            # Configurar la vigencia
            self.crear_turno_widget.btn_activo.setChecked(True)
            
            # Agregar detalles
            dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
            horas_ingreso = ["09:00" for _ in range(5)]
            horas_salida = ["18:15" for _ in range(4)] + ["16:00"]
            duraciones = [555, 555, 555, 555, 420]
            
            for i, dia in enumerate(dias):
                # Configurar el formulario de detalle
                self.crear_turno_widget.dia_combo.setCurrentText(dia)
                self.crear_turno_widget.hora_ingreso_edit.setTime(QTime(9, 0))
                if dia == "Viernes":
                    self.crear_turno_widget.hora_salida_edit.setTime(QTime(16, 0))
                else:
                    self.crear_turno_widget.hora_salida_edit.setTime(QTime(18, 15))
                
                # Agregar el detalle
                self.crear_turno_widget.agregar_detalle()
            
            self.lbl_resultado.setText("Resultado: Turno existente cargado correctamente")
            
        except Exception as e:
            self.lbl_resultado.setText(f"Error al cargar turno existente: {str(e)}")
    
    def guardar_turno(self):
        """Intenta guardar el turno, debería detectar que ya existe."""
        try:
            # Verificar que el turno actual tiene el mismo ID que el existente
            id_turno = self.crear_turno_widget.id_turno_label.text()
            if id_turno != "76":
                self.lbl_resultado.setText(f"Error: El ID del turno debería ser 76, pero es {id_turno}")
                return
            
            # Guardar el turno
            self.crear_turno_widget.guardar_turno()
            
            # El resultado se mostrará en los diálogos de la aplicación
            self.lbl_resultado.setText("Resultado: Se intentó guardar el turno. Verifica si se mostró la alerta de duplicidad.")
            
        except Exception as e:
            self.lbl_resultado.setText(f"Error al guardar turno: {str(e)}")

if __name__ == "__main__":
    # Crear la aplicación
    app = QApplication(sys.argv)
    
    # Crear la ventana principal
    window = TestDuplicadosWindow()
    window.show()
    
    # Ejecutar la aplicación
    sys.exit(app.exec()) 