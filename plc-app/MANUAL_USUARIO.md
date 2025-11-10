# 📘 Manual de Usuario - Sistema de Control de Calidad Industrial

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Acceso al Sistema](#acceso-al-sistema)
3. [Dashboard Principal](#dashboard-principal)
4. [Módulo de Producción](#módulo-de-producción)
5. [Módulo de Historial](#módulo-de-historial)
6. [Módulo de Gestión](#módulo-de-gestión)
   - [Recetas](#recetas)
   - [Lotes](#lotes)
   - [Usuarios](#usuarios)
   - [Roles y Permisos](#roles-y-permisos)
7. [Exportación de Datos](#exportación-de-datos)
8. [Solución de Problemas](#solución-de-problemas)
9. [Glosario de Términos](#glosario-de-términos)

---

## 1. Introducción

### 1.1 ¿Qué es este sistema?

Este sistema de control de calidad industrial permite gestionar y monitorear la producción de cables en tiempo real, registrando cada pieza procesada, sus resultados de calidad, y generando reportes detallados para análisis y trazabilidad.

### 1.2 Características Principales

- ✅ **Monitoreo en Tiempo Real**: Visualización instantánea del estado de la línea de producción
- ✅ **Control de Lotes**: Gestión completa de lotes de producción con objetivos y seguimiento
- ✅ **Registro de Defectos**: Captura automática de imágenes de piezas defectuosas
- ✅ **Reportes y Exportación**: Generación de reportes en formato CSV para análisis
- ✅ **Gestión de Usuarios**: Control de acceso mediante roles y permisos
- ✅ **Historial Completo**: Consulta de todos los lotes procesados con detalles completos

### 1.3 Requisitos del Sistema

- Navegador web moderno (Chrome, Firefox, Edge, Safari)
- Conexión a internet o red local
- Credenciales de acceso proporcionadas por el administrador

---

## 2. Acceso al Sistema

### 2.1 Inicio de Sesión

**Paso 1:** Abra su navegador web y acceda a la dirección del sistema proporcionada por su administrador.

**Paso 2:** Se mostrará la pantalla de inicio de sesión.

<img width="784" height="912" alt="image" src="https://github.com/user-attachments/assets/98fe6ab2-0f3f-4781-97da-fe87a4208a8b" />

{Imagen del login del sistema mostrando los campos de usuario y contraseña, con el botón de inicio de sesión}


**Paso 3:** Ingrese sus credenciales:
- **Usuario**: Ingrese su nombre de usuario
- **Contraseña**: Ingrese su contraseña

**Paso 4:** Haga clic en el botón **"Iniciar Sesión"** o presione **Enter**.

**Nota:** Si olvidó su contraseña, contacte al administrador del sistema.

### 2.2 Pantalla de Carga

Después de iniciar sesión, verá brevemente una pantalla de carga mientras el sistema prepara su sesión.

### 2.3 Primer Acceso

Si es la primera vez que accede al sistema, será redirigido automáticamente al Dashboard Principal.

---

## 3. Dashboard Principal

### 3.1 Vista General

El Dashboard Principal es la pantalla de inicio del sistema y proporciona una vista general del estado del sistema.

<img width="1781" height="911" alt="image" src="https://github.com/user-attachments/assets/cd16d626-b90f-4061-a2a0-74fe9f615824" />

{Imagen del dashboard principal mostrando las tarjetas de estadísticas, lotes recientes y acceso rápido}

### 3.2 Secciones del Dashboard

#### 3.2.1 Encabezado de Bienvenida

En la parte superior encontrará:
- **Saludo personalizado** con su nombre de usuario
- **Título del sistema**: "Sistema de Control de Calidad Industrial"
- **Icono de fábrica** identificando el sistema

<img width="639" height="136" alt="image" src="https://github.com/user-attachments/assets/25f4b6df-0a0a-4c08-8264-6052082cb8f2" />

{Imagen del encabezado de bienvenida con el saludo y nombre de usuario}

#### 3.2.2 Tarjetas de Estadísticas

El dashboard muestra 4 tarjetas principales con estadísticas del sistema:

**1. Recetas Activas**
- Muestra el total de recetas (modelos) configuradas en el sistema
- Icono: Lista de verificación
- Color: Azul (Primary)

<img width="421" height="183" alt="image" src="https://github.com/user-attachments/assets/7c8fbe29-5d47-4887-9cfd-0e1743ed7f47" />

{Imagen de la tarjeta de Recetas Activas con el número total}

**2. Lotes Activos**
- Muestra la cantidad de lotes actualmente en producción
- Icono: Indicador de actividad
- Color: Amarillo (Warning)

<img width="431" height="195" alt="image" src="https://github.com/user-attachments/assets/600c07ce-a588-47cf-a524-606a9e7c5404" />

{Imagen de la tarjeta de Lotes Activos con el número actual}

**3. Piezas OK**
- Muestra el total acumulado de piezas aprobadas en todos los lotes
- Icono: Check verde
- Color: Verde (Success)

<img width="432" height="208" alt="image" src="https://github.com/user-attachments/assets/0ff67ca4-2212-4ced-8345-d52ee4ede488" />

{Imagen de la tarjeta de Piezas OK con el total acumulado}

#### 3.2.3 Lotes Recientes

Muestra una tabla con los últimos 5 lotes procesados, incluyendo:
- Nombre del lote
- Receta (PPN)
- Estado (Abierto, Cerrado, Pausado)
- Piezas OK y NOK
- Fecha de inicio
- Creado por

<img width="1771" height="356" alt="image" src="https://github.com/user-attachments/assets/63f8b751-8f5d-4459-8e14-d928e5af8c52" />

{Imagen de la tabla de Lotes Recientes}

### 3.3 Navegación

#### 3.3.1 Barra Lateral (Sidebar)

La barra lateral izquierda contiene el menú principal de navegación:

<img width="125" height="922" alt="image" src="https://github.com/user-attachments/assets/3079cc3e-d38b-41e2-998d-4070334cb1da" />

{Imagen de la barra lateral con todos los elementos del menú}

**Elementos del Menú:**
- **🏠 Dashboard**: Regresa a la página principal
- **🏭 Production**: Control de producción en tiempo real
- **📊 History**: Historial de lotes completados
- **⚙️ Management**: Gestión de recetas, lotes, usuarios y roles
- **🚪 Logout**: Cerrar sesión

**Nota:** Solo verá las opciones para las que tiene permisos. Si no tiene acceso a una sección, no aparecerá en el menú.

#### 3.3.2 Cerrar Sesión

**Paso 1:** Haga clic en el botón **"Logout"** en la parte inferior de la barra lateral.

**Paso 2:** Se cerrará su sesión y será redirigido a la pantalla de inicio de sesión.

<img width="134" height="144" alt="image" src="https://github.com/user-attachments/assets/fed85b52-7ed5-44e5-8a2e-1f9034459514" />

{Imagen del botón de logout en la barra lateral}

---

## 4. Módulo de Producción

### 4.1 Acceso al Módulo

**Paso 1:** Desde el Dashboard Principal, haga clic en **"Production"** en la barra lateral o en el botón de acceso rápido.

**Paso 2:** Se abrirá la página de Control de Producción.

<img width="1904" height="915" alt="image" src="https://github.com/user-attachments/assets/b9253404-a05c-4e13-acfa-592c97034984" />

{Imagen de la página de producción mostrando el estado de la línea y controles}

### 4.2 Vista General de Producción

La página de producción muestra información en tiempo real sobre el estado de la línea de producción.

<img width="1470" height="809" alt="image" src="https://github.com/user-attachments/assets/ad1b4361-7012-48d6-a58f-0778611a126c" />

{Imagen completa de la página de producción con todas las secciones visibles}

### 4.3 Secciones de la Página de Producción

#### 4.3.1 Información del Lote Activo

Si hay un lote en producción, se muestra:
- **Nombre del lote**
- **Receta (PPN)** asociada
- **Model ID** del PLC
- **Objetivo de piezas OK**
- **Progreso actual**

<img width="1336" height="125" alt="image" src="https://github.com/user-attachments/assets/ce2a4c95-61a2-4d0e-9df6-d433c179c212" />

{Imagen de la sección de información del lote activo}

#### 4.3.2 Métricas en Tiempo Real

Se muestran 4 métricas principales:

**1. Eficiencia**
- Porcentaje de eficiencia de la línea
- Icono: Gráfico de barras

<img width="209" height="120" alt="image" src="https://github.com/user-attachments/assets/a349a000-8f8f-4253-b326-e986039898bd" />

{Imagen de la tarjeta de Eficiencia}

**2. Precisión**
- Porcentaje de piezas OK vs total
- Icono: Objetivo

<img width="265" height="153" alt="image" src="https://github.com/user-attachments/assets/f12bfaf8-4d70-4309-b284-ba40e523d806" />

{Imagen de la tarjeta de Precisión}

**3. Total de Piezas**
- Contador total de piezas procesadas
- Icono: Contador

<img width="1344" height="79" alt="image" src="https://github.com/user-attachments/assets/9ce1f234-f874-4c97-8de9-73777796cd4d" />

{Imagen de la tarjeta de Total de Piezas}

#### 4.3.4 Contadores de Piezas

Se muestran dos contadores grandes:
- **Piezas OK**: Contador verde con el total de piezas aprobadas
- **Piezas NOK**: Contador rojo con el total de piezas rechazadas

<img width="522" height="107" alt="image" src="https://github.com/user-attachments/assets/28716fe9-a222-40a4-9d8b-0b4d31eaa1b5" />

{Imagen de los contadores grandes de Piezas OK y NOK}

#### 4.3.5 Datos del PLC

Sección que muestra los datos en bruto recibidos del PLC:
- **Estado General**: OK, FALLA, MANTENIMIENTO
- **Estado de Pieza**: OK, NOK
- **Código de Falla**: Si aplica
- **Model ID**: ID del modelo actual
- **Estado de Cámara**: Activa/Inactiva
- **Estado Eléctrico**: OK/Error
- **Bandera de Listo**: Sí/No

<img width="1254" height="178" alt="image" src="https://github.com/user-attachments/assets/70f2ce27-5600-4e37-ae94-7718f354fa67" />

{Imagen de la sección de Datos del PLC con todos los campos}

#### 4.3.6 Piezas Recientes

Tabla que muestra las últimas piezas procesadas con:
- **Índice**: Número de pieza
- **Resultado**: OK o NOK
- **Código de Falla**: Si aplica
- **Timestamp**: Fecha y hora de procesamiento
- **Imagen**: Si tiene imagen asociada

<img width="1342" height="171" alt="image" src="https://github.com/user-attachments/assets/daecbd5a-228b-464b-97d1-6a20d84514b6" />

{Imagen de la tabla de Piezas Recientes}

### 4.4 Iniciar Producción

**Paso 1:** Verifique que no haya un lote activo. Si hay uno, debe detenerlo primero.

**Paso 2:** Haga clic en el botón **"Iniciar Producción"** (si tiene permisos).

**Paso 3:** Seleccione el lote que desea iniciar de la lista desplegable.

**Paso 4:** Verifique la información del lote:
- Nombre del lote
- Receta (PPN)
- Model ID del PLC
- Objetivo de piezas OK

**Paso 5:** Haga clic en **"Confirmar"** para iniciar la producción.

**Paso 6:** El sistema iniciará la producción y comenzará a recibir datos del PLC.

<img width="1372" height="794" alt="image" src="https://github.com/user-attachments/assets/0bfe43e7-24e3-4809-949d-097bd3d2b513" />

{Imagen de inicio de producción}

### 4.5 Detener Producción

**Paso 1:** Haga clic en el botón **"Detener Producción"** (si tiene permisos).

**Paso 2:** Se abrirá un modal de confirmación.

<img width="698" height="649" alt="image" src="https://github.com/user-attachments/assets/bdf59ed9-74ee-4c01-87d3-2d3d3027c6b3" />

{Imagen del modal de confirmación para detener producción}

**Paso 3:** Revise la información:
- Nombre del lote que se detendrá
- Piezas procesadas hasta el momento
- Advertencia sobre la acción

**Paso 4:** Haga clic en **"Confirmar"** para detener la producción o **"Cancelar"** para continuar.

**Nota:** Al detener la producción, el lote se marcará como pausado y podrá reanudarse más tarde.

### 4.6 Manejo de Errores

#### 4.6.1 Modal de Error de Pieza

Cuando se detecta una pieza defectuosa, aparece automáticamente un modal de error:

<img width="658" height="751" alt="image" src="https://github.com/user-attachments/assets/675bad13-8405-40a4-9cc5-551c0f3282aa" />

{Imagen del modal de error mostrando la pieza defectuosa}

**Información mostrada:**
- **Mensaje de error**: Descripción del problema
- **Imagen del defecto**: Imagen capturada de la pieza defectuosa
- **Código de falla**: Código específico del tipo de falla
- **Índice de pieza**: Número de pieza defectuosa
- **Lote afectado**: Nombre del lote en producción

**Acciones disponibles:**
- **"Revisar"**: Cierra el modal y continúa la producción
- **"Detener Producción"**: Detiene la producción inmediatamente

#### 4.6.2 Paro de Emergencia

Si el PLC envía una señal de mantenimiento o paro de emergencia, 
El sistema automaticamente cierra la linea de produccion que se este ejecutando en ese momento:

- La producción se detiene automáticamente y debe reiniciarse manualmente después del mantenimiento

#### 4.6.3 Modal de Error de Model ID

Si el PLC envía un Model ID que no coincide con el lote activo, aparece un modal de error:

<img width="656" height="721" alt="image" src="https://github.com/user-attachments/assets/d05b9f6c-fed5-4666-815b-a0e9d6ba3262" />

{Imagen del modal de error de Model ID mostrando el mismatch}

**Información mostrada:**
- **Model ID Esperado**: El ID correcto para el lote activo
- **Model ID Recibido**: El ID que envió el PLC
- **Lote afectado**: Nombre del lote
- **Receta (PPN)**: Receta asociada
- **Tabla de referencia**: Lista de todos los Model IDs válidos (1-7)

**Importante:** La pieza NO se guarda en la base de datos para mantener la integridad de los datos.

**Acción requerida:**
- Verificar la configuración del PLC
- Asegurarse de que el PLC esté enviando el Model ID correcto

### 4.7 Actualización en Tiempo Real

La página de producción se actualiza automáticamente cada segundo mostrando:
- Nuevas piezas procesadas
- Cambios en las métricas
- Actualización del estado del PLC
- Nuevos errores detectados

**Nota:** No es necesario refrescar la página manualmente.

---

## 5. Módulo de Historial

### 5.1 Acceso al Módulo

**Paso 1:** Desde el Dashboard Principal o la barra lateral, haga clic en **"History"**.

**Paso 2:** Se abrirá la página de Historial de Lotes.

<img width="1470" height="804" alt="image" src="https://github.com/user-attachments/assets/4198ce05-a32c-434e-9b19-ab92231ecd50" />

{Imagen de la página de historial mostrando la lista de lotes}

### 5.2 Vista General del Historial

La página de historial muestra todos los lotes que han sido procesados o están pausados.

<img width="1340" height="419" alt="image" src="https://github.com/user-attachments/assets/9a356a80-9c3f-4fa2-b8df-6770cc8decb9" />

{Imagen completa de la página de historial con filtros y tabla}

### 5.3 Funcionalidades del Historial

#### 5.3.1 Búsqueda de Lotes

**Paso 1:** En el campo de búsqueda, ingrese el nombre del lote o el PPN de la receta.

**Paso 2:** Los resultados se filtrarán automáticamente mientras escribe.

<img width="1365" height="476" alt="image" src="https://github.com/user-attachments/assets/425cb570-e11b-4a85-a079-9026e85ff4d2" />

{Imagen del campo de búsqueda con texto de ejemplo}

#### 5.3.2 Filtro por Estado

**Paso 1:** Haga clic en el menú desplegable de estado.

**Paso 2:** Seleccione el estado deseado:
- **Todos**: Muestra todos los lotes
- **Cerrados**: Solo lotes completados
- **Pausados**: Solo lotes pausados

<img width="1370" height="510" alt="image" src="https://github.com/user-attachments/assets/d9600b1c-c9f7-4dae-bb13-6f9507bdd69c" />

{Imagen del filtro de estado con las opciones}

#### 5.3.3 Tabla de Lotes

La tabla muestra la siguiente información para cada lote:

**Columnas:**
- **Nombre**: Nombre del lote
- **Receta (PPN)**: Part Number de la receta
- **Estado**: OPEN, CLOSED, PAUSED
- **Piezas OK**: Cantidad de piezas aprobadas
- **Piezas NOK**: Cantidad de piezas rechazadas
- **Total**: Suma de piezas OK y NOK
- **Precisión**: Porcentaje de precisión
- **Fecha de Inicio**: Cuándo se inició el lote
- **Fecha de Cierre**: Cuándo se cerró (si aplica)
- **Creado por**: Usuario que creó el lote
- **Acciones**: Botón para ver detalles

<img width="1349" height="315" alt="image" src="https://github.com/user-attachments/assets/17312417-e9f2-4f85-8db1-c4d6c10a1ff2" />

{Imagen de la tabla de lotes con todas las columnas visibles}

#### 5.3.4 Ver Detalles de un Lote

**Paso 1:** En la columna "Acciones", haga clic en el botón **"View Details"** del lote que desea ver.

**Paso 2:** Se abrirá la página de detalles del lote.

<img width="171" height="114" alt="image" src="https://github.com/user-attachments/assets/e31f50f8-432f-4d68-b052-2b9ee386e59a" />

{Imagen del botón "View Details" en la tabla}

### 5.4 Página de Detalles del Lote

La página de detalles muestra información completa sobre un lote específico.

<img width="1470" height="811" alt="image" src="https://github.com/user-attachments/assets/8f5a4381-6b49-4327-9a3a-b4b7a9cc3f08" />

<img width="1371" height="804" alt="image" src="https://github.com/user-attachments/assets/ef880698-15ff-4094-bb72-ba4da26e29ac" />

{Imagen completa de la página de detalles del lote}

#### 5.4.1 Información General del Lote

<img width="1367" height="651" alt="image" src="https://github.com/user-attachments/assets/c4f4336b-3c04-4fb6-a339-222fb090b942" />

Se muestra en la parte superior:
- **Nombre del lote**
- **Receta (PPN)** asociada
- **Estado actual**: OPEN, CLOSED, PAUSED
- **Fecha de inicio**
- **Fecha de cierre** (si aplica)
- **Creado por**: Usuario que creó el lote

{Imagen de la sección de información general del lote}

#### 5.4.2 Estadísticas del Lote

Se muestran 4 tarjetas con estadísticas:

**1. Piezas OK**
- Total de piezas aprobadas
- Icono: Check verde
- Color: Verde

<img width="351" height="150" alt="image" src="https://github.com/user-attachments/assets/7e8bade6-4495-4004-8a96-e1bb44a303c8" />

{Imagen de la tarjeta de Piezas OK}

**2. Piezas NOK**
- Total de piezas rechazadas
- Icono: X rojo
- Color: Rojo

<img width="306" height="130" alt="image" src="https://github.com/user-attachments/assets/87b7eade-79ee-4ff6-bc52-65d4a7fbc88a" />

{Imagen de la tarjeta de Piezas NOK}

**3. Total de Piezas**
- Suma de piezas OK y NOK
- Icono: Paquete
- Color: Azul

<img width="286" height="121" alt="image" src="https://github.com/user-attachments/assets/e8f614c5-5c63-43b0-ab0d-dd00ffb19a11" />

{Imagen de la tarjeta de Total de Piezas}

Si el lote tiene piezas defectuosas con imágenes, se muestra una galería:

<img width="850" height="531" alt="image" src="https://github.com/user-attachments/assets/67a90185-633c-4301-bcac-93f43c68c896" />

{Imagen de la galería de imágenes de defectos}

**Funcionalidades:**
- **Vista en miniatura**: Cada imagen se muestra como una miniatura
- **Clic para ampliar**: Haga clic en una imagen para verla en tamaño completo
- **Información de la imagen**: Al pasar el mouse, se muestra el tipo de falla y timestamp

**Paso 1:** Haga clic en una imagen de la galería.

**Paso 2:** Se abrirá un modal con la imagen en tamaño completo.

<img width="1054" height="663" alt="image" src="https://github.com/user-attachments/assets/37e093eb-7a2f-4b4a-8331-b58825dc97b3" />

{Imagen del modal de imagen ampliada}

**Paso 3:** En el modal puede ver:
- Imagen en alta resolución
- Tipo de falla
- Timestamp de captura
- Botón para cerrar

**Paso 4:** Haga clic fuera del modal o en el botón X para cerrar.

#### 5.4.4 Tabla de Piezas

Tabla completa con todas las piezas del lote:

**Columnas:**
- **Índice**: Número de pieza
- **Resultado**: OK o NOK
- **Código de Falla**: Si aplica
- **Timestamp**: Fecha y hora de procesamiento
- **Tiene Imagen**: Indicador si hay imagen asociada

<img width="1299" height="483" alt="image" src="https://github.com/user-attachments/assets/71ba411f-8d0c-4bbb-8fbd-13ebf04c9f15" />

{Imagen de la tabla de piezas con todas las columnas}

**Funcionalidades:**
- **Ordenamiento**: Haga clic en el encabezado de una columna para ordenar
- **Scroll**: Si hay muchas piezas, puede hacer scroll vertical
- **Búsqueda**: Use Ctrl+F para buscar texto específico

### 5.5 Exportación de Datos

#### 5.5.1 Exportar un Lote Individual

**Paso 1:** En la página de detalles del lote, haga clic en el botón **"Export to CSV"**.

<img width="1334" height="287" alt="image" src="https://github.com/user-attachments/assets/79958703-856a-4c5f-b78c-63019c2dc79f" />

{Imagen del botón "Export to CSV" en la página de detalles}

**Paso 2:** Se descargará automáticamente un archivo CSV con:
- Información general del lote
- Estadísticas completas
- Lista detallada de todas las piezas
- Información de imágenes asociadas

<img width="1199" height="956" alt="image" src="https://github.com/user-attachments/assets/2ac3c41c-c24d-49ba-8f1f-4c55f348412b" />


**Paso 3:** El archivo se guardará en su carpeta de descargas con el nombre: `lote_{nombre_lote}_{fecha}.csv`

#### 5.5.2 Exportar Todos los Lotes

**Paso 1:** En la página principal de historial, haga clic en el botón **"Export All to CSV"**.

{Imagen del botón "Export All to CSV" en la página de historial}

**Paso 2:** Se descargará un archivo CSV con todos los lotes filtrados (según los filtros aplicados).

**Paso 3:** El archivo incluirá:
- Información de todos los lotes
- Estadísticas de cada lote
- Fecha de generación del reporte

<img width="966" height="298" alt="image" src="https://github.com/user-attachments/assets/7e4929ad-78fd-46ef-bfaa-3a2d43291c95" />


**Paso 4:** El archivo se guardará con el nombre: `lotes_{fecha_hora}.csv`

**Nota:** Los archivos CSV pueden abrirse en Excel, Google Sheets o cualquier editor de texto.

---

## 6. Módulo de Gestión

### 6.1 Acceso al Módulo

**Paso 1:** Desde el Dashboard Principal o la barra lateral, haga clic en **"Management"**.

**Paso 2:** Se abrirá la página principal de Gestión.

<img width="1470" height="567" alt="image" src="https://github.com/user-attachments/assets/3d478fdc-6060-4fe1-bfec-b2ddc1ef729e" />

{Imagen de la página principal de gestión con las 4 secciones}

### 6.2 Secciones de Gestión

La página principal muestra 4 secciones principales:

1. **📖 Recipes (Recetas)**: Gestión de recetas/modelos
2. **📦 Lots (Lotes)**: Gestión de lotes de producción
3. **👥 Users (Usuarios)**: Gestión de usuarios del sistema
4. **🛡️ Roles & Permissions (Roles y Permisos)**: Configuración de roles y permisos

<img width="1072" height="244" alt="image" src="https://github.com/user-attachments/assets/48a94501-1d21-4651-be5e-5f78e0fd89b5" />

{Imagen de las 4 tarjetas de secciones de gestión}

**Nota:** Solo verá las secciones para las que tiene permisos de acceso.

---

## 6.3 Recetas

### 6.3.1 Acceso a Recetas

**Paso 1:** En la página de Gestión, haga clic en la tarjeta **"Recipes"**.

**Paso 2:** Se abrirá la página de gestión de recetas.

{Imagen de la página de recetas con la tabla de recetas}

### 6.3.2 Vista de Recetas

La página muestra una tabla con todas las recetas configuradas en el sistema.

<img width="1352" height="727" alt="image" src="https://github.com/user-attachments/assets/d9b7b3a3-d538-40cc-abdf-f9ad5753c014" />

{Imagen completa de la página de recetas con tabla y controles}

#### 6.3.3 Información de las Recetas

Cada receta muestra:
- **Model ID**: ID del modelo para el PLC (1-7)
- **PPN (Part Number)**: Número de parte único
- **Cable NP**: Número de cable
- **Descripción**: Descripción del artículo
- **Conductores**: Cantidad de conductores
- **Terminales**: Terminales L1, L2, L3, L4, L5
- **Estado**: Activa/Inactiva
- **Acciones**: Botones para editar o eliminar

<img width="1296" height="474" alt="image" src="https://github.com/user-attachments/assets/61794069-0a4f-4c15-a44d-38ccf6726cc0" />

{Imagen de la tabla de recetas con todas las columnas}

### 6.3.4 Crear una Nueva Receta

**Paso 1:** Haga clic en el botón **"New Recipe"** (si tiene permisos).

{Imagen del botón "New Recipe"}

**Paso 2:** Se abrirá un modal para crear la receta.

<img width="493" height="707" alt="image" src="https://github.com/user-attachments/assets/a161dec8-e8eb-490b-a8a4-1a456ca7c9cb" />

{Imagen del modal de creación de receta}

**Paso 3:** Complete los siguientes campos:

- **Model ID** (Requerido):
  - Seleccione un ID del 1 al 7
  - Cada ID debe ser único
  - Este ID se envía al PLC para identificar el modelo

- **PPN (Part Number)** (Requerido):
  - Ingrese el número de parte único
  - Ejemplo: "1020746", "1020746-02", "698330001"
  - Debe ser único en el sistema

- **Cable NP** (Requerido):
  - Ingrese el número de cable
  - Ejemplo: "CABLE-001"

- **Quantity** (Requerido):
  - Cantidad en pies
  - Ejemplo: 100.0

- **Unit of Measure** (Requerido):
  - Unidad de medida
  - Generalmente "FT" (Feet)

- **Item Description** (Requerido):
  - Descripción del artículo
  - Ejemplo: "Cable 2 conductores"

- **Cantidad de Conductores** (Requerido):
  - Número de conductores
  - Ejemplo: 2 o 4

- **Terminales** (Opcional):
  - L1 Terminal
  - L2 Terminal
  - L3 Terminal
  - L4 Terminal
  - L5 Terminal

- **Estado**:
  - Marque "Activa" para habilitar la receta
  - Desmarque para deshabilitar

**Paso 4:** Haga clic en **"Create"** para guardar la receta.

**Paso 5:** Si hay errores, se mostrarán mensajes de validación.

*** OJO: LAS RECETAS NUEVAS QUE SE AGREGEN TIENEN QUE REGISTRARSE EN EL PLC DE NO HACERLO LOS LOTES CON LAS RECETAS NUEVAS NO FUNCIONARAN CORRECTAMENTE

### 6.3.5 Editar una Receta

**Paso 1:** En la tabla de recetas, haga clic en el botón de editar (icono de lápiz) de la receta que desea modificar.

<img width="172" height="93" alt="image" src="https://github.com/user-attachments/assets/4f83d819-82b8-4fc3-a2b3-d8d7eb57cbbe" />

{Imagen del botón de editar en la tabla}

**Paso 2:** Se abrirá un modal con los datos actuales de la receta.

<img width="485" height="700" alt="image" src="https://github.com/user-attachments/assets/94b33e55-468f-495b-8c13-a190d013929b" />

{Imagen del modal de edición de receta}

**Paso 3:** Modifique los campos que desee cambiar.

**Paso 4:** Haga clic en **"Update"** para guardar los cambios.

**Nota:** El Model ID y el PPN no pueden modificarse una vez creada la receta.

### 6.3.6 Eliminar una Receta

**Paso 1:** En la tabla de recetas, haga clic en el botón de eliminar (icono de basura) de la receta que desea eliminar.

<img width="62" height="66" alt="image" src="https://github.com/user-attachments/assets/9a0a402b-4100-4859-9c7b-ad8c68c6f180" />

{Imagen del botón de eliminar}

**Paso 2:** Se mostrará un mensaje de confirmación.

**Paso 3:** Confirme la eliminación.

**Advertencia:** No se puede eliminar una receta que esté asociada a lotes existentes.

### 6.3.7 Buscar Recetas

**Paso 1:** Use el campo de búsqueda para filtrar recetas por:
- PPN (Part Number)
- Descripción
- Cable NP

**Paso 2:** Los resultados se filtrarán automáticamente mientras escribe.

<img width="1359" height="160" alt="image" src="https://github.com/user-attachments/assets/459cd29e-7978-4917-b1e3-4cc8ee05435f" />

{Imagen del campo de búsqueda de recetas}

---

## 6.4 Lotes

### 6.4.1 Acceso a Lotes

**Paso 1:** En la página de Gestión, haga clic en la tarjeta **"Lots"**.

**Paso 2:** Se abrirá la página de gestión de lotes.

<img width="529" height="144" alt="image" src="https://github.com/user-attachments/assets/f217e930-8e06-463f-b5b3-9114a47dd1f8" />

{Imagen de la página de lotes con la tabla}

### 6.4.2 Vista de Lotes

La página muestra una tabla con todos los lotes del sistema.

<img width="1470" height="806" alt="image" src="https://github.com/user-attachments/assets/2b240bc1-2677-4829-b43e-14dfd3a8beae" />

{Imagen completa de la página de lotes}

#### 6.4.3 Información de los Lotes

Cada lote muestra:
- **Nombre**: Nombre único del lote
- **Receta**: PPN de la receta asociada
- **Estado**: OPEN, CLOSED, PAUSED
- **Piezas OK**: Cantidad de piezas aprobadas
- **Piezas NOK**: Cantidad de piezas rechazadas
- **Objetivo**: Meta de piezas OK
- **Fecha de Inicio**: Cuándo se inició
- **Fecha de Cierre**: Cuándo se cerró (si aplica)
- **Creado por**: Usuario que creó el lote
- **Acciones**: Botones para editar o eliminar

<img width="1338" height="339" alt="image" src="https://github.com/user-attachments/assets/fd36e616-ccde-4973-86ca-153dc70e0cd1" />

{Imagen de la tabla de lotes con todas las columnas}

### 6.4.4 Crear un Nuevo Lote

**Paso 1:** Haga clic en el botón **"New Lot"** (si tiene permisos).

<img width="1363" height="98" alt="image" src="https://github.com/user-attachments/assets/9ec02263-3d19-48cc-82de-19f3cde8a7ab" />

{Imagen del botón "New Lot"}

**Paso 2:** Se abrirá un modal para crear el lote.

<img width="897" height="439" alt="image" src="https://github.com/user-attachments/assets/7f650926-9c8c-480d-aef6-ccfb51315d4e" />

{Imagen del modal de creación de lote}

**Paso 3:** Complete los siguientes campos:

- **Nombre del Lote** (Requerido):
  - Ingrese un nombre único para el lote
  - Ejemplo: "LOTE-2024-001"
  - No puede duplicarse

- **Receta** (Requerido):
  - Seleccione la receta de la lista desplegable
  - Solo se muestran recetas activas
  - El Model ID se asignará automáticamente

- **Objetivo de Piezas OK** (Requerido):
  - Ingrese la cantidad objetivo de piezas aprobadas
  - Ejemplo: 1000
  - Debe ser un número positivo

**Paso 4:** Haga clic en **"Create"** para crear el lote.

**Paso 5:** El lote se creará con estado "OPEN" y estará listo para iniciar producción.

### 6.4.5 Editar un Lote

**Paso 1:** En la tabla de lotes, haga clic en el botón de editar (icono de lápiz) del lote que desea modificar.

<img width="158" height="203" alt="image" src="https://github.com/user-attachments/assets/87d95e89-9b2d-488f-bc87-520450371405" />

{Imagen del botón de editar}

**Paso 2:** Se abrirá un modal con los datos actuales del lote.

<img width="283" height="293" alt="image" src="https://github.com/user-attachments/assets/ddcbded4-68aa-4c22-be17-8a86a3396e21" />

{Imagen del modal de edición de lote}

**Paso 3:** Puede modificar:
- **Objetivo de Piezas OK**: Ajustar la meta
- **Estado**: Cambiar entre OPEN, CLOSED, PAUSED

**Paso 4:** Haga clic en **"Update"** para guardar los cambios.

**Nota:** El nombre del lote y la receta no pueden modificarse una vez creado el lote.

### 6.4.6 Cerrar un Lote

**Paso 1:** Edite el lote que desea cerrar.

**Paso 2:** En el campo "Estado", seleccione **"CLOSED"**.

**Paso 3:** Guarde los cambios.

**Nota:** Un lote cerrado no puede reabrirse. Asegúrese de que la producción esté completa antes de cerrarlo.

### 6.4.7 Eliminar un Lote

**Paso 1:** En la tabla de lotes, haga clic en el botón de eliminar (icono de basura) del lote que desea eliminar.

<img width="67" height="57" alt="image" src="https://github.com/user-attachments/assets/5969081a-e970-473b-9415-8f18bb70ed53" />

{Imagen del botón de eliminar}

**Paso 2:** Se mostrará un mensaje de confirmación.

<img width="455" height="146" alt="image" src="https://github.com/user-attachments/assets/8472f00b-78d6-4ff6-a624-eac1bf8b877f" />


**Paso 3:** Confirme la eliminación.

**Advertencia:** Eliminar un lote también eliminará todas las piezas e imágenes asociadas. Esta acción no se puede deshacer.

### 6.4.8 Buscar Lotes

**Paso 1:** Use el campo de búsqueda para filtrar lotes por:
- Nombre del lote
- PPN de la receta

**Paso 2:** Los resultados se filtrarán automáticamente.

<img width="1349" height="233" alt="image" src="https://github.com/user-attachments/assets/8a0a77d8-c20f-4f29-811b-91f66447eecb" />

{Imagen del campo de búsqueda de lotes}

---

## 6.5 Usuarios

### 6.5.1 Acceso a Usuarios

**Paso 1:** En la página de Gestión, haga clic en la tarjeta **"Users"**.

**Paso 2:** Se abrirá la página de gestión de usuarios.

<img width="634" height="146" alt="image" src="https://github.com/user-attachments/assets/98bca81e-05c6-4b0f-814c-32570b562189" />

{Imagen de la página de usuarios con la tabla}

### 6.5.2 Vista de Usuarios

La página muestra una tabla con todos los usuarios del sistema.

<img width="1470" height="792" alt="image" src="https://github.com/user-attachments/assets/e479adc4-0e41-4caf-bf05-ee4da630d083" />

{Imagen completa de la página de usuarios}

#### 6.5.3 Información de los Usuarios

Cada usuario muestra:
- **Usuario**: Nombre de usuario
- **Estado**: Activo/Inactivo
- **Roles**: Roles asignados
- **Fecha de Creación**: Cuándo se creó la cuenta
- **Acciones**: Botones para editar o eliminar

<img width="1298" height="223" alt="image" src="https://github.com/user-attachments/assets/5372a141-62da-4cd1-9c21-951149159c89" />

{Imagen de la tabla de usuarios con todas las columnas}

### 6.5.4 Crear un Nuevo Usuario

**Paso 1:** Haga clic en el botón **"New User"** (si tiene permisos).

{Imagen del botón "New User"}

**Paso 2:** Se abrirá un modal para crear el usuario.

<img width="553" height="484" alt="image" src="https://github.com/user-attachments/assets/8f27cd7a-8179-4956-bd13-a3794a4620bf" />

{Imagen del modal de creación de usuario}

**Paso 3:** Complete los siguientes campos:

- **Usuario** (Requerido):
  - Ingrese un nombre de usuario único
  - Ejemplo: "operador01"
  - No puede duplicarse

- **Contraseña** (Requerido):
  - Ingrese una contraseña segura
  - Mínimo 6 caracteres recomendado
  - Se mostrará/ocultará con el icono de ojo

- **Confirmar Contraseña** (Requerido):
  - Ingrese la misma contraseña para confirmar

- **Roles** (Requerido):
  - Seleccione uno o más roles de la lista
  - Los roles determinan los permisos del usuario
  - Puede seleccionar múltiples roles

- **Estado**:
  - Marque "Activo" para habilitar el usuario
  - Desmarque para deshabilitar (el usuario no podrá iniciar sesión)

**Paso 4:** Haga clic en **"Create"** para crear el usuario.

**Paso 5:** El usuario podrá iniciar sesión inmediatamente si está activo.

### 6.5.5 Editar un Usuario

**Paso 1:** En la tabla de usuarios, haga clic en el botón de editar (icono de lápiz) del usuario que desea modificar.

<img width="82" height="62" alt="image" src="https://github.com/user-attachments/assets/dd919bb9-a91d-4ed4-9d16-a77d596bcb98" />

{Imagen del botón de editar}

**Paso 2:** Se abrirá un modal con los datos actuales del usuario.

<img width="260" height="231" alt="image" src="https://github.com/user-attachments/assets/6c8f3967-1eb5-4302-ad72-0d7e6c41b975" />

{Imagen del modal de edición de usuario}

**Paso 3:** Puede modificar:
- **Nombre de usuario**: Dejar en blanco para mantener la actual, o ingresar una nueva

**Paso 4:** Haga clic en **"Update"** para guardar los cambios.

### 6.5.6 Eliminar un Usuario

**Paso 1:** En la tabla de usuarios, haga clic en el botón de eliminar (icono de basura) del usuario que desea eliminar.

<img width="58" height="120" alt="image" src="https://github.com/user-attachments/assets/2c71d4c5-2a3d-4241-a689-30a29fd2b487" />

{Imagen del botón de eliminar}

**Paso 2:** Se mostrará un mensaje de confirmación.

**Paso 3:** Confirme la eliminación.

**Advertencia:** Eliminar un usuario también eliminará todas sus sesiones activas. Esta acción no se puede deshacer.

### 6.5.7 Buscar Usuarios

**Paso 1:** Use el campo de búsqueda para filtrar usuarios por nombre de usuario.

**Paso 2:** Los resultados se filtrarán automáticamente.

<img width="1339" height="165" alt="image" src="https://github.com/user-attachments/assets/844be1bb-d95b-4b6d-95dc-8b775d18a22d" />

{Imagen del campo de búsqueda de usuarios}

---

## 6.6 Roles y Permisos

### 6.6.1 Acceso a Roles y Permisos

**Paso 1:** En la página de Gestión, haga clic en la tarjeta **"Roles & Permissions"**.

**Paso 2:** Se abrirá la página de gestión de roles.

<img width="662" height="121" alt="image" src="https://github.com/user-attachments/assets/d1a85eb3-e078-490f-b5ca-5e10bcc0eba3" />

{Imagen de la página de roles con la tabla}

### 6.6.2 Vista de Roles

La página muestra una tabla con todos los roles configurados en el sistema.

<img width="1470" height="603" alt="image" src="https://github.com/user-attachments/assets/f821b262-ec2d-4290-929c-8ccdd890893e" />

{Imagen completa de la página de roles}

#### 6.6.3 Información de los Roles

Cada rol muestra:
- **Nombre del Rol**: Nombre único del rol
- **Descripción**: Descripción del rol
- **Permisos**: Cantidad de permisos asignados
- **Usuarios**: Usuarios que tienen este rol asignado
- **Acciones**: Botones para gestionar permisos, editar o eliminar

<img width="1295" height="236" alt="image" src="https://github.com/user-attachments/assets/d34a6f83-6e86-4ef6-abef-4b42f74d27b5" />

{Imagen de la tabla de roles con todas las columnas}

### 6.6.4 Crear un Nuevo Rol

**Paso 1:** Haga clic en el botón **"New Role"** (si tiene permisos).

{Imagen del botón "New Role"}

**Paso 2:** Se abrirá un modal para crear el rol.

<img width="209" height="103" alt="image" src="https://github.com/user-attachments/assets/c450adcc-7ae7-4485-a4dd-ae8d23ae94d6" />

{Imagen del modal de creación de rol}

**Paso 3:** Complete los siguientes campos:

- **Nombre del Rol** (Requerido):
  - Ingrese un nombre único para el rol
  - Ejemplo: "Operador", "Supervisor", "Administrador"
  - No puede duplicarse

- **Descripción** (Requerido):
  - Ingrese una descripción del rol
  - Ejemplo: "Rol para operadores de línea de producción"

- **Permisos** (Opcional):
  - Seleccione los permisos que desea asignar al rol
  - Los permisos están organizados por categorías:
    - **production**: Control de producción
    - **history**: Acceso al historial
    - **management**: Gestión de datos
  - Puede seleccionar múltiples permisos

 <img width="396" height="606" alt="image" src="https://github.com/user-attachments/assets/4ffee7e6-98cd-484e-a122-617e6b07cf1f" />


**Paso 4:** Haga clic en **"Create"** para crear el rol.

**Paso 5:** El rol estará disponible para asignar a usuarios.

### 6.6.5 Gestionar Permisos de un Rol

**Paso 1:** En la tabla de roles, haga clic en el botón de permisos (icono de escudo) del rol que desea modificar.

<img width="57" height="158" alt="image" src="https://github.com/user-attachments/assets/0e55c5bb-2fbf-4a0f-854f-c8f4828011af" />

{Imagen del botón de permisos}

**Paso 2:** Se abrirá un modal para gestionar los permisos.

<img width="409" height="624" alt="image" src="https://github.com/user-attachments/assets/723fd768-029f-474d-a2a1-44ac55649fc6" />

{Imagen del modal de gestión de permisos}

**Paso 3:** Los permisos están organizados por categorías:

**Categoría: Production**
- `production.ver`: Ver página de producción
- `production.control.start`: Iniciar producción
- `production.control.stop`: Detener producción
- `production.metrics.ver`: Ver métricas

**Categoría: History**
- `history.ver`: Ver historial de lotes
- `history.lotes.detalles`: Ver detalles de lotes
- `history.lotes.exportar`: Exportar datos a CSV

**Categoría: Management**
- `management.ver`: Acceder a gestión
- `management.recetas.*`: Gestión completa de recetas
- `management.lotes.*`: Gestión completa de lotes
- `management.usuarios.*`: Gestión completa de usuarios
- `management.roles.*`: Gestión completa de roles

**Paso 4:** Marque o desmarque los permisos que desea asignar o quitar.

**Paso 5:** Use el filtro de categoría para encontrar permisos específicos.

**Paso 6:** Haga clic en **"Update Permissions"** para guardar los cambios.

### 6.6.6 Editar un Rol

**Paso 1:** En la tabla de roles, haga clic en el botón de editar (icono de lápiz) del rol que desea modificar.

<img width="57" height="177" alt="image" src="https://github.com/user-attachments/assets/0970d45e-ffb4-4075-aab6-9a2f5e686e19" />

{Imagen del botón de editar}

**Paso 2:** Se abrirá un modal con los datos actuales del rol.

<img width="283" height="327" alt="image" src="https://github.com/user-attachments/assets/b3cbd3d1-cdb0-425b-b0ee-600ac7415903" />

{Imagen del modal de edición de rol}

**Paso 3:** Puede modificar:
- **Descripción**: Cambiar la descripción del rol

**Paso 4:** Haga clic en **"Update"** para guardar los cambios.

**Nota:** El nombre del rol no puede modificarse una vez creado.

### 6.6.7 Eliminar un Rol

**Paso 1:** En la tabla de roles, haga clic en el botón de eliminar (icono de basura) del rol que desea eliminar.

**Paso 2:** Se mostrará un mensaje de confirmación.

**Paso 3:** Confirme la eliminación.

**Advertencia:** No se puede eliminar un rol que tenga usuarios asignados. Primero debe quitar el rol de todos los usuarios.

### 6.6.8 Buscar Roles

**Paso 1:** Use el campo de búsqueda para filtrar roles por nombre.

**Paso 2:** Los resultados se filtrarán automáticamente.

<img width="1344" height="254" alt="image" src="https://github.com/user-attachments/assets/e686df98-5044-42b3-912a-87f638b6670a" />

{Imagen del campo de búsqueda de roles}

---

## 7. Exportación de Datos

### 7.1 Formato de Exportación

Todos los datos se exportan en formato **CSV (Comma-Separated Values)**, que puede abrirse en:
- Microsoft Excel
- Google Sheets
- LibreOffice Calc
- Cualquier editor de texto

### 7.2 Exportar desde Historial

#### 7.2.1 Exportar Todos los Lotes Filtrados

**Paso 1:** En la página de Historial, aplique los filtros deseados (búsqueda y estado).

**Paso 2:** Haga clic en el botón **"Export All to CSV"**.

<img width="215" height="72" alt="image" src="https://github.com/user-attachments/assets/ea1b8074-ad27-4f5b-b8b4-5bd9b8f05a4e" />

{Imagen del botón de exportar todos los lotes}

**Paso 3:** Se descargará un archivo CSV con todos los lotes que coincidan con los filtros aplicados.

**Paso 4:** El archivo incluirá:
- Encabezado con fecha de generación
- Información de cada lote:
  - Nombre del lote
  - PPN de la receta
  - Descripción
  - Estado
  - Piezas OK
  - Piezas NOK
  - Total
  - Precisión
  - Creado por
  - Fecha de inicio
  - Fecha de cierre

#### 7.2.2 Exportar un Lote Individual

**Paso 1:** En la página de detalles del lote, haga clic en el botón **"Export to CSV"**.

<img width="1349" height="130" alt="image" src="https://github.com/user-attachments/assets/13b2ac70-25b1-435a-a926-097e7fde51a0" />

{Imagen del botón de exportar lote individual}

**Paso 2:** Se descargará un archivo CSV con información detallada del lote.

**Paso 3:** El archivo incluirá:
- Información general del lote
- Estadísticas completas
- Lista detallada de todas las piezas con:
  - Índice
  - Resultado (OK/NOK)
  - Código de falla
  - Timestamp
  - Información de imágenes asociadas

### 7.3 Ubicación de Archivos Exportados

Los archivos se descargan automáticamente en la carpeta de descargas de su navegador:
- **Windows**: `C:\Users\[Usuario]\Downloads`
- **Mac**: `~/Downloads`
- **Linux**: `~/Downloads`

### 7.4 Nombres de Archivos

Los archivos se nombran automáticamente con el siguiente formato:
- **Todos los lotes**: `lotes_YYYYMMDD_HHMMSS.csv`
- **Lote individual**: `lote_[nombre_lote]_YYYYMMDD_HHMMSS.csv`

Ejemplo: `lotes_20241215_143022.csv`

---

## 8. Solución de Problemas

### 8.1 Problemas de Inicio de Sesión

#### 8.1.1 No Puedo Iniciar Sesión

**Síntomas:**
- Mensaje de error al intentar iniciar sesión
- Credenciales no reconocidas

**Soluciones:**
1. Verifique que su nombre de usuario y contraseña sean correctos
2. Asegúrese de que no haya espacios adicionales
3. Verifique que la tecla "Bloq Mayús" no esté activada
4. Contacte al administrador si olvidó su contraseña

#### 8.1.2 Sesión Expirada

**Síntomas:**
- Redirigido automáticamente al login
- Mensaje de sesión expirada

**Soluciones:**
1. Inicie sesión nuevamente
2. Si el problema persiste, contacte al administrador

### 8.2 Problemas de Producción

#### 8.2.1 No Puedo Iniciar Producción

**Síntomas:**
- El botón "Iniciar Producción" no aparece o está deshabilitado
- Error al intentar iniciar producción

**Soluciones:**
1. Verifique que tenga el permiso `production.control.start`
2. Asegúrese de que no haya otro lote activo
3. Verifique que haya lotes disponibles para iniciar
4. Contacte al administrador si el problema persiste

#### 8.2.2 La Producción No Se Actualiza

**Síntomas:**
- Los datos no se actualizan en tiempo real
- Los contadores no cambian

**Soluciones:**
1. Verifique la conexión a internet o red local
2. Refresque la página (F5)
3. Verifique que el PLC esté conectado y enviando datos
4. Contacte al técnico de sistemas si el problema persiste

#### 8.2.3 Error de Model ID

**Síntomas:**
- Aparece un modal de error de Model ID
- La producción se detiene

**Soluciones:**
1. Verifique la configuración del PLC
2. Asegúrese de que el PLC esté enviando el Model ID correcto
3. Consulte la tabla de referencia de Model IDs en el modal
4. Contacte al técnico de PLC para corregir la configuración

#### 8.2.4 Paro de Emergencia por Mantenimiento

**Síntomas:**
- Aparece un modal de paro de emergencia
- La producción se detiene automáticamente

**Acciones:**
1. Complete las tareas de mantenimiento necesarias
2. Verifique el estado del equipo
3. Reinicie la producción manualmente cuando esté listo
4. No intente forzar la producción durante el mantenimiento

### 8.3 Problemas de Visualización

#### 8.3.1 Las Imágenes No Se Muestran

**Síntomas:**
- Las imágenes de defectos no aparecen
- Iconos de imagen rotos

**Soluciones:**
1. Verifique la conexión a internet o red local
2. Refresque la página (F5)
3. Verifique que el servidor de imágenes esté funcionando
4. Contacte al administrador si el problema persiste

#### 8.3.2 La Página Se Ve Desordenada

**Síntomas:**
- Elementos mal alineados
- Colores incorrectos
- Fuentes extrañas

**Soluciones:**
1. Refresque la página (F5)
2. Limpie la caché del navegador (Ctrl+Shift+Delete)
3. Actualice su navegador a la última versión
4. Intente con otro navegador

### 8.4 Problemas de Exportación

#### 8.4.1 No Puedo Exportar Datos

**Síntomas:**
- El botón de exportar no funciona
- No se descarga el archivo

**Soluciones:**
1. Verifique que tenga el permiso `history.lotes.exportar`
2. Verifique que su navegador permita descargas
3. Revise la carpeta de descargas
4. Intente con otro navegador

#### 8.4.2 El Archivo CSV Está Vacío

**Síntomas:**
- El archivo se descarga pero está vacío
- Solo tiene encabezados

**Soluciones:**
1. Verifique que haya datos para exportar
2. Ajuste los filtros en la página de historial
3. Intente exportar un lote específico
4. Contacte al administrador si el problema persiste

### 8.5 Problemas de Permisos

#### 8.5.1 No Veo Algunas Secciones

**Síntomas:**
- No aparecen opciones en el menú
- No puedo acceder a ciertas páginas

**Soluciones:**
1. Esto es normal según sus permisos asignados
2. Contacte al administrador si necesita acceso adicional
3. Verifique sus roles asignados en la sección de usuarios

#### 8.5.2 No Puedo Realizar Acciones

**Síntomas:**
- Los botones de crear/editar/eliminar no aparecen
- Mensaje de "Sin permisos"

**Soluciones:**
1. Verifique que tenga los permisos necesarios
2. Contacte al administrador para solicitar permisos adicionales
3. Verifique sus roles asignados

### 8.6 Contacto de Soporte

Si después de intentar estas soluciones el problema persiste, contacte al administrador del sistema o al equipo de soporte técnico proporcionando:
- Descripción detallada del problema
- Pasos para reproducir el problema
- Capturas de pantalla si es posible
- Mensajes de error específicos

---

## 9. Glosario de Términos

### 9.1 Términos Generales

**Dashboard**
- Panel principal del sistema que muestra estadísticas y acceso rápido a las funcionalidades.

**Lote**
- Un conjunto de piezas que se producen juntas con un objetivo específico. Cada lote tiene un nombre único, una receta asociada y un objetivo de piezas OK.

**Receta**
- Configuración de un modelo de cable que incluye especificaciones técnicas como número de conductores, terminales, PPN, etc. Cada receta tiene un Model ID único (1-7) que se comunica al PLC.

**PPN (Part Number)**
- Número de parte único que identifica una receta específica. Ejemplo: "1020746", "698330001".

**Model ID**
- Identificador numérico (1-7) que se envía al PLC para identificar qué modelo de cable se está produciendo. Cada receta tiene un Model ID único.

**Pieza**
- Una unidad individual de cable procesada. Cada pieza puede ser OK (aprobada) o NOK (rechazada).

**PLC (Programmable Logic Controller)**
- Controlador lógico programable que controla la línea de producción y envía datos al sistema.

### 9.2 Estados y Resultados

**OK (Aprobado)**
- Pieza que pasó todas las pruebas de calidad.

**NOK (No Aprobado / Rechazado)**
- Pieza que falló alguna prueba de calidad.

**Estado del Lote:**
- **OPEN**: Lote abierto y en producción o listo para iniciar
- **CLOSED**: Lote cerrado y completado
- **PAUSED**: Lote pausado temporalmente

**Estado de la Línea:**
- **Activo**: La línea está en producción
- **Pausado**: La producción está pausada
- **Detenido**: La producción está detenida
- **Mantenimiento**: La línea está en modo mantenimiento

### 9.3 Códigos de Falla

Los códigos de falla son números que identifican el tipo de defecto detectado:

- **0**: Sin falla (pieza OK)
- **1-255**: Códigos específicos de falla según la configuración del PLC

Cada código de falla puede tener una descripción asociada en el sistema.

### 9.4 Permisos y Roles

**Rol**
- Conjunto de permisos que se asignan a un usuario. Los roles determinan qué acciones puede realizar un usuario en el sistema.

**Permiso**
- Autorización específica para realizar una acción en el sistema. Los permisos están organizados por categorías (production, history, management).

**Ejemplos de Permisos:**
- `production.ver`: Ver la página de producción
- `production.control.start`: Iniciar producción
- `history.lotes.exportar`: Exportar datos a CSV
- `management.recetas.crear`: Crear nuevas recetas

### 9.5 Métricas

**Tasa de Producción**
- Número de piezas procesadas por minuto.

**Eficiencia**
- Porcentaje que indica qué tan eficientemente está funcionando la línea de producción.

**Precisión**
- Porcentaje de piezas OK vs el total de piezas procesadas. Se calcula como: (Piezas OK / Total de Piezas) × 100.

---

## 10. Preguntas Frecuentes (FAQ)

### 10.1 ¿Cómo cambio mi contraseña?

Actualmente, la funcionalidad de cambio de contraseña debe ser realizada por un administrador. Contacte al administrador del sistema para solicitar un cambio de contraseña.

### 10.2 ¿Puedo tener múltiples lotes activos al mismo tiempo?

No, solo puede haber un lote activo a la vez. Debe detener o cerrar el lote actual antes de iniciar uno nuevo.

### 10.3 ¿Qué pasa si cierro accidentalmente un lote?

Solo el administrador del sistema puede cerrar un lote sin terminar. Asegúrese de que la producción esté completa antes de cerrar un lote.

### 10.4 ¿Los datos se guardan automáticamente?

Sí, todos los datos de producción se guardan automáticamente en tiempo real. No es necesario guardar manualmente.

### 10.5 ¿Puedo exportar datos de un rango de fechas específico?

Actualmente, la exportación incluye todos los lotes filtrados. Use los filtros de búsqueda y estado para limitar los lotes que desea exportar.

### 10.6 ¿Qué navegadores son compatibles?

El sistema funciona mejor con navegadores modernos:
- Google Chrome (recomendado)
- Mozilla Firefox
- Microsoft Edge
- Safari (Mac)

### 10.7 ¿Necesito conexión a internet?

El sistema puede funcionar en una red local sin necesidad de internet, siempre que el servidor esté accesible en la red.

### 10.8 ¿Cómo sé qué permisos tengo?

Sus permisos están determinados por los roles asignados a su usuario. Contacte al administrador para conocer sus permisos específicos o para solicitar permisos adicionales.

### 10.9 ¿Qué debo hacer si veo un error de Model ID?

1. No intente continuar la producción
2. Verifique la configuración del PLC
3. Consulte la tabla de referencia de Model IDs en el modal de error
4. Contacte al técnico de PLC para corregir la configuración
5. Una vez corregido, reinicie la producción

### 10.10 ¿Las imágenes de defectos se guardan permanentemente?

Sí, todas las imágenes de piezas defectuosas se guardan permanentemente y están asociadas al lote y pieza correspondiente. Pueden consultarse en el historial.

---

## 11. Apéndices

### 11.1 Referencia Rápida de Model IDs

| Model ID | PPN Ejemplo | Conductores | Descripción |
|----------|-------------|-------------|-------------|
| 1 | 1020746 | 2 | Cable estándar 2 conductores |
| 2 | 1020746-02 | 2 | Variante 02 |
| 3 | 1020746-03 | 2 | Variante 03 |
| 4 | 1020746-04 | 2 | Variante 04 |
| 5 | 1020746-05 | 2 | Variante 05 |
| 6 | 1020746-06 | 2 | Variante 06 |
| 7 | 698330001 | 4 | Cable 4 conductores |

**Nota:** Los PPNs reales pueden variar según su configuración. Consulte la sección de Recetas para ver los Model IDs configurados en su sistema.

### 11.2 Atajos de Teclado

- **F5**: Refrescar la página
- **Ctrl + F**: Buscar en la página actual
- **Esc**: Cerrar modales
- **Enter**: Confirmar acciones en formularios

### 11.3 Formatos de Fecha y Hora

El sistema muestra fechas y horas en el siguiente formato:
- **Fecha**: DD/MM/YYYY (Día/Mes/Año)
- **Hora**: HH:MM (Hora:Minuto en formato 24 horas)
- **Ejemplo**: 15/12/2024 14:30

### 11.4 Límites del Sistema

- **Model IDs**: Máximo 7 (1-7)
- **Caracteres en nombre de lote**: Sin límite específico, pero se recomienda mantener nombres cortos y descriptivos
- **Piezas por lote**: Sin límite técnico
- **Usuarios**: Sin límite técnico
- **Roles**: Sin límite técnico

---

## 12. Conclusión

Este manual cubre todas las funcionalidades principales del Sistema de Control de Calidad Industrial. Si tiene preguntas adicionales o necesita asistencia, no dude en contactar al administrador del sistema o al equipo de soporte técnico.

**¡Gracias por usar el sistema!**

---

**Versión del Manual:** 1.0  
**Fecha de Actualización:** Noviembre 2025  
**Sistema:** Control de Calidad Industrial - Amphenol By AxmeTech

