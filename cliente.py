import socket
import os

# --- Configuración del Cliente ---
HOST = '127.0.0.1'  # Dirección del servidor
PORT = 5000         # Puerto del servidor
BUFFER_SIZE = 4096  # Tamaño del búfer para recibir datos

def iniciar_cliente():
    """Inicializa y ejecuta el cliente de sockets TCP."""
    
    print("=" * 60)
    print("--- CLIENTE TCP DE TRANSFERENCIA DE ARCHIVOS ---")
    print("=" * 60)
    
    # Solicitar al usuario el nombre del archivo
    print("\nArchivos disponibles para solicitar:")
    print("  - archivo_servidor.txt (texto)")
    print("  - documento.pdf (PDF)")
    print("  - imagen.jpg (imagen)")
    print("  - video.mp4 (video)")
    print("  - documento.docx (Word)")
    
    nombre_archivo = input("\nIngresa el nombre del archivo que deseas solicitar: ").strip()
    
    if not nombre_archivo:
        print("[!] ERROR: Debes ingresar un nombre de archivo.")
        return
    
    # Definir el nombre del archivo recibido (mantiene la extensión original)
    nombre_base, extension = os.path.splitext(nombre_archivo)
    archivo_recibido = f"{nombre_base}_recibido{extension}"
    
    print(f"\n[*] Intentando conectar con el servidor en {HOST}:{PORT}...")
    
    try:
        # 1. CREACIÓN DEL SOCKET
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"[+] Socket de cliente creado correctamente.")

        # 2. SOLICITUD DE CONEXIÓN (CONNECT)
        client_socket.connect((HOST, PORT))
        print(f"[+] CONEXIÓN ESTABLECIDA con el servidor.")
        print("=" * 60)

        # 3. ENVÍO DE LA SOLICITUD DE ARCHIVO
        print(f"\n[*] Solicitando archivo: '{nombre_archivo}'")
        client_socket.sendall(nombre_archivo.encode('utf-8'))
        print(f"[+] Solicitud enviada al servidor.")

        # 4. RECEPCIÓN DE LA RESPUESTA INICIAL (Estado y Tamaño)
        print(f"[*] Esperando respuesta del servidor...")
        response = client_socket.recv(BUFFER_SIZE).decode('utf-8')
        
        # Analizar la respuesta
        if response.startswith("FILE_EXISTS|"):
            _, file_size_str = response.split("|")
            file_size = int(file_size_str)
            
            print(f"[+] Archivo ENCONTRADO en el servidor.")
            print(f"    - Tamaño: {file_size} bytes ({file_size/1024:.2f} KB)")
            print("=" * 60)
            print(f"\n[*] Iniciando RECEPCIÓN del archivo...")

            # 5. RECEPCIÓN Y ESCRITURA DEL ARCHIVO (modo binario para cualquier tipo)
            received_bytes = 0
            
            with open(archivo_recibido, 'wb') as f:
                while received_bytes < file_size:
                    # Calcular cuántos bytes faltan
                    remaining = file_size - received_bytes
                    # Recibir hasta BUFFER_SIZE bytes, pero no más de los que faltan
                    to_receive = min(BUFFER_SIZE, remaining)
                    
                    chunk = client_socket.recv(to_receive)
                    if not chunk:
                        print(f"\n[!] ERROR: Conexión cerrada inesperadamente.")
                        print(f"    Datos recibidos: {received_bytes}/{file_size} bytes")
                        break
                        
                    f.write(chunk)
                    received_bytes += len(chunk)
                    
                    # Mostrar progreso
                    progress = (received_bytes / file_size) * 100
                    print(f"    Progreso: {received_bytes}/{file_size} bytes ({progress:.1f}%)", end='\r')

            print()  # Nueva línea después del progreso
            
            if received_bytes == file_size:
                print("=" * 60)
                print(f"[+] TRANSFERENCIA EXITOSA")
                print(f"[+] Archivo guardado como: '{archivo_recibido}'")
                print(f"    - Tamaño final: {received_bytes} bytes ({received_bytes/1024:.2f} KB)")
                print("=" * 60)
            else:
                print("=" * 60)
                print(f"[!] TRANSFERENCIA INCOMPLETA")
                print(f"    - Esperado: {file_size} bytes")
                print(f"    - Recibido: {received_bytes} bytes")
                print("=" * 60)
            
        elif response == "FILE_NOT_FOUND":
            # 5. NOTIFICACIÓN DE FALLA (Archivo no encontrado)
            print("=" * 60)
            print(f"[!] FALLA: Archivo NO ENCONTRADO")
            print(f"    El servidor no tiene el archivo '{nombre_archivo}'")
            print("=" * 60)
        
        else:
            print("=" * 60)
            print(f"[!] FALLA: Respuesta desconocida del servidor")
            print(f"    Respuesta recibida: {response}")
            print("=" * 60)

    except ConnectionRefusedError:
        # 5. NOTIFICACIÓN DE FALLA (No conexión)
        print("=" * 60)
        print("[!] FALLA: No se pudo establecer la conexión con el servidor")
        print("    Posibles causas:")
        print("    - El servidor no está ejecutándose")
        print("    - El servidor no está escuchando en el puerto especificado")
        print("    - Firewall bloqueando la conexión")
        print("=" * 60)
        
    except socket.gaierror:
        print("=" * 60)
        print("[!] FALLA: Error de dirección")
        print("    Verifica la dirección IP y el puerto del servidor")
        print("=" * 60)
        
    except Exception as e:
        print("=" * 60)
        print(f"[!] ERROR inesperado: {e}")
        print("=" * 60)
        
    finally:
        # 6. CIERRE DE LA SESIÓN
        if 'client_socket' in locals():
            client_socket.close()
            print(f"\n[+] CIERRE DE SESIÓN completado.")
            print(f"[+] Socket del cliente cerrado correctamente.")
            print("=" * 60)
            
if __name__ == "__main__":
    iniciar_cliente()