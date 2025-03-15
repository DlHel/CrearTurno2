#!/usr/bin/env python
"""
Script para ejecutar todas las pruebas del proyecto.

Uso:
    python run_tests.py [opciones]

Opciones:
    --unit: Ejecutar solo pruebas unitarias
    --ui: Ejecutar solo pruebas de interfaz de usuario
    --integration: Ejecutar solo pruebas de integración
    --cov: Generar informe de cobertura
    --verbose: Mostrar información detallada
    --help: Mostrar esta ayuda
"""

import sys
import subprocess
import os

def main():
    """Función principal que ejecuta las pruebas según los argumentos proporcionados."""
    # Opciones por defecto
    args = ["pytest"]
    
    # Procesar argumentos
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return 0
    
    if "--unit" in sys.argv:
        args.append("-m unit")
    
    if "--ui" in sys.argv:
        args.append("-m ui")
    
    if "--integration" in sys.argv:
        args.append("-m integration")
    
    if "--cov" in sys.argv:
        args.append("--cov=src --cov-report=term-missing --cov-report=html")
    
    if "--verbose" in sys.argv or "-v" in sys.argv:
        args.append("-v")
    
    # Ejecutar pytest con los argumentos
    cmd = " ".join(args)
    print(f"Ejecutando: {cmd}")
    return subprocess.call(cmd, shell=True)

if __name__ == "__main__":
    sys.exit(main()) 