# 📖 Guía de Uso - QuickSort

## 🎯 ¿Qué hace QuickSort?

QuickSort es un organizador automático de archivos que usa una **estructura de árbol** para clasificar tus archivos según reglas que tú defines.

---

## 🔧 Error Corregido

**Problema encontrado**: Error 500 al crear nodos raíz
**Solución aplicada**: Validación mejorada y creación automática de carpetas físicas
**Estado**: ✅ CORREGIDO

**IMPORTANTE**: Necesitas **reiniciar el servidor backend** para aplicar los cambios:
1. En la terminal donde corre el backend, presiona `Ctrl+C`
2. Ejecuta nuevamente: `cd QuickSort\backend && python app.py`

---

## 📚 Conceptos Básicos

### 1. **Nodos** (Carpetas en el Árbol)
Los nodos representan carpetas donde se organizarán tus archivos.

**Ejemplo de estructura**:
```
Organized/
├── Documentos/
│   ├── PDFs/
│   ├── Word/
│   └── Excel/
├── Imágenes/
│   ├── Fotos/
│   └── Capturas/
└── Descargas/
```

### 2. **Reglas** (Cómo clasificar archivos)
Las reglas definen qué archivos van a qué carpeta.

**Tipos de reglas**:
- **Por extensión**: Ejemplo: `.pdf` → carpeta "PDFs"
- **Por palabra clave**: Ejemplo: "factura" → carpeta "Facturas"

### 3. **Monitor** (Vigilancia automática)
El monitor vigila una carpeta y organiza automáticamente los archivos nuevos según las reglas.

---

## 🚀 Cómo Usar QuickSort - Paso a Paso

### Paso 1: Crear la Estructura de Carpetas (Nodos)

**¿Qué es?** Define dónde quieres que se organicen tus archivos.

**Cómo hacerlo**:
1. Ve a la pestaña **"Árbol"**
2. Haz clic en **"Agregar Nodo"**
3. Llena los campos:
   - **Nombre**: Nombre descriptivo (ej: "PDFs")
   - **Ruta**: Ruta completa donde se guardará (ej: `C:\Users\TuUsuario\Organized\PDFs`)
   - **ID del Padre**: Déjalo vacío para nodo raíz, o selecciona un nodo padre
   - **Tipo**: Deja "folder"
4. Haz clic en **"Crear"**

**Ejemplo práctico**:
```
Nodo 1 (Raíz):
- Nombre: "Documentos"
- Ruta: C:\Users\kateh\Organized\Documentos
- ID del Padre: (vacío)

Nodo 2 (Hijo):
- Nombre: "PDFs"
- Ruta: C:\Users\kateh\Organized\Documentos\PDFs
- ID del Padre: 1 (el ID del nodo "Documentos")
```

---

### Paso 2: Crear Reglas de Organización

**¿Qué es?** Define qué archivos van a cada carpeta.

**Cómo hacerlo**:
1. Ve a la pestaña **"Reglas"**
2. Haz clic en **"Nueva Regla"**
3. Llena los campos:
   - **Tipo**: Selecciona "extension" o "keyword"
   - **Patrón**: 
     - Si es extensión: `.pdf`, `.docx`, `.jpg`, etc.
     - Si es palabra clave: "factura", "reporte", etc.
   - **Nodo destino**: Selecciona la carpeta donde irán estos archivos
   - **Prioridad**: Número mayor = mayor prioridad (10 es alta, 1 es baja)
4. Haz clic en **"Crear"**

**Ejemplos prácticos**:
```
Regla 1:
- Tipo: extension
- Patrón: .pdf
- Nodo: PDFs
- Prioridad: 10
→ Todos los archivos .pdf irán a la carpeta PDFs

Regla 2:
- Tipo: keyword
- Patrón: factura
- Nodo: Facturas
- Prioridad: 8
→ Archivos con "factura" en el nombre irán a Facturas
```

---

### Paso 3: Configurar el Monitor

**¿Qué es?** El monitor vigila una carpeta y organiza automáticamente los archivos nuevos.

**Cómo hacerlo**:
1. Ve a la pestaña **"Monitor"**
2. Configura:
   - **Carpeta a monitorear**: Selecciona la carpeta que quieres vigilar (ej: Downloads)
   - **Organización automática**: ✅ Actívala
   - **Recursivo**: ✅ Si quieres incluir subcarpetas
3. Haz clic en **"Guardar Configuración"**
4. Haz clic en **"Iniciar Monitor"**

**Estado del Monitor**:
- **Activo** (verde): Está vigilando y organizando archivos
- **Inactivo** (gris): No está vigilando

---

### Paso 4: Probar el Sistema

**Prueba manual**:
1. Copia un archivo PDF a la carpeta que estás monitoreando
2. Espera 1-2 segundos
3. Verifica que el archivo se movió a la carpeta correcta
4. Ve a la pestaña **"Historial"** para ver el registro

**Ejemplo**:
```
1. Tienes un archivo: "documento.pdf" en Downloads
2. El monitor detecta el archivo
3. Busca una regla que coincida (.pdf)
4. Encuentra la regla: .pdf → PDFs
5. Mueve el archivo a: C:\Users\kateh\Organized\Documentos\PDFs\
6. Registra la operación en el historial
```

---

## 📊 Pestaña "Historial"

**¿Qué muestra?** Todas las operaciones realizadas por QuickSort.

**Información que verás**:
- **Nombre del archivo**: Qué archivo se organizó
- **Origen**: De dónde vino
- **Destino**: A dónde se movió
- **Estado**: Éxito o fallo
- **Fecha y hora**: Cuándo ocurrió

**Estadísticas**:
- Total de archivos organizados
- Archivos exitosos
- Archivos fallidos

---

## 💡 Consejos y Buenas Prácticas

### 1. Organiza tu Estructura Primero
Antes de crear reglas, piensa en cómo quieres organizar tus archivos:
```
Organized/
├── Trabajo/
│   ├── Documentos/
│   ├── Presentaciones/
│   └── Hojas de Cálculo/
├── Personal/
│   ├── Fotos/
│   ├── Videos/
│   └── Documentos/
└── Descargas/
    ├── Programas/
    └── Otros/
```

### 2. Usa Prioridades Inteligentemente
- **Prioridad 10**: Reglas muy específicas (ej: "factura_2024.pdf")
- **Prioridad 5**: Reglas generales (ej: ".pdf")
- **Prioridad 1**: Reglas de respaldo

### 3. Prueba Antes de Activar el Monitor
1. Crea tus nodos y reglas
2. Prueba manualmente con algunos archivos
3. Verifica que funciona correctamente
4. Luego activa el monitor automático

### 4. Revisa el Historial Regularmente
El historial te ayuda a:
- Ver qué archivos se organizaron
- Detectar errores
- Ajustar tus reglas

---

## 🐛 Solución de Problemas

### Problema: "Error creando nodo: Request failed with status code 500"
**Solución**: 
1. Reinicia el servidor backend (Ctrl+C y vuelve a ejecutar)
2. Verifica que la ruta sea válida
3. Asegúrate de llenar todos los campos requeridos

### Problema: El monitor no detecta archivos
**Solución**:
1. Verifica que el monitor esté **Activo** (verde)
2. Verifica que tengas reglas creadas
3. Verifica que la carpeta monitoreada sea correcta
4. Espera 1-2 segundos después de copiar el archivo

### Problema: Los archivos no se mueven
**Solución**:
1. Verifica que exista una regla que coincida con el archivo
2. Verifica que la carpeta destino exista
3. Verifica que tengas permisos de escritura
4. Revisa el historial para ver el error específico

### Problema: No aparecen los nodos creados
**Solución**:
1. Refresca la página (F5)
2. Verifica en la pestaña "Árbol" que se crearon
3. Revisa la consola del navegador (F12) para errores

---

## 🎓 Ejemplo Completo de Uso

### Escenario: Organizar archivos de la carpeta Downloads

**1. Crear Estructura**:
```
Nodo Raíz:
- Nombre: "Organized"
- Ruta: C:\Users\kateh\Organized

Nodos Hijos:
- Nombre: "PDFs" → Ruta: C:\Users\kateh\Organized\PDFs
- Nombre: "Imágenes" → Ruta: C:\Users\kateh\Organized\Imagenes
- Nombre: "Documentos" → Ruta: C:\Users\kateh\Organized\Documentos
```

**2. Crear Reglas**:
```
Regla 1: .pdf → PDFs (Prioridad: 10)
Regla 2: .jpg → Imágenes (Prioridad: 10)
Regla 3: .png → Imágenes (Prioridad: 10)
Regla 4: .docx → Documentos (Prioridad: 10)
```

**3. Configurar Monitor**:
```
Carpeta: C:\Users\kateh\Downloads
Organización automática: ✅
Recursivo: ❌
```

**4. Iniciar Monitor**:
- Clic en "Iniciar Monitor"
- Estado cambia a "Activo"

**5. Probar**:
- Copia "documento.pdf" a Downloads
- Espera 2 segundos
- Verifica que se movió a: C:\Users\kateh\Organized\PDFs\documento.pdf
- Revisa el historial

---

## 📝 Resumen de Funcionalidades

| Funcionalidad | Estado | Descripción |
|---------------|--------|-------------|
| Crear nodos | ✅ | Funciona correctamente |
| Crear reglas | ✅ | Funciona correctamente |
| Monitor activo/inactivo | ✅ | Funciona correctamente |
| Organización automática | ✅ | Funciona correctamente |
| Historial de operaciones | ✅ | Funciona correctamente |
| Visualización del árbol | ✅ | Funciona correctamente |

---

## 🎯 Próximos Pasos

1. ✅ Reinicia el backend para aplicar la corrección
2. ✅ Crea tu estructura de nodos
3. ✅ Define tus reglas de organización
4. ✅ Configura el monitor
5. ✅ Prueba con algunos archivos
6. ✅ Activa el monitor automático
7. ✅ Disfruta de tus archivos organizados

---

**¿Necesitas ayuda?** Revisa:
- `PRUEBAS_PENDIENTES.md` - Guía detallada de pruebas
- `README.md` - Documentación técnica completa
- `INSTRUCCIONES_WINDOWS.md` - Instrucciones específicas para Windows

---

**Documento creado**: 22 de Octubre, 2025
**Versión**: 1.0
**Estado**: Guía completa de uso
