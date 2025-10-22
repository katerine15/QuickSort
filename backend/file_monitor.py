"""
Módulo para monitorear carpetas y detectar nuevos archivos
"""
import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FileEventHandler(FileSystemEventHandler):
    """Manejador de eventos del sistema de archivos"""
    
    def __init__(self, organizer, auto_organize=True):
        """
        Inicializa el manejador de eventos
        
        Args:
            organizer: Instancia de FileOrganizer
            auto_organize: Si debe organizar automáticamente
        """
        super().__init__()
        self.organizer = organizer
        self.auto_organize = auto_organize
        self.pending_files = []
        self.processing = False
    
    def on_created(self, event):
        """Se ejecuta cuando se crea un archivo"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        logger.info(f"Nuevo archivo detectado: {file_path}")
        
        # Esperar un momento para asegurar que el archivo esté completamente escrito
        time.sleep(0.5)
        
        if self.auto_organize:
            self._organize_file(file_path)
        else:
            self.pending_files.append(file_path)
    
    def on_moved(self, event):
        """Se ejecuta cuando se mueve un archivo"""
        if event.is_directory:
            return
        
        logger.info(f"Archivo movido: {event.src_path} -> {event.dest_path}")
    
    def _organize_file(self, file_path):
        """Organiza un archivo de forma segura"""
        try:
            # Verificar que el archivo existe y no está siendo usado
            if os.path.exists(file_path) and os.path.isfile(file_path):
                result = self.organizer.organize_file(file_path)
                
                if result['success']:
                    logger.info(f"Archivo organizado exitosamente: {result['filename']}")
                else:
                    logger.warning(f"No se pudo organizar: {result['filename']} - {result['error']}")
        
        except Exception as e:
            logger.error(f"Error organizando archivo {file_path}: {e}")
    
    def get_pending_files(self):
        """Obtiene la lista de archivos pendientes"""
        return self.pending_files.copy()
    
    def clear_pending_files(self):
        """Limpia la lista de archivos pendientes"""
        self.pending_files.clear()
    
    def organize_pending_files(self):
        """Organiza todos los archivos pendientes"""
        if self.processing:
            logger.warning("Ya hay una organización en proceso")
            return
        
        self.processing = True
        pending = self.pending_files.copy()
        self.pending_files.clear()
        
        for file_path in pending:
            self._organize_file(file_path)
        
        self.processing = False


class FileMonitor:
    """Monitor de carpetas para detectar nuevos archivos"""
    
    def __init__(self, organizer, watch_folder=None, auto_organize=True, recursive=False):
        """
        Inicializa el monitor de archivos
        
        Args:
            organizer: Instancia de FileOrganizer
            watch_folder: Carpeta a monitorear
            auto_organize: Si debe organizar automáticamente
            recursive: Si debe monitorear subcarpetas
        """
        self.organizer = organizer
        self.watch_folder = watch_folder
        self.auto_organize = auto_organize
        self.recursive = recursive
        
        self.observer = None
        self.event_handler = None
        self.is_running = False
        self.monitor_thread = None
    
    def start(self):
        """Inicia el monitoreo"""
        if self.is_running:
            logger.warning("El monitor ya está en ejecución")
            return False
        
        if not self.watch_folder or not os.path.exists(self.watch_folder):
            logger.error(f"Carpeta inválida: {self.watch_folder}")
            return False
        
        try:
            self.event_handler = FileEventHandler(self.organizer, self.auto_organize)
            self.observer = Observer()
            self.observer.schedule(
                self.event_handler,
                self.watch_folder,
                recursive=self.recursive
            )
            
            self.observer.start()
            self.is_running = True
            
            logger.info(f"Monitor iniciado en: {self.watch_folder}")
            logger.info(f"Auto-organizar: {self.auto_organize}, Recursivo: {self.recursive}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error iniciando monitor: {e}")
            return False
    
    def stop(self):
        """Detiene el monitoreo"""
        if not self.is_running:
            logger.warning("El monitor no está en ejecución")
            return False
        
        try:
            if self.observer:
                self.observer.stop()
                self.observer.join(timeout=5)
            
            self.is_running = False
            logger.info("Monitor detenido")
            return True
        
        except Exception as e:
            logger.error(f"Error deteniendo monitor: {e}")
            return False
    
    def set_watch_folder(self, folder_path):
        """Cambia la carpeta a monitorear"""
        was_running = self.is_running
        
        if was_running:
            self.stop()
        
        self.watch_folder = folder_path
        
        if was_running:
            self.start()
    
    def set_auto_organize(self, auto_organize):
        """Activa o desactiva la organización automática"""
        self.auto_organize = auto_organize
        if self.event_handler:
            self.event_handler.auto_organize = auto_organize
        
        logger.info(f"Auto-organizar establecido a: {auto_organize}")
    
    def get_status(self):
        """Obtiene el estado del monitor"""
        return {
            'is_running': self.is_running,
            'watch_folder': self.watch_folder,
            'auto_organize': self.auto_organize,
            'recursive': self.recursive,
            'pending_files': len(self.event_handler.pending_files) if self.event_handler else 0
        }
    
    def get_pending_files(self):
        """Obtiene archivos pendientes de organizar"""
        if self.event_handler:
            return self.event_handler.get_pending_files()
        return []
    
    def organize_pending_files(self):
        """Organiza archivos pendientes manualmente"""
        if self.event_handler:
            self.event_handler.organize_pending_files()
            return True
        return False
    
    def scan_existing_files(self):
        """Escanea archivos existentes en la carpeta monitoreada"""
        if not self.watch_folder or not os.path.exists(self.watch_folder):
            logger.error("Carpeta de monitoreo no válida")
            return []
        
        existing_files = []
        
        try:
            if self.recursive:
                for root, dirs, files in os.walk(self.watch_folder):
                    for filename in files:
                        file_path = os.path.join(root, filename)
                        existing_files.append(file_path)
            else:
                for item in os.listdir(self.watch_folder):
                    file_path = os.path.join(self.watch_folder, item)
                    if os.path.isfile(file_path):
                        existing_files.append(file_path)
            
            logger.info(f"Encontrados {len(existing_files)} archivos existentes")
        
        except Exception as e:
            logger.error(f"Error escaneando archivos existentes: {e}")
        
        return existing_files
    
    def organize_existing_files(self):
        """Organiza todos los archivos existentes en la carpeta"""
        existing_files = self.scan_existing_files()
        results = []
        
        for file_path in existing_files:
            result = self.organizer.organize_file(file_path)
            results.append(result)
        
        return {
            'total_files': len(existing_files),
            'results': results,
            'stats': self.organizer.get_stats()
        }
    
    def __del__(self):
        """Destructor para asegurar que el monitor se detenga"""
        if self.is_running:
            self.stop()
