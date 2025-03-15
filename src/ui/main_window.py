from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QStackedWidget, QLabel, QTabWidget, QHBoxLayout, QMessageBox,
    QDialog, QApplication
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon, QPixmap
import os
from .crear_turno import CrearTurnoWidget
from .buscar_turno import BuscarTurnoWidget
from .horario_flexible import HorarioFlexibleWidget
from .consulta_turno import ConsultaTurnoWidget
from .marcaje_asistencia import MarcajeAsistenciaWidget

# Comentamos las importaciones que no existen aún
# from .marcaje_asistencia import MarcajeAsistenciaWidget

class BienvenidaDialog(QDialog):
    """Diálogo de bienvenida que se muestra al iniciar la aplicación por primera vez."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bienvenido a Gestión de Turnos")
        self.setMinimumSize(650, 450)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #cdd6f4;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #89b4fa, stop:1 #74c7ec);
                color: #1e1e2e;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #74c7ec, stop:1 #89b4fa);
            }
            QPushButton:pressed {
                background: #89b4fa;
            }
        """)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Título
        title_label = QLabel("¡Bienvenido al Sistema de Gestión de Turnos!")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            color: #89b4fa;
            padding: 10px;
            background-color: #181825;
            border-radius: 8px;
            border-bottom: 2px solid #89b4fa;
        """)
        layout.addWidget(title_label)
        
        # Contenedor para el contenido principal
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            background-color: #181825;
            border-radius: 8px;
            border: 1px solid #313244;
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Descripción
        description_label = QLabel(
            "Esta aplicación le permite gestionar turnos de trabajo de manera eficiente y organizada."
        )
        description_label.setWordWrap(True)
        description_label.setFont(QFont("Segoe UI", 12))
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(description_label)
        
        # Características principales
        features_label = QLabel("Características principales:")
        features_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        features_label.setStyleSheet("color: #f9e2af;")
        content_layout.addWidget(features_label)
        
        # Lista de características
        features = [
            "✓ Creación y edición de turnos",
            "✓ Búsqueda optimizada de turnos en base de datos",
            "✓ Detección y gestión de turnos duplicados",
            "✓ Generación de scripts SQL",
            "✓ Interfaz moderna y fácil de usar"
        ]
        
        for feature in features:
            feature_label = QLabel(feature)
            feature_label.setFont(QFont("Segoe UI", 11))
            feature_label.setStyleSheet("padding-left: 20px; color: #a6e3a1;")
            content_layout.addWidget(feature_label)
        
        # Nota
        note_label = QLabel(
            "Nota: Esta aplicación se conecta a la base de datos Oracle para gestionar la información de turnos."
        )
        note_label.setWordWrap(True)
        note_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Normal, True))  # Italic
        note_label.setStyleSheet("color: #cba6f7; margin-top: 10px;")
        note_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(note_label)
        
        # Agregar el contenedor al layout principal
        layout.addWidget(content_widget)
        
        # Botón de aceptar
        accept_button = QPushButton("Comenzar")
        accept_button.setMinimumHeight(40)
        accept_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        accept_button.clicked.connect(self.accept)
        
        # Contenedor para el botón
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(accept_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addStretch()

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
        
        # Mostrar diálogo de bienvenida si es la primera vez
        self.check_first_run()

    def setup_dark_theme(self):
        """Configura el tema oscuro para toda la aplicación."""
        # Aplicar estilo global
        self.setStyleSheet("""
            QMainWindow, QDialog {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #313244;
                background-color: #1e1e2e;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #181825;
                color: #cdd6f4;
                padding: 10px 20px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #89b4fa, stop:1 #74c7ec);
                color: #1e1e2e;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
            QTabBar::tab:hover:!selected {
                background-color: #313244;
            }
            QLabel {
                color: #cdd6f4;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #89b4fa, stop:1 #74c7ec);
                color: #1e1e2e;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #74c7ec, stop:1 #89b4fa);
            }
            QPushButton:pressed {
                background: #89b4fa;
            }
            QMessageBox {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QMessageBox QPushButton {
                min-width: 80px;
                min-height: 30px;
            }
            QScrollBar:vertical {
                border: none;
                background: #181825;
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #313244;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #45475a;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                border: none;
                background: #181825;
                height: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background: #313244;
                min-width: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #45475a;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
        
        # Configurar la paleta de colores
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#1e1e2e"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#cdd6f4"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#181825"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#1e1e2e"))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#313244"))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#cdd6f4"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#cdd6f4"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#313244"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#cdd6f4"))
        palette.setColor(QPalette.ColorRole.BrightText, QColor("#f9e2af"))
        palette.setColor(QPalette.ColorRole.Link, QColor("#89b4fa"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#89b4fa"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#1e1e2e"))
        
        self.setPalette(palette)
        QApplication.setPalette(palette)

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
        # Crear e inicializar los módulos
        # Módulo Crear Turno
        self.crear_turno_tab = CrearTurnoWidget()
        self.tab_widget.addTab(self.crear_turno_tab, "Crear Turno")
        self.tab_widget.setTabToolTip(0, "Crear y gestionar turnos para funcionarios")
        
        # Módulo Buscar Turno
        self.buscar_turno_tab = BuscarTurnoWidget()
        self.tab_widget.addTab(self.buscar_turno_tab, "Buscar y Editar Turno")
        self.tab_widget.setTabToolTip(1, "Buscar y editar turnos existentes")
        
        # Módulo Horario Flexible
        self.horario_flexible_tab = HorarioFlexibleWidget()
        self.tab_widget.addTab(self.horario_flexible_tab, "Horario Flexible")
        self.tab_widget.setTabToolTip(2, "Gestionar horarios flexibles para funcionarios")
        
        # Módulo Consulta Turno
        self.consulta_turno_tab = ConsultaTurnoWidget()
        self.tab_widget.addTab(self.consulta_turno_tab, "Consulta Turno")
        self.tab_widget.setTabToolTip(3, "Consultar turnos asignados por funcionario")
        
        # Módulo Marcaje Asistencia
        self.marcaje_asistencia_tab = MarcajeAsistenciaWidget()
        self.tab_widget.addTab(self.marcaje_asistencia_tab, "Marcaje Asistencia")
        self.tab_widget.setTabToolTip(4, "Registrar y consultar marcajes de asistencia")

    def check_first_run(self):
        """Verifica si es la primera ejecución de la aplicación y muestra el diálogo de bienvenida."""
        settings = QSettings("PegaSystems", "GestionTurnos")
        first_run = settings.value("first_run", True, type=bool)
        
        if first_run:
            dialog = BienvenidaDialog(self)
            dialog.exec()
            settings.setValue("first_run", False) 