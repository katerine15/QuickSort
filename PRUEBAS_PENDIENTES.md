# 🧪 Guía de Pruebas Pendientes - QuickSort

## 📊 Estado Actual (Verificado)

### ✅ Backend - FUNCIONAL
- ✅ Código revisado y corregido (3 errores críticos)
- ✅ Dependencias instaladas
- ✅ Base de datos inicializada (database.db)
- ✅ Servidor ejecutándose en http://localhost:5000
- ✅ Logs confirman inicialización correcta

### 🔄 Frontend - EN EJECUCIÓN
- ✅ Node.js v20.14.0 instalado
- ✅ Dependencias instaladas (node_modules/)
- ✅ Servidor React iniciado con `npm start`
- 🔄 Compilando (debería abrir automáticamente en el navegador)

---

## 🧪 Pruebas que Debes Realizar

### 1. Verificar Frontend (Interfaz Web)

**Paso 1: Abrir la Aplicación**
- El navegador debería abrirse automáticamente en http://localhost:3000
- Si no se abre, abre manualmente: http://localhost:3000

**Paso 2: Verificar Carga**
- ✅ La aplicación carga sin errores
- ✅ Se muestra el título "QuickSort - Organizador Automático de Archivos"
- ✅ Se ven 4 pestañas: Árbol, Monitor, Reglas, Historial

**Paso 3: Probar Navegación**
- ✅ Clic en pestaña "Árbol" - se muestra correctamente
- ✅ Clic en pestaña "Monitor" - se muestra correctamente
- ✅ Clic en pestaña "Reglas" - se muestra correctamente
- ✅ Clic en pestaña "Historial" - se muestra correctamente

---

### 2. Probar Funcionalidad del Árbol

**En la pestaña "Árbol":**

1. **Crear Nodo Raíz**:
   - Clic en "Agregar Nodo"
   - Nombre: "Documentos"
   - Ruta: "C:\Users\TuUsuario\Organized\Documentos"
   - Tipo: "folder"
   - Clic en "Crear"
   - ✅ Verificar que aparece en el árbol

2. **Crear Nodo Hijo**:
   - Seleccionar nodo "Documentos"
   - Clic en "Agregar Hijo"
   - Nombre: "PDFs"
   - Ruta: "C:\Users\TuUsuario\Organized\Documentos\PDFs"
   - Clic en "Crear"
   - ✅ Verificar que aparece como hijo de "Documentos"

3. **Visualizar Árbol**:
   - ✅ El árbol se muestra correctamente
   - ✅ Se puede expandir/contraer nodos
   - ✅ Se muestra la jerarquía correctamente

---

### 3. Probar Funcionalidad de Reglas

**En la pestaña "Reglas":**

1. **Crear Regla por Extensión**:
   - Clic en "Nueva Regla"
   - Tipo: "extension"
   - Patrón: ".pdf"
   - Nodo destino: Seleccionar "PDFs"
   - Prioridad: 10
   - Clic en "Crear"
   - ✅ Verificar que aparece en la lista de reglas

2. **Crear Regla por Palabra Clave**:
   - Clic en "Nueva Regla"
   - Tipo: "keyword"
   - Patrón: "factura"
   - Nodo destino: Seleccionar nodo apropiado
   - Prioridad: 5
   - Clic en "Crear"
   - ✅ Verificar que aparece en la lista

3. **Editar Regla**:
   - Clic en "Editar" en una regla
   - Cambiar prioridad
   - Guardar
   - ✅ Verificar que se actualizó

4. **Eliminar Regla**:
   - Clic en "Eliminar" en una regla
   - Confirmar
   - ✅ Verificar que se eliminó

---

### 4. Probar Funcionalidad del Monitor

**En la pestaña "Monitor":**

1. **Configurar Monitor**:
   - Carpeta a monitorear: Seleccionar carpeta (ej: Downloads)
   - ✅ Activar "Organización automática"
   - ✅ Activar/Desactivar "Recursivo" según necesites
   - Clic en "Guardar Configuración"
   - ✅ Verificar que se guardó

2. **Iniciar Monitor**:
   - Clic en "Iniciar Monitor"
   - ✅ Verificar que el estado cambia a "Activo"
   - ✅ Verificar que se muestra "Monitoreando..."

3. **Probar Organización Automática**:
   - Copiar un archivo PDF a la carpeta monitoreada
   - ✅ Verificar que el archivo se mueve automáticamente
   - ✅ Verificar que aparece en el historial

4. **Detener Monitor**:
   - Clic en "Detener Monitor"
   - ✅ Verificar que el estado cambia a "Inactivo"

---

### 5. Probar Funcionalidad del Historial

**En la pestaña "Historial":**

1. **Ver Logs**:
   - ✅ Se muestran los logs de operaciones
   - ✅ Se muestra: nombre de archivo, origen, destino, estado, fecha

2. **Filtrar Logs**:
   - Usar filtros si están disponibles
   - ✅ Verificar que funciona correctamente

3. **Ver Estadísticas**:
   - ✅ Se muestran estadísticas (total, exitosos, fallidos)
   - ✅ Los números son correctos

---

### 6. Probar Endpoints de la API (Opcional)

**Usando Postman, Insomnia o curl:**

1. **Health Check**:
   ```
   GET http://localhost:5000/api/health
   ```
   ✅ Respuesta: `{"status": "ok"}`

2. **Obtener Árbol**:
   ```
   GET http://localhost:5000/api/tree
   ```
   ✅ Respuesta: JSON con estructura del árbol

3. **Obtener Nodos**:
   ```
   GET http://localhost:5000/api/tree/nodes
   ```
   ✅ Respuesta: Lista de nodos

4. **Crear Nodo**:
   ```
   POST http://localhost:5000/api/tree/nodes
   Body: {
     "name": "Test",
     "path": "C:\\Test",
     "parent_id": null,
     "node_type": "folder"
   }
   ```
   ✅ Respuesta: Nodo creado

5. **Obtener Reglas**:
   ```
   GET http://localhost:5000/api/rules
   ```
   ✅ Respuesta: Lista de reglas

6. **Crear Regla**:
   ```
   POST http://localhost:5000/api/rules
   Body: {
     "node_id": 1,
     "rule_type": "extension",
     "pattern": ".txt",
     "priority": 5
   }
   ```
   ✅ Respuesta: Regla creada

7. **Estado del Monitor**:
   ```
   GET http://localhost:5000/api/monitor/status
   ```
   ✅ Respuesta: Estado del monitor

8. **Obtener Logs**:
   ```
   GET http://localhost:5000/api/logs?limit=10
   ```
   ✅ Respuesta: Lista de logs

---

## 🐛 Problemas Comunes y Soluciones

### Problema 1: Frontend no carga
**Solución**:
- Verificar que el backend esté corriendo en puerto 5000
- Verificar que el frontend esté corriendo en puerto 3000
- Revisar la consola del navegador (F12) para errores

### Problema 2: Error de CORS
**Solución**:
- Ya está configurado Flask-CORS en el backend
- Si persiste, verificar que el backend esté corriendo

### Problema 3: No se crean nodos
**Solución**:
- Verificar que la ruta sea válida
- Verificar que tengas permisos en la carpeta
- Revisar logs del backend

### Problema 4: Monitor no detecta archivos
**Solución**:
- Verificar que la carpeta existe
- Verificar que el monitor esté activo
- Verificar que haya reglas configuradas

---

## 📝 Checklist de Pruebas

### Frontend
- [ ] Aplicación carga correctamente
- [ ] Navegación entre pestañas funciona
- [ ] Se pueden crear nodos
- [ ] Se pueden crear reglas
- [ ] Se puede configurar el monitor
- [ ] Se puede iniciar/detener el monitor
- [ ] Se muestra el historial
- [ ] No hay errores en consola

### Backend
- [ ] Servidor responde en puerto 5000
- [ ] Endpoint /api/health funciona
- [ ] Se pueden crear nodos vía API
- [ ] Se pueden crear reglas vía API
- [ ] El monitor detecta archivos nuevos
- [ ] Los archivos se organizan correctamente
- [ ] Los logs se registran en la BD

### Integración
- [ ] Frontend se comunica con backend
- [ ] Los cambios en frontend se reflejan en backend
- [ ] Los cambios en backend se reflejan en frontend
- [ ] El flujo completo funciona: crear nodo → crear regla → monitorear → organizar

---

## 🎯 Flujo de Prueba Completo

**Prueba End-to-End Recomendada**:

1. **Preparación**:
   - Crear carpeta de prueba: `C:\Test\Downloads`
   - Crear carpeta de destino: `C:\Test\Organized`

2. **Configuración**:
   - Crear nodo raíz: "Organized" → `C:\Test\Organized`
   - Crear nodo hijo: "PDFs" → `C:\Test\Organized\PDFs`
   - Crear regla: extensión ".pdf" → nodo "PDFs", prioridad 10

3. **Monitoreo**:
   - Configurar monitor para `C:\Test\Downloads`
   - Activar organización automática
   - Iniciar monitor

4. **Prueba**:
   - Copiar un archivo PDF a `C:\Test\Downloads`
   - Esperar 1-2 segundos
   - Verificar que el archivo se movió a `C:\Test\Organized\PDFs`
   - Verificar que aparece en el historial

5. **Verificación**:
   - ✅ Archivo movido correctamente
   - ✅ Log registrado en historial
   - ✅ Estado "success" en el log
   - ✅ Ruta de origen y destino correctas

---

## 📊 Reporte de Pruebas

**Después de completar las pruebas, documenta:**

### Pruebas Exitosas:
- [ ] Lista de funcionalidades que funcionan correctamente

### Pruebas Fallidas:
- [ ] Lista de funcionalidades que no funcionan
- [ ] Descripción del error
- [ ] Pasos para reproducir

### Observaciones:
- [ ] Problemas de rendimiento
- [ ] Problemas de UX
- [ ] Sugerencias de mejora

---

## ✅ Criterios de Éxito

El proyecto se considera **100% funcional** si:

1. ✅ Frontend carga sin errores
2. ✅ Backend responde a todas las peticiones
3. ✅ Se pueden crear nodos y reglas
4. ✅ El monitor detecta archivos nuevos
5. ✅ Los archivos se organizan correctamente según las reglas
6. ✅ Los logs se registran correctamente
7. ✅ No hay errores en consola ni en logs del servidor

---

**Documento creado**: 22 de Octubre, 2025
**Versión**: 1.0
**Estado**: Listo para pruebas manuales
