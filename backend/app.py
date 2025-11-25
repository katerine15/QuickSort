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
from lista import listaDobleEnlace
from listStructure import Tree as BSTree, Node as BSNode
from graphStructure import connect_project_folders, compute_keyword_relations

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


def _build_linked_list(iterable):
    """Crea una lista doblemente enlazada desde un iterable."""
    ll = listaDobleEnlace()
    for item in iterable:
        ll.insertar_final(item)
    return ll


def _linked_list_to_pylist(linked):
    """Convierte una lista doblemente enlazada en lista Python."""
    result = []
    current = linked.inicio
    while current:
        result.append(current.dato)
        current = current.siguiente
    return result


def _build_bst(iterable, key=lambda x: x.id):
    """
    Crea un árbol binario de búsqueda (usando listStructure.Tree) a partir de un iterable.
    Almacena tuplas (clave, objeto) para hacer comparaciones seguras.
    """
    tree = BSTree()
    for item in iterable:
        k = key(item)
        tree.insert((k, item))
    return tree


def _bst_inorder_to_list(tree):
    """
    Convierte el BST en lista Python en orden ascendente de clave.
    """
    result = []

    def _inorder(node):
        if not node:
            return
        _inorder(node.left)
        # node.value es una tupla (clave, objeto)
        result.append(node.value[1])
        _inorder(node.right)

    _inorder(tree.root)
    return result


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
    root_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'Organized')
    file_tree = FileOrganizationTree(root_path)

    # Cargar nodos y reglas desde la base de datos
    with app.app_context():
        nodes = TreeNode.query.order_by(TreeNode.id).all()
        rules = OrganizationRule.query.all()

        logger.info(f"Cargando {len(nodes)} nodos y {len(rules)} reglas desde la base de datos")

        # Crear un diccionario para mapear reglas por node_id
        rules_by_node = {}
        for rule in rules:
            if rule.node_id not in rules_by_node:
                rules_by_node[rule.node_id] = []
            rules_by_node[rule.node_id].append(rule)

        # Crear un diccionario para mapear nodos por ID para búsqueda rápida
        nodes_by_id = {node.id: node for node in nodes}
        
        # Función recursiva para agregar nodos y sus hijos
        def add_node_recursive(node_db, parent_tree_node=None):
            """Agrega un nodo y sus hijos recursivamente al árbol"""
            if parent_tree_node is None:
                # Es el nodo raíz, usar file_tree.root
                tree_node = file_tree.root
                logger.info(f"Procesando nodo raíz con {len(node_db.rules.all())} reglas")
            else:
                # Crear nuevo nodo en el árbol
                tree_node = file_tree.add_node(
                    parent_tree_node.path,
                    node_db.name,
                    node_db.path,
                    node_db.node_type
                )
                if tree_node:
                    logger.info(f"Nodo agregado al árbol: {node_db.name} (path: {node_db.path})")
                else:
                    logger.warning(f"No se pudo agregar nodo {node_db.name} al árbol")
                    return
            
            # Cargar reglas para este nodo
            if node_db.id in rules_by_node:
                for rule in rules_by_node[node_db.id]:
                    tree_node.add_rule(
                        rule_type=rule.rule_type,
                        pattern=rule.pattern,
                        priority=rule.priority
                    )
                logger.info(f"  → {len(rules_by_node[node_db.id])} reglas cargadas para {node_db.name}")
            
            # Procesar hijos
            children = [n for n in nodes if n.parent_id == node_db.id]
            for child in children:
                add_node_recursive(child, tree_node)
        
        # Encontrar nodos raíz (sin parent_id) y procesarlos
        root_nodes = [n for n in nodes if n.parent_id is None]
        
        if root_nodes:
            # Si hay nodos raíz en la BD, procesarlos
            for root_node in root_nodes:
                add_node_recursive(root_node, None)
        
        logger.info(f"Árbol inicializado con {len(file_tree.get_all_nodes())} nodos en memoria")
    
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
        nodes_query = TreeNode.query.all()
        nodes_bst = _build_bst(nodes_query, key=lambda n: n.id or 0)
        nodes = _bst_inorder_to_list(nodes_bst)
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
        graph_result = None
        
        # Validar datos requeridos
        if not data.get('name'):
            return jsonify({
                'success': False,
                'message': 'El nombre del nodo es requerido'
            }), 400
        
        # Construir la ruta automáticamente basándose en el padre
        parent_id = data.get('parent_id')
        node_path = None
        
        if parent_id:
            # Si tiene padre, construir ruta dentro del padre
            parent = TreeNode.query.get(parent_id)
            if not parent:
                return jsonify({
                    'success': False,
                    'message': f'Nodo padre con ID {parent_id} no encontrado'
                }), 404
            
            # Construir ruta: ruta_padre/nombre_hijo
            node_path = os.path.join(parent.path, data['name'])
            logger.info(f"Construyendo ruta de hijo: {node_path} (padre: {parent.path})")
        else:
            # Si no tiene padre, usar la ruta proporcionada o construir una por defecto
            if data.get('path'):
                node_path = data['path']
            else:
                # Ruta por defecto basada en la carpeta de organización
                root_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'Organized')
                node_path = os.path.join(root_path, data['name'])
            logger.info(f"Construyendo ruta de nodo raíz: {node_path}")
        
        # Verificar que no exista ya un nodo con esa ruta
        existing_node = TreeNode.query.filter_by(path=node_path).first()
        if existing_node:
            return jsonify({
                'success': False,
                'message': f'Ya existe un nodo con la ruta: {node_path}'
            }), 400
        
        # Crear el nodo en la base de datos
        new_node = TreeNode(
            name=data['name'],
            path=node_path,
            parent_id=parent_id,
            node_type=data.get('node_type', 'folder')
        )
        
        db.session.add(new_node)
        db.session.commit()
        
        # Crear la carpeta física si no existe
        try:
            os.makedirs(node_path, exist_ok=True)
            logger.info(f"Carpeta física creada: {node_path}")
        except Exception as folder_error:
            logger.warning(f"No se pudo crear la carpeta física: {folder_error}")
        
        # Actualizar árbol en memoria
        if file_tree:
            if parent_id:
                parent = TreeNode.query.get(parent_id)
                if parent:
                    file_tree.add_node(parent.path, data['name'], node_path, data.get('node_type', 'folder'))
                    logger.info(f"Nodo agregado al árbol en memoria como hijo de {parent.name}")
            else:
                # Si es nodo raíz, agregarlo directamente
                logger.info(f"Nodo raíz agregado al árbol en memoria")
        
        logger.info(f"Nodo creado exitosamente: {new_node.name} (ID: {new_node.id}, Ruta: {node_path})")

        # Analizar relaciones por grafos para sugerir copia/backup usando palabras clave de la nueva carpeta
        try:
            graph_base_path = data.get('graph_base_path') or (os.path.dirname(node_path) if os.path.isdir(os.path.dirname(node_path)) else node_path)
            graph_result = connect_project_folders(
                base_path=graph_base_path,
                current_folder=node_path,
                backup_dir=data.get('graph_backup_dir'),
                copy_on_confirm=False,
                create_backup=data.get('graph_create_backup', False)
            )
        except Exception as graph_error:
            logger.warning(f"No se pudo analizar relaciones de grafos para {node_path}: {graph_error}")
            graph_result = None
        
        return jsonify({
            'success': True,
            'node': new_node.to_dict(include_children=False),
            'graph': graph_result,
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


@app.route('/api/tree/nodes/<int:node_id>', methods=['PUT'])
def update_node(node_id):
    """Actualiza un nodo del árbol"""
    try:
        node = TreeNode.query.get(node_id)
        if not node:
            return jsonify({
                'success': False,
                'message': 'Nodo no encontrado'
            }), 404

        data = request.get_json()
        old_path = node.path

        if 'name' in data:
            node.name = data['name']
        if 'path' in data:
            node.path = data['path']
        if 'parent_id' in data:
            node.parent_id = data['parent_id']
        if 'node_type' in data:
            node.node_type = data['node_type']

        db.session.commit()

        # Actualizar árbol en memoria
        if file_tree:
            # Buscar el nodo en el árbol y actualizarlo
            tree_node = file_tree.find_node_by_path(old_path)
            if tree_node:
                if 'name' in data:
                    tree_node.name = data['name']
                if 'path' in data:
                    tree_node.path = data['path']
                if 'node_type' in data:
                    tree_node.node_type = data['node_type']

        return jsonify({
            'success': True,
            'node': node.to_dict(),
            'message': 'Nodo actualizado'
        }), 200

    except Exception as e:
        logger.error(f"Error actualizando nodo: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
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

        def delete_subtree(n):
            # Eliminar hijos recursivamente para evitar restricciones de FK
            for child in n.children.all():
                print(child)
                delete_subtree(child)
            db.session.delete(n)

        delete_subtree(node)
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
        rules_query = OrganizationRule.query.all()
        rules_bst = _build_bst(rules_query, key=lambda r: r.id or 0)
        rules = _bst_inorder_to_list(rules_bst)
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
        
        # Normalizar el patrón si es una regla de extensión
        pattern = data['pattern'].strip()
        if data['rule_type'] == 'extension':
            # Asegurar que las extensiones tengan el punto al inicio
            if pattern and not pattern.startswith('.'):
                pattern = '.' + pattern
        
        new_rule = OrganizationRule(
            node_id=data['node_id'],
            rule_type=data['rule_type'],
            pattern=pattern,
            priority=data.get('priority', 0),
            is_active=data.get('is_active', True)
        )

        db.session.add(new_rule)
        db.session.commit()

        # Actualizar árbol en memoria
        if file_tree:
            node = TreeNode.query.get(data['node_id'])
            if node:
                # Encontrar el nodo en el árbol
                tree_node = file_tree.find_node_by_path(node.path)
                if tree_node:
                    tree_node.add_rule(
                        rule_type=new_rule.rule_type,
                        pattern=new_rule.pattern,
                        priority=new_rule.priority
                    )

        logger.info(f"Regla creada: {new_rule.rule_type} - {new_rule.pattern} para nodo {data['node_id']}")

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
            pattern = data['pattern'].strip()
            # Normalizar el patrón si es una regla de extensión
            if rule.rule_type == 'extension':
                if pattern and not pattern.startswith('.'):
                    pattern = '.' + pattern
            rule.pattern = pattern
        if 'priority' in data:
            rule.priority = data['priority']
        if 'is_active' in data:
            rule.is_active = data['is_active']

        db.session.commit()

        # Actualizar árbol en memoria
        if file_tree:
            node = TreeNode.query.get(rule.node_id)
            if node:
                # Encontrar el nodo en el árbol
                tree_node = file_tree.find_node_by_path(node.path)
                if tree_node:
                    # Limpiar reglas existentes y recargar
                    tree_node.rules = []
                    node_rules = OrganizationRule.query.filter_by(node_id=rule.node_id).all()
                    for node_rule in node_rules:
                        tree_node.add_rule(
                            rule_type=node_rule.rule_type,
                            pattern=node_rule.pattern,
                            priority=node_rule.priority
                        )

        logger.info(f"Regla actualizada: {rule.rule_type} - {rule.pattern}")

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

        # Actualizar árbol en memoria
        if file_tree:
            node = TreeNode.query.get(rule.node_id)
            if node:
                # Encontrar el nodo en el árbol
                tree_node = file_tree.find_node_by_path(node.path)
                if tree_node:
                    # Limpiar reglas existentes y recargar
                    tree_node.rules = []
                    node_rules = OrganizationRule.query.filter_by(node_id=rule.node_id).all()
                    for node_rule in node_rules:
                        tree_node.add_rule(
                            rule_type=node_rule.rule_type,
                            pattern=node_rule.pattern,
                            priority=node_rule.priority
                        )

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
        
        if 'message' in result and result['message'] == 'No hay reglas definidas para organizar archivos':
            return jsonify({
                'success': False,
                'message': result['message']
            }), 400
        
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


# ==================== RUTAS DE GRAFOS (RELACIONES DE CARPETAS) ====================

@app.route('/api/graph/connect', methods=['POST'])
def connect_graph_folders():
    """
    Construye relaciones de carpetas mediante grafos y prepara plan de copia/backup.
    Pensado para que el frontend muestre un toast de confirmación antes de copiar.
    """
    try:
        data = request.get_json() or {}
        base_path = data.get('base_path') or (MonitorConfig.query.first().watch_folder if MonitorConfig.query.first() else None)
        current_folder = data.get('current_folder') or base_path
        backup_dir = data.get('backup_dir')
        copy_on_confirm = data.get('copy_on_confirm', False)
        create_backup = data.get('create_backup', False)
        preferred_related_folder = data.get('preferred_related_folder')

        if not base_path or not current_folder:
            return jsonify({
                'success': False,
                'message': 'base_path y current_folder son requeridos'
            }), 400

        result = connect_project_folders(
            base_path=base_path,
            current_folder=current_folder,
            backup_dir=backup_dir,
            copy_on_confirm=copy_on_confirm,
            create_backup=create_backup,
            preferred_related_folder=preferred_related_folder
        )

        return jsonify({
            'success': True,
            'result': result
        }), 200
    except Exception as e:
        logger.error(f"Error conectando carpetas por grafos: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/tree/relations', methods=['GET'])
def get_tree_relations():
    """
    Calcula relaciones entre nodos del árbol basadas en palabras clave en los nombres.
    No accede al sistema de archivos; usa únicamente los nombres y rutas almacenadas.
    """
    try:
        nodes = TreeNode.query.all()
        payload = [{'name': n.name, 'path': n.path} for n in nodes]
        relations = compute_keyword_relations(payload)

        return jsonify({
            'success': True,
            'relations': relations
        }), 200
    except Exception as e:
        logger.error(f"Error obteniendo relaciones de nodos: {e}")
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
        logs_query = FileLog.query.order_by(FileLog.timestamp.desc()).limit(limit).all()
        # Para mantener el orden por timestamp descendente, invertimos el orden después de insertar por id.
        logs_bst = _build_bst(logs_query, key=lambda l: l.id or 0)
        logs = list(reversed(_bst_inorder_to_list(logs_bst)))
        
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
    
    app.run(debug=False, host='0.0.0.0', port=5000)
