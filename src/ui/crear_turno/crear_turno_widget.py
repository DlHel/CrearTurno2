from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QTimeEdit, QLineEdit,
    QTableWidget, QTableWidgetItem, QMessageBox,
    QFileDialog, QGroupBox, QCheckBox, QFrame,
    QDialog, QTextEdit, QDialogButtonBox, QHeaderView,
    QListWidget, QFormLayout, QSpacerItem, QSizePolicy,
    QSplitter, QListWidgetItem, QSpinBox, QGridLayout
)
from PyQt6.QtGui import QFont, QKeyEvent, QIntValidator, QColor, QIcon, QSyntaxHighlighter, QTextCharFormat
from PyQt6.QtCore import Qt, QTime, pyqtSignal, QTimer, QRegularExpression
from datetime import datetime, time, timedelta
import sys
sys.path.append('src')
from src.models.turno import Turno, TurnoDetalleDiario
from src.database.turno_dao import TurnoDAO

class TimeEditMejorado(QTimeEdit):
    """Control de tiempo mejorado que facilita la entrada de horas."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDisplayFormat("HH:mm")
        self.setButtonSymbols(QTimeEdit.ButtonSymbols.NoButtons)  # Ocultar botones de spinbox
        
        # Variables para gestionar entrada numérica
        self._buffer_numerico = ""
        self._posicion_cursor = 0
        self._ultima_tecla = None
        
        # Crear botón para mostrar selector de hora
        self._btn_selector = QPushButton("🕒")
        self._btn_selector.setFixedWidth(30)
        self._btn_selector.setStyleSheet("""
            QPushButton {
                background: #3c3c3c;
                border: none;
                border-radius: 4px;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #4c4c4c;
            }
            QPushButton:pressed {
                background: #2c2c2c;
            }
        """)
        self._btn_selector.clicked.connect(self._mostrar_selector_hora)
        
        # Estilo
        self.setStyleSheet("""
            QTimeEdit {
                padding: 8px;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                background: #252526;
                color: white;
                font-size: 14px;
            }
            QTimeEdit:focus {
                border: 1px solid #007acc;
            }
        """)
    
    def _mostrar_selector_hora(self):
        """Muestra un diálogo con un selector visual de hora."""
        dialog = QDialog(self.parent())
        dialog.setWindowTitle("Seleccionar Hora")
        dialog.setMinimumSize(300, 400)
        dialog.setModal(True)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: white;
            }
            QLabel {
                color: white;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # Título
        titulo = QLabel("Seleccione la hora:")
        titulo.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(titulo)
        
        # Contenedor para horas y minutos
        tiempo_container = QWidget()
        tiempo_layout = QHBoxLayout(tiempo_container)
        
        # Selector de horas
        horas_container = QWidget()
        horas_layout = QVBoxLayout(horas_container)
        horas_label = QLabel("Horas")
        horas_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        horas_layout.addWidget(horas_label)
        
        horas_list = QListWidget()
        horas_list.setStyleSheet("""
            QListWidget {
                background-color: #252526;
                color: white;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #264f78;
            }
        """)
        for hora in range(24):
            horas_list.addItem(f"{hora:02d}")
        # Seleccionar hora actual
        horas_list.setCurrentRow(self.time().hour())
        horas_layout.addWidget(horas_list)
        
        # Selector de minutos
        minutos_container = QWidget()
        minutos_layout = QVBoxLayout(minutos_container)
        minutos_label = QLabel("Minutos")
        minutos_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        minutos_layout.addWidget(minutos_label)
        
        minutos_list = QListWidget()
        minutos_list.setStyleSheet("""
            QListWidget {
                background-color: #252526;
                color: white;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #264f78;
            }
        """)
        # Agregar minutos en incrementos de 5
        for minuto in range(0, 60, 5):
            minutos_list.addItem(f"{minuto:02d}")
        # También agregar opción para otros minutos
        minutos_list.addItem("Otro...")
        # Seleccionar minuto actual (el más cercano a los increments de 5)
        minuto_actual = self.time().minute()
        minuto_idx = round(minuto_actual / 5)
        if minuto_idx >= 12:  # Evitar índice fuera de rango
            minuto_idx = 11
        minutos_list.setCurrentRow(minuto_idx)
        minutos_layout.addWidget(minutos_list)
        
        # Input para "otros" minutos
        otros_minutos_container = QWidget()
        otros_minutos_layout = QHBoxLayout(otros_minutos_container)
        otros_minutos_label = QLabel("Otro minuto:")
        otros_minutos_input = QLineEdit()
        otros_minutos_input.setStyleSheet("""
            QLineEdit {
                background-color: #252526;
                color: white;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        otros_minutos_input.setValidator(QIntValidator(0, 59))
        otros_minutos_input.setText(str(minuto_actual))
        otros_minutos_layout.addWidget(otros_minutos_label)
        otros_minutos_layout.addWidget(otros_minutos_input)
        
        minutos_list.currentRowChanged.connect(
            lambda idx: otros_minutos_container.setVisible(idx == 12)
        )
        otros_minutos_container.setVisible(False)
        
        minutos_layout.addWidget(otros_minutos_container)
        
        # Añadir selectors al contenedor de tiempo
        tiempo_layout.addWidget(horas_container)
        tiempo_layout.addWidget(minutos_container)
        layout.addWidget(tiempo_container)
        
        # Botones
        button_layout = QHBoxLayout()
        aceptar_btn = QPushButton("Aceptar")
        aceptar_btn.setStyleSheet("""
            QPushButton {
                background: #007acc;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #0098ff;
            }
        """)
        
        cancelar_btn = QPushButton("Cancelar")
        cancelar_btn.setStyleSheet("""
            QPushButton {
                background: #555555;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #666666;
            }
        """)
        
        button_layout.addWidget(aceptar_btn)
        button_layout.addWidget(cancelar_btn)
        layout.addLayout(button_layout)
        
        # Conectar botones
        aceptar_btn.clicked.connect(lambda: self._aplicar_seleccion_hora(
            horas_list.currentRow(),
            minutos_list.currentRow(),
            otros_minutos_input.text(),
            dialog
        ))
        cancelar_btn.clicked.connect(dialog.reject)
        
        # Mostrar diálogo
        dialog.exec()
    
    def _aplicar_seleccion_hora(self, hora_idx, minuto_idx, otro_minuto, dialog):
        """Aplica la hora seleccionada en el diálogo."""
        hora = hora_idx
        
        # Determinar minutos
        if minuto_idx == 12:  # Opción "Otro..."
            try:
                minuto = int(otro_minuto)
                if minuto < 0 or minuto > 59:
                    minuto = 0
            except ValueError:
                minuto = 0
        else:
            minuto = minuto_idx * 5
        
        # Establecer la hora
        self.setTime(QTime(hora, minuto))
        
        # Cerrar el diálogo
        dialog.accept()
    
    def keyPressEvent(self, event: QKeyEvent):
        """Maneja la entrada de teclado para permitir una entrada más natural de la hora."""
        key = event.key()
        
        # Backspace/Delete - borrar todo
        if key == Qt.Key.Key_Backspace or key == Qt.Key.Key_Delete:
            self._buffer_numerico = ""
            self.setTime(QTime(0, 0))
            return
        
        # Si es un número, procesarlo
        if key >= Qt.Key.Key_0 and key <= Qt.Key.Key_9:
            digit = key - Qt.Key.Key_0  # Convertir a dígito
            
            # Si el buffer está vacío o tiene 4 dígitos, empezar de nuevo
            if not self._buffer_numerico or len(self._buffer_numerico) == 4:
                self._buffer_numerico = str(digit)
            else:
                self._buffer_numerico += str(digit)
                
            # Auto-formatear según la longitud
            if len(self._buffer_numerico) == 1:
                # Si es un solo dígito, podría ser hora o minuto
                hora = 0
                minuto = int(self._buffer_numerico)
            elif len(self._buffer_numerico) == 2:
                # Dos dígitos - verificar si es una hora válida
                valor = int(self._buffer_numerico)
                if valor > 23:
                    # Es hora y minuto
                    hora = int(self._buffer_numerico[0])
                    minuto = int(self._buffer_numerico[1])
                else:
                    # Es solo hora
                    hora = valor
                    minuto = 0
            elif len(self._buffer_numerico) == 3:
                # Tres dígitos - primera cifra es hora, las otras dos son minutos
                hora = int(self._buffer_numerico[0])
                minutos_str = self._buffer_numerico[1:]
                minuto = int(minutos_str)
                if minuto > 59:
                    minuto = 59
            elif len(self._buffer_numerico) == 4:
                # Cuatro dígitos - HH:MM
                horas_str = self._buffer_numerico[:2]
                minutos_str = self._buffer_numerico[2:]
                hora = int(horas_str)
                if hora > 23:
                    hora = 23
                minuto = int(minutos_str)
                if minuto > 59:
                    minuto = 59
            
            # Establecer la hora
            self.setTime(QTime(hora, minuto))
            return
            
        # Para cualquier otra tecla, usar el comportamiento predeterminado
        super().keyPressEvent(event)
    
    def focusInEvent(self, event):
        """Al recibir el foco, seleccionar todo el texto."""
        super().focusInEvent(event)
        QTimer.singleShot(0, self.selectAll)


class ScriptPreviewDialog(QDialog):
    """Diálogo para mostrar una vista previa del script SQL."""
    
    def __init__(self, script, parent=None):
        super().__init__(parent)
        self.script = script
        self.init_ui()
        
    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        self.setWindowTitle("Vista Previa del Script SQL")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("Vista Previa del Script SQL")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #007acc; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Editor de texto para mostrar el script
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                font-family: "Consolas", monospace;
                padding: 10px;
                selection-background-color: #264f78;
            }
        """)
        self.text_edit.setText(self.script)
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)  # Evitar envolver líneas para SQL
        layout.addWidget(self.text_edit)
        
        # Botones
        button_layout = QHBoxLayout()
        
        self.export_button = QPushButton("Exportar")
        self.export_button.setStyleSheet("""
            QPushButton {
                background: #007acc;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #0098ff;
            }
            QPushButton:pressed {
                background: #005c99;
            }
        """)
        self.export_button.clicked.connect(self.export_script)
        
        self.register_button = QPushButton("Registrar en Google Sheets")
        self.register_button.setStyleSheet("""
            QPushButton {
                background: #2ea44f;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #3ab65c;
            }
            QPushButton:pressed {
                background: #259c46;
            }
        """)
        self.register_button.clicked.connect(self.register_to_sheets)
        
        self.close_button = QPushButton("Cerrar")
        self.close_button.setStyleSheet("""
            QPushButton {
                background: #555555;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #666666;
            }
            QPushButton:pressed {
                background: #444444;
            }
        """)
        self.close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.register_button)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def export_script(self):
        """Exporta el script a un archivo."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Script SQL",
            "",
            "Archivos SQL (*.sql);;Todos los archivos (*)"
        )
        
        if filename:
            # Asegurar que el archivo termine en .sql
            if not filename.lower().endswith('.sql'):
                filename += '.sql'
            
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.script)
                QMessageBox.information(
                    self,
                    "Éxito",
                    f"Script guardado en {filename}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error al guardar el archivo: {str(e)}"
                )
    
    def register_to_sheets(self):
        """Registra los turnos en Google Sheets."""
        # Aquí se implementaría la integración con Google Sheets
        QMessageBox.information(
            self,
            "Registrar en Google Sheets",
            "Esta funcionalidad está en desarrollo."
        )

class CrearTurnoWidget(QWidget):
    """Widget para crear turnos"""

    def __init__(self, parent=None):
        """Inicializa el widget de creación de turnos."""
        super().__init__(parent)
        
        # Inicializar variables
        self.dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        self.detalles = []
        self.turno_actual = None
        self.turnos_creados = []
        self.tabla_con_datos = False
        self.is_dark_mode = False
        self.detalle_editando_id = None
        self.turno_dao = TurnoDAO()
        
        print("Inicializando CrearTurnoWidget")
        
        # Configurar la interfaz de usuario
        self.setup_ui()
        
        # Inicializar el turno
        self.inicializar_nuevo_turno()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Establecer estilo global para el widget
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                background-color: #181825;
                border-radius: 8px;
                border: 1px solid #313244;
                margin-top: 1ex;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                color: #89b4fa;
            }
            QLabel {
                color: #cdd6f4;
            }
            QLineEdit, QComboBox, QSpinBox, QTimeEdit {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 5px;
                color: #cdd6f4;
                selection-background-color: #89b4fa;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTimeEdit:focus {
                border: 1px solid #89b4fa;
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
            QPushButton:disabled {
                background: #45475a;
                color: #6c7086;
            }
            QTableWidget {
                background-color: #181825;
                alternate-background-color: #1e1e2e;
                border: 1px solid #313244;
                border-radius: 4px;
                gridline-color: #313244;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #89b4fa;
                color: #1e1e2e;
            }
            QHeaderView::section {
                background-color: #313244;
                color: #cdd6f4;
                padding: 5px;
                border: 1px solid #45475a;
            }
            QCheckBox {
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 1px solid #45475a;
            }
            QCheckBox::indicator:unchecked {
                background-color: #313244;
            }
            QCheckBox::indicator:checked {
                background-color: #89b4fa;
                image: url(check.png);
            }
        """)
        
        # Título
        title_label = QLabel("Crear Turno")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            color: #89b4fa;
            margin-bottom: 10px;
            padding: 10px;
            background-color: #181825;
            border-radius: 8px;
            border-bottom: 2px solid #89b4fa;
        """)
        main_layout.addWidget(title_label)

        # Sección 1: Información del turno (compacta)
        turno_info_group = QGroupBox("Información del Turno")
        turno_info_layout = QVBoxLayout(turno_info_group)
        turno_info_layout.setContentsMargins(15, 20, 15, 15)
        turno_info_layout.setSpacing(10)
        
        # Fila 1: ID, Nombre, Vigencia y Total de horas en una sola línea
        info_layout = QHBoxLayout()
        
        # ID del Turno
        id_container = QWidget()
        id_layout = QHBoxLayout(id_container)
        id_layout.setContentsMargins(0, 0, 0, 0)
        id_layout.setSpacing(5)
        
        id_label = QLabel("ID del Turno:")
        id_label.setStyleSheet("font-weight: bold;")
        self.id_turno_label = QLabel("76")
        self.id_turno_label.setStyleSheet("""
            background-color: #313244;
            padding: 5px 10px;
            border-radius: 4px;
            font-weight: bold;
            color: #f9e2af;
        """)
        
        id_layout.addWidget(id_label)
        id_layout.addWidget(self.id_turno_label)
        
        # Nombre
        nombre_container = QWidget()
        nombre_layout = QHBoxLayout(nombre_container)
        nombre_layout.setContentsMargins(0, 0, 0, 0)
        nombre_layout.setSpacing(5)
        
        nombre_label = QLabel("Nombre:")
        nombre_label.setStyleSheet("font-weight: bold;")
        self.nombre_turno_label = QLabel("Se generará automáticamente")
        self.nombre_turno_label.setStyleSheet("""
            background-color: #313244;
            padding: 5px 10px;
            border-radius: 4px;
            font-style: italic;
            color: #f9e2af;
        """)
        
        nombre_layout.addWidget(nombre_label)
        nombre_layout.addWidget(self.nombre_turno_label)
        
        # Vigencia
        vigencia_container = QWidget()
        vigencia_layout = QHBoxLayout(vigencia_container)
        vigencia_layout.setContentsMargins(0, 0, 0, 0)
        vigencia_layout.setSpacing(5)
        
        vigencia_label = QLabel("Vigencia:")
        vigencia_label.setStyleSheet("font-weight: bold;")
        
        # Usar botones en lugar de spinner para vigencia
        vigencia_btn_container = QWidget()
        vigencia_btn_layout = QHBoxLayout(vigencia_btn_container)
        vigencia_btn_layout.setContentsMargins(0, 0, 0, 0)
        vigencia_btn_layout.setSpacing(0)
        
        self.btn_activo = QPushButton("1")
        self.btn_activo.setCheckable(True)
        self.btn_activo.setChecked(True)
        self.btn_activo.setFixedWidth(30)
        self.btn_activo.setToolTip("Activo")
        self.btn_activo.setStyleSheet("""
            QPushButton {
                background: #a6e3a1;
                color: #1e1e2e;
                border: none;
                border-radius: 4px 0 0 4px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:checked {
                background: #a6e3a1;
                border: 2px solid #89b4fa;
            }
            QPushButton:!checked {
                background: #45475a;
                color: #cdd6f4;
            }
        """)
        
        self.btn_inactivo = QPushButton("0")
        self.btn_inactivo.setCheckable(True)
        self.btn_inactivo.setFixedWidth(30)
        self.btn_inactivo.setToolTip("Inactivo")
        self.btn_inactivo.setStyleSheet("""
            QPushButton {
                background: #f38ba8;
                color: #1e1e2e;
                border: none;
                border-radius: 0 4px 4px 0;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:checked {
                background: #f38ba8;
                border: 2px solid #89b4fa;
            }
            QPushButton:!checked {
                background: #45475a;
                color: #cdd6f4;
            }
        """)
        
        # Conectar botones para que actúen como radio buttons
        self.btn_activo.clicked.connect(lambda: self.btn_inactivo.setChecked(False))
        self.btn_inactivo.clicked.connect(lambda: self.btn_activo.setChecked(False))
        
        vigencia_btn_layout.addWidget(self.btn_activo)
        vigencia_btn_layout.addWidget(self.btn_inactivo)
        
        vigencia_layout.addWidget(vigencia_label)
        vigencia_layout.addWidget(vigencia_btn_container)
        
        # Total Horas Semanales
        horas_container = QWidget()
        horas_layout = QHBoxLayout(horas_container)
        horas_layout.setContentsMargins(0, 0, 0, 0)
        horas_layout.setSpacing(5)
        
        horas_label = QLabel("Total Horas:")
        horas_label.setStyleSheet("font-weight: bold;")
        self.horas_semanales_label = QLabel("0.0 horas")
        self.horas_semanales_label.setStyleSheet("""
            background-color: #313244;
            padding: 5px 10px;
            border-radius: 4px;
            font-weight: bold;
            color: #f9e2af;
        """)
        
        horas_layout.addWidget(horas_label)
        horas_layout.addWidget(self.horas_semanales_label)
        
        # Añadir todos los contenedores a la fila de información
        info_layout.addWidget(id_container)
        info_layout.addWidget(nombre_container)
        info_layout.addWidget(vigencia_container)
        info_layout.addWidget(horas_container)
        
        turno_info_layout.addLayout(info_layout)
        
        # Fila 2: Nombre personalizado y botón generar
        nombre_custom_layout = QHBoxLayout()
        
        nombre_custom_label = QLabel("Nombre personalizado:")
        nombre_custom_label.setStyleSheet("font-weight: bold;")
        self.nombre_custom_edit = QLineEdit()
        self.nombre_custom_edit.setPlaceholderText("Nombre del turno (opcional)")
        
        generar_btn = QPushButton("Generar")
        generar_btn.setFixedWidth(100)
        generar_btn.clicked.connect(self.actualizar_nombre_automaticamente)
        
        nombre_custom_layout.addWidget(nombre_custom_label)
        nombre_custom_layout.addWidget(self.nombre_custom_edit)
        nombre_custom_layout.addWidget(generar_btn)
        
        turno_info_layout.addLayout(nombre_custom_layout)
        
        # Añadir el grupo de información del turno al layout principal
        main_layout.addWidget(turno_info_group)
        
        # Sección 2: Detalle de Jornada
        jornada_group = QGroupBox("Detalle de Jornada")
        jornada_layout = QVBoxLayout(jornada_group)
        jornada_layout.setContentsMargins(15, 20, 15, 15)
        jornada_layout.setSpacing(15)
        
        # Días de la semana
        dias_label = QLabel("Días de la Semana:")
        dias_label.setStyleSheet("font-weight: bold;")
        
        dias_layout = QHBoxLayout()
        dias_layout.setSpacing(10)
        
        self.dia_checks = {}
        dias = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        
        for dia in dias:
            check = QCheckBox(dia)
            check.setStyleSheet("""
                QCheckBox {
                    padding: 5px;
                    border-radius: 4px;
                }
                QCheckBox:hover {
                    background-color: #313244;
                }
            """)
            self.dia_checks[dia] = check
            dias_layout.addWidget(check)
        
        dias_layout.addStretch()
        
        # Horas
        horas_layout = QGridLayout()
        horas_layout.setSpacing(10)
        
        ingreso_label = QLabel("Hora de Ingreso:")
        ingreso_label.setStyleSheet("font-weight: bold;")
        self.hora_ingreso = TimeEditMejorado()
        self.hora_ingreso.setTime(QTime(9, 0))
        self.hora_ingreso.setDisplayFormat("HH:mm")
        
        salida_label = QLabel("Hora de Salida:")
        salida_label.setStyleSheet("font-weight: bold;")
        self.hora_salida = TimeEditMejorado()
        self.hora_salida.setTime(QTime(18, 0))
        self.hora_salida.setDisplayFormat("HH:mm")
        
        duracion_label = QLabel("Duración:")
        duracion_label.setStyleSheet("font-weight: bold;")
        self.duracion_label = QLabel("9h 00m (540 min)")
        self.duracion_label.setStyleSheet("""
            background-color: #313244;
            padding: 5px 10px;
            border-radius: 4px;
            color: #f9e2af;
        """)
        
        horas_layout.addWidget(ingreso_label, 0, 0)
        horas_layout.addWidget(self.hora_ingreso, 0, 1)
        horas_layout.addWidget(salida_label, 0, 2)
        horas_layout.addWidget(self.hora_salida, 0, 3)
        horas_layout.addWidget(duracion_label, 0, 4)
        horas_layout.addWidget(self.duracion_label, 0, 5)
        
        # Botón agregar
        self.btn_agregar_detalle = QPushButton("Agregar Detalle")
        self.btn_agregar_detalle.setIcon(QIcon.fromTheme("list-add"))
        self.btn_agregar_detalle.clicked.connect(self.agregar_detalle)
        self.btn_agregar_detalle.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #a6e3a1, stop:1 #94e2d5);
                color: #1e1e2e;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #94e2d5, stop:1 #a6e3a1);
            }
            QPushButton:pressed {
                background: #a6e3a1;
            }
        """)
        
        # Agregar todo al layout de jornada
        jornada_layout.addWidget(dias_label)
        jornada_layout.addLayout(dias_layout)
        jornada_layout.addLayout(horas_layout)
        jornada_layout.addWidget(self.btn_agregar_detalle, alignment=Qt.AlignmentFlag.AlignRight)
        
        main_layout.addWidget(jornada_group)
        
        # Sección 3: Detalles Agregados
        detalles_group = QGroupBox("Detalles Agregados")
        detalles_layout = QVBoxLayout(detalles_group)
        detalles_layout.setContentsMargins(15, 20, 15, 15)
        detalles_layout.setSpacing(10)
        
        # Tabla de detalles
        self.tabla_detalles = QTableWidget()
        self.tabla_detalles.setColumnCount(5)
        self.tabla_detalles.setHorizontalHeaderLabels(["ID", "Día", "Hora Ingreso", "Hora Salida", "Duración"])
        self.tabla_detalles.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_detalles.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabla_detalles.setAlternatingRowColors(True)
        self.tabla_detalles.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_detalles.verticalHeader().setVisible(False)
        
        detalles_layout.addWidget(self.tabla_detalles)
        
        # Etiqueta de información del turno
        self.info_turno_label = QLabel("No hay detalles agregados")
        self.info_turno_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #313244, stop:1 #45475a);
                border-radius: 6px;
                padding: 10px;
                margin-top: 5px;
                font-size: 12px;
                color: #cdd6f4;
                border-left: 3px solid #89b4fa;
            }
        """)
        detalles_layout.addWidget(self.info_turno_label)
        
        # Botones de acción para la tabla
        botones_layout = QHBoxLayout()
        
        self.editar_btn = QPushButton("Editar Seleccionado")
        self.editar_btn.setEnabled(False)
        self.editar_btn.setIcon(QIcon.fromTheme("document-edit"))
        self.editar_btn.setStyleSheet("""
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
            QPushButton:disabled {
                background: #45475a;
                color: #6c7086;
            }
        """)
        self.editar_btn.clicked.connect(self.editar_detalle_seleccionado)
        botones_layout.addWidget(self.editar_btn)
        
        self.eliminar_btn = QPushButton("Eliminar Seleccionado")
        self.eliminar_btn.setEnabled(False)
        self.eliminar_btn.setIcon(QIcon.fromTheme("edit-delete"))
        self.eliminar_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f38ba8, stop:1 #eba0ac);
                color: #1e1e2e;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #eba0ac, stop:1 #f38ba8);
            }
            QPushButton:pressed {
                background: #f38ba8;
            }
            QPushButton:disabled {
                background: #45475a;
                color: #6c7086;
            }
        """)
        self.eliminar_btn.clicked.connect(self.eliminar_detalle_seleccionado)
        botones_layout.addWidget(self.eliminar_btn)
        
        detalles_layout.addLayout(botones_layout)
        
        main_layout.addWidget(detalles_group)
        
        # Botones finales
        botones_finales_layout = QHBoxLayout()
        
        self.limpiar_btn = QPushButton("Limpiar")
        self.limpiar_btn.setIcon(QIcon.fromTheme("edit-clear"))
        self.limpiar_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #45475a, stop:1 #313244);
                color: #cdd6f4;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #313244, stop:1 #45475a);
            }
            QPushButton:pressed {
                background: #313244;
            }
        """)
        self.limpiar_btn.clicked.connect(self.limpiar_formulario)
        botones_finales_layout.addWidget(self.limpiar_btn)
        
        botones_finales_layout.addStretch()
        
        self.guardar_btn = QPushButton("Guardar")
        self.guardar_btn.setIcon(QIcon.fromTheme("document-save"))
        self.guardar_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #a6e3a1, stop:1 #94e2d5);
                color: #1e1e2e;
                border: none;
                padding: 10px 30px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #94e2d5, stop:1 #a6e3a1);
            }
            QPushButton:pressed {
                background: #a6e3a1;
            }
        """)
        self.guardar_btn.clicked.connect(self.guardar_turno)
        botones_finales_layout.addWidget(self.guardar_btn)
        
        main_layout.addLayout(botones_finales_layout)
        
        # Conexiones de señales
        self.tabla_detalles.itemSelectionChanged.connect(self.actualizar_estado_botones)
        self.hora_ingreso.timeChanged.connect(self.actualizar_duracion)
        self.hora_salida.timeChanged.connect(self.actualizar_duracion)
        
        # Inicializar estado
        self.limpiar_formulario()
        self.actualizar_duracion()

    def actualizar_estado_botones(self):
        """Actualiza el estado de los botones según la selección."""
        hay_seleccion = len(self.tabla_detalles.selectedItems()) > 0
        self.editar_btn.setEnabled(hay_seleccion)
        self.eliminar_btn.setEnabled(hay_seleccion)
        
    def editar_detalle_seleccionado(self):
        """Permite editar el detalle seleccionado en la tabla."""
        filas_seleccionadas = self.tabla_detalles.selectedItems()
        if not filas_seleccionadas:
            return
        
        # Obtener la fila seleccionada
        fila = filas_seleccionadas[0].row()
        
        # Obtener el ID del detalle
        id_detalle = self.tabla_detalles.item(fila, 0).text()
        
        # Buscar el detalle en la lista
        detalle = None
        for d in self.detalles:
            if str(d["id"]) == id_detalle:
                detalle = d
                break
        
        if not detalle:
            self.mostrar_mensaje_personalizado(
                "Error", 
                "No se encontró el detalle seleccionado.",
                QMessageBox.Icon.Critical
            )
            return
        
        # Configurar el formulario con los datos del detalle
        dia = detalle["dia"]
        if dia in self.dia_checks:
            self.dia_checks[dia].setChecked(True)
            
        # Desmarcar los demás días
        for d, checkbox in self.dia_checks.items():
            if d != dia:
                checkbox.setChecked(False)
        
        # Establecer las horas
        hora_ingreso = QTime.fromString(detalle["hora_ingreso"], "HH:mm")
        hora_salida = QTime.fromString(detalle["hora_salida"], "HH:mm")
        
        self.hora_ingreso.setTime(hora_ingreso)
        self.hora_salida.setTime(hora_salida)
        
        # Guardar el ID del detalle que estamos editando
        self.detalle_editando_id = detalle["id"]
        
        # Cambiar el texto del botón de agregar
        self.btn_agregar_detalle.setText("Actualizar Detalle")
        self.btn_agregar_detalle.setStyleSheet("""
            QPushButton {
                background: #ff8c00;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #ffa500;
            }
            QPushButton:pressed {
                background: #cc7000;
            }
        """)
        
    def eliminar_detalle_seleccionado(self):
        """Elimina el detalle seleccionado en la tabla."""
        filas_seleccionadas = self.tabla_detalles.selectedItems()
        if not filas_seleccionadas:
            return
        
        # Obtener la fila seleccionada
        fila = filas_seleccionadas[0].row()
        
        # Obtener el ID del detalle
        id_detalle = self.tabla_detalles.item(fila, 0).text()
        
        # Confirmar la eliminación
        confirmacion = QMessageBox()
        confirmacion.setWindowTitle("Confirmar eliminación")
        confirmacion.setText(f"¿Está seguro de eliminar el detalle seleccionado?")
        confirmacion.setIcon(QMessageBox.Icon.Question)
        confirmacion.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        confirmacion.setDefaultButton(QMessageBox.StandardButton.No)
        
        # Aplicar estilo personalizado
        confirmacion.setStyleSheet("""
            QMessageBox {
                background-color: #252526;
                color: white;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                background-color: #333333;
                color: white;
                border: 1px solid #555555;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
            QPushButton:pressed {
                background-color: #222222;
            }
        """)
        
        resultado = confirmacion.exec()
        
        if resultado == QMessageBox.StandardButton.Yes:
            # Buscar y eliminar el detalle
            for i, detalle in enumerate(self.detalles):
                if str(detalle["id"]) == id_detalle:
                    self.detalles.pop(i)
                    break
            
            # Actualizar la tabla
            self.actualizar_tabla_detalles()
            
            # Mostrar mensaje
            self.mostrar_mensaje_personalizado(
                "Éxito", 
                "Detalle eliminado correctamente.",
                QMessageBox.Icon.Information
            )
            
            # Si estábamos editando este detalle, cancelar la edición
            if self.detalle_editando_id == int(id_detalle):
                self.cancelar_edicion()
                
    def cancelar_edicion(self):
        """Cancela el modo de edición."""
        self.detalle_editando_id = None
        self.btn_agregar_detalle.setText("Agregar Detalle")
        self.btn_agregar_detalle.setStyleSheet("""
            QPushButton {
                background: #007acc;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #0098ff;
            }
            QPushButton:pressed {
                background: #005c99;
            }
        """)
        
        # Limpiar selección de días
        for checkbox in self.dia_checks.values():
            checkbox.setChecked(False)
        
        # Restablecer horas predeterminadas
        self.hora_ingreso.setTime(QTime(9, 0))
        self.hora_salida.setTime(QTime(18, 0))

    def actualizar_duracion(self):
        """
        Actualiza la duración según las horas de ingreso y salida.
        Si la hora de salida es menor que la hora de ingreso, se asume que
        es del día siguiente.
        
        Returns:
            int: Duración en minutos
        """
        try:
            # Obtener las horas
            hora_ingreso = self.hora_ingreso.time()
            hora_salida = self.hora_salida.time()
            
            # Convertir a minutos
            ingreso_mins = hora_ingreso.hour() * 60 + hora_ingreso.minute()
            salida_mins = hora_salida.hour() * 60 + hora_salida.minute()
            
            # Si la salida es antes que la entrada, asumimos que es del día siguiente
            if salida_mins < ingreso_mins:
                duracion = (24 * 60 - ingreso_mins) + salida_mins
            else:
                duracion = salida_mins - ingreso_mins
            
            # Actualizar el campo de duración
            if hasattr(self, 'duracion_label'):
                horas = duracion // 60
                minutos = duracion % 60
                self.duracion_label.setText(f"{horas}h {minutos:02d}m ({duracion} min)")
            
            return duracion
        except Exception as e:
            # Manejar cualquier error
            print(f"Error al calcular duración: {str(e)}")
            return 0

    def _obtener_detalle_actual(self):
        """
        Obtiene los datos del detalle actual desde el formulario.
        
        Returns:
            dict: Diccionario con los datos del detalle actual
        """
        print("Obteniendo detalle actual del formulario")
        
        # Obtener días seleccionados
        dias_seleccionados = []
        for nombre_abreviado, checkbox in self.dia_checks.items():
            if checkbox.isChecked():
                # Convertir abreviatura a nombre completo
                if nombre_abreviado == "Lun":
                    dias_seleccionados.append("Lunes")
                elif nombre_abreviado == "Mar":
                    dias_seleccionados.append("Martes")
                elif nombre_abreviado == "Mié":
                    dias_seleccionados.append("Miércoles")
                elif nombre_abreviado == "Jue":
                    dias_seleccionados.append("Jueves")
                elif nombre_abreviado == "Vie":
                    dias_seleccionados.append("Viernes")
                elif nombre_abreviado == "Sáb":
                    dias_seleccionados.append("Sábado")
                elif nombre_abreviado == "Dom":
                    dias_seleccionados.append("Domingo")
        
        print(f"Días seleccionados: {dias_seleccionados}")
        
        # Obtener horas de ingreso y salida
        hora_ingreso = self.hora_ingreso.time()
        hora_salida = self.hora_salida.time()
        
        # Formatear horas como strings HH:MM
        hora_ingreso_str = f"{hora_ingreso.hour():02d}:{hora_ingreso.minute():02d}"
        hora_salida_str = f"{hora_salida.hour():02d}:{hora_salida.minute():02d}"
        
        # Calcular duración en minutos
        duracion_minutos = hora_ingreso.secsTo(hora_salida) // 60
        
        print(f"Horario: {hora_ingreso_str} a {hora_salida_str}, Duración: {duracion_minutos} minutos")
        
        return {
            "dias": dias_seleccionados,
            "hora_ingreso": hora_ingreso_str,
            "hora_salida": hora_salida_str,
            "duracion_minutos": duracion_minutos
        }

    def agregar_detalle(self):
        """Agrega un detalle al turno actual."""
        try:
            print("Iniciando agregar_detalle")
            # Obtener los datos del detalle actual
            detalle_actual = self._obtener_detalle_actual()
            print(f"Detalle actual: {detalle_actual}")
            
            # Validar que al menos un día esté seleccionado
            if not detalle_actual["dias"]:
                QMessageBox.warning(
                    self,
                    "Día Requerido",
                    "Debe seleccionar al menos un día de la semana."
                )
                return
            
            # Validar que la hora de salida sea posterior a la de ingreso
            hora_ingreso = datetime.strptime(detalle_actual["hora_ingreso"], "%H:%M")
            hora_salida = datetime.strptime(detalle_actual["hora_salida"], "%H:%M")
            
            if hora_salida <= hora_ingreso:
                QMessageBox.warning(
                    self,
                    "Horario Inválido",
                    "La hora de salida debe ser posterior a la hora de ingreso."
                )
                return
            
            # Obtener el último ID de detalle para asignar IDs temporales
            try:
                ultimo_id_detalle = self.turno_dao.obtener_ultimo_id_detalle()
                print(f"Último ID de detalle obtenido: {ultimo_id_detalle}")
                # Contar cuántos detalles nuevos vamos a agregar para reservar IDs
                dias_nuevos = [dia for dia in detalle_actual["dias"] if not any(d["dia"] == dia for d in self.detalles)]
                id_actual = ultimo_id_detalle
            except Exception as e:
                print(f"Error al obtener último ID de detalle: {str(e)}")
                # Si hay error, usar un ID temporal negativo
                id_actual = -1
                for detalle in self.detalles:
                    if detalle.get("id", 0) < id_actual:
                        id_actual = detalle.get("id", 0)
                id_actual -= 1  # Usar un ID negativo menor que todos los existentes
            
            # Procesar cada día seleccionado
            for dia in detalle_actual["dias"]:
                print(f"Procesando día: {dia}")
                # Verificar si ya existe un detalle para este día
                existe_detalle = False
                indice_existente = -1
                
                for i, detalle in enumerate(self.detalles):
                    if detalle["dia"] == dia:
                        if self.detalle_editando_id is not None and detalle.get("id") == self.detalle_editando_id:
                            # Estamos editando este detalle, así que lo actualizaremos
                            indice_existente = i
                            existe_detalle = True
                            print(f"Actualizando detalle existente en índice {i}")
                            break
                        elif self.detalle_editando_id is None:
                            # No estamos en modo edición, así que es un duplicado
                            QMessageBox.warning(
                                self,
                                "Detalle Duplicado",
                                f"Ya existe un detalle para el día {dia}."
                            )
                            existe_detalle = True
                            break
                
                # Si no existe o estamos editando, agregar/actualizar el detalle
                if not existe_detalle or (existe_detalle and indice_existente >= 0):
                    nuevo_detalle = {
                        "dia": dia,
                        "hora_ingreso": detalle_actual["hora_ingreso"],
                        "hora_salida": detalle_actual["hora_salida"],
                        "duracion_minutos": detalle_actual["duracion_minutos"]
                    }
                    
                    # Si estamos editando, mantener el ID original
                    if self.detalle_editando_id is not None and indice_existente >= 0:
                        nuevo_detalle["id"] = self.detalles[indice_existente].get("id", 0)
                        self.detalles[indice_existente] = nuevo_detalle
                        print(f"Detalle actualizado: {nuevo_detalle}")
                    elif not existe_detalle:
                        # Asignar un ID temporal al nuevo detalle
                        nuevo_detalle["id"] = id_actual
                        id_actual += 1
                        self.detalles.append(nuevo_detalle)
                        print(f"Nuevo detalle agregado: {nuevo_detalle}")
            
            # Actualizar la tabla de detalles
            self.actualizar_tabla_detalles()
            
            # Limpiar selección de días
            for checkbox in self.dia_checks.values():
                checkbox.setChecked(False)
            
            # Resetear modo de edición
            self.detalle_editando_id = None
            self.btn_agregar_detalle.setText("Agregar")
            
        except Exception as e:
            print(f"Error en agregar_detalle: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Error",
                f"Ocurrió un error al agregar el detalle: {str(e)}"
            )

    def mostrar_mensaje_personalizado(self, titulo, mensaje, icono=QMessageBox.Icon.Information):
        """Muestra un mensaje con estilo personalizado."""
        msg_box = QMessageBox()
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setIcon(icono)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        # Estilo personalizado
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #252526;
                color: white;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                background-color: #333333;
                color: white;
                border: 1px solid #555555;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
            QPushButton:pressed {
                background-color: #222222;
            }
        """)
        
        return msg_box.exec()

    def actualizar_tabla_detalles(self):
        """Actualiza la tabla de detalles con los datos actuales."""
        # Limpiar tabla
        self.tabla_detalles.setRowCount(0)
        
        # Si no hay detalles, mostrar mensaje
        if not self.detalles:
            self.info_turno_label.setText("No hay detalles agregados")
            return
        
        # Ordenar detalles por día de la semana
        dias_orden = {
            "Lunes": 1, "Martes": 2, "Miércoles": 3,
            "Jueves": 4, "Viernes": 5, "Sábado": 6, "Domingo": 7
        }
        detalles_ordenados = sorted(
            self.detalles,
            key=lambda x: dias_orden[x["dia"]]
        )
        
        print(f"Actualizando tabla con {len(detalles_ordenados)} detalles")
        
        # Agregar filas a la tabla
        for detalle in detalles_ordenados:
            fila = self.tabla_detalles.rowCount()
            self.tabla_detalles.insertRow(fila)
            
            # ID (usar 0 si no existe)
            id_detalle = detalle.get("id", 0)
            id_item = QTableWidgetItem(str(id_detalle))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Aplicar estilo al ID para destacarlo
            if id_detalle > 0:
                id_item.setForeground(QColor("#f9e2af"))  # Color amarillo para IDs asignados
                id_item.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            
            self.tabla_detalles.setItem(fila, 0, id_item)
            
            # Día
            dia_item = QTableWidgetItem(detalle["dia"])
            dia_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_detalles.setItem(fila, 1, dia_item)
            
            # Hora de ingreso
            hora_ingreso = detalle["hora_ingreso"]
            if isinstance(hora_ingreso, QTime):
                hora_ingreso_str = hora_ingreso.toString("HH:mm")
            elif isinstance(hora_ingreso, str):
                hora_ingreso_str = hora_ingreso
            else:
                hora_ingreso_str = hora_ingreso.strftime("%H:%M")
                
            hora_ingreso_item = QTableWidgetItem(hora_ingreso_str)
            hora_ingreso_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_detalles.setItem(fila, 2, hora_ingreso_item)
            
            # Hora de salida
            hora_salida = detalle.get("hora_salida")
            if hora_salida:
                if isinstance(hora_salida, QTime):
                    hora_salida_str = hora_salida.toString("HH:mm")
                elif isinstance(hora_salida, str):
                    hora_salida_str = hora_salida
                else:
                    hora_salida_str = hora_salida.strftime("%H:%M")
            else:
                # Calcular hora de salida a partir de la duración
                duracion = detalle.get("duracion_minutos", detalle.get("duracion", 0))
                hora_ingreso_dt = datetime.strptime(hora_ingreso_str, "%H:%M")
                hora_salida_dt = hora_ingreso_dt + timedelta(minutes=duracion)
                hora_salida_str = hora_salida_dt.strftime("%H:%M")
                
            hora_salida_item = QTableWidgetItem(hora_salida_str)
            hora_salida_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_detalles.setItem(fila, 3, hora_salida_item)
            
            # Duración
            duracion = detalle.get("duracion_minutos", detalle.get("duracion", 0))
            horas = duracion // 60
            minutos = duracion % 60
            duracion_item = QTableWidgetItem(f"{horas}h {minutos:02d}m ({duracion} min)")
            duracion_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_detalles.setItem(fila, 4, duracion_item)
        
        # Actualizar información del turno
        self.actualizar_info_turno()

    def actualizar_info_turno(self):
        """
        Actualiza la información del turno en la interfaz.
        """
        if not self.detalles:
            self.info_turno_label.setText("No hay detalles agregados")
            self.horas_semanales_label.setText("0.0 horas")
            return
        
        # Calcular horas semanales
        total_minutos = 0
        for detalle in self.detalles:
            if "duracion_minutos" in detalle:
                total_minutos += detalle["duracion_minutos"]
            elif "duracion" in detalle:
                total_minutos += detalle["duracion"]
        
        horas = total_minutos // 60
        minutos = total_minutos % 60
        horas_semanales = f"{horas}.{minutos//6}" if minutos else f"{horas}.0"
        
        print(f"Total minutos: {total_minutos}, Horas semanales: {horas_semanales}")
        
        # Actualizar etiqueta de horas semanales
        self.horas_semanales_label.setText(f"{horas_semanales} horas")
        
        # Generar nombre automático si no hay uno
        nombre = self.nombre_custom_edit.text().strip()
        if not nombre:
            nombre = self._generar_nombre_turno()
            self.nombre_turno_label.setText(nombre)
        
        # Obtener ID y vigencia
        id_turno = self.id_turno_label.text()
        vigencia = "A" if self.btn_activo.isChecked() else "I"
        
        # Actualizar etiqueta de información en formato: ID-Nombre-Vigencia-Total horas
        # Usar un formato más legible pero manteniendo la estructura solicitada
        self.info_turno_label.setText(
            f"<span style='font-weight:bold;color:#f9e2af;'>{id_turno}</span>-"
            f"<span style='font-weight:bold;color:#a6e3a1;'>{nombre}</span>-"
            f"<span style='font-weight:bold;color:#89b4fa;'>{vigencia}</span>-"
            f"<span style='font-weight:bold;color:#f38ba8;'>{horas_semanales} horas</span>"
        )

    def _generar_nombre_turno(self, id_turno=None) -> str:
        """
        Genera el nombre del turno siguiendo el formato: ID-HorasSemanales DiasAbreviados
        Ejemplos:
        - De lunes a viernes: 77-22 Lu a Vi
        - De lunes a miércoles: 77-22 Lu a Mi
        - Días no consecutivos: 77-22 Lu/Mi a Vi o 77-22 Lu a Ma/ Ju a Vi
        
        Args:
            id_turno: ID del turno (opcional, si no se proporciona se usa "XX")
            
        Returns:
            Nombre generado para el turno
        """
        if not self.detalles:
            return "(Auto)"

        # Calcular horas semanales (en horas enteras)
        total_minutos = 0
        for detalle in self.detalles:
            if "duracion_minutos" in detalle:
                total_minutos += detalle["duracion_minutos"]
            elif "duracion" in detalle:
                total_minutos += detalle["duracion"]
        
        horas_semanales = total_minutos / 60
        horas_semanales_enteras = int(horas_semanales)
        
        # Ordenar detalles por día de la semana
        dias_orden = {
            "Lunes": 1, "Martes": 2, "Miércoles": 3,
            "Jueves": 4, "Viernes": 5, "Sábado": 6, "Domingo": 7
        }
        detalles_ordenados = sorted(
            self.detalles,
            key=lambda x: dias_orden[x["dia"]]
        )

        # Obtener abreviaturas de días (exactamente 2 letras)
        abreviaturas = {
            "Lunes": "Lu", "Martes": "Ma", "Miércoles": "Mi",
            "Jueves": "Ju", "Viernes": "Vi", "Sábado": "Sa", "Domingo": "Do"
        }

        # Construir el rango de días
        dias_jornada = [d["dia"] for d in detalles_ordenados]
        dias_abr = [abreviaturas[d] for d in dias_jornada]
        
        # Detectar rangos consecutivos
        rangos = []
        if len(dias_jornada) > 0:
            rango_inicio = 0
            for i in range(1, len(dias_jornada)):
                if dias_orden[dias_jornada[i]] != dias_orden[dias_jornada[i-1]] + 1:
                    # Fin de un rango
                    if rango_inicio == i - 1:
                        # Rango de un solo día
                        rangos.append(dias_abr[rango_inicio])
                    else:
                        # Rango de varios días
                        rangos.append(f"{dias_abr[rango_inicio]} a {dias_abr[i-1]}")
                    rango_inicio = i
            
            # Procesar el último rango
            if rango_inicio == len(dias_jornada) - 1:
                rangos.append(dias_abr[rango_inicio])
            else:
                rangos.append(f"{dias_abr[rango_inicio]} a {dias_abr[-1]}")
        
        nombre_dias = "/".join(rangos)
        
        # Construir nombre completo
        id_prefix = id_turno if id_turno else self.id_turno_label.text() or "XX"
        return f"{id_prefix}-{horas_semanales_enteras} {nombre_dias}"

    def editar_turno_creado(self, indice, dialog_parent=None):
        """Edita un turno creado en la sesión actual."""
        # Este método es un placeholder para mantener compatibilidad
        # con el código existente. En la nueva implementación, la edición
        # se maneja directamente en la interfaz principal.
        pass
        
    def eliminar_turno_creado(self, indice, tabla=None):
        """Elimina un turno creado en la sesión actual."""
        # Este método es un placeholder para mantener compatibilidad
        # con el código existente. En la nueva implementación, la eliminación
        # se maneja directamente en la interfaz principal.
        pass

    def limpiar_formulario(self):
        """Limpia todos los campos del formulario."""
        # Limpiar campos de información general
        self.nombre_custom_edit.clear()
        
        # Establecer vigencia por defecto (activo)
        self.btn_activo.setChecked(True)
        self.btn_inactivo.setChecked(False)
        
        # Limpiar selección de días
        for checkbox in self.dia_checks.values():
            checkbox.setChecked(False)
        
        # Restablecer horas predeterminadas
        self.hora_ingreso.setTime(QTime(9, 0))  # 9:00 AM
        self.hora_salida.setTime(QTime(18, 0))  # 6:00 PM
        
        # Limpiar lista de detalles
        self.detalles = []
        self.tabla_detalles.setRowCount(0)
        
        # Actualizar información
        self.actualizar_tabla_detalles()
        
        # Inicializar un nuevo turno
        self.inicializar_nuevo_turno(True)
        
        # Actualizar estado de botones
        self.editar_btn.setEnabled(False)
        self.eliminar_btn.setEnabled(False)

    def guardar_turno(self):
        """Guarda el turno actual y genera SQL si es válido."""
        if not self.validar_turno():
            return
        
        try:
            print("Iniciando guardado de turno")
            # Actualizar datos del turno
            self.turno_actual.nombre = self.nombre_custom_edit.text().strip() or self._generar_nombre_turno()
            self.turno_actual.vigencia = "A" if self.btn_activo.isChecked() else "I"
            
            print(f"Turno a guardar: ID={self.turno_actual.id_turno}, Nombre={self.turno_actual.nombre}, Vigencia={self.turno_actual.vigencia}")
            
            # Convertir los detalles del formato de diccionario al modelo TurnoDetalleDiario
            self.turno_actual.detalles = []
            print(f"Procesando {len(self.detalles)} detalles")
            
            for detalle_dict in self.detalles:
                print(f"Procesando detalle: {detalle_dict}")
                # Convertir QTime a time de Python si es necesario
                hora_ingreso = detalle_dict["hora_ingreso"]
                if isinstance(hora_ingreso, QTime):
                    hora_ingreso = time(hour=hora_ingreso.hour(), minute=hora_ingreso.minute())
                elif isinstance(hora_ingreso, str):
                    hora_ingreso = datetime.strptime(hora_ingreso, "%H:%M").time()
                
                # Crear un objeto TurnoDetalleDiario con todos los parámetros requeridos
                detalle = TurnoDetalleDiario(
                    id_turno_detalle_diario=detalle_dict.get("id", 0),
                    id_turno=self.turno_actual.id_turno,
                    jornada=detalle_dict["dia"],
                    hora_ingreso=hora_ingreso,
                    duracion=detalle_dict.get("duracion_minutos", detalle_dict.get("duracion", 0))
                )
                print(f"Detalle creado: ID={detalle.id_turno_detalle_diario}, Día={detalle.jornada}, Hora={detalle.hora_ingreso}, Duración={detalle.duracion}")
                self.turno_actual.detalles.append(detalle)
            
            # Asignar IDs a los detalles del turno
            try:
                self.turno_dao.asignar_ids(self.turno_actual)
                print(f"IDs asignados: Turno={self.turno_actual.id_turno}, Detalles={[d.id_turno_detalle_diario for d in self.turno_actual.detalles]}")
                
                # Actualizar los IDs en la lista de detalles para mostrarlos en la interfaz
                for i, detalle in enumerate(self.turno_actual.detalles):
                    if i < len(self.detalles):
                        self.detalles[i]["id"] = detalle.id_turno_detalle_diario
                
                # Actualizar la tabla para mostrar los nuevos IDs
                self.actualizar_tabla_detalles()
            except Exception as e:
                print(f"Error al asignar IDs: {str(e)}")
                # Continuar con el proceso a pesar del error
            
            # Verificar duplicados
            turnos_similares = self.turno_dao.buscar_turnos_similares(self.turno_actual)
            
            if turnos_similares:
                # Mostrar aviso de duplicidad
                msg = f"Se encontraron {len(turnos_similares)} turnos similares o idénticos:\n\n"
                
                for id_turno, nombre, detalles in turnos_similares[:3]:  # Mostrar solo los primeros 3
                    msg += f"• Turno ID: {id_turno}, Nombre: {nombre}\n"
                    for detalle in detalles[:3]:  # Mostrar solo los primeros 3 detalles
                        jornada = detalle['jornada']
                        hora_ingreso = detalle['hora_ingreso'].strftime("%H:%M")
                        hora_salida = detalle['hora_salida'].strftime("%H:%M") if 'hora_salida' in detalle else "N/A"
                        duracion = detalle['duracion']
                        msg += f"  - {jornada}: {hora_ingreso} a {hora_salida} ({duracion} min)\n"
                    msg += "\n"
                
                if len(turnos_similares) > 3:
                    msg += f"Y {len(turnos_similares) - 3} turnos más...\n\n"
                
                msg += "¿Desea continuar con la creación a pesar de la duplicidad?"
                
                respuesta = QMessageBox.question(
                    self,
                    "Turnos Similares Encontrados",
                    msg,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if respuesta == QMessageBox.StandardButton.No:
                    return
            
            # Guardar turno en la base de datos
            print("Guardando turno en la base de datos")
            self.turno_dao.guardar_turno(self.turno_actual)
            
            # Guardar turno en la lista de creados
            if self.turno_actual not in self.turnos_creados:
                self.turnos_creados.append(self.turno_actual)
            
            # Preguntar si se desea agregar un nuevo turno
            respuesta = QMessageBox.question(
                self,
                "Turno Guardado",
                f"El turno '{self.turno_actual.nombre}' ha sido guardado.\n\n¿Desea agregar un nuevo turno?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if respuesta == QMessageBox.StandardButton.Yes:
                # Guardar el turno actual e iniciar uno nuevo
                self.inicializar_nuevo_turno(limpiar_tabla=True)
                return
            
            # Si no se desea agregar un nuevo turno, preguntar si se desea ver el script SQL
            respuesta = QMessageBox.question(
                self,
                "Generar Script SQL",
                f"¿Desea generar y ver el script SQL para todos los turnos creados ({len(self.turnos_creados)} turnos)?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if respuesta == QMessageBox.StandardButton.Yes:
                # Generar script SQL para todos los turnos
                self.generar_script_sql()
            
        except Exception as e:
            print(f"Error al guardar turno: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Error al guardar",
                f"Ocurrió un error al guardar el turno: {str(e)}"
            )

    def generar_script_sql(self):
        """Genera y muestra el script SQL para los turnos creados."""
        if not self.turnos_creados:
            QMessageBox.warning(
                self,
                "Sin Turnos",
                "No hay turnos para generar script SQL."
            )
            return
        
        try:
            # Generar script SQL para todos los turnos creados
            script = ""
            
            # Añadir encabezado
            script += "-- Script SQL para todos los turnos creados\n"
            script += f"-- Total de turnos: {len(self.turnos_creados)}\n"
            script += "-- Fecha de generación: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n"
            
            # Asegurar que cada turno tenga un ID único
            ultimo_id_turno = self.turno_dao.obtener_ultimo_id_turno()
            ultimo_id_detalle = self.turno_dao.obtener_ultimo_id_detalle()
            
            # Crear una copia de los turnos para no modificar los originales
            turnos_procesados = []
            
            for i, turno_original in enumerate(self.turnos_creados):
                # Crear una copia del turno
                turno = Turno()
                turno.id_turno = ultimo_id_turno + i
                turno.nombre = turno_original.nombre
                turno.vigencia = turno_original.vigencia
                turno.frecuencia = turno_original.frecuencia
                
                # Copiar los detalles con IDs correlativos
                for j, detalle_original in enumerate(turno_original.detalles):
                    detalle = TurnoDetalleDiario(
                        id_turno_detalle_diario=ultimo_id_detalle + j,
                        id_turno=turno.id_turno,
                        jornada=detalle_original.jornada,
                        hora_ingreso=detalle_original.hora_ingreso,
                        duracion=detalle_original.duracion
                    )
                    turno.detalles.append(detalle)
                
                turnos_procesados.append(turno)
                ultimo_id_detalle += len(turno.detalles)
                
            # Generar script para cada turno
            for i, turno in enumerate(turnos_procesados):
                print(f"Generando SQL para turno {i+1}/{len(turnos_procesados)}: ID={turno.id_turno}, Nombre={turno.nombre}")
                
                # Usar el método de TurnoDAO para generar el script
                turno_script = self.turno_dao.generar_script_sql(turno)
                if turno_script:
                    script += f"-- ======== TURNO {i+1}: {turno.nombre} ========\n"
                    script += turno_script + "\n\n"
                else:
                    # Fallback al método anterior si el de TurnoDAO falla
                    script += f"-- ======== TURNO {i+1}: {turno.nombre} ========\n"
                    # INSERT para la tabla TURNO
                    script += f"INSERT INTO ASISTENCIAS.TURNO (ID_TURNO, NOMBRE, VIGENCIA, FRECUENCIA) VALUES ({turno.id_turno},'{turno.nombre}', '{turno.vigencia}', 'Diarios');\n"
                    
                    # INSERTs para los detalles
                    for detalle in turno.detalles:
                        print(f"  Detalle: ID={detalle.id_turno_detalle_diario}, Día={detalle.jornada}, Hora={detalle.hora_ingreso}, Duración={detalle.duracion}")
                        script += f"INSERT INTO ASISTENCIAS.TURNO_DETALLE_DIARIO (ID_TURNO_DETALLE_DIARIO, ID_TURNO, JORNADA, HORA_INGRESO, DURACION) VALUES ({detalle.id_turno_detalle_diario}, {turno.id_turno}, '{detalle.jornada}', TO_DATE('2025-01-01 {detalle.hora_ingreso.strftime('%H:%M')}:00', 'YYYY-MM-DD HH24:MI:SS'), {detalle.duracion});\n"
                    
                    script += "\n"
        
            # Mostrar diálogo con script SQL
            self.mostrar_dialogo_sql(script)
            
        except Exception as e:
            print(f"Error al generar script SQL: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Error al generar script",
                f"Ocurrió un error al generar el script SQL: {str(e)}"
            )

    def mostrar_dialogo_sql(self, script):
        """Muestra un diálogo con el script SQL generado y opciones para exportarlo."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Script SQL Generado")
        dialog.setMinimumSize(800, 600)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: white;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título
        title = QLabel("Script SQL para Inserción de Turnos")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #007acc; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Descripción
        descripcion = QLabel("El siguiente script SQL puede ser ejecutado en la base de datos para insertar los turnos creados:")
        descripcion.setWordWrap(True)
        layout.addWidget(descripcion)
        
        # Campo de texto con el script
        text_edit = QTextEdit()
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #252526;
                color: #dcdcdc;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                line-height: 1.5;
            }
        """)
        text_edit.setPlainText(script)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        # Botones
        button_layout = QHBoxLayout()
        
        # Botón Exportar
        export_button = QPushButton("Exportar a Archivo...")
        export_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0098ff;
            }
        """)
        export_button.clicked.connect(lambda: self.exportar_script(script))
        button_layout.addWidget(export_button)
        
        # Botón Registrar (para Google Sheets - futuro)
        sheets_button = QPushButton("Registrar en Google Sheets")
        sheets_button.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #66bb6a;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #999999;
            }
        """)
        sheets_button.setEnabled(False)  # Deshabilitado por ahora
        sheets_button.setToolTip("Próximamente: Registrar turnos en Google Sheets")
        button_layout.addWidget(sheets_button)
        
        # Botón Cerrar
        close_button = QPushButton("Cerrar")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """)
        close_button.clicked.connect(dialog.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Mostrar diálogo
        dialog.exec()
        
        # Reiniciar después de cerrar el diálogo
        self.turnos_creados = []
        self.inicializar_nuevo_turno(limpiar_tabla=True)

    def exportar_script(self, script):
        """Exporta el script SQL a un archivo."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar Script SQL",
                "",
                "Archivos SQL (*.sql);;Archivos de texto (*.txt);;Todos los archivos (*.*)"
            )
            
            if filename:
                # Agregar extensión .sql si no tiene extensión
                if '.' not in filename:
                    filename += '.sql'
                    
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(script)
                
                QMessageBox.information(
                    self,
                    "Archivo Guardado",
                    f"El script SQL ha sido guardado en:\n{filename}"
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al exportar",
                f"Ocurrió un error al exportar el script: {str(e)}"
            )

    def inicializar_nuevo_turno(self, limpiar_tabla=False):
        """Inicializa un nuevo turno para la creación."""
        self.turno_actual = Turno()
        
        try:
            # Limpiar la caché para forzar la obtención de un nuevo ID
            self.turno_dao.db.clear_cache()
            
            # Obtener el próximo ID desde la base de datos
            id_turno = self.turno_dao.obtener_ultimo_id_turno()
            print(f"Último ID de turno obtenido de la base de datos: {id_turno}")
            
            # Asignar el ID al turno actual
            self.turno_actual.id_turno = id_turno
            self.id_turno_label.setText(str(id_turno))
            
            # Establecer valores por defecto
            self.turno_actual.vigencia = 1
            self.btn_activo.setChecked(True)
            self.btn_inactivo.setChecked(False)
            
            # Limpiar la tabla de detalles si se solicita
            if limpiar_tabla:
                self.detalles = []
                self.tabla_detalles.setRowCount(0)
                self.tabla_con_datos = False
            
            # Limpiar campos
            self.nombre_custom_edit.clear()
            
            # Actualizar etiquetas de información
            self.horas_semanales_label.setText("0.0 horas")
            self.nombre_turno_label.setText("Se generará automáticamente")
            self.info_turno_label.setText("No hay detalles agregados")
            
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error al inicializar",
                f"No se pudo obtener el próximo ID de turno: {str(e)}"
            )
            self.id_turno_label.setText("Error")

    def validar_turno(self):
        """Valida el turno actual antes de guardarlo."""
        if not self.detalles:
            QMessageBox.warning(
                self,
                "Faltan detalles",
                "Debe agregar al menos un detalle al turno antes de guardarlo.",
                QMessageBox.StandardButton.Ok
            )
            return False
        
        if not self.nombre_custom_edit.text().strip():
            # Generar nombre automáticamente
            nombre_generado = self._generar_nombre_turno()
            self.nombre_custom_edit.setText(nombre_generado)
            self.actualizar_nombre_turno()
        
        # Verificar que al menos uno de los botones de vigencia esté seleccionado
        if not self.btn_activo.isChecked() and not self.btn_inactivo.isChecked():
            QMessageBox.warning(
                self,
                "Vigencia no seleccionada",
                "Debe seleccionar si el turno está activo (1) o inactivo (0).",
                QMessageBox.StandardButton.Ok
            )
            return False
        
        # Actualizar la vigencia en el turno actual
        self.turno_actual.vigencia = 1 if self.btn_activo.isChecked() else 0
        
        return True

    def actualizar_nombre_automaticamente(self):
        """
        Genera y establece automáticamente el nombre del turno basado en los detalles.
        """
        if not self.detalles:
            # Mostrar advertencia si no hay detalles
            QMessageBox.warning(
                self,
                "No hay detalles",
                "No se puede generar un nombre automáticamente sin agregar detalles de jornada.",
                QMessageBox.StandardButton.Ok
            )
            return
        
        # Generar nombre basado en los detalles
        nombre_generado = self._generar_nombre_turno()
        
        # Establecer el nombre en el campo de entrada
        self.nombre_custom_edit.setText(nombre_generado)
        
        # Mostrar mensaje de confirmación
        QMessageBox.information(
            self,
            "Nombre Generado",
            f"Se ha generado automáticamente el nombre: {nombre_generado}",
            QMessageBox.StandardButton.Ok
        )

    def actualizar_nombre_turno(self):
        """Actualiza el nombre del turno basado en los detalles actuales."""
        if not hasattr(self, 'turno_actual') or not self.turno_actual:
            return
        
        # Generar nombre basado en los detalles
        nombre_generado = self._generar_nombre_turno()
        
        # Actualizar la etiqueta de nombre
        self.nombre_turno_label.setText(nombre_generado)
        
        # Si hay un nombre personalizado, usarlo en lugar del generado
        nombre_custom = self.nombre_custom_edit.text().strip()
        if nombre_custom:
            self.turno_actual.nombre = nombre_custom
        else:
            self.turno_actual.nombre = nombre_generado

def highlight_sql(text_edit):
    """
    Aplica un resaltado de sintaxis SQL básico a un QTextEdit.
    
    Args:
        text_edit: El QTextEdit al que aplicar el resaltado
    """
    # Palabras clave SQL (convertidas a minúsculas para comparación case-insensitive)
    keywords = [
        "SELECT", "FROM", "WHERE", "INSERT", "INTO", "VALUES",
        "UPDATE", "SET", "DELETE", "CREATE", "TABLE", "ALTER",
        "DROP", "INDEX", "AND", "OR", "NOT", "NULL", "IS",
        "LIKE", "IN", "BETWEEN", "JOIN", "INNER", "LEFT",
        "RIGHT", "OUTER", "GROUP", "BY", "HAVING", "ORDER",
        "ASC", "DESC", "LIMIT", "OFFSET", "UNION", "ALL",
        "BEGIN", "END", "DECLARE", "PROCEDURE", "FUNCTION",
        "COMMIT", "ROLLBACK", "TRIGGER", "FOREIGN", "KEY",
        "PRIMARY", "CONSTRAINT", "UNIQUE", "CHECK", "DEFAULT"
    ]
    
    # Funciones SQL
    functions = [
        "COUNT", "SUM", "AVG", "MIN", "MAX", "COALESCE",
        "IFNULL", "NULLIF", "CAST", "CONVERT", "TO_DATE",
        "TO_CHAR", "TO_NUMBER", "SUBSTR", "SUBSTRING",
        "CONCAT", "TRIM", "LTRIM", "RTRIM", "UPPER", "LOWER",
        "NEXTVAL", "CURRVAL", "NVL", "DECODE", "REPLACE",
        "LENGTH", "ROUND", "TRUNC", "SYSDATE", "EXTRACT"
    ]
    
    # Tipos de datos
    data_types = [
        "INT", "INTEGER", "SMALLINT", "BIGINT", "DECIMAL",
        "NUMERIC", "FLOAT", "REAL", "DOUBLE", "CHAR",
        "VARCHAR", "TEXT", "DATE", "TIME", "TIMESTAMP",
        "BOOLEAN", "BLOB", "CLOB", "NUMBER", "RAW",
        "LONG", "BINARY", "VARBINARY", "DATETIME"
    ]
    
    # Crear un resaltador personalizado
    class SQLHighlighter(QSyntaxHighlighter):
        def __init__(self, parent=None):
            super().__init__(parent)
            
            # Crear formatos para diferentes elementos
            self.keyword_format = QTextCharFormat()
            self.keyword_format.setForeground(QColor("#569CD6"))  # Azul
            self.keyword_format.setFontWeight(QFont.Weight.Bold)
            
            self.function_format = QTextCharFormat()
            self.function_format.setForeground(QColor("#DCDCAA"))  # Amarillo
            
            self.data_type_format = QTextCharFormat()
            self.data_type_format.setForeground(QColor("#4EC9B0"))  # Verde azulado
            
            self.comment_format = QTextCharFormat()
            self.comment_format.setForeground(QColor("#6A9955"))  # Verde
            self.comment_format.setFontItalic(True)
            
            self.string_format = QTextCharFormat()
            self.string_format.setForeground(QColor("#CE9178"))  # Naranja
            
            self.number_format = QTextCharFormat()
            self.number_format.setForeground(QColor("#B5CEA8"))  # Verde claro
            
            # Crear las reglas de resaltado
            self.rules = []
            
            # Reglas para palabras clave
            for word in keywords:
                pattern = QRegularExpression(r'\b' + word + r'\b', QRegularExpression.PatternOption.CaseInsensitiveOption)
                self.rules.append((pattern, self.keyword_format))
            
            # Reglas para funciones
            for func in functions:
                pattern = QRegularExpression(r'\b' + func + r'\b', QRegularExpression.PatternOption.CaseInsensitiveOption)
                self.rules.append((pattern, self.function_format))
            
            # Reglas para tipos de datos
            for dtype in data_types:
                pattern = QRegularExpression(r'\b' + dtype + r'\b', QRegularExpression.PatternOption.CaseInsensitiveOption)
                self.rules.append((pattern, self.data_type_format))
            
            # Reglas para comentarios
            self.rules.append((QRegularExpression(r'--.*$'), self.comment_format))
            
            # Reglas para cadenas
            self.rules.append((QRegularExpression(r"'[^']*'"), self.string_format))
            
            # Reglas para números
            self.rules.append((QRegularExpression(r'\b\d+\b'), self.number_format))
        
        def highlightBlock(self, text):
            # Aplicar todas las reglas
            for pattern, format in self.rules:
                match_iterator = pattern.globalMatch(text)
                while match_iterator.hasNext():
                    match = match_iterator.next()
                    self.setFormat(match.capturedStart(), match.capturedLength(), format)
    
    try:
        # Obtener el texto actual y documentos
        document = text_edit.document()
        
        # Aplicar el resaltador al documento
        highlighter = SQLHighlighter(document)
        
        # Guardar el resaltador como atributo del QTextEdit para evitar que sea eliminado por el recolector de basura
        text_edit.highlighter = highlighter
    except Exception as e:
        print(f"Error al aplicar resaltado SQL: {str(e)}")
        # Continuar sin resaltado si hay un error