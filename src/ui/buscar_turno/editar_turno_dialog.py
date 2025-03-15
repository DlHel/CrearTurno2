from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTimeEdit, QLineEdit, QSpinBox,
    QTableWidget, QTableWidgetItem, QMessageBox,
    QFileDialog, QGroupBox, QCheckBox, QFrame,
    QDialogButtonBox, QTextEdit
)
from PyQt6.QtCore import Qt, QTime
from PyQt6.QtGui import QFont
from datetime import datetime, time
import sys
sys.path.append('src')
from src.models.turno import Turno, TurnoDetalleDiario
from src.database.turno_dao import TurnoDAO
from PyQt6.QtCore import pyqtSignal

class EditarTurnoDialog(QDialog):
    """Diálogo para editar un turno existente."""

    turno_actualizado = pyqtSignal(Turno)

    def __init__(self, turno, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Turno")
        self.setMinimumSize(900, 700)
        self.setModal(True)

        # Crear copia profunda del turno para no afectar el original
        self.turno_original = turno
        self.turno_editable = self._clonar_turno(turno)

        # Mantener registro de los cambios realizados
        self.detalles_eliminados = []
        self.detalles_modificados = []
        self.detalles_nuevos = []

        # Variables para el DAO
        self.turno_dao = TurnoDAO()

        # Configurar UI
        self.setup_ui()
        self.cargar_datos_turno()

    def setup_ui(self):
        """Configura la interfaz de usuario del diálogo."""
        self.setWindowTitle("Editar Turno")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título
        title = QLabel(f"Editar Turno: {self.turno_editable.nombre}")
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

        self.id_label = QLabel(f"ID: {self.turno_editable.id_turno}")
        self.nombre_label = QLabel(f"Nombre: {self.turno_editable.nombre}")

        # Vigencia editable
        vigencia_layout = QHBoxLayout()
        vigencia_label = QLabel("Vigencia:")
        vigencia_label.setStyleSheet("color: white;")
        self.vigencia_spin = QSpinBox()
        self.vigencia_spin.setMinimum(0)
        self.vigencia_spin.setMaximum(1)
        # Convertir vigencia a entero antes de asignarla al QSpinBox
        try:
            vigencia_valor = int(self.turno_editable.vigencia)
        except (ValueError, TypeError):
            # Si no se puede convertir a entero, usar 1 como valor predeterminado
            vigencia_valor = 1
        self.vigencia_spin.setValue(vigencia_valor)
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

        self.horas_label = QLabel(f"Horas semanales: {self.turno_editable._total_horas_semanales:.1f}")

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

        buttonBox.accepted.connect(self.guardar_cambios)
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
        self.turno_editable.vigencia = self.vigencia_spin.value()

        # Convertir la vigencia original a entero para comparar
        try:
            vigencia_original = int(self.turno_original.vigencia)
        except (ValueError, TypeError):
            vigencia_original = 1

        # Registrar el cambio si es diferente al original
        if self.turno_editable.vigencia != vigencia_original:
            # Marcar que hay cambios en la vigencia
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
            detalle_existente = next((d for d in self.turno_editable.detalles if d.jornada == dia), None)

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
                self.turno_editable.detalles = [d for d in self.turno_editable.detalles if d.jornada != dia]

            # Crear y agregar el nuevo detalle
            nuevo_detalle = TurnoDetalleDiario(
                id_turno_detalle_diario=None,  # Se asignará después si es nuevo
                id_turno=self.turno_editable.id_turno,
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

            self.turno_editable.detalles.append(nuevo_detalle)

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
            self.turno_editable.detalles,
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
        self.horas_label.setText(f"Horas semanales: {self.turno_editable._total_horas_semanales:.1f}")

        # Actualizar nombre del turno
        self.turno_editable.nombre = self._generar_nombre_turno()
        self.nombre_label.setText(f"Nombre: {self.turno_editable.nombre}")

        # Actualizar título del diálogo
        self.setWindowTitle(f"Editar Turno: {self.turno_editable.nombre}")

    def _generar_nombre_turno(self) -> str:
        """Genera el nombre del turno basado en el ID y los días configurados."""
        if not self.turno_editable.detalles:
            return self.turno_original.nombre

        # Ordenar detalles por día
        dias_orden = {
            "Lunes": 1, "Martes": 2, "Miércoles": 3,
            "Jueves": 4, "Viernes": 5, "Sábado": 6, "Domingo": 7
        }
        detalles_ordenados = sorted(
            self.turno_editable.detalles,
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
        horas_semanales = int(self.turno_editable._total_horas_semanales)
        return f"{self.turno_editable.id_turno}-{horas_semanales} {nombre_dias}"

    def editar_detalle(self, row: int):
        """Permite editar un detalle existente."""
        detalle = self.turno_editable.detalles[row]

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
        detalle = self.turno_editable.detalles[row]

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
        self.turno_editable.detalles.pop(row)
        self.actualizar_tabla_detalles()
        self.actualizar_info_turno()

    def guardar_cambios(self):
        """Guarda los cambios realizados en el turno."""
        if not self._validar_cambios():
            return

        try:
            # Verificar si hubo cambios
            if not self._hay_cambios():
                QMessageBox.information(
                    self,
                    "Sin cambios",
                    "No se detectaron cambios en el turno."
                )
                self.reject()
                return

            # Generar script SQL
            script = self.generar_script_sql()
            if not script:
                return

            # Preguntar si quiere ver el script
            respuesta = QMessageBox.question(
                self,
                "Guardar Cambios",
                "Los cambios están listos para ser guardados.\n\n"
                "¿Desea ver el script SQL antes de finalizar?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )

            if respuesta == QMessageBox.StandardButton.Yes:
                # Mostrar script SQL
                self.mostrar_script_sql(script)
            else:
                # Proceder con los cambios
                self.turno_actualizado.emit(self.turno_editable)
                self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al guardar",
                f"Ocurrió un error al guardar los cambios: {str(e)}"
            )

    def mostrar_script_sql(self, script):
        """Muestra un diálogo con el script SQL y opciones para exportarlo."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Script SQL para Actualización")
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
        title = QLabel("Script SQL para Actualización de Turno")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #007acc; margin-bottom: 10px;")
        layout.addWidget(title)

        # Descripción
        descripcion = QLabel("El siguiente script SQL puede ser ejecutado en la base de datos para actualizar el turno:")
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

        # Botón Finalizar
        accept_button = QPushButton("Finalizar Edición")
        accept_button.setStyleSheet("""
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
        """)
        accept_button.clicked.connect(lambda: self._finalizar_edicion(dialog))
        button_layout.addWidget(accept_button)

        # Botón Cancelar
        cancel_button = QPushButton("Cancelar")
        cancel_button.setStyleSheet("""
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
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        # Mostrar diálogo
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.turno_actualizado.emit(self.turno_editable)
            self.accept()

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

    def _finalizar_edicion(self, dialog):
        """Finaliza la edición emitiendo la señal y cerrando el diálogo."""
        dialog.accept()
        self.turno_actualizado.emit(self.turno_editable)
        self.accept()

    def _hay_cambios(self):
        """Verifica si se han realizado cambios en el turno."""
        # Cambios en datos básicos
        if self.turno_editable.nombre != self.turno_original.nombre:
            return True
            
        # Comparar vigencia (convertir a entero para comparar)
        try:
            vigencia_original = int(self.turno_original.vigencia)
        except (ValueError, TypeError):
            vigencia_original = 1
            
        if self.turno_editable.vigencia != vigencia_original:
            return True

        # Cambios en detalles
        if self.detalles_eliminados or self.detalles_nuevos or self.detalles_modificados:
            return True

        return False

    def _validar_cambios(self):
        """Valida que los cambios sean coherentes."""
        # Verificar nombre
        if not self.turno_editable.nombre:
            QMessageBox.warning(
                self,
                "Validación",
                "El turno debe tener un nombre."
            )
            return False

        # Verificar que tenga al menos un detalle
        if not self.turno_editable.detalles:
            QMessageBox.warning(
                self,
                "Validación",
                "El turno debe tener al menos un detalle de jornada."
            )
            return False

        return True

    def _clonar_turno(self, turno):
        """Crea una copia independiente del turno."""
        clon = Turno()
        clon.id_turno = turno.id_turno
        clon.nombre = turno.nombre
        
        # Convertir vigencia a entero
        try:
            clon.vigencia = int(turno.vigencia)
        except (ValueError, TypeError):
            clon.vigencia = 1
            
        clon.frecuencia = turno.frecuencia

        for detalle in turno.detalles:
            nuevo_detalle = TurnoDetalleDiario(
                id_turno_detalle_diario=detalle.id_turno_detalle_diario,
                id_turno=detalle.id_turno,
                jornada=detalle.jornada,
                hora_ingreso=time(
                    hour=detalle.hora_ingreso.hour,
                    minute=detalle.hora_ingreso.minute
                ),
                duracion=detalle.duracion
            )
            if detalle.hora_salida:
                nuevo_detalle.hora_salida = time(
                    hour=detalle.hora_salida.hour,
                    minute=detalle.hora_salida.minute
                )
            else:
                nuevo_detalle.calcular_hora_salida()

            clon.detalles.append(nuevo_detalle)

        return clon

    def generar_script_sql(self):
        """
        Genera el script SQL para los cambios realizados en el turno
        siguiendo el orden: UPDATE, DELETE, INSERT.
        """
        try:
            script = ""

            # 1. UPDATEs (primero la tabla principal si cambió el nombre o vigencia)
            nombre_cambio = self.turno_editable.nombre != self.turno_original.nombre
            vigencia_cambio = self.turno_editable.vigencia != self.turno_original.vigencia

            if nombre_cambio or vigencia_cambio:
                script += f"-- Actualizar tabla TURNO\n"
                script += f"UPDATE ASISTENCIAS.TURNO SET\n"

                updates = []
                if nombre_cambio:
                    updates.append(f"NOMBRE = '{self.turno_editable.nombre}'")
                if vigencia_cambio:
                    updates.append(f"VIGENCIA = '{self.turno_editable.vigencia}'")

                script += ", ".join(updates)
                script += f"\nWHERE ID_TURNO = {self.turno_editable.id_turno};\n\n"

            # UPDATEs para los detalles modificados
            if self.detalles_modificados:
                script += f"-- Actualizar detalles modificados\n"
                for detalle in self.detalles_modificados:
                    id_detalle = detalle.id_turno_detalle_diario
                    script += f"UPDATE ASISTENCIAS.TURNO_DETALLE_DIARIO SET\n"
                    script += f"  JORNADA = '{detalle.jornada}',\n"
                    script += f"  HORA_INGRESO = TO_DATE('2025-01-01 {detalle.hora_ingreso.strftime('%H:%M')}:00', 'YYYY-MM-DD HH24:MI:SS'),\n"
                    script += f"  DURACION = {detalle.duracion}\n"
                    script += f"WHERE ID_TURNO_DETALLE_DIARIO = {id_detalle};\n\n"

            # 2. DELETEs para los detalles eliminados
            if self.detalles_eliminados:
                script += f"-- Eliminar detalles\n"
                for id_detalle in self.detalles_eliminados:
                    script += f"DELETE FROM ASISTENCIAS.TURNO_DETALLE_DIARIO WHERE ID_TURNO_DETALLE_DIARIO = {id_detalle};\n"
                script += "\n"

            # 3. INSERTs para los nuevos detalles
            if self.detalles_nuevos:
                script += f"-- Insertar nuevos detalles\n"
                for detalle in self.detalles_nuevos:
                    script += f"INSERT INTO ASISTENCIAS.TURNO_DETALLE_DIARIO\n"
                    script += f"  (ID_TURNO_DETALLE_DIARIO, ID_TURNO, JORNADA, HORA_INGRESO, DURACION)\n"
                    script += f"VALUES (\n"
                    script += f"  {detalle.id_turno_detalle_diario},\n"
                    script += f"  {self.turno_editable.id_turno},\n"
                    script += f"  '{detalle.jornada}',\n"
                    script += f"  TO_DATE('2025-01-01 {detalle.hora_ingreso.strftime('%H:%M')}:00', 'YYYY-MM-DD HH24:MI:SS'),\n"
                    script += f"  {detalle.duracion}\n"
                    script += f");\n\n"

            return script

        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error al generar SQL",
                f"Ocurrió un error al generar el script SQL: {str(e)}"
            )
            return None 