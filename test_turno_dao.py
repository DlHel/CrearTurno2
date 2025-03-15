import sys
import os
from datetime import time

# Agregar el directorio src al path para poder importar los módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from database.turno_dao import TurnoDAO
from models.turno import Turno, TurnoDetalleDiario

def crear_turno_con_dias_minusculas():
    """Crea un turno con días en minúsculas."""
    turno = Turno()
    turno.id_turno = None
    turno.nombre = "Turno de prueba - Lu-Ju 9:00-18:15, Vi 9:00-16:00"
    
    # Agregar detalles para Lunes a Jueves (9:00 a 18:15)
    for dia in ['lunes', 'martes', 'miércoles', 'jueves']:
        detalle = TurnoDetalleDiario(
            id_turno_detalle_diario=None,
            id_turno=None,
            jornada=dia,
            hora_ingreso=time(9, 0),  # 9:00 AM
            duracion=555  # 9 horas y 15 minutos (555 minutos)
        )
        turno.agregar_detalle(detalle)
    
    # Agregar detalle para Viernes (9:00 a 16:00)
    detalle_viernes = TurnoDetalleDiario(
        id_turno_detalle_diario=None,
        id_turno=None,
        jornada='viernes',
        hora_ingreso=time(9, 0),  # 9:00 AM
        duracion=420  # 7 horas (420 minutos)
    )
    turno.agregar_detalle(detalle_viernes)
    
    return turno

def crear_turno_con_dias_mayusculas():
    """Crea un turno con días en mayúsculas."""
    turno = Turno()
    turno.id_turno = None
    turno.nombre = "Turno de prueba - Lu-Ju 9:00-18:15, Vi 9:00-16:00"
    
    # Agregar detalles para Lunes a Jueves (9:00 a 18:15)
    for dia in ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES']:
        detalle = TurnoDetalleDiario(
            id_turno_detalle_diario=None,
            id_turno=None,
            jornada=dia,
            hora_ingreso=time(9, 0),  # 9:00 AM
            duracion=555  # 9 horas y 15 minutos (555 minutos)
        )
        turno.agregar_detalle(detalle)
    
    # Agregar detalle para Viernes (9:00 a 16:00)
    detalle_viernes = TurnoDetalleDiario(
        id_turno_detalle_diario=None,
        id_turno=None,
        jornada='VIERNES',
        hora_ingreso=time(9, 0),  # 9:00 AM
        duracion=420  # 7 horas (420 minutos)
    )
    turno.agregar_detalle(detalle_viernes)
    
    return turno

def crear_turno_con_dias_mixtos():
    """Crea un turno con días en formato mixto (algunos con mayúsculas, otros con minúsculas)."""
    turno = Turno()
    turno.id_turno = None
    turno.nombre = "Turno de prueba - Lu-Ju 9:00-18:15, Vi 9:00-16:00"
    
    # Agregar detalles para Lunes a Jueves (9:00 a 18:15) con formato mixto
    dias = ['Lunes', 'MARTES', 'Miércoles', 'jueves']
    for dia in dias:
        detalle = TurnoDetalleDiario(
            id_turno_detalle_diario=None,
            id_turno=None,
            jornada=dia,
            hora_ingreso=time(9, 0),  # 9:00 AM
            duracion=555  # 9 horas y 15 minutos (555 minutos)
        )
        turno.agregar_detalle(detalle)
    
    # Agregar detalle para Viernes (9:00 a 16:00)
    detalle_viernes = TurnoDetalleDiario(
        id_turno_detalle_diario=None,
        id_turno=None,
        jornada='VIERNES',
        hora_ingreso=time(9, 0),  # 9:00 AM
        duracion=420  # 7 horas (420 minutos)
    )
    turno.agregar_detalle(detalle_viernes)
    
    return turno

def main():
    try:
        # Crear instancia de TurnoDAO
        turno_dao = TurnoDAO()
        
        # Verificar conexión a la base de datos
        print("Verificando conexión a la base de datos...")
        turno_dao._verificar_conexion()
        print("Conexión establecida correctamente")
        
        # Obtener el turno ID=1 de la base de datos
        print("\n--- OBTENIENDO TURNO ID=1 ---")
        turno_original = turno_dao.buscar_por_id(1)
        
        if not turno_original:
            print("No se encontró el turno ID=1")
            return
        
        print(f"Turno encontrado: ID={turno_original.id_turno}, Nombre={turno_original.nombre}")
        print(f"Detalles: {len(turno_original.detalles)} días")
        for d in turno_original.detalles:
            print(f"  - {d.jornada}: {d.hora_ingreso} - Duración: {d.duracion} min - Salida: {d.hora_salida}")
        
        # Crear turnos de prueba con diferentes formatos de días
        print("\n--- CREANDO TURNOS DE PRUEBA ---")
        turno_minusculas = crear_turno_con_dias_minusculas()
        turno_mayusculas = crear_turno_con_dias_mayusculas()
        turno_mixto = crear_turno_con_dias_mixtos()
        
        print("\nTurno con días en minúsculas:")
        for d in turno_minusculas.detalles:
            print(f"  - {d.jornada}: {d.hora_ingreso} - Duración: {d.duracion} min - Salida: {d.hora_salida}")
        
        print("\nTurno con días en mayúsculas:")
        for d in turno_mayusculas.detalles:
            print(f"  - {d.jornada}: {d.hora_ingreso} - Duración: {d.duracion} min - Salida: {d.hora_salida}")
        
        print("\nTurno con días en formato mixto:")
        for d in turno_mixto.detalles:
            print(f"  - {d.jornada}: {d.hora_ingreso} - Duración: {d.duracion} min - Salida: {d.hora_salida}")
        
        # Buscar turnos similares para cada formato
        print("\n--- BUSCANDO TURNOS SIMILARES PARA TURNO CON DÍAS EN MINÚSCULAS ---")
        similares_minusculas = turno_dao.buscar_turnos_similares(turno_minusculas)
        
        print("\n--- BUSCANDO TURNOS SIMILARES PARA TURNO CON DÍAS EN MAYÚSCULAS ---")
        similares_mayusculas = turno_dao.buscar_turnos_similares(turno_mayusculas)
        
        print("\n--- BUSCANDO TURNOS SIMILARES PARA TURNO CON DÍAS EN FORMATO MIXTO ---")
        similares_mixto = turno_dao.buscar_turnos_similares(turno_mixto)
        
        # Verificar resultados
        print("\n--- RESULTADOS ---")
        print(f"Turnos similares encontrados (minúsculas): {len(similares_minusculas)}")
        print(f"Turnos similares encontrados (mayúsculas): {len(similares_mayusculas)}")
        print(f"Turnos similares encontrados (mixto): {len(similares_mixto)}")
        
        # Verificar si el turno ID=1 está entre las coincidencias
        ids_minusculas = [id_turno for id_turno, _, _ in similares_minusculas]
        ids_mayusculas = [id_turno for id_turno, _, _ in similares_mayusculas]
        ids_mixto = [id_turno for id_turno, _, _ in similares_mixto]
        
        print("\nVerificando si el turno ID=1 está entre las coincidencias:")
        print(f"  - Minúsculas: {'✅ SÍ' if 1 in ids_minusculas else '❌ NO'}")
        print(f"  - Mayúsculas: {'✅ SÍ' if 1 in ids_mayusculas else '❌ NO'}")
        print(f"  - Mixto: {'✅ SÍ' if 1 in ids_mixto else '❌ NO'}")
        
        # Mostrar detalles de las coincidencias
        if 1 in ids_minusculas:
            idx = ids_minusculas.index(1)
            print("\nDetalles del turno similar encontrado (minúsculas):")
            id_turno, nombre, detalles = similares_minusculas[idx]
            print(f"  ID={id_turno}, Nombre={nombre}")
            print(f"  Detalles: {len(detalles)} días")
            for detalle in detalles:
                print(f"    {detalle['jornada']}: {detalle['hora_ingreso']} - Salida: {detalle['hora_salida']}")
        
    except Exception as e:
        print(f"Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 