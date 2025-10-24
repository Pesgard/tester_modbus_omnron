# 🔧 Guía Rápida de Referencia PLC

**Sistema de Trazabilidad y Control de Calidad Industrial**

---

## 📡 CONEXIÓN

```
Backend IP: localhost (o IP del servidor)
Puerto TCP: 3000
Formato: [int,int,int,int,int,int,int,int]
Timeout: 5000ms
```

---

## 📋 CONTRATO DE 8 BITS

### Estructura del Array

```
[0]  [1]  [2]  [3]  [4]  [5]  [6]  [7]
 │    │    │    │    │    │    │    │
 │    │    │    │    │    │    │    └─ reserved (futuro)
 │    │    │    │    │    │    └────── ready_flag (1=enviar)
 │    │    │    │    │    └─────────── electrical_status
 │    │    │    │    └──────────────── camera_status
 │    │    │    └───────────────────── model_id (1-7)
 │    │    └────────────────────────── failure_code (0-4)
 │    └─────────────────────────────── piece_status (0=NOK, 1=OK)
 └──────────────────────────────────── general_status
```

### Valores por Índice

| Índice | Campo | Valores |
|--------|-------|---------|
| **[0]** | general_status | 0=Detenido, 1=Activo, 2=Error, 3=Mantenimiento |
| **[1]** | piece_status | 0=NOK, 1=OK |
| **[2]** | failure_code | 0=Sin falla, 1=Hipot, 2=Etiqueta, 3=Modelo, 4=Terminal |
| **[3]** | model_id | 1-7 (ver tabla de recetas) |
| **[4]** | camera_status | 0=OK, 1=Captura imagen |
| **[5]** | electrical_status | 0=OK, 1=Falla |
| **[6]** | ready_flag | 0=No enviar, 1=Enviar |
| **[7]** | reserved | 0 (no usar) |

---

## 🎯 CÓDIGOS DE FALLA (failure_code)

### 0 - Sin Falla ✅
```
Significado: Pieza aprobada
Acción PLC: Continuar producción
Backend: Incrementa piezas_ok
Imagen: No
```

### 1 - Test Hipot Falla ⚡
```
Significado: Aislamiento eléctrico insuficiente
Acción PLC: Disparar cámara
Backend: Pausa producción, espera imagen
Imagen: Sí (terminal eléctrico)
electrical_status: 1
```

### 2 - Etiqueta Incorrecta 🏷️
```
Significado: QR/Barcode no coincide
Acción PLC: Disparar cámara
Backend: Pausa producción, espera imagen
Imagen: Sí (etiqueta)
```

### 3 - Modelo Incorrecto 📦
```
Significado: model_id no existe o inactivo
Acción PLC: Detener, notificar supervisor
Backend: Error crítico, pausa producción
Imagen: Opcional
```

### 4 - Terminal Incorrecta 🔧
```
Significado: Tipo de terminal no coincide
Acción PLC: Disparar cámara
Backend: Pausa producción, espera imagen
Imagen: Sí (terminal instalado)
```

---

## 🔩 MAPEO DE RECETAS (model_id)

| ID | PPN | Cable NP | L1 | L2 | Conductores | Longitud |
|----|-----|----------|----|----|-------------|----------|
| **1** | 1020746 | 664030001 | Ferrul | Ferrul | 5 | 16.0 FT |
| **2** | 1020746-02 | 664030001 | Ferrul | Ferrul | 5 | 16.5 FT |
| **3** | 1020747 | 664030001 | Ferrul | Ferrul | 5 | 16.5 FT |
| **4** | 683950001 | 664030001 | **Terminal** | Ferrul | 5 | 17.5 FT |
| **5** | 694030001 | 664030001 | **Terminal** | Ferrul | 5 | 20.666 FT |
| **6** | 717140001 | 664030001 | Ferrul | Ferrul | 5 | 20.67 FT |
| **7** | 698330001 | 698340001 | Ferrul | Ferrul | **4** | 20.2 FT |

### ⚠️ ATENCIÓN ESPECIAL

- **Modelos 4 y 5:** Único que usan **Terminal** en L1
- **Modelo 7:** Solo tiene **4 conductores** (sin Tierra)

---

## ✅ CHECKLIST PRE-ENVÍO

Antes de establecer `ready_flag = 1`:

- [ ] Array tiene 8 elementos
- [ ] Valores entre 0-9
- [ ] model_id entre 1-7
- [ ] Si piece_status=0 → failure_code>0
- [ ] Si piece_status=1 → failure_code=0
- [ ] Si camera_status=1 → imagen lista

---

## 📊 TABLA DE DECISIÓN

| Hipot | Visual | Terminal | Etiqueta | → Status | → Código |
|-------|--------|----------|----------|----------|----------|
| ✅ | ✅ | ✅ | ✅ | 1 (OK) | 0 |
| ❌ | - | - | - | 0 (NOK) | 1 |
| ✅ | - | - | ❌ | 0 (NOK) | 2 |
| ✅ | - | ❌ | - | 0 (NOK) | 4 |

**Prioridad:** Hipot > Terminal > Etiqueta

---

## 🧪 EJEMPLOS DE ARRAYS

### ✅ Pieza OK - Modelo 1
```
[1, 1, 0, 1, 0, 0, 1, 0]
     ^  ^  ^
     OK │  Sin falla
        Modelo 1
```

### ❌ Falla Hipot - Modelo 3
```
[1, 0, 1, 3, 0, 1, 1, 0]
     ^  ^  ^     ^
     NOK│  Mod 3 Eléctrico falló
        Hipot
```

### ❌ Terminal Incorrecto - Modelo 4
```
[1, 0, 4, 4, 1, 0, 1, 0]
     ^  ^  ^  ^
     NOK│  │  Captura imagen
        │  Modelo 4 (debe tener Terminal L1)
        Terminal incorrecto
```

### ❌ Etiqueta Incorrecta - Modelo 2
```
[1, 0, 2, 2, 1, 0, 1, 0]
     ^  ^  ^  ^
     NOK│  │  Captura imagen
        │  Modelo 2
        Etiqueta
```

---

## 🔍 VALIDACIÓN DE TERMINALES

### Por Model ID:

```
Models 1, 2, 3, 6, 7:
  L1 = Ferrul
  L2 = Ferrul

Models 4, 5:
  L1 = Terminal  ⚡ IMPORTANTE
  L2 = Ferrul
  
Model 7:
  Solo 4 conductores ⚠️
```

---

## ⚙️ CÓDIGO PLC (Ejemplo)

```c
// Configurar model_id
CASE recipe_selector OF
  1: model_id := 1;  // 1020746
  2: model_id := 2;  // 1020746-02
  3: model_id := 3;  // 1020747
  4: model_id := 4;  // 683950001 (Terminal L1)
  5: model_id := 5;  // 694030001 (Terminal L1)
  6: model_id := 6;  // 717140001
  7: model_id := 7;  // 698330001 (4 cond)
END_CASE;

// Compilar array
data[0] := 1;              // general_status
data[1] := piece_ok;       // piece_status
data[2] := failure_type;   // failure_code
data[3] := model_id;       // model_id
data[4] := need_image;     // camera_status
data[5] := hipot_failed;   // electrical_status
data[6] := 1;              // ready_flag
data[7] := 0;              // reserved

// Enviar
SEND_TCP(data);
```

---

## 🚨 ERRORES COMUNES

### ❌ Producción no se inicia
**Causa:** model_id del PLC ≠ receta del lote  
**Solución:** Verificar lote activo en pantalla

### ❌ Todas las piezas marcan "Modelo incorrecto"
**Causa:** model_id > 7 o < 1  
**Solución:** Verificar selector de receta en PLC

### ❌ Imágenes no se procesan
**Causa:** camera_status = 0 cuando debería ser 1  
**Solución:** Verificar trigger de cámara

### ❌ Backend rechaza paquetes
**Causa:** ready_flag = 0  
**Solución:** Establecer ready_flag = 1 siempre que datos estén completos

---

## 📞 CONTACTO TÉCNICO

**En caso de problemas:**
1. Verificar logs del backend: `/var/log/plc-app/`
2. Verificar estado en dashboard: `http://localhost:5173/dashboard/production`
3. Contactar a soporte técnico

---

**Versión:** 1.0.0  
**Última actualización:** Enero 2025  
**Documento para:** Operadores y Técnicos de PLC

