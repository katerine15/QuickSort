"""
Implementación de estructura de árbol para organización de archivos
"""
import os
from typing import List, Optional, Dict, Any


class TreeNode:
    """Nodo del árbol de organización"""
    
    def __init__(self, name: str, path: str, parent=None, node_type: str = 'folder'):
        self.name = name
        self.path = path
        self.parent = parent
        self.children: List['TreeNode'] = []
        self.node_type = node_type
        self.rules: List[Dict[str, Any]] = []
    
    def add_child(self, child: 'TreeNode') -> 'TreeNode':
        """Agrega un hijo al nodo actual"""
        child.parent = self
        self.children.append(child)
        return child
    
    def remove_child(self, child: 'TreeNode') -> bool:
        """Elimina un hijo del nodo actual"""
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            return True
        return False
    
    def find_child(self, name: str) -> Optional['TreeNode']:
        """Busca un hijo por nombre"""
        for child in self.children:
            if child.name == name:
                return child
        return None
    
    def get_depth(self) -> int:
        """Obtiene la profundidad del nodo en el árbol"""
        depth = 0
        current = self.parent
        while current is not None:
            depth += 1
            current = current.parent
        return depth
    
    def get_path_list(self) -> List[str]:
        """Obtiene la lista de nombres desde la raíz hasta este nodo"""
        path_list = []
        current = self
        while current is not None:
            path_list.insert(0, current.name)
            current = current.parent
        return path_list
    
    def add_rule(self, rule_type: str, pattern: str, priority: int = 0) -> Dict[str, Any]:
        """Agrega una regla de organización al nodo"""
        rule = {
            'rule_type': rule_type,
            'pattern': pattern,
            'priority': priority,
            'is_active': True
        }
        self.rules.append(rule)
        self.rules.sort(key=lambda x: x['priority'], reverse=True)
        return rule
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el nodo a diccionario"""
        return {
            'name': self.name,
            'path': self.path,
            'node_type': self.node_type,
            'depth': self.get_depth(),
            'children': [child.to_dict() for child in self.children],
            'rules': self.rules
        }
    
    def __repr__(self):
        return f'<TreeNode {self.name} ({len(self.children)} children)>'


class FileOrganizationTree:
    """Árbol de organización de archivos"""
    
    def __init__(self, root_path: str):
        self.root = TreeNode(name='Root', path=root_path, node_type='root')
    
    def add_node(self, parent_path: str, name: str, path: str, node_type: str = 'folder') -> Optional[TreeNode]:
        """Agrega un nodo al árbol"""
        parent = self.find_node_by_path(parent_path)
        if parent:
            new_node = TreeNode(name=name, path=path, node_type=node_type)
            parent.add_child(new_node)
            return new_node
        return None
    
    def find_node_by_path(self, path: str) -> Optional[TreeNode]:
        """Busca un nodo por su ruta"""
        return self._find_node_recursive(self.root, path)
    
    def _find_node_recursive(self, node: TreeNode, path: str) -> Optional[TreeNode]:
        """Búsqueda recursiva de nodo por ruta"""
        if node.path == path:
            return node
        
        for child in node.children:
            result = self._find_node_recursive(child, path)
            if result:
                return result
        
        return None
    
    def find_node_by_name(self, name: str) -> Optional[TreeNode]:
        """Busca un nodo por su nombre"""
        return self._find_node_by_name_recursive(self.root, name)
    
    def _find_node_by_name_recursive(self, node: TreeNode, name: str) -> Optional[TreeNode]:
        """Búsqueda recursiva de nodo por nombre"""
        if node.name == name:
            return node
        
        for child in node.children:
            result = self._find_node_by_name_recursive(child, name)
            if result:
                return result
        
        return None
    
    def get_all_nodes(self) -> List[TreeNode]:
        """Obtiene todos los nodos del árbol"""
        nodes = []
        self._collect_nodes_recursive(self.root, nodes)
        return nodes
    
    def _collect_nodes_recursive(self, node: TreeNode, nodes: List[TreeNode]):
        """Recolecta todos los nodos recursivamente"""
        nodes.append(node)
        for child in node.children:
            self._collect_nodes_recursive(child, nodes)
    
    def find_destination_for_file(self, filename: str, file_extension: str) -> Optional[TreeNode]:
        """
        Encuentra el nodo de destino para un archivo basado en las reglas
        Retorna el nodo con la regla de mayor prioridad que coincida
        """
        import logging
        logger = logging.getLogger(__name__)
        
        best_match = None
        best_priority = -1
        
        all_nodes = self.get_all_nodes()
        
        # Normalizar la extensión del archivo (asegurar que tenga el punto)
        normalized_file_ext = file_extension.lower().strip()
        if normalized_file_ext and not normalized_file_ext.startswith('.'):
            normalized_file_ext = '.' + normalized_file_ext
        
        logger.info(f"🔍 Buscando destino para archivo: {filename}")
        logger.info(f"   Extensión normalizada: '{normalized_file_ext}'")
        logger.info(f"   Total de nodos a revisar: {len(all_nodes)}")
        
        matches_found = []
        
        for node in all_nodes:
            if not node.rules:
                continue
                
            logger.info(f"   📁 Revisando nodo: {node.name} ({len(node.rules)} reglas)")
            
            for rule in node.rules:
                if not rule.get('is_active', True):
                    logger.info(f"      ⏭️  Regla inactiva: {rule['rule_type']} - {rule['pattern']}")
                    continue
                
                match = False
                match_reason = ""
                
                if rule['rule_type'] == 'extension':
                    # Normalizar el patrón de la regla (asegurar que tenga el punto)
                    normalized_pattern = rule['pattern'].lower().strip()
                    if normalized_pattern and not normalized_pattern.startswith('.'):
                        normalized_pattern = '.' + normalized_pattern
                    
                    logger.info(f"      🔧 Regla extensión: '{rule['pattern']}' → '{normalized_pattern}'")
                    
                    # Comparar extensiones normalizadas
                    if normalized_file_ext == normalized_pattern:
                        match = True
                        match_reason = f"extensión '{normalized_file_ext}' coincide con '{normalized_pattern}'"
                    else:
                        logger.info(f"         ❌ No coincide: '{normalized_file_ext}' != '{normalized_pattern}'")
                
                elif rule['rule_type'] == 'keyword':
                    keyword_pattern = rule['pattern'].lower().strip()
                    filename_lower = filename.lower()
                    
                    logger.info(f"      🔑 Regla keyword: '{rule['pattern']}' → '{keyword_pattern}'")
                    
                    if keyword_pattern in filename_lower:
                        match = True
                        match_reason = f"palabra clave '{keyword_pattern}' encontrada en '{filename}'"
                    else:
                        logger.info(f"         ❌ No coincide: '{keyword_pattern}' no está en '{filename_lower}'")
                
                if match:
                    logger.info(f"      ✅ COINCIDENCIA: {match_reason} (prioridad: {rule['priority']})")
                    matches_found.append({
                        'node': node,
                        'rule': rule,
                        'priority': rule['priority'],
                        'reason': match_reason
                    })
                    
                    if rule['priority'] > best_priority:
                        best_match = node
                        best_priority = rule['priority']
                        logger.info(f"      ⭐ Nueva mejor coincidencia: {node.name} (prioridad: {best_priority})")
        
        if best_match:
            logger.info(f"✅ Destino encontrado: {best_match.name} (prioridad: {best_priority})")
            logger.info(f"   Ruta de destino: {best_match.path}")
        else:
            logger.warning(f"❌ No se encontró destino para: {filename}")
            if matches_found:
                logger.info(f"   Se encontraron {len(matches_found)} coincidencias pero ninguna fue seleccionada")
            else:
                logger.info(f"   No se encontraron coincidencias en ninguna regla")
        
        return best_match
    
    def create_folder_structure(self, base_path: str):
        """Crea la estructura de carpetas física en el sistema"""
        self._create_folders_recursive(self.root, base_path)
    
    def _create_folders_recursive(self, node: TreeNode, base_path: str):
        """Crea carpetas recursivamente"""
        if node.node_type != 'root':
            folder_path = os.path.join(base_path, node.path)
            os.makedirs(folder_path, exist_ok=True)
        
        for child in node.children:
            self._create_folders_recursive(child, base_path)
    
    def has_rules(self) -> bool:
        """Verifica si el árbol tiene alguna regla definida"""
        all_nodes = self.get_all_nodes()
        for node in all_nodes:
            if node.rules:
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el árbol completo a diccionario"""
        return {
            'root': self.root.to_dict(),
            'total_nodes': len(self.get_all_nodes()),
            'has_rules': self.has_rules()
        }
    
    def print_tree(self, node: Optional[TreeNode] = None, prefix: str = '', is_last: bool = True):
        """Imprime el árbol en formato visual"""
        if node is None:
            node = self.root
        
        connector = '└── ' if is_last else '├── '
        print(prefix + connector + node.name)
        
        children = node.children
        for i, child in enumerate(children):
            extension = '    ' if is_last else '│   '
            self.print_tree(child, prefix + extension, i == len(children) - 1)
    
    def __repr__(self):
        return f'<FileOrganizationTree with {len(self.get_all_nodes())} nodes>'
