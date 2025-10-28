#!/usr/bin/env python3
"""
Simulador PLC - Cliente de Testing CLI
Simula el envío de paquetes TCP y transferencia de imágenes del PLC real
"""

import socket
import json
import time
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
import threading
from PIL import Image, ImageDraw, ImageFont
import random

# ========================================
# CONFIGURACIÓN
# ========================================
TCP_HOST = 'localhost'
TCP_PORT = 900  # Cambiado de 5000 a 900 para coincidir con tu backend
FTP_DIR = os.path.expanduser('~/ftp/plc_images')


# Colores ANSI
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Códigos de falla
FAILURE_CODES = {
    0: 'Sin falla',
    1: 'Test hipot',
    2: 'Etiqueta incorrecta',
    3: 'Modelo incorrecto',
    4: 'Terminal incorrecta',
    99: 'Falla desconocida'
}

# Estados del sistema
GENERAL_STATUS = {
    0: 'RUNNING',
    1: 'STOPPED',
    2: 'ERROR',
    3: 'MAINTENANCE'
}

# Paquetes predefinidos
PRESETS = {
    '1': {
        'name': '✅ Pieza OK',
        'packet': [0, 0, 0, 1, 0, 0, 1, 0],
        'needs_image': False
    },
    '2': {
        'name': '❌ NOK - Etiqueta incorrecta',
        'packet': [0, 1, 2, 1, 1, 0, 1, 0],
        'needs_image': True
    },
    '3': {
        'name': '⚡ NOK - Test Hipot',
        'packet': [0, 1, 1, 1, 0, 1, 1, 0],
        'needs_image': True
    },
    '4': {
        'name': '🔌 NOK - Terminal incorrecta',
        'packet': [0, 1, 4, 1, 1, 0, 1, 0],
        'needs_image': True
    },
    '5': {
        'name': '🚨 Sistema en ERROR',
        'packet': [2, 1, 1, 1, 0, 1, 1, 0],
        'needs_image': True
    },
    '6': {
        'name': '🛠️ Modo Mantenimiento - Sistema detenido',
        'packet': [3, 0, 0, 1, 0, 0, 1, 0],
        'needs_image': False
    },
    '7': {
        'name': '🔧 Modo Mantenimiento - Con pieza NOK',
        'packet': [3, 1, 99, 1, 0, 0, 1, 0],
        'needs_image': False
    },
    '8': {
        'name': '🚫 Paquete Inválido (ready=0)',
        'packet': [0, 0, 0, 1, 0, 0, 0, 0],
        'needs_image': False
    }
}


# ========================================
# CLASE PLCClient
# ========================================
class PLCClient:
    def __init__(self):
        self.socket = None
        self.connected = False
        self.receive_thread = None
        self.stop_receive = False

    def connect(self):
        """Conectar al servidor TCP"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((TCP_HOST, TCP_PORT))
            self.connected = True
            
            # Iniciar hilo de recepción
            self.stop_receive = False
            self.receive_thread = threading.Thread(target=self._receive_packets, daemon=True)
            self.receive_thread.start()
            
            return True, f"✅ Conectado a {TCP_HOST}:{TCP_PORT}"
        except Exception as e:
            self.connected = False
            return False, f"❌ Error de conexión: {str(e)}"

    def disconnect(self):
        """Desconectar del servidor"""
        if self.socket:
            try:
                self.stop_receive = True
                self.connected = False
                self.socket.close()
                if self.receive_thread:
                    self.receive_thread.join(timeout=1)
                return True, "🔌 Desconectado correctamente"
            except:
                pass
        return False, "Ya estaba desconectado"

    def _receive_packets(self):
        """Hilo para recibir paquetes del servidor"""
        self.socket.settimeout(1.0)
        buffer = b''
        
        while not self.stop_receive and self.connected:
            try:
                data = self.socket.recv(1024)
                if not data:
                    log_message("🔴 Servidor cerró la conexión", Colors.RED)
                    self.connected = False
                    break
                
                buffer += data
                
                # Procesar paquetes completos de 8 bytes
                while len(buffer) >= 8:
                    packet_bytes = buffer[:8]
                    buffer = buffer[8:]
                    
                    packet = list(packet_bytes)
                    self._display_received_packet(packet)
                    
            except socket.timeout:
                continue
            except Exception as e:
                if self.connected and not self.stop_receive:
                    log_message(f"❌ Error al recibir: {str(e)}", Colors.RED)
                break

    def _display_received_packet(self, packet):
        """Mostrar paquete recibido en consola"""
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print(f"\n{Colors.CYAN}{'═' * 64}")
        print(f"📥 PAQUETE RECIBIDO DEL SERVIDOR [{timestamp}]")
        print(f"{'═' * 64}{Colors.ENDC}")
        print(f"{Colors.BOLD}Array:{Colors.ENDC} {packet}")
        print(f"{Colors.BOLD}Bytes:{Colors.ENDC} {[hex(b) for b in packet]}")
        print(f"\n{Colors.YELLOW}Decodificación:{Colors.ENDC}")
        print(f"  [0] General Status:    {GENERAL_STATUS.get(packet[0], 'Desconocido')} ({packet[0]})")
        print(f"  [1] Piece Status:      {'OK' if packet[1] == 0 else 'NOK'} ({packet[1]})")
        print(f"  [2] Failure Code:      {FAILURE_CODES.get(packet[2], 'Desconocido')} ({packet[2]})")
        print(f"  [3] Model ID:          {packet[3]}")
        print(f"  [4] Camera Status:     {'OK' if packet[4] == 0 else 'Falla visual'} ({packet[4]})")
        print(f"  [5] Electrical Status: {'OK' if packet[5] == 0 else 'Falla eléctrica'} ({packet[5]})")
        print(f"  [6] Ready Flag:        {'✅ Válido' if packet[6] == 1 else '🚫 Ignorar'} ({packet[6]})")
        print(f"  [7] Reserved:          {packet[7]}")
        print(f"{Colors.CYAN}{'═' * 64}{Colors.ENDC}\n")

    def send_packet(self, packet):
        """Enviar paquete de datos como bytes binarios"""
        if not self.connected:
            return False, "❌ No conectado al servidor"

        try:
            # Convertir array a bytes binarios (cada valor es un byte)
            # El PLC envía directamente los 8 bytes sin formato JSON
            data = bytes(packet)
            self.socket.sendall(data)
            return True, f"📤 Paquete enviado: {packet} (bytes: {list(data)})"
        except Exception as e:
            self.connected = False
            return False, f"❌ Error al enviar: {str(e)}"

    def send_image(self, image_path, failure_code, delay=0.5):
        """Copiar imagen al directorio FTP"""
        try:
            # Verificar que el archivo existe
            if not os.path.exists(image_path):
                return False, f"❌ Archivo no encontrado: {image_path}"

            # Crear directorio si no existe
            os.makedirs(FTP_DIR, exist_ok=True)

            # Esperar antes de enviar (simula procesamiento PLC)
            time.sleep(delay)

            # Generar nombre de archivo
            timestamp = int(time.time() * 1000)
            ext = Path(image_path).suffix
            dest_name = f"error_{failure_code}_test_{timestamp}{ext}"
            dest_path = os.path.join(FTP_DIR, dest_name)

            # Copiar archivo
            shutil.copy2(image_path, dest_path)

            return True, f"📸 Imagen enviada: {dest_name}"
        except Exception as e:
            return False, f"❌ Error al enviar imagen: {str(e)}"

    def generate_and_send_image(self, failure_code, delay=0.5):
        """Generar imagen automáticamente y enviarla"""
        try:
            # Crear directorio si no existe
            os.makedirs(FTP_DIR, exist_ok=True)

            # Esperar antes de enviar (simula procesamiento PLC)
            time.sleep(delay)

            # Generar nombre de archivo
            timestamp = int(time.time() * 1000)
            dest_name = f"error_{failure_code}_test_{timestamp}.jpg"
            dest_path = os.path.join(FTP_DIR, dest_name)

            # Generar imagen con el defecto
            self._create_defect_image(dest_path, failure_code)

            return True, f"📸 Imagen generada y enviada: {dest_name}"
        except Exception as e:
            return False, f"❌ Error al generar imagen: {str(e)}"

    def _create_defect_image(self, path, failure_code):
        """Crear imagen simulada de defecto"""
        # Dimensiones de imagen
        width, height = 1920, 1080

        # Colores según tipo de falla
        colors = {
            1: ('#FF0000', '#FFCCCC', 'FALLA ELÉCTRICA - HIPOT'),  # Rojo
            2: ('#FFA500', '#FFE5CC', 'ETIQUETA INCORRECTA'),  # Naranja
            3: ('#FF00FF', '#FFCCFF', 'MODELO INCORRECTO'),  # Magenta
            4: ('#FFFF00', '#FFFFCC', 'TERMINAL INCORRECTA'),  # Amarillo
            99: ('#800080', '#E5CCE5', 'FALLA DESCONOCIDA')  # Púrpura
        }

        color_main, color_bg, defect_text = colors.get(failure_code, ('#FF0000', '#FFCCCC', 'DEFECTO'))

        # Crear imagen
        img = Image.new('RGB', (width, height), color_bg)
        draw = ImageDraw.Draw(img)

        # Dibujar patrón de fondo (simula componente electrónico)
        for _ in range(50):
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = x1 + random.randint(50, 200), y1 + random.randint(50, 200)
            draw.rectangle([x1, y1, x2, y2], outline='#CCCCCC', width=2)

        # Dibujar área del defecto (círculo rojo)
        defect_x = random.randint(width // 4, 3 * width // 4)
        defect_y = random.randint(height // 4, 3 * height // 4)
        defect_radius = random.randint(100, 200)

        draw.ellipse(
            [defect_x - defect_radius, defect_y - defect_radius,
             defect_x + defect_radius, defect_y + defect_radius],
            fill=color_main,
            outline='#000000',
            width=5
        )

        # Intentar cargar fuente, si no existe usar default
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 50)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Título principal
        title = "DEFECTO DETECTADO"
        bbox = draw.textbbox((0, 0), title, font=font_large)
        title_width = bbox[2] - bbox[0]
        draw.rectangle([50, 50, width - 50, 180], fill='#000000')
        draw.text(((width - title_width) // 2, 80), title, fill='#FFFFFF', font=font_large)

        # Tipo de defecto
        bbox = draw.textbbox((0, 0), defect_text, font=font_medium)
        defect_width = bbox[2] - bbox[0]
        draw.rectangle([50, 200, width - 50, 280], fill=color_main)
        draw.text(((width - defect_width) // 2, 215), defect_text, fill='#000000', font=font_medium)

        # Información adicional
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        info_lines = [
            f"Código de falla: {failure_code}",
            f"Timestamp: {timestamp}",
            f"Posición: X={defect_x}, Y={defect_y}",
            f"Severidad: {'CRÍTICA' if failure_code in [1, 3] else 'MEDIA'}",
            "Estado: RECHAZADO"
        ]

        y_offset = height - 250
        for line in info_lines:
            draw.text((100, y_offset), line, fill='#000000', font=font_small)
            y_offset += 40

        # Marcador en el defecto
        draw.line([defect_x - 50, defect_y, defect_x + 50, defect_y], fill='#00FF00', width=3)
        draw.line([defect_x, defect_y - 50, defect_x, defect_y + 50], fill='#00FF00', width=3)

        # Guardar imagen
        img.save(path, 'JPEG', quality=85)

        return path


# ========================================
# FUNCIONES DE UTILIDAD
# ========================================
def clear_screen():
    """Limpiar la pantalla"""
    os.system('clear' if os.name != 'nt' else 'cls')


def print_header():
    """Imprimir encabezado"""
    clear_screen()
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║           🧪 SIMULADOR PLC - CLIENTE DE TESTING               ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")


def print_packet_info(packet):
    """Imprimir información del paquete"""
    print(f"\n{Colors.YELLOW}📦 Estructura del Paquete:{Colors.ENDC}")
    print(f"   Array: {Colors.BOLD}{packet}{Colors.ENDC}")
    print(f"\n   [0] General Status:    {GENERAL_STATUS.get(packet[0], 'Desconocido')}")
    print(f"   [1] Piece Status:      {'OK' if packet[1] == 0 else 'NOK'}")
    print(f"   [2] Failure Code:      {FAILURE_CODES.get(packet[2], 'Desconocido')}")
    print(f"   [3] Model ID:          {packet[3]}")
    print(f"   [4] Camera Status:     {'OK' if packet[4] == 0 else 'Falla visual'}")
    print(f"   [5] Electrical Status: {'OK' if packet[5] == 0 else 'Falla eléctrica'}")
    print(f"   [6] Ready Flag:        {'✅ Válido' if packet[6] == 1 else '🚫 Ignorar'}")
    print(f"   [7] Reserved:          {packet[7]}")


def log_message(msg, color=Colors.ENDC):
    """Imprimir mensaje con timestamp"""
    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    print(f"{color}[{timestamp}] {msg}{Colors.ENDC}")


def pause():
    """Pausar y esperar Enter"""
    input(f"\n{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")


# ========================================
# MENÚ PRINCIPAL
# ========================================
def main_menu(client):
    """Mostrar menú principal"""
    while True:
        print_header()

        # Estado de conexión
        if client.connected:
            print(f"{Colors.GREEN}🟢 Estado: CONECTADO{Colors.ENDC} ({TCP_HOST}:{TCP_PORT})\n")
        else:
            print(f"{Colors.RED}🔴 Estado: DESCONECTADO{Colors.ENDC}\n")

        print(f"{Colors.BOLD}MENÚ PRINCIPAL{Colors.ENDC}")
        print("═" * 64)
        print(f"{Colors.CYAN}1.{Colors.ENDC} Conectar al servidor TCP")
        print(f"{Colors.CYAN}2.{Colors.ENDC} Enviar paquete predefinido")
        print(f"{Colors.CYAN}3.{Colors.ENDC} Crear paquete personalizado")
        print(f"{Colors.CYAN}4.{Colors.ENDC} Envío automático (múltiples paquetes)")
        print(f"{Colors.CYAN}5.{Colors.ENDC} Secuencias de test automatizadas")
        print(f"{Colors.CYAN}6.{Colors.ENDC} 🛠️  Enviar estado de Mantenimiento")
        print(f"{Colors.CYAN}7.{Colors.ENDC} Configuración")
        print(f"{Colors.CYAN}8.{Colors.ENDC} Desconectar")
        print(f"{Colors.RED}0.{Colors.ENDC} Salir")
        print("═" * 64)

        choice = input(f"\n{Colors.BOLD}Selecciona una opción: {Colors.ENDC}").strip()

        if choice == '1':
            connect_menu(client)
        elif choice == '2':
            preset_menu(client)
        elif choice == '3':
            custom_packet_menu(client)
        elif choice == '4':
            auto_send_menu(client)
        elif choice == '5':
            test_sequences_menu(client)
        elif choice == '6':
            maintenance_menu(client)
        elif choice == '7':
            config_menu(client)
        elif choice == '8':
            if client.connected:
                success, msg = client.disconnect()
                log_message(msg, Colors.GREEN if success else Colors.RED)
                pause()
        elif choice == '0':
            if client.connected:
                client.disconnect()
            print(f"\n{Colors.CYAN}👋 ¡Hasta luego!{Colors.ENDC}\n")
            sys.exit(0)


# ========================================
# MENÚ DE CONEXIÓN
# ========================================
def connect_menu(client):
    """Menú de conexión"""
    print_header()
    print(f"{Colors.BOLD}🔌 CONEXIÓN TCP{Colors.ENDC}\n")

    if client.connected:
        log_message("Ya estás conectado", Colors.YELLOW)
        pause()
        return

    log_message(f"Intentando conectar a {TCP_HOST}:{TCP_PORT}...", Colors.CYAN)
    success, msg = client.connect()

    log_message(msg, Colors.GREEN if success else Colors.RED)
    pause()


# ========================================
# MENÚ DE PAQUETES PREDEFINIDOS
# ========================================
def preset_menu(client):
    """Menú de paquetes predefinidos"""
    print_header()
    print(f"{Colors.BOLD}🎯 PAQUETES PREDEFINIDOS{Colors.ENDC}\n")

    if not client.connected:
        log_message("Debes conectarte primero", Colors.RED)
        pause()
        return

    for key, preset in PRESETS.items():
        print(f"{Colors.CYAN}{key}.{Colors.ENDC} {preset['name']}")
    print(f"{Colors.RED}0.{Colors.ENDC} Volver")

    choice = input(f"\n{Colors.BOLD}Selecciona un paquete: {Colors.ENDC}").strip()

    if choice == '0':
        return

    if choice not in PRESETS:
        log_message("Opción inválida", Colors.RED)
        pause()
        return

    preset = PRESETS[choice]
    packet = preset['packet']

    print(f"\n{Colors.GREEN}Has seleccionado: {preset['name']}{Colors.ENDC}")
    print_packet_info(packet)

    # Preguntar si enviar imagen
    send_image = False
    image_path = None

    if preset['needs_image']:
        print(f"\n{Colors.YELLOW}⚠️  Esta pieza requiere imagen (failureCode > 0){Colors.ENDC}")
        print(f"{Colors.CYAN}Opciones:{Colors.ENDC}")
        print(f"  1. Generar imagen automáticamente")
        print(f"  2. Usar imagen existente")
        print(f"  3. No enviar imagen")

        img_choice = input(f"{Colors.BOLD}Selecciona opción (1/2/3): {Colors.ENDC}").strip()

        if img_choice == '1':
            send_image = 'auto'
        elif img_choice == '2':
            send_image = 'manual'
            image_path = input(f"{Colors.BOLD}Ruta de la imagen: {Colors.ENDC}").strip()

            if not os.path.exists(image_path):
                log_message(f"Archivo no encontrado: {image_path}", Colors.RED)
                pause()
                return
        else:
            send_image = False

    # Confirmar envío
    print(f"\n{Colors.YELLOW}¿Confirmar envío?{Colors.ENDC}")
    confirm = input(f"{Colors.BOLD}(s/n): {Colors.ENDC}").strip().lower()

    if confirm != 's':
        log_message("Envío cancelado", Colors.YELLOW)
        pause()
        return

    # Enviar paquete
    success, msg = client.send_packet(packet)
    log_message(msg, Colors.GREEN if success else Colors.RED)

    # Enviar imagen si es necesario
    if send_image and success:
        failure_code = packet[2]
        log_message("Esperando 500ms antes de enviar imagen...", Colors.CYAN)

        if send_image == 'auto':
            # Generar imagen automáticamente
            success_img, msg_img = client.generate_and_send_image(failure_code)
            log_message(msg_img, Colors.GREEN if success_img else Colors.RED)
        elif send_image == 'manual' and image_path:
            # Usar imagen proporcionada
            success_img, msg_img = client.send_image(image_path, failure_code)
            log_message(msg_img, Colors.GREEN if success_img else Colors.RED)

    pause()


# ========================================
# MENÚ DE PAQUETE PERSONALIZADO
# ========================================
def custom_packet_menu(client):
    """Menú para crear paquete personalizado"""
    print_header()
    print(f"{Colors.BOLD}🛠️  CREAR PAQUETE PERSONALIZADO{Colors.ENDC}\n")

    if not client.connected:
        log_message("Debes conectarte primero", Colors.RED)
        pause()
        return

    try:
        print(f"{Colors.CYAN}Ingresa los valores del paquete (0-9):{Colors.ENDC}\n")

        # General Status
        print(f"Estados disponibles: {', '.join([f'{k}={v}' for k, v in GENERAL_STATUS.items()])}")
        general = int(input(f"[0] General Status (0-3): ").strip())

        # Piece Status
        piece = int(input(f"[1] Piece Status (0=OK, 1=NOK): ").strip())

        # Failure Code
        print(f"Códigos: {', '.join([f'{k}={v}' for k, v in FAILURE_CODES.items()])}")
        failure = int(input(f"[2] Failure Code (0,1,2,3,4,99): ").strip())

        # Model ID
        model = int(input(f"[3] Model ID (0-9): ").strip())

        # Camera Status
        camera = int(input(f"[4] Camera Status (0=OK, 1=Falla): ").strip())

        # Electrical Status
        electrical = int(input(f"[5] Electrical Status (0=OK, 1=Falla): ").strip())

        # Ready Flag
        ready = int(input(f"[6] Ready Flag (0=Ignorar, 1=Procesar): ").strip())

        # Reserved
        reserved = int(input(f"[7] Reserved (0-9): ").strip())

        packet = [general, piece, failure, model, camera, electrical, ready, reserved]

        print_packet_info(packet)

        # Preguntar por imagen
        if failure > 0 and piece == 1:
            print(f"\n{Colors.YELLOW}⚠️  Este paquete indica falla (failureCode={failure}){Colors.ENDC}")
            print(f"{Colors.CYAN}Opciones:{Colors.ENDC}")
            print(f"  1. Generar imagen automáticamente")
            print(f"  2. Usar imagen existente")
            print(f"  3. No enviar imagen")

            img_choice = input(f"{Colors.BOLD}Selecciona opción (1/2/3): {Colors.ENDC}").strip()

            # Enviar paquete primero
            success, msg = client.send_packet(packet)
            log_message(msg, Colors.GREEN if success else Colors.RED)

            if success and img_choice in ['1', '2']:
                log_message("Esperando 500ms antes de enviar imagen...", Colors.CYAN)

                if img_choice == '1':
                    success_img, msg_img = client.generate_and_send_image(failure)
                    log_message(msg_img, Colors.GREEN if success_img else Colors.RED)
                else:
                    image_path = input(f"{Colors.BOLD}Ruta de la imagen: {Colors.ENDC}").strip()
                    if os.path.exists(image_path):
                        success_img, msg_img = client.send_image(image_path, failure)
                        log_message(msg_img, Colors.GREEN if success_img else Colors.RED)
                    else:
                        log_message(f"Archivo no encontrado: {image_path}", Colors.RED)
        else:
            success, msg = client.send_packet(packet)
            log_message(msg, Colors.GREEN if success else Colors.RED)

    except ValueError:
        log_message("Error: Debes ingresar números válidos", Colors.RED)
    except Exception as e:
        log_message(f"Error: {str(e)}", Colors.RED)

    pause()


# ========================================
# MENÚ DE ENVÍO AUTOMÁTICO
# ========================================
def auto_send_menu(client):
    """Menú de envío automático"""
    print_header()
    print(f"{Colors.BOLD}🤖 ENVÍO AUTOMÁTICO{Colors.ENDC}\n")

    if not client.connected:
        log_message("Debes conectarte primero", Colors.RED)
        pause()
        return

    # Seleccionar preset
    print(f"{Colors.CYAN}Selecciona el tipo de paquete a enviar:{Colors.ENDC}\n")
    for key, preset in PRESETS.items():
        print(f"{key}. {preset['name']}")

    choice = input(f"\n{Colors.BOLD}Paquete: {Colors.ENDC}").strip()

    if choice not in PRESETS:
        log_message("Opción inválida", Colors.RED)
        pause()
        return

    preset = PRESETS[choice]

    # Cantidad
    try:
        count = int(input(f"{Colors.BOLD}Cantidad de paquetes: {Colors.ENDC}").strip())
        delay = float(input(f"{Colors.BOLD}Delay entre paquetes (segundos): {Colors.ENDC}").strip())
    except ValueError:
        log_message("Valores inválidos", Colors.RED)
        pause()
        return

    print(f"\n{Colors.YELLOW}Se enviarán {count} paquetes con {delay}s de delay{Colors.ENDC}")
    confirm = input(f"{Colors.BOLD}¿Continuar? (s/n): {Colors.ENDC}").strip().lower()

    if confirm != 's':
        return

    print(f"\n{Colors.GREEN}Iniciando envío automático...{Colors.ENDC}")
    print(f"{Colors.YELLOW}Presiona Ctrl+C para detener{Colors.ENDC}\n")

    successful = 0
    failed = 0

    try:
        for i in range(count):
            success, msg = client.send_packet(preset['packet'])

            if success:
                successful += 1
                print(f"{Colors.GREEN}[{i + 1}/{count}] ✓ Enviado{Colors.ENDC}")
            else:
                failed += 1
                print(f"{Colors.RED}[{i + 1}/{count}] ✗ Falló: {msg}{Colors.ENDC}")

            if i < count - 1:
                time.sleep(delay)

    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⏸️  Envío detenido por el usuario{Colors.ENDC}")

    print(f"\n{Colors.BOLD}Resumen:{Colors.ENDC}")
    print(f"  {Colors.GREEN}Exitosos: {successful}{Colors.ENDC}")
    print(f"  {Colors.RED}Fallidos: {failed}{Colors.ENDC}")

    pause()


# ========================================
# MENÚ DE SECUENCIAS DE TEST
# ========================================
def test_sequences_menu(client):
    """Menú de secuencias de test automatizadas"""
    print_header()
    print(f"{Colors.BOLD}🧪 SECUENCIAS DE TEST{Colors.ENDC}\n")

    if not client.connected:
        log_message("Debes conectarte primero", Colors.RED)
        pause()
        return

    print(f"{Colors.CYAN}1.{Colors.ENDC} Test Básico - Solo piezas OK (x10)")
    print(f"{Colors.CYAN}2.{Colors.ENDC} Test Mixto - OK + NOK (x20)")
    print(f"{Colors.CYAN}3.{Colors.ENDC} Test Fallas - Solo NOK con diferentes códigos")
    print(f"{Colors.CYAN}4.{Colors.ENDC} Test Completo - Flujo realista (x50)")
    print(f"{Colors.RED}0.{Colors.ENDC} Volver")

    choice = input(f"\n{Colors.BOLD}Selecciona secuencia: {Colors.ENDC}").strip()

    if choice == '0':
        return
    elif choice == '1':
        run_test_basic(client)
    elif choice == '2':
        run_test_mixed(client)
    elif choice == '3':
        run_test_failures(client)
    elif choice == '4':
        run_test_complete(client)
    else:
        log_message("Opción inválida", Colors.RED)

    pause()


def run_test_basic(client):
    """Test básico - Solo OK"""
    print(f"\n{Colors.GREEN}▶️  Ejecutando Test Básico...{Colors.ENDC}\n")

    for i in range(10):
        success, msg = client.send_packet([0, 0, 0, 1, 0, 0, 1, 0])
        status = "✓" if success else "✗"
        color = Colors.GREEN if success else Colors.RED
        print(f"{color}[{i + 1}/10] {status} Pieza OK{Colors.ENDC}")
        time.sleep(0.5)

    log_message("Test completado", Colors.GREEN)


def run_test_mixed(client):
    """Test mixto - OK + NOK"""
    print(f"\n{Colors.YELLOW}▶️  Ejecutando Test Mixto...{Colors.ENDC}\n")

    packets = [
                  ([0, 0, 0, 1, 0, 0, 1, 0], "OK", False),
                  ([0, 0, 0, 1, 0, 0, 1, 0], "OK", False),
                  ([0, 1, 2, 1, 1, 0, 1, 0], "NOK - Etiqueta", True),
                  ([0, 0, 0, 1, 0, 0, 1, 0], "OK", False),
                  ([0, 1, 1, 1, 0, 1, 1, 0], "NOK - Hipot", True),
              ] * 4  # Repetir 4 veces = 20 paquetes

    for i, (packet, desc, needs_image) in enumerate(packets):
        success, msg = client.send_packet(packet)
        status = "✓" if success else "✗"
        color = Colors.GREEN if success else Colors.RED
        print(f"{color}[{i + 1}/20] {status} {desc}{Colors.ENDC}")

        # Generar imagen si es NOK
        if success and needs_image:
            failure_code = packet[2]
            client.generate_and_send_image(failure_code, delay=0.3)

        time.sleep(0.7)

    log_message("Test completado", Colors.GREEN)


def run_test_failures(client):
    """Test de fallas - Solo NOK"""
    print(f"\n{Colors.RED}▶️  Ejecutando Test de Fallas...{Colors.ENDC}\n")

    failures = [
        ([0, 1, 1, 1, 0, 1, 1, 0], "Hipot"),
        ([0, 1, 2, 1, 1, 0, 1, 0], "Etiqueta"),
        ([0, 1, 3, 1, 0, 0, 1, 0], "Modelo"),
        ([0, 1, 4, 1, 1, 0, 1, 0], "Terminal"),
        ([0, 1, 99, 1, 1, 1, 1, 0], "Desconocida"),
    ]

    for packet, desc in failures:
        success, msg = client.send_packet(packet)
        status = "✓" if success else "✗"
        color = Colors.GREEN if success else Colors.RED
        print(f"{color}{status} NOK - {desc}{Colors.ENDC}")

        # Generar imagen para cada falla
        if success:
            failure_code = packet[2]
            client.generate_and_send_image(failure_code, delay=0.5)

        time.sleep(1.0)

    log_message("Test completado", Colors.GREEN)


def run_test_complete(client):
    """Test completo - Flujo realista"""
    print(f"\n{Colors.CYAN}▶️  Ejecutando Test Completo (50 piezas)...{Colors.ENDC}\n")

    import random

    ok_count = 0
    nok_count = 0

    for i in range(50):
        # 85% OK, 15% NOK (realista)
        if random.random() < 0.85:
            packet = [0, 0, 0, 1, 0, 0, 1, 0]
            desc = "OK"
            ok_count += 1
            color = Colors.GREEN
            needs_image = False
        else:
            failure_code = random.choice([1, 2, 4])
            packet = [0, 1, failure_code, 1, 1, 0, 1, 0]
            desc = f"NOK - {FAILURE_CODES[failure_code]}"
            nok_count += 1
            color = Colors.RED
            needs_image = True

        success, msg = client.send_packet(packet)
        status = "✓" if success else "✗"
        print(f"{color}[{i + 1}/50] {status} {desc}{Colors.ENDC}")

        # Generar imagen si es NOK
        if success and needs_image:
            client.generate_and_send_image(failure_code, delay=0.2)

        time.sleep(0.3)

    print(f"\n{Colors.BOLD}Resumen:{Colors.ENDC}")
    print(f"  {Colors.GREEN}OK: {ok_count} ({ok_count * 100 / 50:.1f}%){Colors.ENDC}")
    print(f"  {Colors.RED}NOK: {nok_count} ({nok_count * 100 / 50:.1f}%){Colors.ENDC}")

    log_message("Test completado", Colors.GREEN)


# ========================================
# MENÚ DE MANTENIMIENTO
# ========================================
def maintenance_menu(client):
    """Menú de modo mantenimiento"""
    print_header()
    print(f"{Colors.BOLD}🛠️  MODO MANTENIMIENTO{Colors.ENDC}\n")

    if not client.connected:
        log_message("Debes conectarte primero", Colors.RED)
        pause()
        return

    print(f"{Colors.YELLOW}Enviar señal de estado de mantenimiento al servidor{Colors.ENDC}\n")
    
    print(f"{Colors.CYAN}1.{Colors.ENDC} 🛠️  Entrar en Mantenimiento (sistema detenido)")
    print(f"{Colors.CYAN}2.{Colors.ENDC} 🔧 Mantenimiento con pieza rechazada")
    print(f"{Colors.CYAN}3.{Colors.ENDC} ▶️  Salir de Mantenimiento (modo RUNNING)")
    print(f"{Colors.CYAN}4.{Colors.ENDC} 🔄 Enviar estado de Mantenimiento continuo")
    print(f"{Colors.RED}0.{Colors.ENDC} Volver")

    choice = input(f"\n{Colors.BOLD}Selecciona opción: {Colors.ENDC}").strip()

    if choice == '0':
        return
    elif choice == '1':
        # Mantenimiento - sistema detenido
        packet = [3, 0, 0, 1, 0, 0, 1, 0]
        print(f"\n{Colors.YELLOW}Enviando estado: MAINTENANCE (sistema detenido){Colors.ENDC}")
        print_packet_info(packet)
        
        confirm = input(f"\n{Colors.BOLD}¿Confirmar envío? (s/n): {Colors.ENDC}").strip().lower()
        if confirm == 's':
            success, msg = client.send_packet(packet)
            log_message(msg, Colors.GREEN if success else Colors.RED)
    
    elif choice == '2':
        # Mantenimiento con pieza NOK
        packet = [3, 1, 99, 1, 0, 0, 1, 0]
        print(f"\n{Colors.YELLOW}Enviando estado: MAINTENANCE con pieza rechazada{Colors.ENDC}")
        print_packet_info(packet)
        
        confirm = input(f"\n{Colors.BOLD}¿Confirmar envío? (s/n): {Colors.ENDC}").strip().lower()
        if confirm == 's':
            success, msg = client.send_packet(packet)
            log_message(msg, Colors.GREEN if success else Colors.RED)
    
    elif choice == '3':
        # Salir de mantenimiento
        packet = [0, 0, 0, 1, 0, 0, 1, 0]
        print(f"\n{Colors.GREEN}Enviando estado: RUNNING (normal){Colors.ENDC}")
        print_packet_info(packet)
        
        confirm = input(f"\n{Colors.BOLD}¿Confirmar envío? (s/n): {Colors.ENDC}").strip().lower()
        if confirm == 's':
            success, msg = client.send_packet(packet)
            log_message(msg, Colors.GREEN if success else Colors.RED)
    
    elif choice == '4':
        # Envío continuo de mantenimiento
        print(f"\n{Colors.YELLOW}Modo: Envío continuo de estado MAINTENANCE{Colors.ENDC}")
        try:
            interval = float(input(f"{Colors.BOLD}Intervalo entre envíos (segundos): {Colors.ENDC}").strip())
        except ValueError:
            log_message("Valor inválido", Colors.RED)
            pause()
            return
        
        packet = [3, 0, 0, 1, 0, 0, 1, 0]
        print(f"\n{Colors.GREEN}Iniciando envío continuo...{Colors.ENDC}")
        print(f"{Colors.YELLOW}Presiona Ctrl+C para detener{Colors.ENDC}\n")
        
        count = 0
        try:
            while True:
                success, msg = client.send_packet(packet)
                count += 1
                if success:
                    print(f"{Colors.GREEN}[{count}] ✓ Estado MAINTENANCE enviado{Colors.ENDC}")
                else:
                    print(f"{Colors.RED}[{count}] ✗ Error: {msg}{Colors.ENDC}")
                    break
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}⏸️  Envío detenido (total: {count} paquetes){Colors.ENDC}")
    
    else:
        log_message("Opción inválida", Colors.RED)
    
    pause()


# ========================================
# MENÚ DE CONFIGURACIÓN
# ========================================
def config_menu(client):
    """Menú de configuración"""
    global TCP_HOST, TCP_PORT, FTP_DIR

    print_header()
    print(f"{Colors.BOLD}⚙️  CONFIGURACIÓN{Colors.ENDC}\n")

    print(f"Host TCP actual:     {Colors.CYAN}{TCP_HOST}{Colors.ENDC}")
    print(f"Puerto TCP actual:   {Colors.CYAN}{TCP_PORT}{Colors.ENDC}")
    print(f"Directorio FTP:      {Colors.CYAN}{FTP_DIR}{Colors.ENDC}")

    print(f"\n{Colors.YELLOW}Nota: Los cambios no afectan a conexiones activas{Colors.ENDC}")

    print(f"\n{Colors.CYAN}1.{Colors.ENDC} Cambiar Host TCP")
    print(f"{Colors.CYAN}2.{Colors.ENDC} Cambiar Puerto TCP")
    print(f"{Colors.CYAN}3.{Colors.ENDC} Cambiar Directorio FTP")
    print(f"{Colors.CYAN}4.{Colors.ENDC} Verificar directorio FTP")
    print(f"{Colors.RED}0.{Colors.ENDC} Volver")

    choice = input(f"\n{Colors.BOLD}Selecciona opción: {Colors.ENDC}").strip()

    if choice == '1':
        new_host = input(f"{Colors.BOLD}Nuevo host (actual: {TCP_HOST}): {Colors.ENDC}").strip()
        if new_host:
            TCP_HOST = new_host
            log_message(f"Host cambiado a: {TCP_HOST}", Colors.GREEN)
    elif choice == '2':
        try:
            new_port = int(input(f"{Colors.BOLD}Nuevo puerto (actual: {TCP_PORT}): {Colors.ENDC}").strip())
            TCP_PORT = new_port
            log_message(f"Puerto cambiado a: {TCP_PORT}", Colors.GREEN)
        except ValueError:
            log_message("Puerto inválido", Colors.RED)
    elif choice == '3':
        new_dir = input(f"{Colors.BOLD}Nuevo directorio: {Colors.ENDC}").strip()
        if new_dir:
            FTP_DIR = os.path.expanduser(new_dir)
            log_message(f"Directorio cambiado a: {FTP_DIR}", Colors.GREEN)
    elif choice == '4':
        if os.path.exists(FTP_DIR):
            log_message(f"✓ Directorio existe: {FTP_DIR}", Colors.GREEN)
            files = os.listdir(FTP_DIR)
            print(f"\nArchivos en directorio: {len(files)}")
            if files:
                print(f"{Colors.CYAN}Últimos 5 archivos:{Colors.ENDC}")
                for f in files[-5:]:
                    print(f"  - {f}")
        else:
            log_message(f"✗ Directorio no existe: {FTP_DIR}", Colors.RED)
            response = input(f"{Colors.BOLD}¿Crear directorio? (s/n): {Colors.ENDC}").strip().lower()
            if response == 's':
                try:
                    os.makedirs(FTP_DIR, exist_ok=True)
                    log_message(f"✓ Directorio creado: {FTP_DIR}", Colors.GREEN)
                except Exception as e:
                    log_message(f"✗ Error al crear: {str(e)}", Colors.RED)

    if choice != '0':
        pause()


# ========================================
# FUNCIÓN PRINCIPAL
# ========================================
def main():
    """Función principal"""
    client = PLCClient()

    try:
        # Verificar directorio FTP al inicio
        if not os.path.exists(FTP_DIR):
            print(f"{Colors.YELLOW}⚠️  Directorio FTP no existe: {FTP_DIR}{Colors.ENDC}")
            response = input(f"{Colors.BOLD}¿Crear ahora? (s/n): {Colors.ENDC}").strip().lower()
            if response == 's':
                os.makedirs(FTP_DIR, exist_ok=True)
                print(f"{Colors.GREEN}✓ Directorio creado{Colors.ENDC}\n")
            time.sleep(1)

        # Menú principal
        main_menu(client)

    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⏸️  Programa interrumpido{Colors.ENDC}")
        if client.connected:
            client.disconnect()
        print(f"{Colors.CYAN}👋 ¡Hasta luego!{Colors.ENDC}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error fatal: {str(e)}{Colors.ENDC}\n")
        if client.connected:
            client.disconnect()
        sys.exit(1)


if __name__ == "__main__":
    main()