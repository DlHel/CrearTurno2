import pytest
from datetime import time
from src.models.turno import Turno, TurnoDetalleDiario

@pytest.mark.unit
class TestTurnoDetalleDiario:
    """Pruebas para la clase TurnoDetalleDiario."""
    
    def test_calcular_hora_salida(self):
        """Prueba que la hora de salida se calcule correctamente."""
        # Caso 1: Hora de ingreso 08:00, duración 480 minutos (8 horas)
        detalle = TurnoDetalleDiario(
            id_turno_detalle_diario=1,
            id_turno=1,
            jornada="Lunes",
            hora_ingreso=time(8, 0),
            duracion=480
        )
        detalle.calcular_hora_salida()
        assert detalle.hora_salida == time(16, 0)
        
        # Caso 2: Hora de ingreso 22:00, duración 480 minutos (8 horas) - cruza medianoche
        detalle = TurnoDetalleDiario(
            id_turno_detalle_diario=2,
            id_turno=1,
            jornada="Martes",
            hora_ingreso=time(22, 0),
            duracion=480
        )
        detalle.calcular_hora_salida()
        assert detalle.hora_salida == time(6, 0)
        
        # Caso 3: Hora de ingreso 14:30, duración 270 minutos (4.5 horas)
        detalle = TurnoDetalleDiario(
            id_turno_detalle_diario=3,
            id_turno=1,
            jornada="Miércoles",
            hora_ingreso=time(14, 30),
            duracion=270
        )
        detalle.calcular_hora_salida()
        assert detalle.hora_salida == time(19, 0)

@pytest.mark.unit
class TestTurno:
    """Pruebas para la clase Turno."""
    
    @pytest.fixture
    def turno_vacio(self):
        """Fixture que devuelve un turno vacío."""
        return Turno()
    
    @pytest.fixture
    def detalle_lunes(self):
        """Fixture que devuelve un detalle para el lunes."""
        return TurnoDetalleDiario(
            id_turno_detalle_diario=1,
            id_turno=1,
            jornada="Lunes",
            hora_ingreso=time(8, 0),
            duracion=480
        )
    
    @pytest.fixture
    def detalle_martes(self):
        """Fixture que devuelve un detalle para el martes."""
        return TurnoDetalleDiario(
            id_turno_detalle_diario=2,
            id_turno=1,
            jornada="Martes",
            hora_ingreso=time(8, 0),
            duracion=480
        )
    
    @pytest.fixture
    def detalle_viernes(self):
        """Fixture que devuelve un detalle para el viernes."""
        return TurnoDetalleDiario(
            id_turno_detalle_diario=3,
            id_turno=1,
            jornada="Viernes",
            hora_ingreso=time(8, 0),
            duracion=480
        )
    
    def test_agregar_detalle(self, turno_vacio, detalle_lunes, detalle_martes):
        """Prueba que se puedan agregar detalles correctamente."""
        # Agregar primer detalle
        assert turno_vacio.agregar_detalle(detalle_lunes) == True
        assert len(turno_vacio.detalles) == 1
        
        # Agregar segundo detalle
        assert turno_vacio.agregar_detalle(detalle_martes) == True
        assert len(turno_vacio.detalles) == 2
        
        # Intentar agregar un detalle duplicado (mismo día)
        detalle_duplicado = TurnoDetalleDiario(
            id_turno_detalle_diario=4,
            id_turno=1,
            jornada="Lunes",
            hora_ingreso=time(9, 0),
            duracion=480
        )
        assert turno_vacio.agregar_detalle(detalle_duplicado) == False
        assert len(turno_vacio.detalles) == 2
    
    def test_actualizar_total_horas(self, turno_vacio, detalle_lunes, detalle_martes):
        """Prueba que el total de horas se actualice correctamente."""
        # Turno vacío debe tener 0 horas
        assert turno_vacio._total_horas_semanales == 0.0
        
        # Agregar un detalle de 8 horas (480 minutos)
        turno_vacio.agregar_detalle(detalle_lunes)
        assert turno_vacio._total_horas_semanales == 8.0
        
        # Agregar otro detalle de 8 horas
        turno_vacio.agregar_detalle(detalle_martes)
        assert turno_vacio._total_horas_semanales == 16.0
    
    def test_actualizar_nombre(self, turno_vacio, detalle_lunes, detalle_martes, detalle_viernes):
        """Prueba que el nombre del turno se actualice correctamente."""
        # Establecer ID del turno
        turno_vacio.id_turno = 123
        
        # Agregar un solo detalle
        turno_vacio.agregar_detalle(detalle_lunes)
        assert turno_vacio.nombre == "123-8 Lu"
        
        # Agregar un segundo detalle no consecutivo
        turno_vacio.agregar_detalle(detalle_viernes)
        assert turno_vacio.nombre == "123-16 Lu/Vi"
        
        # Agregar un detalle intermedio para formar un rango
        turno_vacio.agregar_detalle(detalle_martes)
        assert turno_vacio.nombre == "123-24 Lu a Vi"
    
    def test_to_dict(self, turno_vacio, detalle_lunes):
        """Prueba que el método to_dict funcione correctamente."""
        # Configurar el turno
        turno_vacio.id_turno = 123
        turno_vacio.agregar_detalle(detalle_lunes)
        
        # Convertir a diccionario
        turno_dict = turno_vacio.to_dict()
        
        # Verificar los datos del turno
        assert turno_dict["id_turno"] == 123
        assert turno_dict["nombre"] == "123-8 Lu"
        assert turno_dict["vigencia"] == 1
        assert turno_dict["frecuencia"] == "Diarios"
        assert turno_dict["total_horas_semanales"] == 8.0
        
        # Verificar los detalles
        assert len(turno_dict["detalles"]) == 1
        detalle_dict = turno_dict["detalles"][0]
        assert detalle_dict["id_turno_detalle_diario"] == 1
        assert detalle_dict["id_turno"] == 1
        assert detalle_dict["jornada"] == "Lunes"
        assert detalle_dict["hora_ingreso"] == "08:00"
        assert detalle_dict["hora_salida"] == "16:00"
        assert detalle_dict["duracion"] == 480
    
    def test_from_dict(self):
        """Prueba que el método from_dict funcione correctamente."""
        # Crear un diccionario de turno
        turno_dict = {
            "id_turno": 123,
            "nombre": "Turno de prueba",
            "vigencia": 1,
            "frecuencia": "Diarios",
            "detalles": [
                {
                    "id_turno_detalle_diario": 1,
                    "id_turno": 123,
                    "jornada": "Lunes",
                    "hora_ingreso": "08:00",
                    "duracion": 480
                },
                {
                    "id_turno_detalle_diario": 2,
                    "id_turno": 123,
                    "jornada": "Martes",
                    "hora_ingreso": "09:00",
                    "duracion": 420
                }
            ]
        }
        
        # Crear turno desde diccionario
        turno = Turno.from_dict(turno_dict)
        
        # Verificar los datos del turno
        assert turno.id_turno == 123
        assert turno.vigencia == 1
        assert turno.frecuencia == "Diarios"
        
        # Verificar que se hayan creado los detalles
        assert len(turno.detalles) == 2
        
        # Verificar el primer detalle
        assert turno.detalles[0].jornada == "Lunes"
        assert turno.detalles[0].hora_ingreso == time(8, 0)
        assert turno.detalles[0].duracion == 480
        assert turno.detalles[0].hora_salida == time(16, 0)
        
        # Verificar el segundo detalle
        assert turno.detalles[1].jornada == "Martes"
        assert turno.detalles[1].hora_ingreso == time(9, 0)
        assert turno.detalles[1].duracion == 420
        assert turno.detalles[1].hora_salida == time(16, 0) 