from typing import List, Optional
from datetime import datetime, time
from dataclasses import dataclass

@dataclass
class TurnoDetalleDiario:
    id_turno_detalle_diario: int
    id_turno: int
    jornada: str
    hora_ingreso: time
    duracion: int
    hora_salida: Optional[time] = None

    def calcular_hora_salida(self) -> None:
        """Calcula la hora de salida basada en la hora de ingreso y la duración en minutos."""
        if self.hora_ingreso and self.duracion:
            minutos_totales = self.hora_ingreso.hour * 60 + self.hora_ingreso.minute + self.duracion
            horas = minutos_totales // 60
            minutos = minutos_totales % 60
            self.hora_salida = time(hour=horas % 24, minute=minutos)

class Turno:
    def __init__(self):
        self.id_turno: Optional[int] = None
        self.nombre: str = ""
        self.vigencia: int = 1
        self.frecuencia: str = "Diarios"
        self.detalles: List[TurnoDetalleDiario] = []
        self._total_horas_semanales: float = 0.0

    def agregar_detalle(self, detalle: TurnoDetalleDiario) -> bool:
        """
        Agrega un detalle de turno validando que no exista el mismo día.
        
        Args:
            detalle: Objeto TurnoDetalleDiario a agregar
            
        Returns:
            bool: True si se agregó correctamente, False si ya existe el día
        """
        # Verificar si ya existe un detalle para ese día
        if any(d.jornada == detalle.jornada for d in self.detalles):
            return False
        
        # Calcular hora de salida si no está establecida
        if not detalle.hora_salida:
            detalle.calcular_hora_salida()
        
        self.detalles.append(detalle)
        self._actualizar_total_horas()
        self._actualizar_nombre()
        return True

    def _actualizar_total_horas(self) -> None:
        """Actualiza el total de horas semanales basado en los detalles."""
        self._total_horas_semanales = sum(d.duracion for d in self.detalles) / 60

    def _actualizar_nombre(self) -> None:
        """Actualiza el nombre del turno basado en el ID y los días de la jornada."""
        if not self.detalles:
            return

        # Ordenar días de la semana
        dias_semana = {
            "LUNES": 1, "MARTES": 2, "MIERCOLES": 3, "MIÉRCOLES": 3,
            "JUEVES": 4, "VIERNES": 5, "SÁBADO": 6, "SABADO": 6, "DOMINGO": 7
        }
        
        # Normalizar los nombres de los días a mayúsculas para la ordenación
        detalles_ordenados = []
        for detalle in self.detalles:
            jornada_normalizada = detalle.jornada.upper()
            # Asegurarse de que el día normalizado esté en el diccionario
            if jornada_normalizada not in dias_semana:
                # Si no está, intentar corregir acentos comunes
                if jornada_normalizada == "MIÉRCOLES":
                    jornada_normalizada = "MIERCOLES"
                elif jornada_normalizada == "SÁBADO":
                    jornada_normalizada = "SABADO"
            
            # Verificar que el día normalizado esté en el diccionario
            if jornada_normalizada in dias_semana:
                detalles_ordenados.append((detalle, dias_semana[jornada_normalizada]))
            else:
                # Si aún no está en el diccionario, usar el valor original
                print(f"ADVERTENCIA: Día no reconocido: {detalle.jornada}")
                detalles_ordenados.append((detalle, 99))  # Valor alto para ponerlo al final
        
        # Ordenar por el valor numérico del día
        detalles_ordenados.sort(key=lambda x: x[1])
        detalles_ordenados = [d[0] for d in detalles_ordenados]

        # Obtener abreviaturas de días
        dias = [d.jornada[:2] for d in detalles_ordenados]
        
        # Construir el rango de días
        if len(dias) > 2:
            nombre_dias = f"{dias[0]} a {dias[-1]}"
        else:
            nombre_dias = "/".join(dias)

        # Formar el nombre completo
        self.nombre = f"{self.id_turno}-{int(self._total_horas_semanales)} {nombre_dias}"

    def to_dict(self) -> dict:
        """Convierte el turno a un diccionario para su serialización."""
        return {
            "id_turno": self.id_turno,
            "nombre": self.nombre,
            "vigencia": self.vigencia,
            "frecuencia": self.frecuencia,
            "total_horas_semanales": self._total_horas_semanales,
            "detalles": [
                {
                    "id_turno_detalle_diario": d.id_turno_detalle_diario,
                    "id_turno": d.id_turno,
                    "jornada": d.jornada,
                    "hora_ingreso": d.hora_ingreso.strftime("%H:%M"),
                    "hora_salida": d.hora_salida.strftime("%H:%M") if d.hora_salida else None,
                    "duracion": d.duracion
                }
                for d in self.detalles
            ]
        }

    @staticmethod
    def from_dict(data: dict) -> 'Turno':
        """Crea una instancia de Turno desde un diccionario."""
        turno = Turno()
        turno.id_turno = data.get("id_turno")
        turno.nombre = data.get("nombre", "")
        turno.vigencia = data.get("vigencia", 1)
        turno.frecuencia = data.get("frecuencia", "Diarios")
        
        for detalle in data.get("detalles", []):
            hora_ingreso = datetime.strptime(detalle["hora_ingreso"], "%H:%M").time()
            turno.agregar_detalle(TurnoDetalleDiario(
                id_turno_detalle_diario=detalle.get("id_turno_detalle_diario"),
                id_turno=detalle.get("id_turno"),
                jornada=detalle.get("jornada"),
                hora_ingreso=hora_ingreso,
                duracion=detalle.get("duracion")
            ))
        
        return turno 