from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QComboBox, 
    QLineEdit, QDateEdit, QTimeEdit, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, QDate, QTime
from PyQt6.QtGui import QFont
from src.database.oracle_connection import OracleConnection
import datetime

class MarcajeAsistenciaWidget(QWidget):
    """Widget para gestionar los marcajes de asistencia."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = OracleConnection()
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título
        title = QLabel("Marcaje de Asistencia")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #007acc; margin-bottom: 10px;")
        main_layout.addWidget(title)
        
        # Sección de registro de marcaje
        registro_group = QGroupBox("Registro de Marcaje")
        registro_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        registro_layout = QFormLayout(registro_group)
        registro_layout.setContentsMargins(15, 20, 15, 15)
        registro_layout.setSpacing(15)
        
        # Datos del funcionario
        self.rut_input = QLineEdit()
        self.rut_input.setPlaceholderText("RUT del funcionario")
        self.rut_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background-color: #252526;
                color: white;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
            }
        """)
        registro_layout.addRow("RUT:", self.rut_input)
        
        # Tipo de marcaje
        self.tipo_marcaje_combo = QComboBox()
        self.tipo_marcaje_combo.addItems(["Entrada", "Salida", "Salida Temporal", "Retorno"])
        self.tipo_marcaje_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                background-color: #252526;
                color: white;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: white;
                selection-background-color: #3c3c3c;
            }
        """)
        registro_layout.addRow("Tipo de Marcaje:", self.tipo_marcaje_combo)
        
        # Fecha y hora
        fecha_layout = QHBoxLayout()
        
        self.fecha_marcaje = QDateEdit()
        self.fecha_marcaje.setDisplayFormat("dd/MM/yyyy")
        self.fecha_marcaje.setDate(QDate.currentDate())
        self.fecha_marcaje.setCalendarPopup(True)
        self.fecha_marcaje.setStyleSheet("""
            QDateEdit {
                padding: 5px;
                background-color: #252526;
                color: white;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
            QDateEdit::drop-down {
                border: 0px;
            }
        """)
        
        self.hora_marcaje = QTimeEdit()
        self.hora_marcaje.setDisplayFormat("HH:mm:ss")
        self.hora_marcaje.setTime(QTime.currentTime())
        self.hora_marcaje.setStyleSheet("""
            QTimeEdit {
                padding: 5px;
                background-color: #252526;
                color: white;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
            QTimeEdit::drop-down {
                border: 0px;
            }
        """)
        
        ahora_btn = QPushButton("Ahora")
        ahora_btn.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
        """)
        ahora_btn.clicked.connect(self.establecer_fecha_hora_actual)
        
        fecha_layout.addWidget(self.fecha_marcaje)
        fecha_layout.addWidget(self.hora_marcaje)
        fecha_layout.addWidget(ahora_btn)
        registro_layout.addRow("Fecha y Hora:", fecha_layout)
        
        # Comentario
        self.comentario_input = QLineEdit()
        self.comentario_input.setPlaceholderText("Comentario opcional")
        self.comentario_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background-color: #252526;
                color: white;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
            }
        """)
        registro_layout.addRow("Comentario:", self.comentario_input)
        
        # Botones
        botones_layout = QHBoxLayout()
        
        registrar_btn = QPushButton("Registrar Marcaje")
        registrar_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0098ff;
            }
            QPushButton:pressed {
                background-color: #005f99;
            }
        """)
        registrar_btn.clicked.connect(self.registrar_marcaje)
        
        limpiar_btn = QPushButton("Limpiar")
        limpiar_btn.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
        """)
        limpiar_btn.clicked.connect(self.limpiar_formulario)
        
        botones_layout.addWidget(registrar_btn)
        botones_layout.addWidget(limpiar_btn)
        registro_layout.addRow("", botones_layout)
        
        main_layout.addWidget(registro_group)
        
        # Sección de consulta de marcajes
        consulta_group = QGroupBox("Consulta de Marcajes")
        consulta_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        consulta_layout = QVBoxLayout(consulta_group)
        consulta_layout.setContentsMargins(15, 20, 15, 15)
        consulta_layout.setSpacing(15)
        
        # Filtros de búsqueda
        filtros_layout = QHBoxLayout()
        
        self.buscar_rut = QLineEdit()
        self.buscar_rut.setPlaceholderText("RUT del funcionario")
        self.buscar_rut.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background-color: #252526;
                color: white;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
            }
        """)
        
        buscar_btn = QPushButton("Buscar")
        buscar_btn.setStyleSheet("""
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
            QPushButton:pressed {
                background-color: #005f99;
            }
        """)
        buscar_btn.clicked.connect(self.buscar_marcajes)
        
        filtros_layout.addWidget(QLabel("RUT:"))
        filtros_layout.addWidget(self.buscar_rut)
        filtros_layout.addWidget(buscar_btn)
        
        consulta_layout.addLayout(filtros_layout)
        
        # Tabla de marcajes
        self.marcajes_table = QTableWidget()
        self.marcajes_table.setColumnCount(6)
        self.marcajes_table.setHorizontalHeaderLabels([
            "ID", "Funcionario", "Fecha", "Hora", "Tipo", "Comentario"
        ])
        self.marcajes_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.marcajes_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.marcajes_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.marcajes_table.setAlternatingRowColors(True)
        self.marcajes_table.setStyleSheet("""
            QTableWidget {
                background-color: #252526;
                color: white;
                gridline-color: #3c3c3c;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #264f78;
            }
            QHeaderView::section {
                background-color: #333333;
                color: white;
                padding: 5px;
                border: 1px solid #3c3c3c;
            }
            QTableWidget::item:alternate {
                background-color: #2d2d2d;
            }
        """)
        
        consulta_layout.addWidget(self.marcajes_table)
        
        main_layout.addWidget(consulta_group)
        
    def establecer_fecha_hora_actual(self):
        """Establece la fecha y hora actual en los controles correspondientes."""
        self.fecha_marcaje.setDate(QDate.currentDate())
        self.hora_marcaje.setTime(QTime.currentTime())
    
    def registrar_marcaje(self):
        """Registra un nuevo marcaje de asistencia."""
        # Validar que se haya ingresado el RUT
        rut = self.rut_input.text().strip()
        if not rut:
            QMessageBox.warning(
                self,
                "Datos incompletos",
                "Debe ingresar el RUT del funcionario."
            )
            return
        
        try:
            # Verificar si el funcionario existe
            query_verificar = """
                SELECT ID_PERSONA, NOMBRE, APELLIDO_PATERNO, APELLIDO_MATERNO
                FROM DATOS_TRANSVERSALES.PERSONA
                WHERE RUT = :rut
            """
            resultado = self.db.execute_query(query_verificar, {"rut": rut})
            
            if not resultado:
                QMessageBox.warning(
                    self,
                    "Funcionario no encontrado",
                    f"No se encontró ningún funcionario con el RUT {rut}."
                )
                return
            
            # Obtener datos del funcionario
            id_persona = resultado[0][0]
            nombre_completo = f"{resultado[0][1]} {resultado[0][2]} {resultado[0][3]}"
            
            # Obtener datos del marcaje
            tipo_marcaje = self.tipo_marcaje_combo.currentText()
            fecha = self.fecha_marcaje.date().toString("yyyy-MM-dd")
            hora = self.hora_marcaje.time().toString("HH:mm:ss")
            comentario = self.comentario_input.text()
            
            # Mostrar confirmación
            confirmacion = QMessageBox.question(
                self,
                "Confirmar Marcaje",
                f"¿Está seguro de registrar el siguiente marcaje?\n\n"
                f"Funcionario: {nombre_completo}\n"
                f"Tipo: {tipo_marcaje}\n"
                f"Fecha y hora: {fecha} {hora}\n"
                f"Comentario: {comentario}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if confirmacion == QMessageBox.StandardButton.No:
                return
            
            # Generar script de inserción
            script = f"""
            -- Registrar marcaje para {nombre_completo} (RUT: {rut})
            INSERT INTO ASISTENCIAS.MARCAJE (
                ID_MARCAJE, ID_PERSONA, FECHA, HORA, TIPO, COMENTARIO
            ) VALUES (
                ASISTENCIAS.SEQ_MARCAJE.NEXTVAL,
                {id_persona},
                TO_DATE('{fecha}', 'YYYY-MM-DD'),
                TO_DATE('{hora}', 'HH24:MI:SS'),
                '{tipo_marcaje}',
                '{comentario}'
            );
            
            COMMIT;
            """
            
            # Mostrar script generado
            QMessageBox.information(
                self,
                "Marcaje Registrado",
                f"Se ha generado el siguiente script para registrar el marcaje:\n\n{script}"
            )
            
            # Limpiar formulario después de registro exitoso
            self.limpiar_formulario()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al registrar marcaje",
                f"Ocurrió un error al registrar el marcaje: {str(e)}"
            )
    
    def buscar_marcajes(self):
        """Busca marcajes de un funcionario por RUT."""
        rut = self.buscar_rut.text().strip()
        if not rut:
            QMessageBox.warning(
                self,
                "Datos incompletos",
                "Debe ingresar el RUT del funcionario para realizar la búsqueda."
            )
            return
        
        try:
            # Construir consulta
            query = """
                SELECT m.ID_MARCAJE, p.APELLIDO_PATERNO || ' ' || p.APELLIDO_MATERNO || ', ' || p.NOMBRE AS FUNCIONARIO,
                       m.FECHA, m.HORA, m.TIPO, m.COMENTARIO
                FROM ASISTENCIAS.MARCAJE m
                JOIN DATOS_TRANSVERSALES.PERSONA p ON m.ID_PERSONA = p.ID_PERSONA
                WHERE p.RUT = :rut
                ORDER BY m.FECHA DESC, m.HORA DESC
            """
            
            # Ejecutar consulta
            resultados = self.db.execute_query(query, {"rut": rut})
            
            # Llenar tabla con resultados
            self.marcajes_table.setRowCount(0)
            
            if resultados:
                for row_index, row in enumerate(resultados):
                    self.marcajes_table.insertRow(row_index)
                    
                    # ID Marcaje
                    id_item = QTableWidgetItem(str(row[0]))
                    id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.marcajes_table.setItem(row_index, 0, id_item)
                    
                    # Funcionario
                    self.marcajes_table.setItem(row_index, 1, QTableWidgetItem(row[1]))
                    
                    # Fecha
                    fecha = row[2].strftime("%d/%m/%Y") if row[2] else ""
                    fecha_item = QTableWidgetItem(fecha)
                    fecha_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.marcajes_table.setItem(row_index, 2, fecha_item)
                    
                    # Hora
                    hora = row[3].strftime("%H:%M:%S") if row[3] else ""
                    hora_item = QTableWidgetItem(hora)
                    hora_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.marcajes_table.setItem(row_index, 3, hora_item)
                    
                    # Tipo
                    tipo_item = QTableWidgetItem(row[4])
                    tipo_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.marcajes_table.setItem(row_index, 4, tipo_item)
                    
                    # Comentario
                    comentario = row[5] or ""
                    self.marcajes_table.setItem(row_index, 5, QTableWidgetItem(comentario))
                    
            else:
                QMessageBox.information(
                    self,
                    "Sin resultados",
                    f"No se encontraron marcajes para el funcionario con RUT {rut}."
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error en la búsqueda",
                f"Ocurrió un error al buscar los marcajes: {str(e)}"
            )
    
    def limpiar_formulario(self):
        """Limpia el formulario de registro de marcaje."""
        self.rut_input.clear()
        self.tipo_marcaje_combo.setCurrentIndex(0)
        self.fecha_marcaje.setDate(QDate.currentDate())
        self.hora_marcaje.setTime(QTime.currentTime())
        self.comentario_input.clear() 