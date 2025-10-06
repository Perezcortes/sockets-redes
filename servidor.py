import socket
import os

# --- Configuración del Servidor ---
HOST = '127.0.0.1'  # Escucha en localhost
PORT = 5000         # Puerto donde el servidor escuchará
BUFFER_SIZE = 4096  # Tamaño del búfer para enviar datos en bloques
CARPETA_ARCHIVOS = "./"  # Carpeta donde están los archivos a compartir

def iniciar_servidor():
    """Inicializa y ejecuta el servidor de sockets TCP."""
    
    print("=" * 60)
    print("--- SERVIDOR TCP DE TRANSFERENCIA DE ARCHIVOS ---")
    print("=" * 60)
    print(f"[*] Iniciando servidor en {HOST}:{PORT}...")
    
    try:
        # 1. CREACIÓN DEL SOCKET
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"[+] Socket del servidor creado correctamente.")
        
        # Permite reutilizar la dirección inmediatamente
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # 2. VINCULACIÓN (BIND)
        server_socket.bind((HOST, PORT))
        print(f"[+] Socket vinculado a {HOST}:{PORT}")
        
        # 3. ESCUCHA (LISTEN)
        server_socket.listen(5)
        print(f"[+] Servidor en estado de ESCUCHA.")
        print(f"[*] Esperando conexiones de clientes...")
        print(f"[*] Presiona Ctrl+C para detener el servidor.\n")
        print("=" * 60)
        
        # Bucle principal: acepta múltiples conexiones
        while True:
            # 4. ACEPTACIÓN DE CONEXIÓN (ACCEPT)
            client_socket, client_address = server_socket.accept()
            print(f"\n[+] NUEVA CONEXIÓN establecida desde {client_address[0]}:{client_address[1]}")
            
            try:
                # 5. RECEPCIÓN DE LA SOLICITUD DEL CLIENTE
                nombre_archivo = client_socket.recv(BUFFER_SIZE).decode('utf-8').strip()
                print(f"[*] Cliente solicita el archivo: '{nombre_archivo}'")
                
                # Construye la ruta completa del archivo
                ruta_archivo = os.path.join(CARPETA_ARCHIVOS, nombre_archivo)
                
                # 6. VERIFICACIÓN Y ENVÍO DEL ARCHIVO
                if os.path.exists(ruta_archivo) and os.path.isfile(ruta_archivo):
                    # El archivo existe
                    file_size = os.path.getsize(ruta_archivo)
                    file_ext = os.path.splitext(nombre_archivo)[1].lower()
                    
                    print(f"[+] Archivo ENCONTRADO")
                    print(f"    - Tamaño: {file_size} bytes ({file_size/1024:.2f} KB)")
                    print(f"    - Tipo: {file_ext if file_ext else 'sin extensión'}")
                    
                    # Envía confirmación con el tamaño del archivo
                    response = f"FILE_EXISTS|{file_size}"
                    client_socket.sendall(response.encode('utf-8'))
                    print(f"[*] Notificación enviada al cliente: Archivo disponible")
                    
                    # Pequeña pausa para asegurar que el mensaje se procese
                    import time
                    time.sleep(0.1)
                    
                    # Lee y envía el archivo en bloques (modo binario para soportar cualquier tipo)
                    print(f"[*] Iniciando transferencia del archivo...")
                    sent_bytes = 0
                    with open(ruta_archivo, 'rb') as f:
                        while True:
                            chunk = f.read(BUFFER_SIZE)
                            if not chunk:
                                break
                            client_socket.sendall(chunk)
                            sent_bytes += len(chunk)
                            # Mostrar progreso
                            progress = (sent_bytes / file_size) * 100
                            print(f"    Progreso: {sent_bytes}/{file_size} bytes ({progress:.1f}%)", end='\r')
                    
                    print(f"\n[+] TRANSFERENCIA COMPLETADA: {sent_bytes} bytes enviados")
                    
                else:
                    # El archivo NO existe
                    print(f"[!] Archivo NO ENCONTRADO: '{nombre_archivo}'")
                    client_socket.sendall("FILE_NOT_FOUND".encode('utf-8'))
                    print(f"[*] Notificación enviada al cliente: Archivo no disponible")
                    
            except Exception as e:
                print(f"[!] ERROR al procesar la solicitud del cliente: {e}")
                
            finally:
                # 7. CIERRE DE LA CONEXIÓN CON EL CLIENTE
                client_socket.close()
                print(f"[+] Conexión con {client_address[0]}:{client_address[1]} CERRADA")
                print("=" * 60)
                
    except KeyboardInterrupt:
        print("\n\n[*] Servidor detenido por el usuario (Ctrl+C)")
        
    except Exception as e:
        print(f"\n[!] ERROR inesperado en el servidor: {e}")
        
    finally:
        # 8. CIERRE DEL SOCKET DEL SERVIDOR
        if 'server_socket' in locals():
            server_socket.close()
            print("[+] Socket del servidor cerrado correctamente.")
            print("=" * 60)

if __name__ == "__main__":
    iniciar_servidor()