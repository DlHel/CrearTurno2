from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QComboBox, 
    QLineEdit, QDateEdit, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from src.database.oracle_connection import OracleConnection

class HorarioFlexibleWidget(QWidget):
    """Widget para la gestión y consulta de horarios flexibles."""
    
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
        title = QLabel("Horarios Flexibles")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #007acc; margin-bottom: 10px;")
        main_layout.addWidget(title)
        
        # Sección de filtros
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
            QComboBox::down-arrow {
                image: url(assets/arrow-down.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: white;
                selection-background-color: #3c3c3c;
            }
        """)
        filtros_layout.addRow("Organismo:", self.organismo_combo)
        
        # Fecha
        fecha_layout = QHBoxLayout()
        self.fecha_desde = QDateEdit()
        self.fecha_desde.setDisplayFormat("dd/MM/yyyy")
        self.fecha_desde.setDate(QDate.currentDate().addDays(-30))
        self.fecha_desde.setCalendarPopup(True)
        self.fecha_desde.setStyleSheet("""
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
            QDateEdit::down-arrow {
                image: url(assets/calendar-icon.png);
                width: 12px;
                height: 12px;
            }
        """)
        
        self.fecha_hasta = QDateEdit()
        self.fecha_hasta.setDisplayFormat("dd/MM/yyyy")
        self.fecha_hasta.setDate(QDate.currentDate())
        self.fecha_hasta.setCalendarPopup(True)
        self.fecha_hasta.setStyleSheet("""
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
            QDateEdit::down-arrow {
                image: url(assets/calendar-icon.png);
                width: 12px;
                height: 12px;
            }
        """)
        
        fecha_layout.addWidget(QLabel("Desde:"))
        fecha_layout.addWidget(self.fecha_desde)
        fecha_layout.addWidget(QLabel("Hasta:"))
        fecha_layout.addWidget(self.fecha_hasta)
        
        filtros_layout.addRow("Período:", fecha_layout)
        
        # Búsqueda por identificación
        self.id_busqueda = QLineEdit()
        self.id_busqueda.setPlaceholderText("Número de identificación o nombre")
        self.id_busqueda.setStyleSheet("""
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
        filtros_layout.addRow("Buscar:", self.id_busqueda)
        
        # Botón de búsqueda
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
        buscar_btn.clicked.connect(self.buscar_horarios)
        
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
        
        botones_layout = QHBoxLayout()
        botones_layout.addWidget(buscar_btn)
        botones_layout.addWidget(limpiar_btn)
        filtros_layout.addRow("", botones_layout)
        
        main_layout.addWidget(filtros_group)
        
        # Tabla de resultados
        self.tabla_horarios = QTableWidget()
        self.tabla_horarios.setColumnCount(6)
        self.tabla_horarios.setHorizontalHeaderLabels([
            "ID", "Funcionario", "Fecha", "Hora entrada", "Hora salida", "Estado"
        ])
        self.tabla_horarios.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_horarios.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_horarios.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_horarios.setAlternatingRowColors(True)
        self.tabla_horarios.setStyleSheet("""
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
        
        main_layout.addWidget(self.tabla_horarios)
        
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
            QMessageBox.warning(
                self,
                "Error al cargar organismos",
                f"No se pudieron cargar los organismos: {str(e)}"
            )
    
    def buscar_horarios(self):
        """Busca horarios flexibles según los criterios ingresados."""
        try:
            # Obtener criterios de búsqueda
            id_busqueda = self.id_busqueda.text().strip()
            
            # Construir consulta SQL
            query = """
            SELECT hf.ID_HORARIO_FLEXIBLE, f.NOMBRE, f.APELLIDO, 
                   hf.FECHA, hf.HORA_ENTRADA, hf.HORA_SALIDA, hf.VIGENCIA
            FROM ASISTENCIAS.HORARIO_FLEXIBLE hf
            JOIN ASISTENCIAS.FUNCIONARIO f ON hf.ID_FUNCIONARIO = f.ID_FUNCIONARIO
            WHERE VIGENCIA = 1
            """
            
            # Agregar filtro por ID si se especificó
            params = {}
            if id_busqueda:
                if id_busqueda.isdigit():
                    query += " AND hf.ID_HORARIO_FLEXIBLE = :id_horario"
                    params["id_horario"] = int(id_busqueda)
                else:
                    query += " AND (UPPER(f.NOMBRE) LIKE UPPER('%' || :nombre || '%') OR UPPER(f.APELLIDO) LIKE UPPER('%' || :nombre || '%'))"
                    params["nombre"] = id_busqueda
            
            # Ordenar resultados
            query += " ORDER BY hf.FECHA DESC, f.APELLIDO, f.NOMBRE"
            
            # Ejecutar consulta
            resultados = self.db.execute_query(query, params)
            
            if not resultados:
                self.mostrar_mensaje("No se encontraron horarios flexibles con los criterios especificados")
                return
            
            # Mostrar resultados en la tabla
            self.mostrar_resultados(resultados)
            
        except Exception as e:
            self.mostrar_error(f"Error al buscar horarios: {str(e)}")
    
    def limpiar_filtros(self):
        """Limpia todos los filtros de búsqueda."""
        self.organismo_combo.setCurrentIndex(0)
        self.fecha_desde.setDate(QDate.currentDate().addDays(-30))
        self.fecha_hasta.setDate(QDate.currentDate())
        self.id_busqueda.clear()
        self.tabla_horarios.setRowCount(0)

    def cargar_horarios(self):
        """Carga los horarios flexibles desde la base de datos."""
        try:
            # Conectar a la base de datos
            if not self.db.connect():
                self.mostrar_error("No se pudo conectar a la base de datos")
                return
            
            # Consulta SQL para obtener los horarios flexibles
            query = """
            SELECT hf.ID_HORARIO_FLEXIBLE, f.NOMBRE, f.APELLIDO, 
                   hf.FECHA, hf.HORA_ENTRADA, hf.HORA_SALIDA, hf.VIGENCIA
            FROM ASISTENCIAS.HORARIO_FLEXIBLE hf
            JOIN ASISTENCIAS.FUNCIONARIO f ON hf.ID_FUNCIONARIO = f.ID_FUNCIONARIO
            WHERE VIGENCIA = 1
            ORDER BY hf.FECHA DESC, f.APELLIDO, f.NOMBRE
            """
            
            # Ejecutar la consulta
            resultados = self.db.execute_query(query)
            
            if not resultados:
                self.mostrar_mensaje("No se encontraron horarios flexibles activos")
                return
            
            # Limpiar la tabla
            self.tabla_horarios.setRowCount(0)
            
            # Llenar la tabla con los resultados
            for row_index, row in enumerate(resultados):
                self.tabla_horarios.insertRow(row_index)
                
                # ID
                id_item = QTableWidgetItem(str(row[0]))
                id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla_horarios.setItem(row_index, 0, id_item)
                
                # Funcionario (Nombre + Apellido)
                funcionario = f"{row[1]} {row[2]}"
                funcionario_item = QTableWidgetItem(funcionario)
                self.tabla_horarios.setItem(row_index, 1, funcionario_item)
                
                # Fecha
                fecha = row[3].strftime("%d/%m/%Y") if row[3] else "N/A"
                fecha_item = QTableWidgetItem(fecha)
                fecha_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla_horarios.setItem(row_index, 2, fecha_item)
                
                # Hora entrada
                hora_entrada = row[4].strftime("%H:%M") if row[4] else "N/A"
                hora_entrada_item = QTableWidgetItem(hora_entrada)
                hora_entrada_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla_horarios.setItem(row_index, 3, hora_entrada_item)
                
                # Hora salida
                hora_salida = row[5].strftime("%H:%M") if row[5] else "N/A"
                hora_salida_item = QTableWidgetItem(hora_salida)
                hora_salida_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla_horarios.setItem(row_index, 4, hora_salida_item)
                
                # Estado
                estado_texto = "Activo" if row[6] == 1 else "Inactivo"
                estado_item = QTableWidgetItem(estado_texto)
                estado_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla_horarios.setItem(row_index, 5, estado_item)
            
            # Ajustar tamaño de las columnas
            self.tabla_horarios.resizeColumnsToContents()
            
        except Exception as e:
            self.mostrar_error(f"Error al cargar horarios: {str(e)}")

    def mostrar_error(self, mensaje):
        QMessageBox.critical(self, "Error", mensaje)

    def mostrar_mensaje(self, mensaje):
        QMessageBox.information(self, "Información", mensaje) 