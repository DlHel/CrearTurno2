import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.abspath('.'))

print("Importando módulos...")
try:
    import cx_Oracle
    print("cx_Oracle importado correctamente")
except ImportError as e:
    print(f"Error al importar cx_Oracle: {e}")
    sys.exit(1)

print("Intentando conectar a Oracle...")
try:
    # Datos de conexión
    host = "orauchp-cluster-scan.uchile.cl"
    port = 1525
    service_name = "uchdb_prod.uchile.cl"
    username = "USR_MANTENCION"
    password = "tiMfiayGvJOvvlo"
    
    # Crear DSN
    dsn = cx_Oracle.makedsn(
        host,
        port,
        service_name=service_name
    )
    
    print(f"DSN creado: {dsn}")
    
    # Intentar conectar
    print("Intentando establecer conexión...")
    connection = cx_Oracle.connect(
        user=username,
        password=password,
        dsn=dsn
    )
    
    print("Conexión establecida correctamente")
    
    # Ejecutar una consulta simple
    print("Ejecutando consulta de prueba...")
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM ASISTENCIAS.TURNO")
    result = cursor.fetchone()
    print(f"Número de turnos en la base de datos: {result[0]}")
    
    # Cerrar cursor y conexión
    cursor.close()
    connection.close()
    print("Conexión cerrada correctamente")
    
except Exception as e:
    print(f"Error durante la conexión: {e}")
    import traceback
    traceback.print_exc() 