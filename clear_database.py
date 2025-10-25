"""
Script para limpiar todos los datos de la base de datos
Mantiene la estructura de las tablas pero elimina todos los registros
"""
import os
import sys

# Agregar el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from flask import Flask
from models import db, TreeNode, OrganizationRule, FileLog, MonitorConfig
from config import Config

def clear_database():
    """Limpia todos los datos de la base de datos"""
    print("=" * 60)
    print("LIMPIEZA DE BASE DE DATOS")
    print("=" * 60)
    
    # Crear aplicación Flask
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        try:
            # Contar registros antes de limpiar
            print("\n1. Contando registros actuales:")
            tree_nodes_count = TreeNode.query.count()
            rules_count = OrganizationRule.query.count()
            logs_count = FileLog.query.count()
            config_count = MonitorConfig.query.count()
            
            print(f"   • TreeNodes: {tree_nodes_count}")
            print(f"   • OrganizationRules: {rules_count}")
            print(f"   • FileLogs: {logs_count}")
            print(f"   • MonitorConfig: {config_count}")
            print(f"   Total de registros: {tree_nodes_count + rules_count + logs_count + config_count}")
            
            # Confirmar limpieza
            print("\n2. Limpiando base de datos...")
            
            # Eliminar en orden correcto (respetando foreign keys)
            # Primero los logs (dependen de rules)
            deleted_logs = FileLog.query.delete()
            print(f"   ✓ Eliminados {deleted_logs} registros de FileLogs")
            
            # Luego las reglas (dependen de nodes)
            deleted_rules = OrganizationRule.query.delete()
            print(f"   ✓ Eliminados {deleted_rules} registros de OrganizationRules")
            
            # Luego los nodos del árbol
            deleted_nodes = TreeNode.query.delete()
            print(f"   ✓ Eliminados {deleted_nodes} registros de TreeNodes")
            
            # Finalmente la configuración del monitor
            deleted_config = MonitorConfig.query.delete()
            print(f"   ✓ Eliminados {deleted_config} registros de MonitorConfig")
            
            # Commit de los cambios
            db.session.commit()
            
            # Verificar que todo está limpio
            print("\n3. Verificando limpieza:")
            tree_nodes_count = TreeNode.query.count()
            rules_count = OrganizationRule.query.count()
            logs_count = FileLog.query.count()
            config_count = MonitorConfig.query.count()
            
            print(f"   • TreeNodes: {tree_nodes_count}")
            print(f"   • OrganizationRules: {rules_count}")
            print(f"   • FileLogs: {logs_count}")
            print(f"   • MonitorConfig: {config_count}")
            
            total_remaining = tree_nodes_count + rules_count + logs_count + config_count
            
            if total_remaining == 0:
                print("\n✓ BASE DE DATOS LIMPIADA EXITOSAMENTE")
                print("  Todos los registros han sido eliminados.")
                print("  La estructura de las tablas se mantiene intacta.")
                return True
            else:
                print(f"\n✗ ADVERTENCIA: Quedan {total_remaining} registros")
                return False
                
        except Exception as e:
            print(f"\n✗ ERROR al limpiar la base de datos: {e}")
            db.session.rollback()
            return False
    
    print("=" * 60 + "\n")


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("SCRIPT DE LIMPIEZA DE BASE DE DATOS - QuickSort")
    print("=" * 60)
    print("\n⚠️  ADVERTENCIA: Este script eliminará TODOS los datos de la base de datos.")
    print("   • Nodos del árbol de organización")
    print("   • Reglas de organización")
    print("   • Logs de archivos")
    print("   • Configuración del monitor")
    print("\nLa estructura de las tablas se mantendrá intacta.\n")
    
    # Ejecutar limpieza
    success = clear_database()
    
    if success:
        print("\n" + "=" * 60)
        print("LIMPIEZA COMPLETADA")
        print("=" * 60)
        print("\nLa base de datos está ahora vacía y lista para:")
        print("  • Crear nuevos nodos y reglas")
        print("  • Ejecutar pruebas")
        print("  • Iniciar con datos limpios")
        print("=" * 60 + "\n")
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("LIMPIEZA FALLIDA")
        print("=" * 60)
        print("\nPor favor revisa los errores arriba.")
        print("=" * 60 + "\n")
        sys.exit(1)
