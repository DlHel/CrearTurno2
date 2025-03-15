from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QStackedWidget, QLabel, QTabWidget, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon
import os
from .crear_turno import CrearTurnoWidget
from .buscar_turno import BuscarTurnoWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Gestión de Turnos")
        self.setMinimumSize(1024, 768)
        
        # Configurar el estilo oscuro
        self.setup_dark_theme()
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Menú de pestañas
        self.setup_tabs()
        
        # Configurar módulos
        self.setup_modules()

    def setup_dark_theme(self):
        """Configura el tema oscuro de la aplicación."""
        palette = QPalette()
        
        # Colores base
        background = QColor("#1e1e1e")
        foreground = QColor("#ffffff")
        accent = QColor("#007acc")
        
        # Configurar colores
        palette.setColor(QPalette.ColorRole.Window, background)
        palette.setColor(QPalette.ColorRole.WindowText, foreground)
        palette.setColor(QPalette.ColorRole.Base, QColor("#252526"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#2d2d2d"))
        palette.setColor(QPalette.ColorRole.ToolTipBase, background)
        palette.setColor(QPalette.ColorRole.ToolTipText, foreground)
        palette.setColor(QPalette.ColorRole.Text, foreground)
        palette.setColor(QPalette.ColorRole.Button, background)
        palette.setColor(QPalette.ColorRole.ButtonText, foreground)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, accent)
        palette.setColor(QPalette.ColorRole.Highlight, accent)
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        
        self.setPalette(palette)
        
        # Estilo global de la aplicación
        self.setStyleSheet("""
            QMainWindow {
                background: #1e1e1e;
            }
            QPushButton {
                background: #333333;
                color: white;
                border: 1px solid #555555;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: #444444;
            }
            QPushButton:pressed {
                background: #222222;
            }
            QTabWidget::pane {
                border: 1px solid #3c3c3c;
                background: #1e1e1e;
                top: -1px;
            }
            QTabBar::tab {
                background: #252526;
                color: white;
                padding: 10px 15px;
                border: 1px solid #3c3c3c;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 150px;
                text-align: center;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #007acc;
                color: white;
                border-bottom: none;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
            QTabBar::tab:hover {
                background: #37373d;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
        """)

    def setup_tabs(self):
        """Configura el menú de pestañas horizontal."""
        # Crear el widget de pestañas
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setMovable(True)  # Permitir reordenar pestañas
        self.tab_widget.setTabsClosable(False)  # No mostrar X para cerrar
        
        # Agregar al layout principal
        self.centralWidget().layout().addWidget(self.tab_widget)

    def setup_modules(self):
        """Configura los módulos de la aplicación."""
        # Módulo Crear Turno
        crear_turno = CrearTurnoWidget()
        index = self.tab_widget.addTab(crear_turno, "Crear Turno")
        self.tab_widget.setTabToolTip(index, "Crear y configurar nuevos turnos")
        
        # Módulo Buscar y Editar
        buscar_turno = BuscarTurnoWidget()
        index = self.tab_widget.addTab(buscar_turno, "Buscar y Editar")
        self.tab_widget.setTabToolTip(index, "Buscar y editar turnos existentes")
        
        # Placeholder para los otros módulos
        modules_info = [
            ("Horario Flexible", "Configuración de horarios flexibles"),
            ("Consulta Turno", "Consultar información detallada de turnos"),
            ("Marcaje Asistencia", "Gestionar marcajes de asistencia")
        ]
        
        for module_name, tooltip in modules_info:
            page = QWidget()
            layout = QVBoxLayout(page)
            label = QLabel(f"Módulo: {module_name}\nEn desarrollo...")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            index = self.tab_widget.addTab(page, module_name)
            self.tab_widget.setTabToolTip(index, tooltip) 