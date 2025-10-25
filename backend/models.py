from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class TreeNode(db.Model):
    """Modelo para representar nodos del árbol de organización"""
    __tablename__ = 'tree_nodes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(500), nullable=False, unique=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('tree_nodes.id'), nullable=True)
    node_type = db.Column(db.String(50), default='folder')  # folder, category
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    children = db.relationship('TreeNode', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    rules = db.relationship('OrganizationRule', backref='node', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_children=True, max_depth=10, current_depth=0):
        """
        Convierte el nodo a diccionario
        
        Args:
            include_children: Si incluir los hijos en la serialización
            max_depth: Profundidad máxima de recursión
            current_depth: Profundidad actual (para control interno)
        """
        result = {
            'id': self.id,
            'name': self.name,
            'path': self.path,
            'parent_id': self.parent_id,
            'node_type': self.node_type,
            'created_at': self.created_at.isoformat(),
            'rules_count': self.rules.count()
        }
        
        # Solo incluir hijos si se solicita y no hemos excedido la profundidad máxima
        if include_children and current_depth < max_depth:
            result['children'] = [
                child.to_dict(
                    include_children=True, 
                    max_depth=max_depth, 
                    current_depth=current_depth + 1
                ) 
                for child in self.children
            ]
        else:
            result['children'] = []
        
        return result
    
    def __repr__(self):
        return f'<TreeNode {self.name}>'


class OrganizationRule(db.Model):
    """Modelo para reglas de organización de archivos"""
    __tablename__ = 'organization_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.Integer, db.ForeignKey('tree_nodes.id'), nullable=False)
    rule_type = db.Column(db.String(50), nullable=False)  # extension, keyword, size, date
    pattern = db.Column(db.String(255), nullable=False)  # ej: ".pdf", "invoice", ">10MB"
    priority = db.Column(db.Integer, default=0)  # Mayor prioridad = se evalúa primero
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'node_id': self.node_id,
            'rule_type': self.rule_type,
            'pattern': self.pattern,
            'priority': self.priority,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<OrganizationRule {self.rule_type}: {self.pattern}>'


class FileLog(db.Model):
    """Modelo para registrar movimientos de archivos"""
    __tablename__ = 'file_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_path = db.Column(db.String(500), nullable=False)
    destination_path = db.Column(db.String(500), nullable=False)
    rule_id = db.Column(db.Integer, db.ForeignKey('organization_rules.id'), nullable=True)
    action = db.Column(db.String(50), default='moved')  # moved, copied, deleted
    status = db.Column(db.String(50), default='success')  # success, failed, pending
    error_message = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    rule = db.relationship('OrganizationRule', backref='logs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_path': self.original_path,
            'destination_path': self.destination_path,
            'rule_id': self.rule_id,
            'action': self.action,
            'status': self.status,
            'error_message': self.error_message,
            'timestamp': self.timestamp.isoformat()
        }
    
    def __repr__(self):
        return f'<FileLog {self.filename} - {self.status}>'


class MonitorConfig(db.Model):
    """Modelo para configuración del monitoreo"""
    __tablename__ = 'monitor_config'
    
    id = db.Column(db.Integer, primary_key=True)
    watch_folder = db.Column(db.String(500), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    auto_organize = db.Column(db.Boolean, default=True)
    recursive = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'watch_folder': self.watch_folder,
            'is_active': self.is_active,
            'auto_organize': self.auto_organize,
            'recursive': self.recursive,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<MonitorConfig {self.watch_folder}>'
