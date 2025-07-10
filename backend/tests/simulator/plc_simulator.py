import asyncio
from pymodbus.client import AsyncModbusTcpClient
import random
import time
from datetime import datetime

# Configuración de modelos de productos
PRODUCT_MODELS = {
    1: {
        "name": "Modelo A - 2 Cámaras",
        "cameras": 2,
        "expected_color": "Azul",
        "has_high_pot": True,
        "has_continuity": True,
        "components": ["Resistor", "Capacitor", "Conector"],
        "cycle_time": 2500
    },
    2: {
        "name": "Modelo B - 3 Cámaras", 
        "cameras": 3,
        "expected_color": "Rojo",
        "has_high_pot": True,
        "has_continuity": False,
        "components": ["LED", "Resistor", "Switch", "Cable"],
        "cycle_time": 3200
    },
    3: {
        "name": "Modelo C - 2 Cámaras Premium",
        "cameras": 2, 
        "expected_color": "Verde",
        "has_high_pot": False,
        "has_continuity": True,
        "components": ["Sensor", "Actuador"],
        "cycle_time": 1800
    },
    4: {
        "name": "Modelo D - 3 Cámaras Avanzado",
        "cameras": 3,
        "expected_color": "Amarillo", 
        "has_high_pot": True,
        "has_continuity": True,
        "components": ["MCU", "Crystal", "Resistor", "Capacitor", "Connector"],
        "cycle_time": 4000
    }
}

# Códigos de falla específicos
FAILURE_CODES = {
    0: "SIN_FALLA",
    1: "COMPONENTE_FALTANTE",
    2: "ERROR_ETIQUETA", 
    3: "COLOR_INCORRECTO",
    4: "FALLA_ELECTRICA_GENERAL",
    5: "FALLA_CONTINUIDAD",
    6: "FALLA_HIGH_POT",
    7: "ERROR_CAMARA",
    8: "ERROR_POSICIONAMIENTO"
}

def simulate_camera_inspection(camera_id, inspection_type, expected_value, introduce_failure=False):
    """Simular inspección de cámara individual"""
    if introduce_failure:
        if inspection_type == "etiqueta":
            return {
                "result": 0,  # FAIL
                "confidence": random.uniform(0.7, 0.95),
                "measured": "ETIQUETA_INCORRECTA",
                "expected": expected_value,
                "failure_code": 2  # ERROR_ETIQUETA
            }
        elif inspection_type == "color":
            wrong_colors = ["Negro", "Blanco", "Gris", "Rosa"]
            return {
                "result": 0,  # FAIL
                "confidence": random.uniform(0.7, 0.95),
                "measured": random.choice(wrong_colors),
                "expected": expected_value,
                "failure_code": 3  # COLOR_INCORRECTO
            }
        elif inspection_type == "componente":
            return {
                "result": 0,  # FAIL
                "confidence": random.uniform(0.7, 0.95),
                "measured": "COMPONENTE_FALTANTE",
                "expected": expected_value,
                "failure_code": 1  # COMPONENTE_FALTANTE
            }
    else:
        return {
            "result": 1,  # PASS
            "confidence": random.uniform(0.85, 0.99),
            "measured": expected_value,
            "expected": expected_value,
            "failure_code": 0
        }

def simulate_electrical_test(test_type, expected_range, introduce_failure=False):
    """Simular prueba eléctrica"""
    if introduce_failure:
        # Valor fuera del rango
        if random.random() < 0.5:
            measured = expected_range[0] * random.uniform(0.1, 0.8)  # Muy bajo
        else:
            measured = expected_range[1] * random.uniform(1.2, 2.0)  # Muy alto
        
        failure_code = 6 if test_type == "high_pot" else 5  # HIGH_POT_FAIL or CONTINUITY_FAIL
        
        return {
            "test_type": test_type,
            "result": 0,  # FAIL
            "measured": measured,
            "expected_range": expected_range,
            "voltage": random.uniform(100, 1000),
            "current": random.uniform(0.1, 10.0),
            "failure_code": failure_code
        }
    else:
        # Valor dentro del rango
        measured = random.uniform(expected_range[0], expected_range[1])
        return {
            "test_type": test_type,
            "result": 1,  # PASS
            "measured": measured,
            "expected_range": expected_range,
            "voltage": random.uniform(100, 500),
            "current": random.uniform(0.5, 5.0),
            "failure_code": 0
        }

def simulate_piece_production(piece_number, current_model_id):
    """Simular producción completa de una pieza"""
    model = PRODUCT_MODELS[current_model_id]
    
    # Determinar si habrá fallo (15% probabilidad)
    has_failure = random.random() < 0.15
    
    # Simular inspecciones de cámara
    camera_results = []
    failure_codes = []
    
    # Cámara 1: Verificación de etiqueta
    etiqueta_result = simulate_camera_inspection(
        camera_id=1,
        inspection_type="etiqueta",
        expected_value="ETIQUETA_OK",
        introduce_failure=has_failure and random.random() < 0.3
    )
    camera_results.append(etiqueta_result)
    if etiqueta_result["failure_code"] > 0:
        failure_codes.append(etiqueta_result["failure_code"])
    
    # Cámara 2: Verificación de color
    color_result = simulate_camera_inspection(
        camera_id=2,
        inspection_type="color",
        expected_value=model["expected_color"],
        introduce_failure=has_failure and random.random() < 0.4
    )
    camera_results.append(color_result)
    if color_result["failure_code"] > 0:
        failure_codes.append(color_result["failure_code"])
    
    # Cámara 3: Verificación de componentes (si el modelo tiene 3 cámaras)
    if model["cameras"] == 3:
        component_result = simulate_camera_inspection(
            camera_id=3,
            inspection_type="componente",
            expected_value="COMPONENTES_OK",
            introduce_failure=has_failure and random.random() < 0.3
        )
        camera_results.append(component_result)
        if component_result["failure_code"] > 0:
            failure_codes.append(component_result["failure_code"])
    
    # Pruebas eléctricas
    electrical_results = []
    
    # Prueba High Pot
    if model["has_high_pot"]:
        high_pot_result = simulate_electrical_test(
            test_type="high_pot",
            expected_range=(500.0, 1000.0),
            introduce_failure=has_failure and random.random() < 0.2
        )
        electrical_results.append(high_pot_result)
        if high_pot_result["failure_code"] > 0:
            failure_codes.append(high_pot_result["failure_code"])
    
    # Prueba de continuidad
    if model["has_continuity"]:
        continuity_result = simulate_electrical_test(
            test_type="continuity",
            expected_range=(0.1, 5.0),
            introduce_failure=has_failure and random.random() < 0.15
        )
        electrical_results.append(continuity_result)
        if continuity_result["failure_code"] > 0:
            failure_codes.append(continuity_result["failure_code"])
    
    # Determinar calidad general
    has_camera_fails = any(cam["result"] == 0 for cam in camera_results)
    has_electrical_fails = any(test["result"] == 0 for test in electrical_results)
    
    if has_camera_fails or has_electrical_fails:
        overall_quality = 0  # NOK
    else:
        overall_quality = 1  # OK
    
    # Simular tiempo de ciclo con variación
    base_cycle = model["cycle_time"]
    variation = random.uniform(-0.1, 0.1)  # ±10% variación
    actual_cycle = int(base_cycle * (1 + variation))
    
    return {
        "model": model,
        "camera_results": camera_results,
        "electrical_results": electrical_results,
        "overall_quality": overall_quality,
        "failure_codes": failure_codes,
        "cycle_time": actual_cycle,
        "piece_number": piece_number
    }

async def write_test_data():
    client = AsyncModbusTcpClient("localhost", port=502)
    await client.connect()

    if not client.connected:
        print("No se pudo conectar al servidor Modbus")
        return

    print("🚀 Simulador de PLC Avanzado iniciado - Sistema de Inspección con Cámaras")
    print("📷 Configuración: Cámaras para etiqueta, color y componentes")
    print("⚡ Pruebas eléctricas: High Pot y Continuidad")
    print("🎯 4 modelos diferentes (2-3 cámaras)")
    print("Presiona Ctrl+C para detener\n")
    
    counter = 0
    production_count = 0
    ok_count = 0
    nok_count = 0
    current_model_id = 1
    current_operator = random.randint(100, 103)
    
    try:
        while True:
            counter += 1
            production_count += 1
            
            # Cambiar modelo ocasionalmente (10% probabilidad)
            if random.random() < 0.10:
                current_model_id = random.choice(list(PRODUCT_MODELS.keys()))
                print(f"🔄 Cambiando a {PRODUCT_MODELS[current_model_id]['name']}")
            
            # Simular producción de pieza completa
            piece_data = simulate_piece_production(counter, current_model_id)
            
            if piece_data["overall_quality"] == 1:
                ok_count += 1
            else:
                nok_count += 1
            
            # Simular diferentes estados de línea basados en fallas
            if piece_data["failure_codes"] and random.random() < 0.1:  # 10% de fallas críticas
                line_status = 2  # ERROR
                error_code = piece_data["failure_codes"][0]
            elif counter % 25 == 0:  # Mantenimiento ocasional
                line_status = 3  # MAINTENANCE
                error_code = 101
            else:
                line_status = 1  # RUNNING
                error_code = piece_data["failure_codes"][0] if piece_data["failure_codes"] else 0

            # Variar operador ocasionalmente
            if counter % 12 == 0:
                current_operator = random.randint(100, 103)
            
            # Simular variaciones ambientales
            temperature = int((24.0 + random.uniform(-2, 3)) * 10)
            pressure = int((4.2 + random.uniform(-0.3, 0.5)) * 10)
            vibration = int(random.uniform(0.05, 0.3) * 100)

            # Preparar registros principales (0-9)
            registers_main = [
                current_model_id,                    # 0: product_id
                piece_data["overall_quality"],       # 1: quality_status
                production_count,                    # 2: total_pieces
                ok_count,                           # 3: ok_pieces
                nok_count,                          # 4: nok_pieces
                line_status,                        # 5: line_status
                error_code,                         # 6: error_code
                piece_data["cycle_time"],           # 7: cycle_time
                current_operator,                   # 8: operator_id
                1                                   # 9: station_id
            ]
            
            # Preparar registros de calidad detallados (20-29)
            quality_registers = [0] * 10
            
            # Resultados de cámaras
            if len(piece_data["camera_results"]) >= 1:
                quality_registers[0] = piece_data["camera_results"][0]["result"]  # 20: etiqueta
            if len(piece_data["camera_results"]) >= 2:
                quality_registers[1] = piece_data["camera_results"][1]["result"]  # 21: color
            if len(piece_data["camera_results"]) >= 3:
                quality_registers[2] = piece_data["camera_results"][2]["result"]  # 22: componente
            
            # Resultados de pruebas eléctricas
            for test in piece_data["electrical_results"]:
                if test.get("test_type") == "high_pot":
                    quality_registers[3] = test.get("result", 0)                  # 23: high_pot
                    quality_registers[4] = int(test.get("measured", 0) * 10)      # 24: high_pot_value
                elif test.get("test_type") == "continuity":
                    quality_registers[5] = test.get("result", 0)                  # 25: continuity
                    quality_registers[6] = int(test.get("measured", 0) * 100)     # 26: continuity_value
            
            quality_registers[8] = error_code                                     # 28: failure_code
            quality_registers[9] = piece_data["model"]["cameras"]                 # 29: cameras_used
            
            # Preparar registros de proceso (40-49)
            process_registers = [
                temperature,                        # 40: temperature
                temperature,                        # 41: temperature_line2
                pressure,                           # 42: hydraulic_pressure
                pressure + 5,                       # 43: pneumatic_pressure
                random.randint(800, 1200),          # 44: line_speed
                vibration,                          # 45: motor_vibration
                random.randint(150, 300),           # 46: energy_consumption
                random.randint(80, 95),             # 47: lubricant_level
                0,                                  # 48: sensors_status
                1 if error_code > 0 else 0          # 49: active_alarms
            ]

            # Enviar todos los registros
            await client.write_registers(0, registers_main)
            await client.write_registers(20, quality_registers) 
            await client.write_registers(40, process_registers)

            # Mostrar información detallada del envío
            status_names = {0: "PARADO", 1: "FUNCIONANDO", 2: "ERROR", 3: "MANTENIMIENTO"}
            quality_names = {0: "NOK", 1: "OK"}
            
            status_icon = "✅" if piece_data["overall_quality"] == 1 else "❌"
            
            print(f"{status_icon} Pieza #{counter} - {piece_data['model']['name']}")
            print(f"   🎯 Modelo: {current_model_id} | Calidad: {quality_names[piece_data['overall_quality']]} | Contador: {production_count}")
            print(f"   📊 Estado: {status_names[line_status]} | Error: {error_code}")
            print(f"   ⏱️ Tiempo ciclo: {piece_data['cycle_time']}ms | Operador: {current_operator}")
            
            # Mostrar resultados de cámaras
            for i, cam_result in enumerate(piece_data["camera_results"], 1):
                icon = "✅" if cam_result["result"] == 1 else "❌"
                cam_type = ["etiqueta", "color", "componente"][i-1]
                print(f"   📷 Cámara {i} ({cam_type}): {icon} - Confianza: {cam_result['confidence']:.1%}")
                if cam_result["failure_code"] > 0:
                    print(f"      🔍 Fallo: {FAILURE_CODES[cam_result['failure_code']]}")
            
            # Mostrar resultados de pruebas eléctricas
            for test in piece_data["electrical_results"]:
                test_type = "High Pot" if "high_pot" in str(test) else "Continuidad"
                icon = "✅" if test["result"] == 1 else "❌"
                print(f"   ⚡ {test_type}: {icon} - Valor: {test['measured']:.2f}")
                if test["failure_code"] > 0:
                    print(f"      🔍 Fallo: {FAILURE_CODES[test['failure_code']]}")
            
            print(f"   🌡️ Temperatura: {temperature/10:.1f}°C | Presión: {pressure/10:.1f} bar")
            
            # Mostrar estadísticas cada 10 piezas
            if counter % 10 == 0:
                efficiency = (ok_count / production_count) * 100
                print(f"📈 Estadísticas: {production_count} piezas, {efficiency:.1f}% eficiencia")
            
            print("-" * 70)
            
            # Simular salidas digitales para activar actuadores
            if counter % 8 == 0:
                # Activar señales según estado de calidad
                coil_quality_ok = piece_data["overall_quality"] == 1
                coil_reject = piece_data["overall_quality"] == 0
                
                await client.write_coil(10, coil_quality_ok)   # Señal pieza OK
                await client.write_coil(11, coil_reject)       # Señal rechazo
                await client.write_coil(12, line_status == 1)  # Línea funcionando
                
                print(f"🔌 Salidas: OK={coil_quality_ok}, Rechazo={coil_reject}, Funcionando={line_status == 1}")

            # Pausa entre piezas (simular tiempo de ciclo reducido)
            await asyncio.sleep(2.5)

    except KeyboardInterrupt:
        print("\n🛑 Simulación detenida por usuario")
        final_efficiency = (ok_count / max(1, production_count)) * 100
        print(f"📊 Estadísticas finales: {production_count} piezas, {final_efficiency:.1f}% eficiencia")
    except Exception as e:
        print(f"❌ Error en simulación: {e}")
    finally:
        client.close()
        print("🔌 Conexión cerrada")

async def quick_test():
    """Test rápido para verificar conectividad"""
    print("🔍 Ejecutando test rápido de conectividad...")
    
    client = AsyncModbusTcpClient("localhost", port=502)
    await client.connect()

    if not client.connected:
        print("❌ No se pudo conectar al servidor Modbus en puerto 502")
        print("   Asegúrate de que el servidor esté ejecutándose:")
        print("   python -m app.main")
        return False

    try:
        # Test de escritura simple
        result = await client.write_registers(0, [1, 1, 100, 90, 10, 1, 0, 2500, 101, 1])
        if result.isError():
            print(f"❌ Error en test de escritura: {result}")
            return False
        
        print("✅ Test de conectividad exitoso")
        return True
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        return False
    finally:
        client.close()

if __name__ == "__main__":
    print("🏭 SIMULADOR AVANZADO DE PLC - SISTEMA DE INSPECCIÓN INDUSTRIAL")
    print("=" * 70)
    print("📷 Cámaras: Etiqueta, Color y Componentes")
    print("⚡ Pruebas eléctricas: High Pot y Continuidad") 
    print("🎯 4 modelos con 2-3 cámaras")
    print("❌ Simulación realista de fallas")
    print("=" * 70)
    
    # Ejecutar test de conectividad primero
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    test_passed = loop.run_until_complete(quick_test())
    
    if test_passed:
        print("\n🔄 Iniciando simulación continua...")
        print("   Abre http://localhost:8000 para ver los datos en tiempo real")
        time.sleep(2)
        
        try:
            loop.run_until_complete(write_test_data())
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
    else:
        print("\n❌ No se pudo establecer conexión. Verifica que el servidor esté ejecutándose.")
    
    loop.close()