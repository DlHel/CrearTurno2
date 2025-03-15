from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QComboBox, 
    QLineEdit, QGroupBox, QFormLayout, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.database.oracle_connection import OracleConnection
from src.database.turno_dao import TurnoDAO
from src.models.turno import Turno

class ConsultaTurnoWidget(QWidget):
    """Widget para consultar los turnos asignados a funcionarios."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = OracleConnection()
        self.turno_dao = TurnoDAO()
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título
        title = QLabel("Consulta de Turnos por Funcionario")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #007acc; margin-bottom: 10px;")
        main_layout.addWidget(title)
        
        # Filtros de búsqueda
        filtros_group = QGroupBox("Filtros de búsqueda")
        filtros_group.setStyleSheet("""
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
        
        filtros_layout = QFormLayout(filtros_group)
        filtros_layout.setContentsMargins(15, 20, 15, 15)
        filtros_layout.setSpacing(15)
        
        # Organismo
        self.organismo_combo = QComboBox()
        self.organismo_combo.setStyleSheet("""
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
        filtros_layout.addRow("Organismo:", self.organismo_combo)
        
        # ID o nombre del funcionario
        self.funcionario_input = QLineEdit()
        self.funcionario_input.setPlaceholderText("RUT o nombre del funcionario")
        self.funcionario_input.setStyleSheet("""
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
        filtros_layout.addRow("Funcionario:", self.funcionario_input)
        
        # ID del turno
        self.turno_input = QLineEdit()
        self.turno_input.setPlaceholderText("ID o nombre del turno")
        self.turno_input.setStyleSheet("""
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
        filtros_layout.addRow("Turno:", self.turno_input)
        
        # Botones
        botones_layout = QHBoxLayout()
        
        buscar_btn = QPushButton("Buscar")
        buscar_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 16px;
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
        buscar_btn.clicked.connect(self.buscar_turnos)
        
        limpiar_btn = QPushButton("Limpiar Filtros")
        limpiar_btn.setStyleSheet("""
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
            QPushButton:pressed {
                background-color: #444444;
            }
        """)
        limpiar_btn.clicked.connect(self.limpiar_filtros)
        
        botones_layout.addWidget(buscar_btn)
        botones_layout.addWidget(limpiar_btn)
        filtros_layout.addRow("", botones_layout)
        
        main_layout.addWidget(filtros_group)
        
        # Splitter para dividir la pantalla en dos secciones
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background: #3c3c3c;
                height: 1px;
            }
        """)
        
        # Tabla de funcionarios y turnos asignados
        funcionarios_container = QWidget()
        funcionarios_layout = QVBoxLayout(funcionarios_container)
        funcionarios_layout.setContentsMargins(0, 0, 0, 0)
        
        funcionarios_label = QLabel("Funcionarios y Turnos Asignados")
        funcionarios_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        funcionarios_label.setStyleSheet("color: #007acc; margin-bottom: 5px;")
        funcionarios_layout.addWidget(funcionarios_label)
        
        self.funcionarios_table = QTableWidget()
        self.funcionarios_table.setColumnCount(5)
        self.funcionarios_table.setHorizontalHeaderLabels([
            "ID", "Funcionario", "RUT", "ID Turno", "Nombre Turno"
        ])
        self.funcionarios_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.funcionarios_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.funcionarios_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.funcionarios_table.setAlternatingRowColors(True)
        self.funcionarios_table.setStyleSheet("""
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
        
        funcionarios_layout.addWidget(self.funcionarios_table)
        self.funcionarios_table.itemSelectionChanged.connect(self.cargar_detalle_turno)
        
        # Detalle del turno seleccionado
        detalle_container = QWidget()
        detalle_layout = QVBoxLayout(detalle_container)
        detalle_layout.setContentsMargins(0, 0, 0, 0)
        
        detalle_label = QLabel("Detalle del Turno Seleccionado")
        detalle_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        detalle_label.setStyleSheet("color: #007acc; margin-bottom: 5px;")
        detalle_layout.addWidget(detalle_label)
        
        self.detalle_table = QTableWidget()
        self.detalle_table.setColumnCount(4)
        self.detalle_table.setHorizontalHeaderLabels([
            "Día", "Hora Ingreso", "Hora Salida", "Duración (min)"
        ])
        self.detalle_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.detalle_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.detalle_table.setAlternatingRowColors(True)
        self.detalle_table.setStyleSheet("""
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
        
        detalle_layout.addWidget(self.detalle_table)
        
        # Agregar containers al splitter
        splitter.addWidget(funcionarios_container)
        splitter.addWidget(detalle_container)
        
        # Establecer proporción inicial
        splitter.setSizes([int(self.height() * 0.6), int(self.height() * 0.4)])
        
        main_layout.addWidget(splitter)
        
        # Cargar datos iniciales
        self.cargar_organismos()
    
    def cargar_organismos(self):
        """Carga los organismos desde la base de datos."""
        try:
            self.organismo_combo.clear()
            self.organismo_combo.addItem("Todos los organismos", None)
            
            # Consulta para obtener los organismos
            query = """
                SELECT ID_ORGANISMO, NOMBRE
                FROM DATOS_TRANSVERSALES.ORGANISMO
                WHERE VIGENCIA = 1
                ORDER BY NOMBRE
            """
            
            # Ejecutar consulta
            resultados = self.db.execute_query(query)
            
            if resultados:
                for row in resultados:
                    id_organismo, nombre = row
                    self.organismo_combo.addItem(nombre, id_organismo)
            
        except Exception as e:
            self.mostrar_error(f"Error al cargar organismos: {str(e)}")
    
    def buscar_turnos(self):
        """Busca los turnos asignados según los filtros establecidos."""
        try:
            # Obtener valores de los filtros
            id_organismo = self.organismo_combo.currentData()
            funcionario = self.funcionario_input.text().strip()
            turno = self.turno_input.text().strip()
            
            # Construir consulta base
            query = """
                SELECT p.ID_PERSONA, p.APELLIDO_PATERNO || ' ' || p.APELLIDO_MATERNO || ', ' || p.NOMBRE AS FUNCIONARIO, 
                       p.RUT, t.ID_TURNO, t.NOMBRE
                FROM DATOS_TRANSVERSALES.PERSONA p
                JOIN ASISTENCIAS.PERSONA_TURNO pt ON p.ID_PERSONA = pt.ID_PERSONA
                JOIN ASISTENCIAS.TURNO t ON pt.ID_TURNO = t.ID_TURNO
                WHERE 1=1
            """
            
            # Parámetros para la consulta
            params = {}
            
            # Agregar filtros según los valores ingresados
            if id_organismo:
                query += " AND p.ID_ORGANISMO = :id_organismo"
                params["id_organismo"] = id_organismo
            
            if funcionario:
                query += """
                    AND (
                        UPPER(p.NOMBRE) LIKE UPPER('%' || :funcionario || '%')
                        OR UPPER(p.APELLIDO_PATERNO) LIKE UPPER('%' || :funcionario || '%')
                        OR UPPER(p.APELLIDO_MATERNO) LIKE UPPER('%' || :funcionario || '%')
                        OR p.RUT LIKE '%' || :funcionario || '%'
                    )
                """
                params["funcionario"] = funcionario
            
            if turno:
                # Verificar si es un ID numérico o un nombre
                if turno.isdigit():
                    query += " AND t.ID_TURNO = :id_turno"
                    params["id_turno"] = int(turno)
                else:
                    query += " AND UPPER(t.NOMBRE) LIKE UPPER('%' || :nombre_turno || '%')"
                    params["nombre_turno"] = turno
            
            # Ordenar resultados
            query += " ORDER BY p.APELLIDO_PATERNO, p.APELLIDO_MATERNO, p.NOMBRE"
            
            # Ejecutar consulta
            resultados = self.db.execute_query(query, params)
            
            # Llenar tabla con resultados
            self.funcionarios_table.setRowCount(0)
            
            if resultados:
                for row_index, row in enumerate(resultados):
                    self.funcionarios_table.insertRow(row_index)
                    
                    # ID Persona
                    id_item = QTableWidgetItem(str(row[0]))
                    id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.funcionarios_table.setItem(row_index, 0, id_item)
                    
                    # Funcionario
                    self.funcionarios_table.setItem(row_index, 1, QTableWidgetItem(row[1]))
                    
                    # RUT
                    rut_item = QTableWidgetItem(row[2])
                    rut_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.funcionarios_table.setItem(row_index, 2, rut_item)
                    
                    # ID Turno
                    id_turno_item = QTableWidgetItem(str(row[3]))
                    id_turno_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.funcionarios_table.setItem(row_index, 3, id_turno_item)
                    
                    # Nombre Turno
                    self.funcionarios_table.setItem(row_index, 4, QTableWidgetItem(row[4]))
                    
                # Limpiar tabla de detalles
                self.detalle_table.setRowCount(0)
                
            else:
                QMessageBox.information(
                    self,
                    "Sin resultados",
                    "No se encontraron funcionarios con los filtros proporcionados."
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error en la búsqueda",
                f"Ocurrió un error al buscar los turnos: {str(e)}"
            )
    
    def cargar_detalle_turno(self):
        """Carga el detalle del turno seleccionado."""
        # Obtener fila seleccionada
        indexes = self.funcionarios_table.selectedIndexes()
        if not indexes:
            return
        
        row = indexes[0].row()
        
        # Obtener ID del turno
        id_turno_item = self.funcionarios_table.item(row, 3)
        if not id_turno_item:
            return
        
        try:
            id_turno = int(id_turno_item.text())
            
            # Buscar detalle del turno
            turno = self.turno_dao.buscar_por_id(id_turno)
            
            if not turno:
                QMessageBox.warning(
                    self,
                    "Turno no encontrado",
                    f"No se encontró el detalle del turno con ID {id_turno}."
                )
                return
            
            # Llenar tabla de detalles
            self.detalle_table.setRowCount(0)
            
            # Ordenar por días de la semana
            dias_orden = {
                "Lunes": 1, "Martes": 2, "Miércoles": 3,
                "Jueves": 4, "Viernes": 5, "Sábado": 6, "Domingo": 7
            }
            detalles_ordenados = sorted(
                turno.detalles,
                key=lambda x: dias_orden.get(x.jornada, 99)
            )
            
            for row_index, detalle in enumerate(detalles_ordenados):
                self.detalle_table.insertRow(row_index)
                
                # Día
                self.detalle_table.setItem(row_index, 0, QTableWidgetItem(detalle.jornada))
                
                # Hora Ingreso
                hora_ingreso = detalle.hora_ingreso.strftime("%H:%M")
                ingreso_item = QTableWidgetItem(hora_ingreso)
                ingreso_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.detalle_table.setItem(row_index, 1, ingreso_item)
                
                # Hora Salida
                if detalle.hora_salida:
                    hora_salida = detalle.hora_salida.strftime("%H:%M")
                else:
                    # Calcular hora salida si no está disponible
                    detalle.calcular_hora_salida()
                    hora_salida = detalle.hora_salida.strftime("%H:%M")
                    
                salida_item = QTableWidgetItem(hora_salida)
                salida_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.detalle_table.setItem(row_index, 2, salida_item)
                
                # Duración
                duracion_item = QTableWidgetItem(str(detalle.duracion))
                duracion_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.detalle_table.setItem(row_index, 3, duracion_item)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al cargar detalle",
                f"Ocurrió un error al cargar el detalle del turno: {str(e)}"
            )
    
    def limpiar_filtros(self):
        """Limpia todos los filtros de búsqueda."""
        self.organismo_combo.setCurrentIndex(0)
        self.funcionario_input.clear()
        self.turno_input.clear()
        self.funcionarios_table.setRowCount(0)
        self.detalle_table.setRowCount(0)

    def cargar_turnos(self):
        """Carga los turnos desde la base de datos."""
        try:
            # Conectar a la base de datos
            if not self.db.connect():
                self.mostrar_error("No se pudo conectar a la base de datos")
                return
            
            # Consulta SQL para obtener los turnos
            query = """
            SELECT t.ID_TURNO, t.NOMBRE, t.VIGENCIA, t.FRECUENCIA
            FROM ASISTENCIAS.TURNO t
            WHERE VIGENCIA = 1
            ORDER BY t.ID_TURNO
            """
            
            # Ejecutar la consulta
            resultados = self.db.execute_query(query)
            
            if not resultados:
                self.mostrar_error("No se encontraron turnos activos")
                return
            
            # Limpiar la tabla
            self.tabla_turnos.setRowCount(0)
            
            # Llenar la tabla con los resultados
            for fila, (id_turno, nombre, vigencia, frecuencia) in enumerate(resultados):
                self.tabla_turnos.insertRow(fila)
                
                # ID
                id_item = QTableWidgetItem(str(id_turno))
                id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla_turnos.setItem(fila, 0, id_item)
                
                # Nombre
                nombre_item = QTableWidgetItem(nombre)
                self.tabla_turnos.setItem(fila, 1, nombre_item)
                
                # Frecuencia
                frecuencia_item = QTableWidgetItem(frecuencia)
                frecuencia_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla_turnos.setItem(fila, 2, frecuencia_item)
                
                # Botón para ver detalles
                btn_detalles = QPushButton("Ver Detalles")
                btn_detalles.setStyleSheet("""
                    QPushButton {
                        background-color: #007acc;
                        color: white;
                        border: none;
                        padding: 5px 10px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #0098ff;
                    }
                    QPushButton:pressed {
                        background-color: #005c99;
                    }
                """)
                btn_detalles.clicked.connect(lambda _, id=id_turno: self.ver_detalles_turno(id))
                
                btn_container = QWidget()
                btn_layout = QHBoxLayout(btn_container)
                btn_layout.addWidget(btn_detalles)
                btn_layout.setContentsMargins(5, 2, 5, 2)
                btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                self.tabla_turnos.setCellWidget(fila, 3, btn_container)
            
            # Ajustar tamaño de las columnas
            self.tabla_turnos.resizeColumnsToContents()
            
        except Exception as e:
            self.mostrar_error(f"Error al cargar turnos: {str(e)}")

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error."""
        QMessageBox.critical(
            self,
            "Error",
            mensaje
        )

    def ver_detalles_turno(self, id_turno):
        """Muestra los detalles del turno seleccionado."""
        # Implementa la lógica para mostrar los detalles del turno aquí
        pass

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error."""
        QMessageBox.critical(
            self,
            "Error",
            mensaje
        )

    def ver_detalles_turno(self, id_turno):
        """Muestra los detalles del turno seleccionado."""
        # Implementa la lógica para mostrar los detalles del turno aquí
        pass 