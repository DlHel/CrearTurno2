from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox, QMessageBox, QFileDialog, QSplitter, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from datetime import datetime, time

from models.turno import Turno, TurnoDetalleDiario
from database.turno_dao import TurnoDAO, TurnoDAOError
from .editar_turno_dialog import EditarTurnoDialog

class BuscarTurnoWidget(QWidget):
    """Widget para buscar y editar turnos."""
    
    # Señal para comunicarse con el módulo de edición
    turno_seleccionado = pyqtSignal(Turno)
    
    def __init__(self):
        super().__init__()
        self.turno_dao = TurnoDAO()
        self.turnos_encontrados = []
        self.turno_seleccionado_actual = None
        self.esta_cargando = False
        
        self.setup_ui()
        
        # Cargar todos los turnos al iniciar, con un pequeño retraso para permitir que la interfaz se muestre
        QTimer.singleShot(100, self.cargar_todos_turnos)
        
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título
        title = QLabel("Buscar y Editar Turnos")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #007acc; margin-bottom: 10px;")
        main_layout.addWidget(title)
        
        # Barra de progreso de carga
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximum(0)  # Modo indeterminado
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                background-color: #252526;
                height: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #007acc;
            }
        """)
        self.progress_bar.hide()  # Ocultar inicialmente
        main_layout.addWidget(self.progress_bar)
        
        # Sección de búsqueda
        search_group = QGroupBox("Búsqueda de Turnos")
        search_group.setStyleSheet("""
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
        search_layout = QVBoxLayout(search_group)
        
        # Fila de búsqueda
        search_row = QHBoxLayout()
        
        # Campo de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por ID o nombre del turno...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                background: #2d2d2d;
                color: white;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
            }
        """)
        self.search_input.returnPressed.connect(self.buscar_turnos)
        search_row.addWidget(self.search_input, 3)
        
        # Botón de búsqueda
        self.search_button = QPushButton("Buscar")
        self.search_button.clicked.connect(self.buscar_turnos)
        search_row.addWidget(self.search_button, 1)
        
        # Botón de limpiar
        self.clear_button = QPushButton("Limpiar")
        self.clear_button.clicked.connect(self.limpiar_busqueda)
        search_row.addWidget(self.clear_button, 1)
        
        search_layout.addLayout(search_row)
        main_layout.addWidget(search_group)
        
        # Splitter para dividir la tabla de resultados y el detalle
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setChildrenCollapsible(False)
        
        # Tabla de resultados
        results_group = QGroupBox("Resultados")
        results_group.setStyleSheet("""
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
        results_layout = QVBoxLayout(results_group)
        
        self.results_table = QTableWidget(0, 5)  # Columnas: ID, Nombre, Estado, Detalle, Acciones
        self.results_table.setHorizontalHeaderLabels(["ID", "Nombre", "Estado", "Total Horas", "Acciones"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setStyleSheet("""
            QTableWidget {
                background-color: #252526;
                alternate-background-color: #2d2d2d;
                color: white;
                gridline-color: #3c3c3c;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #333333;
                color: white;
                padding: 5px;
                border: 1px solid #3c3c3c;
            }
            QTableWidget::item:selected {
                background-color: #264f78;
            }
        """)
        self.results_table.itemSelectionChanged.connect(self.mostrar_detalle_turno)
        
        results_layout.addWidget(self.results_table)
        splitter.addWidget(results_group)
        
        # Detalle del turno
        detail_group = QGroupBox("Horarios por Día")
        detail_group.setStyleSheet("""
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
        detail_layout = QVBoxLayout(detail_group)
        
        self.detail_table = QTableWidget(0, 4)  # Columnas: Día, Hora Ingreso, Hora Salida, Duración
        self.detail_table.setHorizontalHeaderLabels(["Día", "Hora Ingreso", "Hora Salida", "Duración (min)"])
        self.detail_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.detail_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.detail_table.setAlternatingRowColors(True)
        self.detail_table.setStyleSheet("""
            QTableWidget {
                background-color: #252526;
                alternate-background-color: #2d2d2d;
                color: white;
                gridline-color: #3c3c3c;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #333333;
                color: white;
                padding: 5px;
                border: 1px solid #3c3c3c;
            }
        """)
        
        detail_layout.addWidget(self.detail_table)
        splitter.addWidget(detail_group)
        
        # Ajustar tamaños iniciales del splitter
        splitter.setSizes([300, 200])
        
        main_layout.addWidget(splitter, 1)
        
        # Botones de acción
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        
        self.edit_button = QPushButton("Editar Turno Seleccionado")
        self.edit_button.setEnabled(False)
        self.edit_button.clicked.connect(self.editar_turno)
        action_layout.addWidget(self.edit_button)
        
        self.change_status_button = QPushButton("Cambiar Estado")
        self.change_status_button.setEnabled(False)
        self.change_status_button.clicked.connect(self.cambiar_estado)
        action_layout.addWidget(self.change_status_button)
        
        main_layout.addLayout(action_layout)
    
    def mostrar_cargando(self, mostrar=True):
        """Muestra u oculta la barra de progreso durante la carga de datos."""
        self.esta_cargando = mostrar
        if mostrar:
            self.progress_bar.show()
            self.search_button.setEnabled(False)
            self.clear_button.setEnabled(False)
        else:
            self.progress_bar.hide()
            self.search_button.setEnabled(True)
            self.clear_button.setEnabled(True)
    
    def buscar_turnos(self):
        """Busca turnos según el criterio ingresado."""
        criterio = self.search_input.text().strip()
        if not criterio:
            QMessageBox.warning(self, "Búsqueda vacía", "Por favor ingrese un criterio de búsqueda.")
            return
        
        self.mostrar_cargando(True)
        try:
            # Realizar búsqueda en base de datos
            self.turnos_encontrados = self.buscar_en_bd(criterio)
            self.mostrar_resultados()
        except TurnoDAOError as e:
            QMessageBox.critical(self, "Error de búsqueda", f"No se pudo realizar la búsqueda: {str(e)}")
        finally:
            self.mostrar_cargando(False)
    
    def buscar_en_bd(self, criterio):
        """Busca turnos en la base de datos según el criterio."""
        try:
            # Si es un número, buscar por ID
            if criterio.isdigit():
                return self.buscar_por_id(int(criterio))
            else:
                # Buscar por nombre (contiene el texto)
                return self.buscar_por_nombre(criterio)
        except Exception as e:
            print(f"Error al buscar en BD: {str(e)}")
            QMessageBox.warning(
                self, 
                "Error de búsqueda", 
                f"No se pudo realizar la búsqueda: {str(e)}"
            )
            return []  # Retornar lista vacía en caso de error
    
    def buscar_por_id(self, id_turno):
        """Busca un turno por su ID."""
        try:
            # Realizar solo la consulta a la tabla ASISTENCIAS.TURNO para obtener información básica
            query = """
            SELECT t.ID_TURNO, t.NOMBRE, t.VIGENCIA, t.FRECUENCIA
            FROM ASISTENCIAS.TURNO t
            WHERE t.ID_TURNO = :id_turno
            """
            results = self.turno_dao.db.execute_query(query, {"id_turno": id_turno})
            return self._procesar_resultados_turnos(results)
        except Exception as e:
            print(f"Error al buscar por ID: {str(e)}")
            raise TurnoDAOError(f"No se pudo buscar por ID: {str(e)}")
    
    def buscar_por_nombre(self, nombre):
        """Busca turnos por nombre."""
        try:
            # Realizar solo la consulta a la tabla ASISTENCIAS.TURNO para obtener información básica
            query = """
            SELECT t.ID_TURNO, t.NOMBRE, t.VIGENCIA, t.FRECUENCIA
            FROM ASISTENCIAS.TURNO t
            WHERE UPPER(t.NOMBRE) LIKE UPPER('%' || :nombre || '%')
            ORDER BY t.ID_TURNO DESC
            """
            results = self.turno_dao.db.execute_query(query, {"nombre": nombre})
            return self._procesar_resultados_turnos(results)
        except Exception as e:
            print(f"Error al buscar por nombre: {str(e)}")
            raise TurnoDAOError(f"No se pudo buscar por nombre: {str(e)}")
    
    def cargar_todos_turnos(self):
        """Carga todos los turnos de la base de datos."""
        self.mostrar_cargando(True)
        try:
            query = """
            SELECT t.ID_TURNO, t.NOMBRE, t.VIGENCIA, t.FRECUENCIA
            FROM ASISTENCIAS.TURNO t
            ORDER BY t.ID_TURNO DESC
            """
            results = self.turno_dao.db.execute_query(query)
            self.turnos_encontrados = self._procesar_resultados_turnos(results)
            self.mostrar_resultados()
        except Exception as e:
            print(f"Error al cargar todos los turnos: {str(e)}")
            QMessageBox.warning(
                self, 
                "Error", 
                f"No se pudieron cargar los turnos: {str(e)}"
            )
            self.turnos_encontrados = []
        finally:
            self.mostrar_cargando(False)
    
    def _procesar_resultados_turnos(self, results):
        """Procesa los resultados de la consulta de turnos (sin detalles)."""
        if not results:
            return []
        
        turnos = []
        for row in results:
            id_turno, nombre, vigencia, frecuencia = row
            
            # Crear turno solo con información básica
            turno = Turno()
            turno.id_turno = id_turno
            turno.nombre = nombre
            turno.vigencia = vigencia
            turno.frecuencia = frecuencia
            turno.detalles = []  # Lista vacía, se cargará bajo demanda
            turno._total_horas_semanales = 0  # Se calculará cuando se carguen los detalles
            
            turnos.append(turno)
        
        return turnos
    
    def _procesar_resultados_bd(self, results):
        """
        Procesa los resultados de la consulta completa (turnos con detalles).
        Este método se mantiene por compatibilidad, pero ya no se usa en la carga inicial.
        """
        if not results:
            return []
        
        turnos = {}
        for row in results:
            id_turno, nombre, vigencia, frecuencia, id_detalle, jornada, hora_ingreso, duracion = row
            
            if id_turno not in turnos:
                turno = Turno()
                turno.id_turno = id_turno
                turno.nombre = nombre
                turno.vigencia = vigencia
                turno.frecuencia = frecuencia
                turno.detalles = []
                turno._total_horas_semanales = 0
                turnos[id_turno] = turno
            
            # Agregar detalle
            detalle = TurnoDetalleDiario(
                id_turno_detalle_diario=id_detalle,
                id_turno=id_turno,
                jornada=jornada,
                hora_ingreso=time(hora_ingreso.hour, hora_ingreso.minute),
                duracion=duracion
            )
            detalle.calcular_hora_salida()
            
            turnos[id_turno].agregar_detalle(detalle)
            
        return list(turnos.values())
    
    def mostrar_resultados(self):
        """Muestra los resultados de la búsqueda en la tabla."""
        self.results_table.setRowCount(0)
        
        if not self.turnos_encontrados:
            QMessageBox.information(self, "Sin resultados", "No se encontraron turnos con el criterio especificado.")
            return
        
        for turno in self.turnos_encontrados:
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(turno.id_turno))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(row, 0, id_item)
            
            # Nombre
            nombre_item = QTableWidgetItem(turno.nombre)
            self.results_table.setItem(row, 1, nombre_item)
            
            # Estado (Vigencia)
            estado = "Activo" if turno.vigencia == 1 else "Inactivo"
            estado_item = QTableWidgetItem(estado)
            estado_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(row, 2, estado_item)
            
            # Total horas semanales
            total_horas = sum(d.duracion for d in turno.detalles) / 60
            total_item = QTableWidgetItem(f"{total_horas:.1f}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(row, 3, total_item)
            
            # Botones de acción
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(2, 2, 2, 2)
            action_layout.setSpacing(5)
            
            edit_btn = QPushButton("Editar")
            edit_btn.setProperty("row", row)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background: #007acc;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background: #0098ff;
                }
            """)
            edit_btn.clicked.connect(lambda _, r=row: self.seleccionar_fila(r))
            action_layout.addWidget(edit_btn)
            
            status_btn = QPushButton("Estado")
            status_btn.setProperty("row", row)
            status_btn.setStyleSheet("""
                QPushButton {
                    background: #555555;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background: #666666;
                }
            """)
            status_btn.clicked.connect(lambda _, r=row: self.seleccionar_fila_y_cambiar_estado(r))
            action_layout.addWidget(status_btn)
            
            action_layout.setStretch(0, 1)
            action_layout.setStretch(1, 1)
            
            self.results_table.setCellWidget(row, 4, action_widget)
    
    def seleccionar_fila(self, row):
        """Selecciona una fila de la tabla."""
        self.results_table.selectRow(row)
        self.edit_button.setEnabled(True)
        self.change_status_button.setEnabled(True)
    
    def seleccionar_fila_y_cambiar_estado(self, row):
        """Selecciona una fila y activa el cambio de estado."""
        self.seleccionar_fila(row)
        self.cambiar_estado()
    
    def mostrar_detalle_turno(self):
        """Muestra los detalles del turno seleccionado."""
        selected_items = self.results_table.selectedItems()
        if not selected_items:
            self.detail_table.setRowCount(0)
            self.turno_seleccionado_actual = None
            self.edit_button.setEnabled(False)
            self.change_status_button.setEnabled(False)
            return
        
        # Obtener el turno seleccionado
        row = selected_items[0].row()
        turno = self.turnos_encontrados[row]
        self.turno_seleccionado_actual = turno
        
        # Activar botones
        self.edit_button.setEnabled(True)
        self.change_status_button.setEnabled(True)
        
        # Cargar detalles del turno seleccionado si aún no se han cargado
        if not turno.detalles:
            self.mostrar_cargando(True)
            self.cargar_detalles_turno(turno.id_turno)
            self.mostrar_cargando(False)
        
        # Mostrar detalles en la tabla
        self.mostrar_detalles_en_tabla(turno)
    
    def cargar_detalles_turno(self, id_turno):
        """Carga los detalles de un turno específico desde la base de datos."""
        try:
            # Realizar consulta a ASISTENCIAS.TURNO_DETALLE_DIARIO solo para el turno seleccionado
            query = """
            SELECT ID_TURNO_DETALLE_DIARIO, JORNADA, HORA_INGRESO, DURACION
            FROM ASISTENCIAS.TURNO_DETALLE_DIARIO
            WHERE ID_TURNO = :id_turno
            ORDER BY JORNADA
            """
            results = self.turno_dao.db.execute_query(query, {"id_turno": id_turno})
            
            # Buscar el turno en la lista de turnos encontrados
            for turno in self.turnos_encontrados:
                if turno.id_turno == id_turno:
                    # Limpiar detalles existentes
                    turno.detalles = []
                    turno._total_horas_semanales = 0
                    
                    # Agregar los detalles
                    for row in results:
                        id_detalle, jornada, hora_ingreso, duracion = row
                        
                        detalle = TurnoDetalleDiario(
                            id_turno_detalle_diario=id_detalle,
                            id_turno=id_turno,
                            jornada=jornada,
                            hora_ingreso=time(hora_ingreso.hour, hora_ingreso.minute),
                            duracion=duracion
                        )
                        detalle.calcular_hora_salida()
                        turno.agregar_detalle(detalle)
                    
                    # Actualizar la tabla de resultados con las horas semanales
                    self.actualizar_horas_semanales_en_tabla(id_turno, turno._total_horas_semanales)
                    break
                    
        except Exception as e:
            print(f"Error al cargar detalles del turno: {str(e)}")
            QMessageBox.warning(
                self, 
                "Error", 
                f"No se pudieron cargar los detalles del turno: {str(e)}"
            )
    
    def mostrar_detalles_en_tabla(self, turno):
        """Muestra los detalles de un turno en la tabla de detalles."""
        self.detail_table.setRowCount(0)
        
        # Ordenar detalles por día
        dias_orden = {
            "Lunes": 1, "Martes": 2, "Miércoles": 3,
            "Jueves": 4, "Viernes": 5, "Sábado": 6, "Domingo": 7
        }
        
        detalles_ordenados = sorted(turno.detalles, key=lambda x: dias_orden.get(x.jornada, 8))
        
        for detalle in detalles_ordenados:
            row = self.detail_table.rowCount()
            self.detail_table.insertRow(row)
            
            # Insertar datos
            self.detail_table.setItem(row, 0, QTableWidgetItem(detalle.jornada))
            self.detail_table.setItem(row, 1, QTableWidgetItem(detalle.hora_ingreso.strftime("%H:%M")))
            self.detail_table.setItem(row, 2, QTableWidgetItem(detalle.hora_salida.strftime("%H:%M")))
            self.detail_table.setItem(row, 3, QTableWidgetItem(str(detalle.duracion)))
            
            # Centrar texto
            for col in range(4):
                item = self.detail_table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def actualizar_horas_semanales_en_tabla(self, id_turno, horas_semanales):
        """Actualiza las horas semanales en la tabla de resultados para un turno específico."""
        for row in range(self.results_table.rowCount()):
            item_id = self.results_table.item(row, 0)
            if item_id and int(item_id.text()) == id_turno:
                self.results_table.setItem(row, 3, QTableWidgetItem(f"{horas_semanales:.1f}"))
                self.results_table.item(row, 3).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                break
    
    def limpiar_busqueda(self):
        """Limpia el campo de búsqueda y los resultados."""
        self.search_input.clear()
        self.results_table.setRowCount(0)
        self.detail_table.setRowCount(0)
        self.turnos_encontrados = []
        self.turno_seleccionado_actual = None
        self.edit_button.setEnabled(False)
        self.change_status_button.setEnabled(False)
    
    def editar_turno(self):
        """Abre el editor de turnos con el turno seleccionado."""
        if not self.turno_seleccionado_actual:
            return
        
        # Crear y mostrar el diálogo de edición
        dialogo = EditarTurnoDialog(self.turno_seleccionado_actual, self)
        resultado = dialogo.exec()
        
        # Si se aceptó el diálogo, actualizar la vista
        if resultado == EditarTurnoDialog.DialogCode.Accepted:
            self.buscar_turnos()  # Refrescar la lista de turnos
            QMessageBox.information(
                self,
                "Turno Actualizado",
                "Los cambios en el turno se han procesado correctamente."
            )
    
    def cambiar_estado(self):
        """Cambia el estado (vigencia) del turno seleccionado."""
        if not self.turno_seleccionado_actual:
            return
        
        # Cambiar vigencia
        nuevo_estado = 0 if self.turno_seleccionado_actual.vigencia == 1 else 1
        estado_texto = "Activo" if nuevo_estado == 1 else "Inactivo"
        
        # Confirmar cambio
        respuesta = QMessageBox.question(
            self,
            "Cambiar Estado",
            f"¿Desea cambiar el estado del turno {self.turno_seleccionado_actual.nombre} a {estado_texto}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            # Actualizar el turno
            self.turno_seleccionado_actual.vigencia = nuevo_estado
            
            # Actualizar la tabla
            for row in range(self.results_table.rowCount()):
                id_item = self.results_table.item(row, 0)
                if id_item and int(id_item.text()) == self.turno_seleccionado_actual.id_turno:
                    estado_item = QTableWidgetItem(estado_texto)
                    estado_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.results_table.setItem(row, 2, estado_item)
                    break
            
            # Generar script SQL
            script = self.generar_script_actualizacion()
            
            # Mostrar script y opciones para exportar
            self.mostrar_script_exportacion(script)
    
    def generar_script_actualizacion(self):
        """Genera el script SQL para actualizar el turno."""
        if not self.turno_seleccionado_actual:
            return ""
        
        # Script para actualizar la vigencia
        script = f"""-- Script de actualización generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- Actualización de estado para el turno {self.turno_seleccionado_actual.id_turno}

UPDATE ASISTENCIAS.TURNO 
SET VIGENCIA = {self.turno_seleccionado_actual.vigencia} 
WHERE ID_TURNO = {self.turno_seleccionado_actual.id_turno};

COMMIT;
"""
        return script
    
    def mostrar_script_exportacion(self, script):
        """Muestra el script SQL y opciones para exportarlo."""
        # Aquí se implementaría una ventana para mostrar el script
        # Por ahora, ofrecemos la opción de exportar directamente
        respuesta = QMessageBox.question(
            self,
            "Script de Actualización",
            f"Se ha generado el script de actualización. ¿Desea exportarlo?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            self.exportar_script(script)
    
    def exportar_script(self, script):
        """Exporta el script SQL a un archivo."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Script SQL",
            f"turno_{self.turno_seleccionado_actual.id_turno}_update.sql",
            "Archivos SQL (*.sql);;Todos los archivos (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(script)
                QMessageBox.information(
                    self,
                    "Exportación Exitosa",
                    f"El script se ha guardado correctamente en:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error al Exportar",
                    f"No se pudo guardar el archivo: {str(e)}"
                )
    
    def _obtener_turnos_ejemplo(self, criterio):
        """Método de compatibilidad para pruebas, ahora no se usa."""
        return [] 