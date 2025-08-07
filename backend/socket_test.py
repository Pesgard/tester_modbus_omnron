import socket
import struct

# Configuración del servidor
HOST = '0.0.0.0'
PORT = 900

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Servidor TCP escuchando en {HOST}:{PORT}...")

try:
    while True:
        conn, addr = server_socket.accept()
        print(f"Conexión aceptada de {addr}")

        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break

                print(f"\nDatos crudos (bits): {data}")

                if len(data) == 8:
                    uint_val = struct.unpack('<Q', data)[0]
                    float_val = struct.unpack('<d', data)[0]

                    print(f" → Como uint64  : {uint_val}")
                    print(f" → Como float64 : {float_val}")
                else:
                    print(f" → Longitud inesperada: {len(data)} bytes")

except KeyboardInterrupt:
    print("\nServidor detenido manualmente.")
finally:
    server_socket.close()
