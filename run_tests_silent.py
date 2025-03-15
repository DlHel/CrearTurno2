#!/usr/bin/env python
"""
Script para ejecutar todas las pruebas del proyecto en modo silencioso.
Registra los resultados en un archivo de log y corrige errores automáticamente.
"""

import sys
import subprocess
import os
import logging
import re
from datetime import datetime

# Configurar logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_command(command):
    """Ejecuta un comando y devuelve la salida y el código de salida."""
    logging.info(f"Ejecutando comando: {command}")
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate()
    return stdout, stderr, process.returncode

def fix_import_errors():
    """Corrige errores de importación en los archivos."""
    logging.info("Buscando y corrigiendo errores de importación...")
    
    # Lista de archivos Python en el proyecto
    python_files = []
    for root, _, files in os.walk("src"):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    
    # Patrones de importación a corregir
    patterns = [
        (r"from ui\.", r"from src.ui."),
        (r"from database\.", r"from src.database."),
        (r"from models\.", r"from src.models."),
        (r"from utils\.", r"from src.utils.")
    ]
    
    # Corregir importaciones en cada archivo
    for file_path in python_files:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        modified = False
        for pattern, replacement in patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                modified = True
        
        if modified:
            logging.info(f"Corrigiendo importaciones en {file_path}")
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)

def fix_indentation_errors():
    """Corrige errores de indentación en los archivos."""
    logging.info("Buscando y corrigiendo errores de indentación...")
    
    # Ejecutar un comando para encontrar archivos con errores de indentación
    stdout, stderr, _ = run_command("python -m pycodestyle --select=E1 src")
    
    # Analizar la salida para encontrar archivos con errores
    error_files = set()
    for line in stdout.splitlines() + stderr.splitlines():
        match = re.match(r'(.*\.py):\d+:\d+: E1', line)
        if match:
            error_files.add(match.group(1))
    
    # Corregir indentación en los archivos con errores
    for file_path in error_files:
        logging.info(f"Corrigiendo indentación en {file_path}")
        run_command(f"autopep8 --select=E1 --in-place {file_path}")

def fix_missing_method_errors():
    """Corrige errores de métodos faltantes en las clases."""
    logging.info("Buscando y corrigiendo errores de métodos faltantes...")
    
    # Buscar el archivo CrearTurnoWidget
    crear_turno_widget_path = "src/ui/crear_turno/crear_turno_widget.py"
    if os.path.exists(crear_turno_widget_path):
        with open(crear_turno_widget_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Verificar si el método actualizar_nombre_turno ya existe
        if "def actualizar_nombre_turno" not in content:
            logging.info(f"Añadiendo método 'actualizar_nombre_turno' a {crear_turno_widget_path}")
            
            # Buscar la clase CrearTurnoWidget
            class_match = re.search(r'class CrearTurnoWidget\([^)]+\):\s+', content)
            if class_match:
                # Añadir el método después de los métodos existentes
                method_to_add = """
    def actualizar_nombre_turno(self):
        \"\"\"Actualiza el nombre del turno basado en los detalles actuales.\"\"\"
        if hasattr(self, 'turno_actual') and self.turno_actual:
            self.turno_actual._actualizar_nombre()
            if self.turno_actual.nombre:
                self.nombre_turno_label.setText(f"Nombre del turno: {self.turno_actual.nombre}")
"""
                
                # Buscar un buen lugar para insertar el método (después del último método)
                last_method_match = re.search(r'    def [^(]+\([^)]*\):[^}]*?\n\n', content, re.DOTALL)
                if last_method_match:
                    insert_pos = last_method_match.end()
                    content = content[:insert_pos] + method_to_add + content[insert_pos:]
                else:
                    # Si no se encuentra un buen lugar, añadirlo al final de la clase
                    content += method_to_add
                
                # Guardar el archivo modificado
                with open(crear_turno_widget_path, 'w', encoding='utf-8') as file:
                    file.write(content)

def main():
    """Función principal que ejecuta las pruebas y corrige errores."""
    logging.info("Iniciando ejecución de pruebas y corrección de errores")
    
    # Instalar dependencias necesarias si no están instaladas
    logging.info("Verificando dependencias...")
    run_command("pip install -q pytest pytest-qt pytest-mock pytest-cov pycodestyle autopep8")
    
    # Corregir errores conocidos antes de ejecutar las pruebas
    fix_import_errors()
    fix_indentation_errors()
    fix_missing_method_errors()
    
    # Ejecutar pruebas unitarias
    logging.info("Ejecutando pruebas unitarias...")
    stdout, stderr, exit_code = run_command("python -m pytest -m unit")
    
    if exit_code != 0:
        logging.warning("Pruebas unitarias fallidas. Corrigiendo errores...")
        
        # Corregir errores comunes
        fix_import_errors()
        fix_indentation_errors()
        fix_missing_method_errors()
        
        # Volver a ejecutar pruebas unitarias
        logging.info("Volviendo a ejecutar pruebas unitarias después de correcciones...")
        stdout, stderr, exit_code = run_command("python -m pytest -m unit")
        
        if exit_code != 0:
            logging.error("Las pruebas unitarias siguen fallando después de las correcciones automáticas.")
            return exit_code
    
    # Ejecutar pruebas de interfaz de usuario
    logging.info("Ejecutando pruebas de interfaz de usuario...")
    stdout, stderr, exit_code = run_command("python -m pytest -m ui")
    
    if exit_code != 0:
        logging.warning("Pruebas de interfaz de usuario fallidas. Corrigiendo errores...")
        
        # Corregir errores específicos de UI
        fix_missing_method_errors()
        
        # Volver a ejecutar pruebas de UI
        logging.info("Volviendo a ejecutar pruebas de UI después de correcciones...")
        stdout, stderr, exit_code = run_command("python -m pytest -m ui")
        
        if exit_code != 0:
            logging.error("Las pruebas de UI siguen fallando después de las correcciones automáticas.")
            return exit_code
    
    # Ejecutar todas las pruebas con cobertura
    logging.info("Ejecutando todas las pruebas con informe de cobertura...")
    stdout, stderr, exit_code = run_command("python -m pytest --cov=src")
    
    if exit_code == 0:
        logging.info("¡Todas las pruebas pasaron exitosamente!")
    else:
        logging.error("Algunas pruebas siguen fallando después de todas las correcciones.")
    
    logging.info(f"Resultados de las pruebas guardados en {log_file}")
    print(f"Proceso completado. Resultados guardados en {log_file}")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main()) 