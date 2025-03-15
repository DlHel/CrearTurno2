import os
import sys

# Agregar el directorio raíz al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from src.database.turno_dao import TurnoDAO
    from src.models.turno import Turno, TurnoDetalleDiario
    print("Importaciones correctas")
except ImportError as e:
    print(f"Error de importación: {e}")
    sys.exit(1)

from datetime import time

def main():
    print("Iniciando prueba de conexión y búsqueda de turnos similares...")
    
    try:
        # Crear instancia del DAO
        dao = TurnoDAO()
        print("DAO creado")
        
        # Crear un turno de prueba
        turno = Turno()
        turno.id_turno = 76
        turno.nombre = "Turno de prueba"
        
        # Agregar detalles al turno
        detalle = TurnoDetalleDiario(
            id_turno_detalle_diario=1,
            id_turno=76,
            jornada='Lunes',
            hora_ingreso=time(9, 0),
            duracion=555
        )
        turno.detalles.append(detalle)
        
        print(f"Turno creado: ID={turno.id_turno}, Nombre={turno.nombre}")
        print(f"Detalles: {len(turno.detalles)} días")
        for d in turno.detalles:
            print(f"  - {d.jornada}: {d.hora_ingreso} - Duración: {d.duracion} min")
        
        # Buscar turnos similares
        print("\nBuscando turnos similares...")
        similares = dao.buscar_turnos_similares(turno)
        
        # Mostrar resultados
        print(f"\nSe encontraron {len(similares)} turnos similares:")
        for idx, (id_turno, nombre, detalles) in enumerate(similares):
            print(f"Turno similar #{idx+1}: ID={id_turno}, Nombre={nombre}")
            print(f"  Detalles: {len(detalles)} días")
            for detalle in detalles:
                print(f"    {detalle['jornada']}: {detalle['hora_ingreso']} - {detalle['hora_salida']}")
    except Exception as e:
        print(f"Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 