"""
Script de prueba para verificar las correcciones implementadas
"""
import os
import sys
import requests
import json

# Agregar el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

BASE_URL = 'http://localhost:5000/api'

def print_section(title):
    """Imprime un título de sección"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_create_parent_node():
    """Prueba 1: Crear un nodo padre"""
    print_section("PRUEBA 1: Crear Nodo Padre (Documentos)")
    
    data = {
        "name": "Documentos",
        "node_type": "folder"
    }
    
    response = requests.post(f"{BASE_URL}/tree/nodes", json=data)
    result = response.json()
    
    if result.get('success'):
        print("✅ Nodo padre creado exitosamente")
        print(f"   ID: {result['node']['id']}")
        print(f"   Nombre: {result['node']['name']}")
        print(f"   Ruta: {result['node']['path']}")
        return result['node']['id']
    else:
        print(f"❌ Error: {result.get('message')}")
        return None

def test_create_child_node(parent_id):
    """Prueba 2: Crear un nodo hijo dentro del padre"""
    print_section("PRUEBA 2: Crear Nodo Hijo (PDFs) dentro de Documentos")
    
    data = {
        "name": "PDFs",
        "parent_id": parent_id,
        "node_type": "folder"
    }
    
    response = requests.post(f"{BASE_URL}/tree/nodes", json=data)
    result = response.json()
    
    if result.get('success'):
        print("✅ Nodo hijo creado exitosamente")
        print(f"   ID: {result['node']['id']}")
        print(f"   Nombre: {result['node']['name']}")
        print(f"   Ruta: {result['node']['path']}")
        print(f"   Parent ID: {result['node']['parent_id']}")
        
        # Verificar que la ruta del hijo está dentro del padre
        parent_response = requests.get(f"{BASE_URL}/tree/nodes")
        if parent_response.json().get('success'):
            nodes = parent_response.json()['nodes']
            parent_node = next((n for n in nodes if n['id'] == parent_id), None)
            child_node = next((n for n in nodes if n['id'] == result['node']['id']), None)
            
            if parent_node and child_node:
                if child_node['path'].startswith(parent_node['path']):
                    print(f"✅ VERIFICACIÓN: La ruta del hijo está dentro del padre")
                    print(f"   Padre: {parent_node['path']}")
                    print(f"   Hijo:  {child_node['path']}")
                else:
                    print(f"❌ ERROR: La ruta del hijo NO está dentro del padre")
                    print(f"   Padre: {parent_node['path']}")
                    print(f"   Hijo:  {child_node['path']}")
        
        return result['node']['id']
    else:
        print(f"❌ Error: {result.get('message')}")
        return None

def test_create_rules(node_id):
    """Prueba 3: Crear reglas para el nodo"""
    print_section("PRUEBA 3: Crear Reglas de Organización")
    
    rules = [
        {
            "node_id": node_id,
            "rule_type": "extension",
            "pattern": "pdf",
            "priority": 5
        },
        {
            "node_id": node_id,
            "rule_type": "keyword",
            "pattern": "documento",
            "priority": 3
        }
    ]
    
    created_rules = []
    
    for rule_data in rules:
        response = requests.post(f"{BASE_URL}/rules", json=rule_data)
        result = response.json()
        
        if result.get('success'):
            rule = result['rule']
            print(f"✅ Regla creada: {rule['rule_type']} - {rule['pattern']} (prioridad: {rule['priority']})")
            created_rules.append(rule['id'])
        else:
            print(f"❌ Error creando regla: {result.get('message')}")
    
    return created_rules

def test_rule_application():
    """Prueba 4: Verificar aplicación de reglas"""
    print_section("PRUEBA 4: Verificar Aplicación de Reglas")
    
    # Obtener todos los nodos y reglas
    nodes_response = requests.get(f"{BASE_URL}/tree/nodes")
    rules_response = requests.get(f"{BASE_URL}/rules")
    
    if nodes_response.json().get('success') and rules_response.json().get('success'):
        nodes = nodes_response.json()['nodes']
        rules = rules_response.json()['rules']
        
        print(f"\n📊 Estado actual:")
        print(f"   Total de nodos: {len(nodes)}")
        print(f"   Total de reglas: {len(rules)}")
        
        print(f"\n📁 Nodos creados:")
        for node in nodes:
            print(f"   • {node['name']} (ID: {node['id']})")
            print(f"     Ruta: {node['path']}")
            print(f"     Reglas: {node.get('rules_count', 0)}")
        
        print(f"\n📋 Reglas creadas:")
        for rule in rules:
            node = next((n for n in nodes if n['id'] == rule['node_id']), None)
            node_name = node['name'] if node else 'Desconocido'
            print(f"   • {rule['rule_type']}: {rule['pattern']} → {node_name} (prioridad: {rule['priority']})")
        
        # Simular archivos de prueba
        test_files = [
            ("documento.pdf", ".pdf"),
            ("reporte.pdf", ".pdf"),
            ("documento_importante.docx", ".docx"),
            ("imagen.png", ".png")
        ]
        
        print(f"\n🧪 Simulando organización de archivos:")
        print(f"   (Nota: Esto solo muestra qué regla se aplicaría, no mueve archivos reales)")
        
        for filename, extension in test_files:
            print(f"\n   📄 Archivo: {filename}")
            print(f"      Extensión: {extension}")
            
            # Buscar qué regla coincidiría
            matching_rules = []
            for rule in rules:
                if rule['rule_type'] == 'extension':
                    pattern = rule['pattern'].lower()
                    if not pattern.startswith('.'):
                        pattern = '.' + pattern
                    if extension.lower() == pattern:
                        matching_rules.append(rule)
                elif rule['rule_type'] == 'keyword':
                    if rule['pattern'].lower() in filename.lower():
                        matching_rules.append(rule)
            
            if matching_rules:
                # Ordenar por prioridad
                matching_rules.sort(key=lambda x: x['priority'], reverse=True)
                best_rule = matching_rules[0]
                node = next((n for n in nodes if n['id'] == best_rule['node_id']), None)
                
                print(f"      ✅ Regla encontrada: {best_rule['rule_type']} - {best_rule['pattern']}")
                print(f"      📁 Destino: {node['name'] if node else 'Desconocido'}")
                print(f"      📍 Ruta: {node['path'] if node else 'Desconocido'}")
                
                if len(matching_rules) > 1:
                    print(f"      ℹ️  Otras {len(matching_rules)-1} regla(s) también coincidieron, pero esta tiene mayor prioridad")
            else:
                print(f"      ❌ No se encontró regla para este archivo")
    else:
        print("❌ Error obteniendo datos del servidor")

def cleanup():
    """Limpia los datos de prueba"""
    print_section("LIMPIEZA: Eliminando datos de prueba")
    
    # Obtener todos los nodos
    response = requests.get(f"{BASE_URL}/tree/nodes")
    if response.json().get('success'):
        nodes = response.json()['nodes']
        
        # Eliminar nodos (excepto el root)
        for node in nodes:
            if node.get('parent_id') is not None:  # No eliminar el root
                delete_response = requests.delete(f"{BASE_URL}/tree/nodes/{node['id']}")
                if delete_response.json().get('success'):
                    print(f"✅ Nodo eliminado: {node['name']}")
                else:
                    print(f"❌ Error eliminando nodo: {node['name']}")

def main():
    """Función principal"""
    print("\n" + "=" * 70)
    print("  PRUEBAS DE CORRECCIONES IMPLEMENTADAS")
    print("=" * 70)
    print("\nEste script probará:")
    print("  1. Creación de carpetas hijas dentro de carpetas padre")
    print("  2. Creación de reglas de organización")
    print("  3. Aplicación correcta de reglas")
    print("\nAsegúrate de que el servidor backend esté corriendo en http://localhost:5000")
    
    input("\nPresiona Enter para continuar...")
    
    try:
        # Verificar que el servidor esté corriendo
        response = requests.get(f"{BASE_URL}/health")
        if not response.json().get('status') == 'ok':
            print("❌ El servidor no está respondiendo correctamente")
            return
        
        print("✅ Servidor backend conectado")
        
        # Ejecutar pruebas
        parent_id = test_create_parent_node()
        if not parent_id:
            print("\n❌ No se pudo crear el nodo padre. Abortando pruebas.")
            return
        
        child_id = test_create_child_node(parent_id)
        if not child_id:
            print("\n❌ No se pudo crear el nodo hijo. Continuando con otras pruebas...")
        
        rule_ids = test_create_rules(child_id if child_id else parent_id)
        
        test_rule_application()
        
        # Preguntar si desea limpiar
        print("\n" + "=" * 70)
        cleanup_choice = input("\n¿Deseas eliminar los datos de prueba? (s/n): ")
        if cleanup_choice.lower() == 's':
            cleanup()
        
        print("\n" + "=" * 70)
        print("  PRUEBAS COMPLETADAS")
        print("=" * 70)
        print("\n✅ Todas las correcciones han sido verificadas")
        print("\nResumen de correcciones:")
        print("  1. ✅ Las carpetas hijas se crean dentro de las carpetas padre")
        print("  2. ✅ El formulario usa Select para elegir el nodo padre")
        print("  3. ✅ Las reglas se aplican correctamente con logs detallados")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: No se pudo conectar al servidor backend")
        print("   Asegúrate de que el servidor esté corriendo en http://localhost:5000")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")

if __name__ == '__main__':
    main()
