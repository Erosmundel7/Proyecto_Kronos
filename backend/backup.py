import os
import shutil
import sys
from datetime import datetime
from CTkMessagebox import CTkMessagebox

# DICCIONARIO PARA GARANTIZAR LOS NOMBRES EN ESPAÑOL
MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

def obtener_ruta_base():
    """Devuelve la carpeta raíz del proyecto (en VS Code) o la carpeta del .exe."""
    if getattr(sys, 'frozen', False):
        # Si corre como .exe, devuelve la carpeta donde está Sistema_Kronos.exe
        return os.path.dirname(sys.executable)
    else:
        # Como backup.py está dentro de /backend, subimos un nivel con dirname para llegar a la raíz
        carpeta_backend = os.path.abspath(os.path.dirname(__file__))
        return os.path.dirname(carpeta_backend)

def obtener_ruta_db():
    """Busca la base de datos en la ubicación exacta donde se encuentre."""
    base_dir = obtener_ruta_base()
    
    # 1. Ruta normal (raíz/backend/database/ProyectoKronos.db)
    ruta_1 = os.path.join(base_dir, "backend", "database", "ProyectoKronos.db")
    if os.path.exists(ruta_1):
        return ruta_1
        
    # 2. Ruta dentro de _internal (por si PyInstaller la movió ahí al compilar)
    if getattr(sys, 'frozen', False):
        ruta_2 = os.path.join(sys._MEIPASS, "backend", "database", "ProyectoKronos.db")
        if os.path.exists(ruta_2):
            return ruta_2
            
    # 3. Ruta relativa directa desde donde se esté ejecutando
    ruta_3 = os.path.abspath(os.path.join("backend", "database", "ProyectoKronos.db"))
    if os.path.exists(ruta_3):
        return ruta_3

    return ruta_1

def auto_backup_diario():
    base_dir = obtener_ruta_base()
    ruta_db_original = obtener_ruta_db()

    ahora = datetime.now()
    nombre_carpeta_mes = f"{MESES_ES[ahora.month]} {ahora.year}"
    
    ruta_destino = os.path.join(base_dir, "Backups_Kronos", nombre_carpeta_mes)
    os.makedirs(ruta_destino, exist_ok=True)
        
    fecha_hoy = ahora.strftime("%Y-%m-%d")
    ruta_backup = os.path.join(ruta_destino, f"Backup_{fecha_hoy}.db")
    
    if os.path.exists(ruta_db_original):
        if not os.path.exists(ruta_backup):
            try:
                shutil.copy2(ruta_db_original, ruta_backup)
            except Exception as e:
                CTkMessagebox(title="Atención", 
                              message=f"Copia de seguridad incompleta.\nPor favor, revise el sistema.\nError: {e}", 
                              icon="warning")

def backup_cierre_caja():
    try:
        base_dir = obtener_ruta_base()
        ruta_db_original = obtener_ruta_db()
        
        ahora = datetime.now()
        nombre_carpeta_mes = f"{MESES_ES[ahora.month]} {ahora.year}"
        ruta_destino = os.path.join(base_dir, "Backups_Kronos", nombre_carpeta_mes)
        
        os.makedirs(ruta_destino, exist_ok=True)
            
        fecha_hora = ahora.strftime("%Y-%m-%d_%H-%M-%S")
        ruta_backup = os.path.join(ruta_destino, f"Backup_Cierre_{fecha_hora}.db")
        
        if os.path.exists(ruta_db_original):
            shutil.copy2(ruta_db_original, ruta_backup)
        else:
            raise FileNotFoundError(f"No se encontró la base de datos en: {ruta_db_original}")
            
    except Exception as e:
        CTkMessagebox(title="Alerta de Backup", 
                      message=f"No se pudo guardar el backup de cierre.\nError: {e}", 
                      icon="warning")