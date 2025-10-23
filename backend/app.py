"""
Aplicación Flask principal - API REST para QuickSort
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, TreeNode, OrganizationRule, FileLog, MonitorConfig
from tree_structure import FileOrganizationTree
from file_organizer import FileOrganizer
from file_monitor import FileMonitor
from config import Config
import os
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Inicializar base de datos
db.init_app(app)

# Variables globales
file_tree = None
file_organizer = None
file_monitor = None


def init_database():
    """Inicializa la base de datos"""
    with app.app_context():
        db.create_all()
        logger.info("Base de datos inicializada")
        
        # Crear configuración de monitor por defecto si no existe
        monitor_config = MonitorConfig.query.first()
        if not monitor_config:
            monitor_config = MonitorConfig(
                watch_folder=Config.DEFAULT_WATCH_FOLDER,
                is_active=False,
                auto_organize=True,
                recursive=False
            )
            db.session.add(monitor_config)
            db.session.commit()
            logger.info("Configuración de monitor creada")


def init_tree():
    """Inicializa el árbol de organización"""
    global file_tree, file_organizer, file_monitor
    
    # Crear árbol desde la base de datos
    root_path = os.path.join(Config.DEFAULT_WATCH_FOLDER, 'Organized')
    file_tree = FileOrganizationTree(root_path)
    
    # Cargar nodos desde la base de datos
    with app.app_context():
        nodes = TreeNode.query.order_by(TreeNode.id).all()
        for node in nodes:
            # Reconstruir árbol desde BD
            if node.parent_id is None:
                # Es un nodo raíz, ya está en file_tree.root
                continue
            else:
                # Agregar nodo al árbol
                parent = TreeNode.query.get(node.parent_id)
                if parent:
                    file_tree.add_node(parent.path, node.name, node.path, node.node_type)
    
    # Inicializar organizador con sesión de BD
    file_organizer = FileOrganizer(file_tree, db.session)
    
    # Inicializar monitor
    monitor_config = MonitorConfig.query.first()
    if monitor_config:
        file_monitor = FileMonitor(
            file_organizer,
            watch_folder=monitor_config.watch_folder,
            auto_organize=monitor_config.auto_organize,
            recursive=monitor_config.recursive
        )
        
        # Auto-iniciar el monitor si estaba activo
        if monitor_config.is_active:
            logger.info("Monitor estaba activo, reiniciando automáticamente...")
            if file_monitor.start():
                logger.info("Monitor reiniciado exitosamente")
            else:
                logger.error("Error al reiniciar el monitor")
                # Actualizar estado en BD si falla
                monitor_config.is_active = False
                db.session.commit()
    
    logger.info("Árbol de organización inicializado")


# ==================== RUTAS DE LA API ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verifica el estado de la API"""
    return jsonify({
        'status': 'ok',
        'message': 'QuickSort API is running'
    }), 200


# ==================== RUTAS DEL ÁRBOL ====================

@app.route('/api/tree', methods=['GET'])
def get_tree():
    """Obtiene la estructura completa del árbol"""
    try:
        if file_tree:
            return jsonify({
                'success': True,
                'tree': file_tree.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Árbol no inicializado'
            }), 500
    except Exception as e:
        logger.error(f"Error obteniendo árbol: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/tree/nodes', methods=['GET'])
def get_all_nodes():
    """Obtiene todos los nodos del árbol"""
    try:
        nodes = TreeNode.query.all()
        return jsonify({
            'success': True,
            'nodes': [node.to_dict() for node in nodes]
        }), 200
    except Exception as e:
        logger.error(f"Error obteniendo nodos: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/tree/nodes', methods=['POST'])
def create_node():
    """Crea un nuevo nodo en el árbol"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data.get('name'):
            return jsonify({
                'success': False,
                'message': 'El nombre del nodo es requerido'
            }), 400
        
        if not data.get('path'):
            return jsonify({
                'success': False,
                'message': 'La ruta del nodo es requerida'
            }), 400
        
        # Crear el nodo en la base de datos
        new_node = TreeNode(
            name=data['name'],
            path=data['path'],
            parent_id=data.get('parent_id'),
            node_type=data.get('node_type', 'folder')
        )
        
        db.session.add(new_node)
        db.session.commit()
        
        # Crear la carpeta física si no existe
        try:
            os.makedirs(data['path'], exist_ok=True)
            logger.info(f"Carpeta creada: {data['path']}")
        except Exception as folder_error:
            logger.warning(f"No se pudo crear la carpeta física: {folder_error}")
        
        # Actualizar árbol en memoria
        if file_tree and data.get('parent_id'):
            parent = TreeNode.query.get(data['parent_id'])
            if parent:
                file_tree.add_node(parent.path, data['name'], data['path'], data.get('node_type', 'folder'))
        
        logger.info(f"Nodo creado: {new_node.name} (ID: {new_node.id})")
        
        return jsonify({
            'success': True,
            'node': new_node.to_dict(),
            'message': 'Nodo creado exitosamente'
        }), 201
    
    except KeyError as e:
        logger.error(f"Campo faltante: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Campo requerido faltante: {str(e)}'
        }), 400
    
    except Exception as e:
        logger.error(f"Error creando nodo: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }), 500


@app.route('/api/tree/nodes/<int:node_id>', methods=['DELETE'])
def delete_node(node_id):
    """Elimina un nodo del árbol"""
    try:
        node = TreeNode.query.get(node_id)
        if not node:
            return jsonify({
                'success': False,
                'message': 'Nodo no encontrado'
            }), 404
        
        db.session.delete(node)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Nodo eliminado'
        }), 200
    
    except Exception as e:
        logger.error(f"Error eliminando nodo: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== RUTAS DE REGLAS ====================

@app.route('/api/rules', methods=['GET'])
def get_rules():
    """Obtiene todas las reglas de organización"""
    try:
        rules = OrganizationRule.query.all()
        return jsonify({
            'success': True,
            'rules': [rule.to_dict() for rule in rules]
        }), 200
    except Exception as e:
        logger.error(f"Error obteniendo reglas: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/rules', methods=['POST'])
def create_rule():
    """Crea una nueva regla de organización"""
    try:
        data = request.get_json()
        
        new_rule = OrganizationRule(
            node_id=data['node_id'],
            rule_type=data['rule_type'],
            pattern=data['pattern'],
            priority=data.get('priority', 0),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(new_rule)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'rule': new_rule.to_dict()
        }), 201
    
    except Exception as e:
        logger.error(f"Error creando regla: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/rules/<int:rule_id>', methods=['PUT'])
def update_rule(rule_id):
    """Actualiza una regla existente"""
    try:
        rule = OrganizationRule.query.get(rule_id)
        if not rule:
            return jsonify({
                'success': False,
                'message': 'Regla no encontrada'
            }), 404
        
        data = request.get_json()
        
        if 'pattern' in data:
            rule.pattern = data['pattern']
        if 'priority' in data:
            rule.priority = data['priority']
        if 'is_active' in data:
            rule.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'rule': rule.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Error actualizando regla: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/rules/<int:rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    """Elimina una regla"""
    try:
        rule = OrganizationRule.query.get(rule_id)
        if not rule:
            return jsonify({
                'success': False,
                'message': 'Regla no encontrada'
            }), 404
        
        db.session.delete(rule)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Regla eliminada'
        }), 200
    
    except Exception as e:
        logger.error(f"Error eliminando regla: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== RUTAS DEL MONITOR ====================

@app.route('/api/monitor/status', methods=['GET'])
def get_monitor_status():
    """Obtiene el estado del monitor"""
    try:
        if file_monitor:
            status = file_monitor.get_status()
            return jsonify({
                'success': True,
                'status': status
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Monitor no inicializado'
            }), 500
    except Exception as e:
        logger.error(f"Error obteniendo estado del monitor: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/monitor/start', methods=['POST'])
def start_monitor():
    """Inicia el monitoreo de archivos"""
    try:
        if not file_monitor:
            return jsonify({
                'success': False,
                'message': 'Monitor no inicializado'
            }), 500
        
        success = file_monitor.start()
        
        if success:
            # Actualizar configuración en BD
            monitor_config = MonitorConfig.query.first()
            if monitor_config:
                monitor_config.is_active = True
                db.session.commit()
        
        return jsonify({
            'success': success,
            'message': 'Monitor iniciado' if success else 'Error iniciando monitor'
        }), 200 if success else 500
    
    except Exception as e:
        logger.error(f"Error iniciando monitor: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/monitor/stop', methods=['POST'])
def stop_monitor():
    """Detiene el monitoreo de archivos"""
    try:
        if not file_monitor:
            return jsonify({
                'success': False,
                'message': 'Monitor no inicializado'
            }), 500
        
        success = file_monitor.stop()
        
        if success:
            # Actualizar configuración en BD
            monitor_config = MonitorConfig.query.first()
            if monitor_config:
                monitor_config.is_active = False
                db.session.commit()
        
        return jsonify({
            'success': success,
            'message': 'Monitor detenido' if success else 'Error deteniendo monitor'
        }), 200 if success else 500
    
    except Exception as e:
        logger.error(f"Error deteniendo monitor: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/monitor/config', methods=['GET'])
def get_monitor_config():
    """Obtiene la configuración del monitor"""
    try:
        config = MonitorConfig.query.first()
        if config:
            return jsonify({
                'success': True,
                'config': config.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Configuración no encontrada'
            }), 404
    except Exception as e:
        logger.error(f"Error obteniendo configuración: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/monitor/config', methods=['PUT'])
def update_monitor_config():
    """Actualiza la configuración del monitor"""
    try:
        config = MonitorConfig.query.first()
        if not config:
            return jsonify({
                'success': False,
                'message': 'Configuración no encontrada'
            }), 404
        
        data = request.get_json()
        was_running = file_monitor.is_running if file_monitor else False
        
        if 'watch_folder' in data:
            config.watch_folder = data['watch_folder']
            if file_monitor:
                file_monitor.set_watch_folder(data['watch_folder'])
        
        if 'auto_organize' in data:
            config.auto_organize = data['auto_organize']
            if file_monitor:
                file_monitor.set_auto_organize(data['auto_organize'])
        
        if 'recursive' in data:
            config.recursive = data['recursive']
            if file_monitor:
                # Si el monitor está corriendo y cambia recursive, reiniciar
                if was_running:
                    file_monitor.stop()
                file_monitor.recursive = data['recursive']
                if was_running:
                    file_monitor.start()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'config': config.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Error actualizando configuración: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/monitor/files', methods=['GET'])
def get_monitor_files():
    """Obtiene la lista de archivos en la carpeta monitoreada"""
    try:
        if not file_monitor:
            return jsonify({
                'success': False,
                'message': 'Monitor no inicializado'
            }), 500
        
        files = file_monitor.scan_existing_files()
        
        # Obtener información adicional de cada archivo
        files_info = []
        for file_path in files:
            try:
                filename = os.path.basename(file_path)
                file_extension = os.path.splitext(filename)[1]
                file_size = os.path.getsize(file_path)
                
                # Buscar destino según reglas
                destination_node = file_tree.find_destination_for_file(filename, file_extension)
                
                files_info.append({
                    'path': file_path,
                    'filename': filename,
                    'extension': file_extension,
                    'size': file_size,
                    'destination': destination_node.path if destination_node else None,
                    'destination_name': destination_node.name if destination_node else None,
                    'has_rule': destination_node is not None
                })
            except Exception as e:
                logger.error(f"Error procesando archivo {file_path}: {e}")
        
        return jsonify({
            'success': True,
            'files': files_info,
            'total': len(files_info),
            'with_rules': sum(1 for f in files_info if f['has_rule']),
            'without_rules': sum(1 for f in files_info if not f['has_rule'])
        }), 200
    
    except Exception as e:
        logger.error(f"Error obteniendo archivos del monitor: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/monitor/organize-all', methods=['POST'])
def organize_all_files():
    """Organiza todos los archivos existentes en la carpeta monitoreada"""
    try:
        if not file_monitor:
            return jsonify({
                'success': False,
                'message': 'Monitor no inicializado'
            }), 500
        
        result = file_monitor.organize_existing_files()
        
        return jsonify({
            'success': True,
            'result': result
        }), 200
    
    except Exception as e:
        logger.error(f"Error organizando archivos: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== RUTAS DE ORGANIZACIÓN ====================

@app.route('/api/organize/file', methods=['POST'])
def organize_single_file():
    """Organiza un archivo individual"""
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        
        if not file_path:
            return jsonify({
                'success': False,
                'message': 'file_path es requerido'
            }), 400
        
        result = file_organizer.organize_file(file_path)
        
        return jsonify({
            'success': result['success'],
            'result': result
        }), 200 if result['success'] else 400
    
    except Exception as e:
        logger.error(f"Error organizando archivo: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/organize/folder', methods=['POST'])
def organize_folder():
    """Organiza todos los archivos en una carpeta"""
    try:
        data = request.get_json()
        folder_path = data.get('folder_path')
        recursive = data.get('recursive', False)
        
        if not folder_path:
            return jsonify({
                'success': False,
                'message': 'folder_path es requerido'
            }), 400
        
        result = file_organizer.organize_folder(folder_path, recursive)
        
        return jsonify({
            'success': True,
            'result': result
        }), 200
    
    except Exception as e:
        logger.error(f"Error organizando carpeta: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/organize/preview', methods=['POST'])
def preview_organization():
    """Previsualiza cómo se organizarían los archivos"""
    try:
        data = request.get_json()
        folder_path = data.get('folder_path')
        recursive = data.get('recursive', False)
        
        if not folder_path:
            return jsonify({
                'success': False,
                'message': 'folder_path es requerido'
            }), 400
        
        preview = file_organizer.preview_organization(folder_path, recursive)
        
        return jsonify({
            'success': True,
            'preview': preview
        }), 200
    
    except Exception as e:
        logger.error(f"Error en previsualización: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== RUTAS DE LOGS ====================

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Obtiene el historial de logs"""
    try:
        limit = request.args.get('limit', 100, type=int)
        logs = FileLog.query.order_by(FileLog.timestamp.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'logs': [log.to_dict() for log in logs]
        }), 200
    
    except Exception as e:
        logger.error(f"Error obteniendo logs: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/logs/stats', methods=['GET'])
def get_log_stats():
    """Obtiene estadísticas de los logs"""
    try:
        total_logs = FileLog.query.count()
        success_logs = FileLog.query.filter_by(status='success').count()
        failed_logs = FileLog.query.filter_by(status='failed').count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total_logs,
                'success': success_logs,
                'failed': failed_logs
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== INICIALIZACIÓN ====================

if __name__ == '__main__':
    with app.app_context():
        init_database()
        init_tree()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
