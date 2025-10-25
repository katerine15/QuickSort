"""
Script de prueba para verificar que las reglas funcionan correctamente
"""
import os
import sys

# Agregar el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from tree_structure import FileOrganizationTree, TreeNode

def test_extension_normalization():
    """Prueba la normalización de extensiones"""
    print("=" * 60)
    print("PRUEBA: Normalización de Extensiones")
    print("=" * 60)
    
    # Crear árbol de prueba
    tree = FileOrganizationTree('/test/path')
    
    # Crear nodos de prueba
    images_node = TreeNode('Imágenes', '/test/path/images')
    documents_node = TreeNode('Documentos', '/test/path/documents')
    
    tree.root.add_child(images_node)
    tree.root.add_child(documents_node)
    
    # Agregar reglas con diferentes formatos
    print("\n1. Agregando reglas con diferentes formatos:")
    
    # Regla sin punto
    images_node.add_rule('extension', 'png', priority=1)
    print("   ✓ Regla agregada: 'png' (sin punto)")
    
    # Regla con punto
    images_node.add_rule('extension', '.jpg', priority=1)
    print("   ✓ Regla agregada: '.jpg' (con punto)")
    
    # Regla para documentos
    documents_node.add_rule('extension', 'pdf', priority=1)
    print("   ✓ Regla agregada: 'pdf' (sin punto)")
    
    documents_node.add_rule('extension', '.docx', priority=1)
    print("   ✓ Regla agregada: '.docx' (con punto)")
    
    # Probar coincidencias
    print("\n2. Probando coincidencias de archivos:")
    
    test_cases = [
        ('foto.png', '.png', 'Imágenes'),
        ('imagen.PNG', '.PNG', 'Imágenes'),
        ('captura.jpg', '.jpg', 'Imágenes'),
        ('foto.JPG', '.JPG', 'Imágenes'),
        ('documento.pdf', '.pdf', 'Documentos'),
        ('reporte.PDF', '.PDF', 'Documentos'),
        ('archivo.docx', '.docx', 'Documentos'),
        ('carta.DOCX', '.DOCX', 'Documentos'),
        ('archivo.txt', '.txt', None),  # Sin regla
    ]
    
    passed = 0
    failed = 0
    
    for filename, extension, expected_node in test_cases:
        result = tree.find_destination_for_file(filename, extension)
        result_name = result.name if result else None
        
        if result_name == expected_node:
            print(f"   ✓ {filename} -> {result_name or 'Sin regla'}")
            passed += 1
        else:
            print(f"   ✗ {filename} -> Esperado: {expected_node}, Obtenido: {result_name}")
            failed += 1
    
    print("\n3. Resultados:")
    print(f"   Pruebas pasadas: {passed}/{len(test_cases)}")
    print(f"   Pruebas fallidas: {failed}/{len(test_cases)}")
    
    return failed == 0


def test_keyword_rules():
    """Prueba las reglas por palabra clave"""
    print("\n" + "=" * 60)
    print("PRUEBA: Reglas por Palabra Clave")
    print("=" * 60)
    
    # Crear árbol de prueba
    tree = FileOrganizationTree('/test/path')
    
    # Crear nodos de prueba
    invoices_node = TreeNode('Facturas', '/test/path/facturas')
    reports_node = TreeNode('Reportes', '/test/path/reportes')
    
    tree.root.add_child(invoices_node)
    tree.root.add_child(reports_node)
    
    # Agregar reglas por palabra clave
    print("\n1. Agregando reglas por palabra clave:")
    invoices_node.add_rule('keyword', 'factura', priority=1)
    print("   ✓ Regla agregada: 'factura'")
    
    reports_node.add_rule('keyword', 'reporte', priority=1)
    print("   ✓ Regla agregada: 'reporte'")
    
    # Probar coincidencias
    print("\n2. Probando coincidencias de archivos:")
    
    test_cases = [
        ('factura_enero.pdf', '.pdf', 'Facturas'),
        ('Factura-2024.docx', '.docx', 'Facturas'),
        ('FACTURA_001.xlsx', '.xlsx', 'Facturas'),
        ('reporte_mensual.pdf', '.pdf', 'Reportes'),
        ('Reporte-Anual.docx', '.docx', 'Reportes'),
        ('REPORTE_VENTAS.xlsx', '.xlsx', 'Reportes'),
        ('documento.pdf', '.pdf', None),  # Sin regla
    ]
    
    passed = 0
    failed = 0
    
    for filename, extension, expected_node in test_cases:
        result = tree.find_destination_for_file(filename, extension)
        result_name = result.name if result else None
        
        if result_name == expected_node:
            print(f"   ✓ {filename} -> {result_name or 'Sin regla'}")
            passed += 1
        else:
            print(f"   ✗ {filename} -> Esperado: {expected_node}, Obtenido: {result_name}")
            failed += 1
    
    print("\n3. Resultados:")
    print(f"   Pruebas pasadas: {passed}/{len(test_cases)}")
    print(f"   Pruebas fallidas: {failed}/{len(test_cases)}")
    
    return failed == 0


def test_priority_rules():
    """Prueba las reglas con diferentes prioridades"""
    print("\n" + "=" * 60)
    print("PRUEBA: Prioridad de Reglas")
    print("=" * 60)
    
    # Crear árbol de prueba
    tree = FileOrganizationTree('/test/path')
    
    # Crear nodos de prueba
    general_images = TreeNode('Imágenes Generales', '/test/path/images')
    important_images = TreeNode('Imágenes Importantes', '/test/path/important_images')
    
    tree.root.add_child(general_images)
    tree.root.add_child(important_images)
    
    # Agregar reglas con diferentes prioridades
    print("\n1. Agregando reglas con diferentes prioridades:")
    general_images.add_rule('extension', '.png', priority=1)
    print("   ✓ Regla agregada: '.png' (prioridad 1) -> Imágenes Generales")
    
    important_images.add_rule('keyword', 'importante', priority=10)
    print("   ✓ Regla agregada: 'importante' (prioridad 10) -> Imágenes Importantes")
    
    # Probar coincidencias
    print("\n2. Probando coincidencias con prioridades:")
    
    test_cases = [
        ('foto.png', '.png', 'Imágenes Generales'),
        ('importante.png', '.png', 'Imágenes Importantes'),  # Mayor prioridad
        ('imagen_importante.png', '.png', 'Imágenes Importantes'),  # Mayor prioridad
    ]
    
    passed = 0
    failed = 0
    
    for filename, extension, expected_node in test_cases:
        result = tree.find_destination_for_file(filename, extension)
        result_name = result.name if result else None
        
        if result_name == expected_node:
            print(f"   ✓ {filename} -> {result_name}")
            passed += 1
        else:
            print(f"   ✗ {filename} -> Esperado: {expected_node}, Obtenido: {result_name}")
            failed += 1
    
    print("\n3. Resultados:")
    print(f"   Pruebas pasadas: {passed}/{len(test_cases)}")
    print(f"   Pruebas fallidas: {failed}/{len(test_cases)}")
    
    return failed == 0


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("INICIANDO PRUEBAS DE REGLAS DE ORGANIZACIÓN")
    print("=" * 60)
    
    all_passed = True
    
    # Ejecutar todas las pruebas
    all_passed &= test_extension_normalization()
    all_passed &= test_keyword_rules()
    all_passed &= test_priority_rules()
    
    # Resumen final
    print("\n" + "=" * 60)
    print("RESUMEN FINAL")
    print("=" * 60)
    
    if all_passed:
        print("✓ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("\nLas reglas ahora funcionan correctamente:")
        print("  • Extensiones con o sin punto funcionan")
        print("  • Palabras clave funcionan correctamente")
        print("  • Prioridades se respetan")
        print("  • Normalización automática funciona")
    else:
        print("✗ ALGUNAS PRUEBAS FALLARON")
        print("\nPor favor revisa los errores arriba.")
    
    print("=" * 60 + "\n")
    
    sys.exit(0 if all_passed else 1)
