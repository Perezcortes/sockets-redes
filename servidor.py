import socket
import os

# --- Configuración del Servidor ---
HOST = '127.0.0.1'  # Escucha en localhost
PORT = 5000         # Puerto donde el servidor escuchará
BUFFER_SIZE = 4096  # Tamaño del búfer para enviar datos en bloques
CARPETA_ARCHIVOS = "./"  # Carpeta donde están los archivos a compartir

def iniciar_servidor():
    """Inicializa y ejecuta el servidor de sockets TCP."""
    
    print(f"--- Servidor TCP ---")
    print(f"[*] Iniciando servidor en {HOST}:{PORT}...")
    
    try:
        # 1. Creación del Socket
        # AF_INET: para IPv4, SOCK_STREAM: para TCP
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"[+] Socket del servidor creado.")
        
        # Permite reutilizar la dirección inmediatamente (útil para reiniciar rápidamente)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # 2. Vinculación (Bind)
        # Asocia el socket con la dirección IP y puerto especificados
        server_socket.bind((HOST, PORT))
        print(f"[+] Socket vinculado a {HOST}:{PORT}")
        
        # 3. Escucha (Listen)
        # Pone el socket en modo escucha para aceptar conexiones entrantes
        # El argumento '5' es el tamaño de la cola de conexiones pendientes
        server_socket.listen(5)
        print(f"[+] Servidor en escucha. Esperando conexiones de clientes...")
        print(f"[*] Presiona Ctrl+C para detener el servidor.\n")
        
        # Bucle principal: el servidor acepta múltiples conexiones
        while True:
            # 4. Aceptación de Conexión (Accept)
            # Bloquea hasta que un cliente se conecta
            client_socket, client_address = server_socket.accept()
            print(f"\n[+] Nueva conexión desde {client_address[0]}:{client_address[1]}")
            
            try:
                # 5. Recepción de la Solicitud del Cliente
                # Espera recibir el nombre del archivo solicitado
                nombre_archivo = client_socket.recv(BUFFER_SIZE).decode('utf-8')
                print(f"[*] Cliente solicita: '{nombre_archivo}'")
                
                # Construye la ruta completa del archivo
                ruta_archivo = os.path.join(CARPETA_ARCHIVOS, nombre_archivo)
                
                # 6. Verificación y Envío del Archivo
                if os.path.exists(ruta_archivo) and os.path.isfile(ruta_archivo):
                    # El archivo existe
                    file_size = os.path.getsize(ruta_archivo)
                    print(f"[+] Archivo encontrado. Tamaño: {file_size} bytes")
                    
                    # Envía confirmación y tamaño del archivo
                    response = f"FILE_EXISTS|{file_size}"
                    client_socket.sendall(response.encode('utf-8'))
                    print(f"[*] Enviando archivo...")
                    
                    # Lee y envía el archivo en bloques
                    sent_bytes = 0
                    with open(ruta_archivo, 'rb') as f:
                        while True:
                            chunk = f.read(BUFFER_SIZE)
                            if not chunk:
                                break
                            client_socket.sendall(chunk)
                            sent_bytes += len(chunk)
                    
                    print(f"[+] Transferencia completada: {sent_bytes} bytes enviados")
                    
                else:
                    # El archivo no existe
                    print(f"[!] Archivo no encontrado: '{nombre_archivo}'")
                    client_socket.sendall("FILE_NOT_FOUND".encode('utf-8'))
                    
            except Exception as e:
                print(f"[!] Error al procesar la solicitud del cliente: {e}")
                
            finally:
                # 7. Cierre de la Conexión con el Cliente
                client_socket.close()
                print(f"[+] Conexión con {client_address[0]}:{client_address[1]} cerrada")
                
    except KeyboardInterrupt:
        print("\n\n[*] Servidor detenido por el usuario (Ctrl+C)")
        
    except Exception as e:
        print(f"\n[!] Error inesperado en el servidor: {e}")
        
    finally:
        # 8. Cierre del Socket del Servidor
        if 'server_socket' in locals():
            server_socket.close()
            print("[+] Socket del servidor cerrado.")

if __name__ == "__main__":
    iniciar_servidor()