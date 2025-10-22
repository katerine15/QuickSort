"""
Módulo para organizar archivos según las reglas del árbol
"""
import os
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FileOrganizer:
    """Clase para organizar archivos automáticamente"""
    
    def __init__(self, tree, db_session=None):
        """
        Inicializa el organizador de archivos
        
        Args:
            tree: Instancia de FileOrganizationTree
            db_session: Sesión de base de datos (opcional)
        """
        self.tree = tree
        self.db_session = db_session
        self.stats = {
            'files_processed': 0,
            'files_moved': 0,
            'files_failed': 0,
            'errors': []
        }
    
    def organize_file(self, file_path: str, action: str = 'move') -> Dict[str, Any]:
        """
        Organiza un archivo individual
        
        Args:
            file_path: Ruta del archivo a organizar
            action: 'move' o 'copy'
        
        Returns:
            Diccionario con el resultado de la operación
        """
        result = {
            'success': False,
            'filename': os.path.basename(file_path),
            'original_path': file_path,
            'destination_path': None,
            'action': action,
            'error': None
        }
        
        try:
            # Verificar que el archivo existe
            if not os.path.isfile(file_path):
                result['error'] = 'El archivo no existe'
                logger.error(f"Archivo no encontrado: {file_path}")
                return result
            
            # Obtener información del archivo
            filename = os.path.basename(file_path)
            file_extension = os.path.splitext(filename)[1]
            
            # Buscar destino según reglas
            destination_node = self.tree.find_destination_for_file(filename, file_extension)
            
            if not destination_node:
                result['error'] = 'No se encontró una regla que coincida'
                logger.warning(f"No hay regla para: {filename}")
                self.stats['files_failed'] += 1
                return result
            
            # Construir ruta de destino
            destination_path = os.path.join(destination_node.path, filename)
            
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            # Manejar archivos duplicados
            if os.path.exists(destination_path):
                destination_path = self._handle_duplicate(destination_path)
            
            # Mover o copiar archivo
            if action == 'move':
                shutil.move(file_path, destination_path)
                logger.info(f"Archivo movido: {filename} -> {destination_path}")
            elif action == 'copy':
                shutil.copy2(file_path, destination_path)
                logger.info(f"Archivo copiado: {filename} -> {destination_path}")
            
            result['success'] = True
            result['destination_path'] = destination_path
            self.stats['files_moved'] += 1
            
            # Registrar en base de datos si está disponible
            if self.db_session:
                self._log_to_database(result)
        
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error organizando {filename}: {e}")
            self.stats['files_failed'] += 1
            self.stats['errors'].append({
                'file': filename,
                'error': str(e)
            })
        
        finally:
            self.stats['files_processed'] += 1
        
        return result
    
    def organize_folder(self, folder_path: str, recursive: bool = False, action: str = 'move') -> Dict[str, Any]:
        """
        Organiza todos los archivos en una carpeta
        
        Args:
            folder_path: Ruta de la carpeta
            recursive: Si debe procesar subcarpetas
            action: 'move' o 'copy'
        
        Returns:
            Diccionario con estadísticas de la operación
        """
        results = []
        
        try:
            if recursive:
                # Procesar recursivamente
                for root, dirs, files in os.walk(folder_path):
                    for filename in files:
                        file_path = os.path.join(root, filename)
                        result = self.organize_file(file_path, action)
                        results.append(result)
            else:
                # Solo archivos en el nivel superior
                for item in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, item)
                    if os.path.isfile(file_path):
                        result = self.organize_file(file_path, action)
                        results.append(result)
        
        except Exception as e:
            logger.error(f"Error organizando carpeta {folder_path}: {e}")
            self.stats['errors'].append({
                'folder': folder_path,
                'error': str(e)
            })
        
        return {
            'stats': self.stats,
            'results': results
        }
    
    def _handle_duplicate(self, file_path: str) -> str:
        """
        Maneja archivos duplicados agregando un número al nombre
        
        Args:
            file_path: Ruta del archivo
        
        Returns:
            Nueva ruta con nombre único
        """
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        name, extension = os.path.splitext(filename)
        
        counter = 1
        new_path = file_path
        
        while os.path.exists(new_path):
            new_filename = f"{name}_{counter}{extension}"
            new_path = os.path.join(directory, new_filename)
            counter += 1
        
        return new_path
    
    def _log_to_database(self, result: Dict[str, Any]):
        """
        Registra la operación en la base de datos
        
        Args:
            result: Resultado de la operación
        """
        try:
            from models import FileLog
            
            log_entry = FileLog(
                filename=result['filename'],
                original_path=result['original_path'],
                destination_path=result['destination_path'] or '',
                action=result['action'],
                status='success' if result['success'] else 'failed',
                error_message=result.get('error'),
                timestamp=datetime.utcnow()
            )
            
            self.db_session.add(log_entry)
            self.db_session.commit()
        
        except Exception as e:
            logger.error(f"Error guardando log en BD: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la organización"""
        return self.stats
    
    def reset_stats(self):
        """Reinicia las estadísticas"""
        self.stats = {
            'files_processed': 0,
            'files_moved': 0,
            'files_failed': 0,
            'errors': []
        }
    
    def preview_organization(self, folder_path: str, recursive: bool = False) -> Dict[str, Any]:
        """
        Previsualiza cómo se organizarían los archivos sin moverlos
        
        Args:
            folder_path: Ruta de la carpeta
            recursive: Si debe procesar subcarpetas
        
        Returns:
            Diccionario con la previsualización
        """
        preview = {
            'files': [],
            'total_files': 0,
            'files_with_rules': 0,
            'files_without_rules': 0
        }
        
        try:
            files_to_check = []
            
            if recursive:
                for root, dirs, files in os.walk(folder_path):
                    for filename in files:
                        files_to_check.append(os.path.join(root, filename))
            else:
                for item in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, item)
                    if os.path.isfile(file_path):
                        files_to_check.append(file_path)
            
            for file_path in files_to_check:
                filename = os.path.basename(file_path)
                file_extension = os.path.splitext(filename)[1]
                
                destination_node = self.tree.find_destination_for_file(filename, file_extension)
                
                file_info = {
                    'filename': filename,
                    'current_path': file_path,
                    'destination': destination_node.path if destination_node else None,
                    'has_rule': destination_node is not None
                }
                
                preview['files'].append(file_info)
                preview['total_files'] += 1
                
                if destination_node:
                    preview['files_with_rules'] += 1
                else:
                    preview['files_without_rules'] += 1
        
        except Exception as e:
            logger.error(f"Error en previsualización: {e}")
            preview['error'] = str(e)
        
        return preview
