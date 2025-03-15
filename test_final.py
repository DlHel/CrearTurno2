import sys
import os
from datetime import time

# Agregar el directorio src al path para poder importar los módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from database.turno_dao import TurnoDAO
from models.turno import Turno, TurnoDetalleDiario

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
        
        # Crear un turno de prueba con los mismos detalles pero con nombres de días en formato mixto
        print("\n--- CREANDO TURNO DE PRUEBA CON FORMATO MIXTO ---")
        turno_prueba = Turno()
        turno_prueba.id_turno = None
        turno_prueba.nombre = "Turno de prueba - Lu-Ju 9:00-18:15, Vi 9:00-16:00"
        
        # Mapeo de días originales a formatos mixtos
        mapeo_dias = {
            "LUNES": "Lunes",
            "MARTES": "martes",
            "MIERCOLES": "Miércoles",
            "JUEVES": "JUEVES",
            "VIERNES": "viernes"
        }
        
        # Copiar los detalles del turno original pero con nombres de días en formato mixto
        for detalle_original in turno_original.detalles:
            jornada_mixta = mapeo_dias.get(detalle_original.jornada, detalle_original.jornada)
            
            detalle_nuevo = TurnoDetalleDiario(
                id_turno_detalle_diario=None,
                id_turno=None,
                jornada=jornada_mixta,
                hora_ingreso=detalle_original.hora_ingreso,
                duracion=detalle_original.duracion
            )
            turno_prueba.agregar_detalle(detalle_nuevo)
        
        print("Turno de prueba creado con éxito:")
        for d in turno_prueba.detalles:
            print(f"  - {d.jornada}: {d.hora_ingreso} - Duración: {d.duracion} min - Salida: {d.hora_salida}")
        
        # Buscar turnos similares para el turno de prueba
        print("\n--- BUSCANDO TURNOS SIMILARES PARA EL TURNO DE PRUEBA ---")
        similares = turno_dao.buscar_turnos_similares(turno_prueba)
        
        # Verificar resultados
        print("\n--- RESULTADOS ---")
        print(f"Turnos similares encontrados: {len(similares)}")
        
        # Verificar si el turno ID=1 está entre las coincidencias
        ids_similares = [id_turno for id_turno, _, _ in similares]
        
        print(f"¿El turno ID=1 está entre las coincidencias? {'✅ SÍ' if 1 in ids_similares else '❌ NO'}")
        
        # Mostrar detalles de las coincidencias
        if similares:
            print("\nDetalles de los turnos similares encontrados:")
            for id_turno, nombre, detalles in similares:
                print(f"  ID={id_turno}, Nombre={nombre}")
                print(f"  Detalles: {len(detalles)} días")
                for detalle in detalles:
                    print(f"    {detalle['jornada']}: {detalle['hora_ingreso']} - Salida: {detalle['hora_salida']}")
        
        print("\nPrueba completada con éxito.")
        
    except Exception as e:
        print(f"Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 