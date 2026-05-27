#!/usr/bin/env python3
"""
Dupon Capacity Planner - Frontend Local Launcher
Este script permite iniciar de forma simple el servidor de desarrollo de Next.js
desde la raíz del proyecto, gestionando subprocesos e interrupciones limpiamente.
"""

import os
import sys
import subprocess

def check_requirements():
    """Verifica que el entorno de Next.js esté correctamente inicializado."""
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
    node_modules_dir = os.path.join(frontend_dir, "node_modules")
    
    if not os.path.exists(frontend_dir):
        print("\033[91m[Error] No se encontró el directorio 'frontend' en la raíz.\033[0m")
        sys.exit(1)
        
    if not os.path.exists(node_modules_dir):
        print("\033[93m[Advertencia] No se detectó la carpeta 'node_modules'. Instalando dependencias de Node...\033[0m")
        try:
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
            print("\033[92m[Éxito] Dependencias de Node instaladas correctamente.\033[0m")
        except subprocess.CalledProcessError:
            print("\033[91m[Error] Falló la instalación automática con 'npm install'. Por favor, ejecútalo manualmente dentro de /frontend.\033[0m")
            sys.exit(1)

def launch():
    """Inicia el servidor Next.js en modo desarrollo."""
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
    
    print("\033[94m" + "="*70)
    print("      DUPON CAPACITY PLANNER - SERVIDOR DE DESARROLLO FRONTEND")
    print("      Iniciando Next.js Turbopack...")
    print("      Dirección local: \033[92mhttp://localhost:3000\033[94m")
    print("      Para apagar el servidor, presiona \033[93mCtrl + C\033[94m")
    print("="*70 + "\033[0m")
    
    try:
        # Iniciamos npm run dev en el directorio de frontend
        process = subprocess.Popen(["npm", "run", "dev"], cwd=frontend_dir)
        
        # Esperamos a que el proceso de Next.js termine
        process.wait()
        
    except KeyboardInterrupt:
        print("\n\n\033[93m[Info] Deteniendo servidor de desarrollo de forma segura...\033[0m")
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
        print("\033[92m[Éxito] Servidor Next.js apagado correctamente.\033[0m")
        sys.exit(0)

if __name__ == "__main__":
    check_requirements()
    launch()
