"""
Script de prueba para verificar los endpoints del backend
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

def print_test_header(test_name):
    """Imprime encabezado de prueba"""
    print("\n" + "="*60)
    print(f"🧪 PRUEBA: {test_name}")
    print("="*60)

def print_result(success, message, data=None):
    """Imprime resultado de prueba"""
    status = "✅ ÉXITO" if success else "❌ FALLO"
    print(f"{status}: {message}")
    if data:
        print(f"Datos: {json.dumps(data, indent=2)}")

def test_health():
    """Prueba el endpoint de health check"""
    print_test_header("Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_result(True, "Backend está funcionando", response.json())
            return True
        else:
            print_result(False, f"Código de estado: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Error de conexión: {e}")
        return False

def test_get_tree():
    """Prueba obtener el árbol"""
    print_test_header("GET /api/tree")
    try:
        response = requests.get(f"{BASE_URL}/tree", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Árbol obtenido correctamente", data)
            return True
        else:
            print_result(False, f"Código de estado: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False

def test_get_nodes():
    """Prueba obtener todos los nodos"""
    print_test_header("GET /api/tree/nodes")
    try:
        response = requests.get(f"{BASE_URL}/tree/nodes", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Nodos obtenidos: {len(data.get('nodes', []))}", data)
            return True
        else:
            print_result(False, f"Código de estado: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False

def test_get_rules():
    """Prueba obtener reglas"""
    print_test_header("GET /api/rules")
    try:
        response = requests.get(f"{BASE_URL}/rules", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Reglas obtenidas: {len(data.get('rules', []))}", data)
            return True
        else:
            print_result(False, f"Código de estado: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False

def test_monitor_status():
    """Prueba obtener estado del monitor"""
    print_test_header("GET /api/monitor/status")
    try:
        response = requests.get(f"{BASE_URL}/monitor/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Estado del monitor obtenido", data)
            return True
        else:
            print_result(False, f"Código de estado: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False

def test_get_logs():
    """Prueba obtener logs"""
    print_test_header("GET /api/logs")
    try:
        response = requests.get(f"{BASE_URL}/logs?limit=10", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Logs obtenidos: {len(data.get('logs', []))}", data)
            return True
        else:
            print_result(False, f"Código de estado: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False

def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("\n" + "🚀"*30)
    print("INICIANDO PRUEBAS DEL BACKEND")
    print("🚀"*30)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL Base: {BASE_URL}")
    
    tests = [
        ("Health Check", test_health),
        ("Get Tree", test_get_tree),
        ("Get Nodes", test_get_nodes),
        ("Get Rules", test_get_rules),
        ("Monitor Status", test_monitor_status),
        ("Get Logs", test_get_logs),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error ejecutando {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen
    print("\n" + "📊"*30)
    print("RESUMEN DE PRUEBAS")
    print("📊"*30)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n{'='*60}")
    print(f"Total: {passed}/{total} pruebas exitosas ({passed*100//total}%)")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! 🎉")
    else:
        print(f"⚠️  {total - passed} prueba(s) fallaron")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Pruebas interrumpidas por el usuario")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Error fatal: {e}")
        exit(1)
