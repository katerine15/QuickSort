import os
from pathlib import Path

# Configuración base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = os.path.join(BASE_DIR, 'backend', 'database.db')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Crear directorio de logs si no existe
os.makedirs(LOGS_DIR, exist_ok=True)

# Configuración de Flask
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-quicksort-2024'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
# Configuración de monitoreo
    DEFAULT_WATCH_FOLDER = os.path.expanduser('~')
    
    MONITOR_INTERVAL = 1  # segundos
    
    # Configuración de organización
    MAX_DEPTH = 10  # Profundidad máxima del árbol
    ENABLE_AUTO_ORGANIZE = True
