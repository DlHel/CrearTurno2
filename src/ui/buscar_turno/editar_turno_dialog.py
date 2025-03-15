from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTimeEdit, QLineEdit, QSpinBox,
    QTableWidget, QTableWidgetItem, QMessageBox,
    QFileDialog, QGroupBox, QCheckBox, QFrame,
    QDialogButtonBox
)
from PyQt6.QtCore import Qt, QTime
from PyQt6.QtGui import QFont
from datetime import datetime, time
import sys
sys.path.append('src')
from models.turno import Turno, TurnoDetalleDiario
from database.turno_dao import TurnoDAO

class EditarTurnoDialog(QDialog):
    def __init__(self, turno: Turno, parent=None):
        super().__init__(parent)
        self.turno_original = turno
        self.turno_actual = Turno()
        self.turno_actual.id_turno = turno.id_turno
        self.turno_actual.nombre = turno.nombre
        self.turno_actual.vigencia = turno.vigencia
        self.turno_actual.frecuencia = turno.frecuencia
        
        # Copiar detalles
        for detalle in turno.detalles:
            nuevo_detalle = TurnoDetalleDiario(
                id_turno_detalle_diario=detalle.id_turno_detalle_diario,
                id_turno=detalle.id_turno,
                jornada=detalle.jornada,
                hora_ingreso=detalle.hora_ingreso,
                duracion=detalle.duracion
            )
            nuevo_detalle.calcular_hora_salida()
            self.turno_actual.agregar_detalle(nuevo_detalle)
        
        self.dao = TurnoDAO()
        
        # Controlar cambios para el script SQL
        self.detalles_eliminados = []
        self.detalles_modificados = []
        self.detalles_nuevos = []
        
        self.setup_ui()
        self.actualizar_tabla_detalles()
        self.actualizar_info_turno()

    def setup_ui(self):
        """Configura la interfaz de usuario del diálogo."""
        self.setWindowTitle("Editar Turno")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título
        title = QLabel(f"Editar Turno: {self.turno_actual.nombre}")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #007acc; margin-bottom: 10px;")
        layout.addWidget(title)

        # Sección de información del turno
        info_group = QGroupBox("Información del Turno")
        info_group.setStyleSheet("""
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
        info_layout = QHBoxLayout(info_group)
        info_layout.setSpacing(15)
        
        self.id_label = QLabel(f"ID: {self.turno_actual.id_turno}")
        self.nombre_label = QLabel(f"Nombre: {self.turno_actual.nombre}")
        
        # Vigencia editable
        vigencia_layout = QHBoxLayout()
        vigencia_label = QLabel("Vigencia:")
        vigencia_label.setStyleSheet("color: white;")
        self.vigencia_spin = QSpinBox()
        self.vigencia_spin.setMinimum(0)
        self.vigencia_spin.setMaximum(1)
        self.vigencia_spin.setValue(self.turno_actual.vigencia)
        self.vigencia_spin.setToolTip("0 = Inactivo, 1 = Activo")
        self.vigencia_spin.setStyleSheet("""
            QSpinBox {
                background: #252526;
                padding: 8px;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                color: white;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                background: #333333;
            }
        """)
        vigencia_layout.addWidget(vigencia_label)
        vigencia_layout.addWidget(self.vigencia_spin)
        
        self.horas_label = QLabel(f"Horas semanales: {self.turno_actual._total_horas_semanales:.1f}")
        
        for label in [self.id_label, self.nombre_label, self.horas_label]:
            label.setStyleSheet("""
                QLabel {
                    background: #252526;
                    padding: 8px 15px;
                    border-radius: 4px;
                    color: white;
                }
            """)
            info_layout.addWidget(label)
        
        # Agregar vigencia como un widget
        vigencia_widget = QFrame()
        vigencia_widget.setStyleSheet("""
            QFrame {
                background: #252526;
                padding: 8px 15px;
                border-radius: 4px;
            }
        """)
        vigencia_widget.setLayout(vigencia_layout)
        info_layout.addWidget(vigencia_widget)
        
        layout.addWidget(info_group)

        # Sección de detalle de jornada
        detalle_group = QGroupBox("Detalle de Jornada")
        detalle_group.setStyleSheet("""
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
        detalle_layout = QVBoxLayout(detalle_group)
        
        # Selector múltiple de días
        dias_frame = QFrame()
        dias_frame.setStyleSheet("""
            QFrame {
                background: #252526;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        dias_layout = QHBoxLayout(dias_frame)
        dias_layout.setSpacing(10)
        dias_layout.setContentsMargins(10, 10, 10, 10)
        
        dias_label = QLabel("Días:")
        dias_label.setStyleSheet("color: white; font-weight: bold;")
        dias_layout.addWidget(dias_label)
        
        self.dias_checkboxes = {}
        for dia in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
            checkbox = QCheckBox(dia[:2])  # Usar abreviatura (Lu, Ma, Mi, etc.)
            checkbox.setToolTip(dia)
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: white;
                    spacing: 5px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
                QCheckBox::indicator:unchecked {
                    border: 1px solid #3c3c3c;
                    background: #252526;
                }
                QCheckBox::indicator:checked {
                    border: 1px solid #007acc;
                    background: #007acc;
                }
            """)
            dias_layout.addWidget(checkbox)
            self.dias_checkboxes[dia] = checkbox
        
        detalle_layout.addWidget(dias_frame)
        
        # Horarios
        horarios_layout = QHBoxLayout()
        
        # Hora de ingreso
        ingreso_layout = QVBoxLayout()
        ingreso_label = QLabel("Hora de Ingreso:")
        ingreso_label.setStyleSheet("color: white;")
        self.hora_ingreso = QTimeEdit()
        self.hora_ingreso.setTime(QTime(9, 0))
        self.hora_ingreso.setStyleSheet("""
            QTimeEdit {
                padding: 8px;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                background: #252526;
                color: white;
            }
            QTimeEdit::up-button, QTimeEdit::down-button {
                width: 20px;
                background: #333333;
            }
        """)
        ingreso_layout.addWidget(ingreso_label)
        ingreso_layout.addWidget(self.hora_ingreso)
        horarios_layout.addLayout(ingreso_layout)
        
        # Hora de salida
        salida_layout = QVBoxLayout()
        salida_label = QLabel("Hora de Salida:")
        salida_label.setStyleSheet("color: white;")
        self.hora_salida = QTimeEdit()
        self.hora_salida.setTime(QTime(18, 0))
        self.hora_salida.setStyleSheet("""
            QTimeEdit {
                padding: 8px;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                background: #252526;
                color: white;
            }
            QTimeEdit::up-button, QTimeEdit::down-button {
                width: 20px;
                background: #333333;
            }
        """)
        salida_layout.addWidget(salida_label)
        salida_layout.addWidget(self.hora_salida)
        horarios_layout.addLayout(salida_layout)
        
        # Duración (solo lectura)
        duracion_layout = QVBoxLayout()
        duracion_title = QLabel("Duración:")
        duracion_title.setStyleSheet("color: white;")
        self.duracion_label = QLabel("540 min")
        self.duracion_label.setStyleSheet("""
            QLabel {
                background: #252526;
                padding: 8px 15px;
                border-radius: 4px;
                color: white;
                font-weight: bold;
            }
        """)
        duracion_layout.addWidget(duracion_title)
        duracion_layout.addWidget(self.duracion_label)
        horarios_layout.addLayout(duracion_layout)
        
        # Botón agregar
        agregar_layout = QVBoxLayout()
        agregar_spacer = QLabel("")
        self.agregar_btn = QPushButton("Agregar")
        self.agregar_btn.setStyleSheet("""
            QPushButton {
                background: #007acc;
                color: white;
                border: none;
                padding: 8px 15px;
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
        self.agregar_btn.clicked.connect(self.agregar_detalle)
        agregar_layout.addWidget(agregar_spacer)
        agregar_layout.addWidget(self.agregar_btn)
        horarios_layout.addLayout(agregar_layout)
        
        detalle_layout.addLayout(horarios_layout)
        layout.addWidget(detalle_group)

        # Tabla de detalles
        tabla_group = QGroupBox("Detalles Agregados")
        tabla_group.setStyleSheet("""
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
        tabla_layout = QVBoxLayout(tabla_group)
        
        self.tabla_detalles = QTableWidget()
        self.tabla_detalles.setColumnCount(6)
        self.tabla_detalles.setHorizontalHeaderLabels([
            "ID", "Día", "Hora Ingreso", 
            "Hora Salida", "Duración", "Acciones"
        ])
        
        # Configurar ancho de columnas
        self.tabla_detalles.horizontalHeader().setStretchLastSection(True)
        
        self.tabla_detalles.setStyleSheet("""
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
        self.tabla_detalles.setAlternatingRowColors(True)
        
        tabla_layout.addWidget(self.tabla_detalles)
        layout.addWidget(tabla_group, 1)  # Dar más espacio a la tabla

        # Botones de acción
        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | 
                                   QDialogButtonBox.StandardButton.Cancel)
        buttonBox.button(QDialogButtonBox.StandardButton.Save).setText("Guardar")
        buttonBox.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        
        # Estilo de los botones
        buttonBox.setStyleSheet("""
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
            QPushButton[text="Cancelar"] {
                background: #333333;
            }
            QPushButton[text="Cancelar"]:hover {
                background: #444444;
            }
            QPushButton[text="Cancelar"]:pressed {
                background: #222222;
            }
        """)
        
        buttonBox.accepted.connect(self.guardar_turno)
        buttonBox.rejected.connect(self.reject)
        
        layout.addWidget(buttonBox)

        # Conectar eventos
        self.hora_ingreso.timeChanged.connect(self.actualizar_duracion)
        self.hora_salida.timeChanged.connect(self.actualizar_duracion)
        self.vigencia_spin.valueChanged.connect(self.actualizar_vigencia)

        # Actualizar duración inicial
        self.actualizar_duracion()

    def actualizar_duracion(self):
        """Calcula y actualiza la duración en minutos."""
        ingreso = self.hora_ingreso.time()
        salida = self.hora_salida.time()
        
        minutos_ingreso = ingreso.hour() * 60 + ingreso.minute()
        minutos_salida = salida.hour() * 60 + salida.minute()
        
        if minutos_salida < minutos_ingreso:
            minutos_salida += 24 * 60
        
        duracion = minutos_salida - minutos_ingreso
        self.duracion_label.setText(f"{duracion} min")

    def actualizar_vigencia(self):
        """Actualiza la vigencia del turno."""
        self.turno_actual.vigencia = self.vigencia_spin.value()
        
        # Registrar el cambio si es diferente al original
        if self.turno_actual.vigencia != self.turno_original.vigencia:
            # Marcar que hay cambio en la vigencia
            self.vigencia_cambiada = True
        else:
            self.vigencia_cambiada = False

    def agregar_detalle(self):
        """Agrega los detalles de jornada seleccionados."""
        # Verificar que al menos un día esté seleccionado
        dias_seleccionados = [dia for dia, checkbox in self.dias_checkboxes.items() 
                             if checkbox.isChecked()]
        
        if not dias_seleccionados:
            QMessageBox.warning(
                self, 
                "Selección de días", 
                "Debe seleccionar al menos un día para agregar a la jornada."
            )
            return
        
        # Obtener horas
        hora_ingreso = self.hora_ingreso.time()
        hora_salida = self.hora_salida.time()
        
        # Calcular duración
        minutos_ingreso = hora_ingreso.hour() * 60 + hora_ingreso.minute()
        minutos_salida = hora_salida.hour() * 60 + hora_salida.minute()
        
        if minutos_salida < minutos_ingreso:
            minutos_salida += 24 * 60
        
        duracion = minutos_salida - minutos_ingreso
        
        # Verificar que la duración sea positiva
        if duracion <= 0:
            QMessageBox.warning(
                self, 
                "Error en horario", 
                "La hora de salida debe ser posterior a la hora de ingreso."
            )
            return
        
        # Agregar un detalle por cada día seleccionado
        for dia in dias_seleccionados:
            # Verificar si ya existe un detalle para este día
            detalle_existente = next((d for d in self.turno_actual.detalles if d.jornada == dia), None)
            
            if detalle_existente:
                # Preguntar si desea sobrescribir
                respuesta = QMessageBox.question(
                    self,
                    "Día duplicado",
                    f"Ya existe un detalle para el día {dia}. ¿Desea sobrescribirlo?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if respuesta == QMessageBox.StandardButton.No:
                    continue
                
                # Si el detalle existente es original y estamos modificándolo
                if detalle_existente in [d for d in self.turno_original.detalles]:
                    if detalle_existente not in self.detalles_modificados:
                        self.detalles_modificados.append(detalle_existente)
                
                # Eliminar el detalle existente del turno actual
                self.turno_actual.detalles = [d for d in self.turno_actual.detalles if d.jornada != dia]
            
            # Crear y agregar el nuevo detalle
            nuevo_detalle = TurnoDetalleDiario(
                id_turno_detalle_diario=None,  # Se asignará después si es nuevo
                id_turno=self.turno_actual.id_turno,
                jornada=dia,
                hora_ingreso=time(hora_ingreso.hour(), hora_ingreso.minute()),
                duracion=duracion
            )
            nuevo_detalle.calcular_hora_salida()
            
            # Si es un día que no estaba en el original, marcarlo como nuevo
            if not any(d.jornada == dia for d in self.turno_original.detalles):
                self.detalles_nuevos.append(nuevo_detalle)
            else:
                # Si es una modificación de un detalle original
                detalle_original = next((d for d in self.turno_original.detalles if d.jornada == dia), None)
                if detalle_original:
                    nuevo_detalle.id_turno_detalle_diario = detalle_original.id_turno_detalle_diario
                    # Si hay cambios, registrarlos
                    if (detalle_original.hora_ingreso != nuevo_detalle.hora_ingreso or
                        detalle_original.duracion != nuevo_detalle.duracion):
                        self.detalles_modificados.append(nuevo_detalle)
            
            self.turno_actual.agregar_detalle(nuevo_detalle)
        
        # Actualizar la tabla y la información del turno
        self.actualizar_tabla_detalles()
        self.actualizar_info_turno()
        
        # Desmarcar los checkboxes
        for checkbox in self.dias_checkboxes.values():
            checkbox.setChecked(False)
        
        # Mostrar mensaje de éxito
        QMessageBox.information(
            self,
            "Detalle agregado",
            f"Se han agregado {len(dias_seleccionados)} día(s) a la jornada."
        )

    def actualizar_tabla_detalles(self):
        """Actualiza la tabla de detalles con los datos actuales."""
        self.tabla_detalles.setRowCount(0)
        
        # Ordenar detalles por día de la semana
        dias_orden = {
            "Lunes": 1, "Martes": 2, "Miércoles": 3,
            "Jueves": 4, "Viernes": 5, "Sábado": 6, "Domingo": 7
        }
        detalles_ordenados = sorted(
            self.turno_actual.detalles,
            key=lambda x: dias_orden[x.jornada]
        )
        
        for detalle in detalles_ordenados:
            row = self.tabla_detalles.rowCount()
            self.tabla_detalles.insertRow(row)
            
            # Agregar datos
            items = [
                (str(detalle.id_turno_detalle_diario or "Nuevo"), "ID único del detalle"),
                (detalle.jornada, "Día de la semana"),
                (detalle.hora_ingreso.strftime("%H:%M"), "Hora de entrada"),
                (detalle.hora_salida.strftime("%H:%M"), "Hora de salida"),
                (str(detalle.duracion), "Duración en minutos")
            ]
            
            for col, (texto, tooltip) in enumerate(items):
                item = QTableWidgetItem(texto)
                item.setToolTip(tooltip)
                
                # Resaltar elementos nuevos o modificados
                if detalle in self.detalles_nuevos:
                    item.setBackground(Qt.GlobalColor.darkGreen)
                    item.setForeground(Qt.GlobalColor.white)
                elif detalle in self.detalles_modificados:
                    item.setBackground(Qt.GlobalColor.darkYellow)
                    item.setForeground(Qt.GlobalColor.black)
                
                self.tabla_detalles.setItem(row, col, item)
            
            # Botones de acción
            acciones_widget = QWidget()
            acciones_layout = QHBoxLayout(acciones_widget)
            editar_btn = QPushButton("Editar")
            eliminar_btn = QPushButton("Eliminar")
            
            editar_btn.setStyleSheet("""
                QPushButton {
                    background: #333333;
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background: #444444;
                }
            """)
            
            eliminar_btn.setStyleSheet("""
                QPushButton {
                    background: #cc0000;
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background: #ff0000;
                }
            """)
            
            editar_btn.clicked.connect(lambda _, r=row: self.editar_detalle(r))
            eliminar_btn.clicked.connect(lambda _, r=row: self.eliminar_detalle(r))
            
            acciones_layout.addWidget(editar_btn)
            acciones_layout.addWidget(eliminar_btn)
            acciones_layout.setContentsMargins(2, 2, 2, 2)
            acciones_layout.setSpacing(4)
            
            self.tabla_detalles.setCellWidget(row, 5, acciones_widget)

    def actualizar_info_turno(self):
        """Actualiza la información del turno en la interfaz."""
        self.horas_label.setText(f"Horas semanales: {self.turno_actual._total_horas_semanales:.1f}")
        
        # Actualizar nombre del turno
        self.turno_actual.nombre = self._generar_nombre_turno()
        self.nombre_label.setText(f"Nombre: {self.turno_actual.nombre}")
        
        # Actualizar título del diálogo
        self.setWindowTitle(f"Editar Turno: {self.turno_actual.nombre}")

    def _generar_nombre_turno(self) -> str:
        """Genera el nombre del turno basado en el ID y los días configurados."""
        if not self.turno_actual.detalles:
            return self.turno_original.nombre

        # Ordenar detalles por día
        dias_orden = {
            "Lunes": 1, "Martes": 2, "Miércoles": 3,
            "Jueves": 4, "Viernes": 5, "Sábado": 6, "Domingo": 7
        }
        detalles_ordenados = sorted(
            self.turno_actual.detalles,
            key=lambda x: dias_orden[x.jornada]
        )

        # Obtener abreviaturas de días
        abreviaturas = {
            "Lunes": "Lu", "Martes": "Ma", "Miércoles": "Mi",
            "Jueves": "Ju", "Viernes": "Vi", "Sábado": "Sa", "Domingo": "Do"
        }

        # Detectar rangos consecutivos
        dias = [d.jornada for d in detalles_ordenados]
        nombre_dias = ""
        
        # Simplificar el algoritmo para detectar rangos
        inicio_rango = 0
        while inicio_rango < len(dias):
            fin_rango = inicio_rango
            # Buscar fin del rango consecutivo
            while (fin_rango + 1 < len(dias) and 
                   dias_orden[dias[fin_rango + 1]] == dias_orden[dias[fin_rango]] + 1):
                fin_rango += 1
            
            # Formatear el rango
            if inicio_rango == fin_rango:
                # Un solo día
                nombre_dias += f"{abreviaturas[dias[inicio_rango]]}/"
            else:
                # Rango de días
                nombre_dias += f"{abreviaturas[dias[inicio_rango]]} a {abreviaturas[dias[fin_rango]]}/"
            
            inicio_rango = fin_rango + 1

        # Eliminar la última barra
        nombre_dias = nombre_dias.rstrip('/')
        
        # Construir nombre completo
        horas_semanales = int(self.turno_actual._total_horas_semanales)
        return f"{self.turno_actual.id_turno}-{horas_semanales} {nombre_dias}"

    def editar_detalle(self, row: int):
        """Permite editar un detalle existente."""
        detalle = self.turno_actual.detalles[row]
        
        # Marcar el día correspondiente
        for checkbox in self.dias_checkboxes.values():
            checkbox.setChecked(False)
        self.dias_checkboxes[detalle.jornada].setChecked(True)
        
        # Establecer horas
        self.hora_ingreso.setTime(QTime(
            detalle.hora_ingreso.hour,
            detalle.hora_ingreso.minute
        ))
        self.hora_salida.setTime(QTime(
            detalle.hora_salida.hour,
            detalle.hora_salida.minute
        ))
        
        # Eliminar el detalle actual
        self.eliminar_detalle(row)

    def eliminar_detalle(self, row: int):
        """Elimina un detalle de la tabla y del turno."""
        detalle = self.turno_actual.detalles[row]
        
        # Si el detalle existía en el turno original, marcarlo para eliminar
        detalle_original = next((d for d in self.turno_original.detalles 
                               if d.jornada == detalle.jornada), None)
        if detalle_original and detalle_original.id_turno_detalle_diario:
            self.detalles_eliminados.append(detalle_original)
        
        # Eliminar de la lista de detalles nuevos o modificados si estaba ahí
        if detalle in self.detalles_nuevos:
            self.detalles_nuevos.remove(detalle)
        elif detalle in self.detalles_modificados:
            self.detalles_modificados.remove(detalle)
        
        # Eliminar del turno actual
        self.turno_actual.detalles.pop(row)
        self.actualizar_tabla_detalles()
        self.actualizar_info_turno()

    def guardar_turno(self):
        """Guarda los cambios en el turno."""
        if not self.turno_actual.detalles:
            QMessageBox.warning(
                self,
                "Error",
                "Debe agregar al menos un detalle de jornada"
            )
            return

        # Verificar si hay cambios
        if (not self.detalles_nuevos and not self.detalles_modificados and 
            not self.detalles_eliminados and self.turno_actual.vigencia == self.turno_original.vigencia):
            QMessageBox.information(
                self,
                "Sin cambios",
                "No se han detectado cambios en el turno."
            )
            self.accept()
            return

        # Generar script SQL
        script = self.generar_script_actualizacion()
        
        # Mostrar opciones para guardar
        respuesta = QMessageBox.question(
            self,
            "Guardar Cambios",
            "Se han generado los cambios. ¿Desea exportar el script SQL?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )
        
        if respuesta == QMessageBox.StandardButton.Cancel:
            return
        
        if respuesta == QMessageBox.StandardButton.Yes:
            # Mostrar diálogo para guardar
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar Script SQL",
                f"turno_{self.turno_actual.id_turno}_update.sql",
                "Archivos SQL (*.sql);;Todos los archivos (*)"
            )
            
            if filename:
                # Asegurar que el archivo termine en .sql
                if not filename.lower().endswith('.sql'):
                    filename += '.sql'
                
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(script)
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
        
        # Cerrar el diálogo con éxito
        self.accept()

    def generar_script_actualizacion(self) -> str:
        """Genera el script SQL de actualización optimizado."""
        script = "-- Script de actualización de turno\n"
        script += f"-- Generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        script += f"-- Turno: {self.turno_actual.nombre} (ID: {self.turno_actual.id_turno})\n\n"
        
        # Primero los UPDATE
        if self.turno_actual.vigencia != self.turno_original.vigencia:
            script += "-- Actualización del estado del turno\n"
            script += f"UPDATE ASISTENCIAS.TURNO SET VIGENCIA = {self.turno_actual.vigencia} "
            script += f"WHERE ID_TURNO = {self.turno_actual.id_turno};\n\n"
        
        if self.turno_actual.nombre != self.turno_original.nombre:
            script += "-- Actualización del nombre del turno\n"
            script += f"UPDATE ASISTENCIAS.TURNO SET NOMBRE = '{self.turno_actual.nombre}' "
            script += f"WHERE ID_TURNO = {self.turno_actual.id_turno};\n\n"
        
        # Actualizaciones de detalles modificados
        if self.detalles_modificados:
            script += "-- Actualización de detalles modificados\n"
            for detalle in self.detalles_modificados:
                script += f"UPDATE ASISTENCIAS.TURNO_DETALLE_DIARIO SET "
                script += f"HORA_INGRESO = TO_DATE('2025-01-01 {detalle.hora_ingreso.strftime('%H:%M')}:00', 'YYYY-MM-DD HH24:MI:SS'), "
                script += f"DURACION = {detalle.duracion} "
                script += f"WHERE ID_TURNO_DETALLE_DIARIO = {detalle.id_turno_detalle_diario};\n"
            script += "\n"
        
        # Luego los DELETE
        if self.detalles_eliminados:
            script += "-- Eliminación de detalles\n"
            for detalle in self.detalles_eliminados:
                script += f"DELETE FROM ASISTENCIAS.TURNO_DETALLE_DIARIO "
                script += f"WHERE ID_TURNO_DETALLE_DIARIO = {detalle.id_turno_detalle_diario};\n"
            script += "\n"
        
        # Finalmente los INSERT
        if self.detalles_nuevos:
            script += "-- Inserción de nuevos detalles\n"
            for detalle in self.detalles_nuevos:
                # Obtener el próximo ID disponible
                if not detalle.id_turno_detalle_diario:
                    detalle.id_turno_detalle_diario = self.dao.obtener_ultimo_id_detalle()
                
                script += f"INSERT INTO ASISTENCIAS.TURNO_DETALLE_DIARIO "
                script += f"(ID_TURNO_DETALLE_DIARIO, ID_TURNO, JORNADA, HORA_INGRESO, DURACION) "
                script += f"VALUES ({detalle.id_turno_detalle_diario}, {self.turno_actual.id_turno}, "
                script += f"'{detalle.jornada}', TO_DATE('2025-01-01 {detalle.hora_ingreso.strftime('%H:%M')}:00', "
                script += f"'YYYY-MM-DD HH24:MI:SS'), {detalle.duracion});\n"
            script += "\n"
        
        script += "COMMIT;\n"
        
        return script 