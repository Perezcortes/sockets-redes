import socket
import os

# --- Configuración del Cliente ---
HOST = '127.0.0.1'  # ¡CORREGIDO! Usamos 127.0.0.1 ya que el servidor está escuchando allí (localhost).
PORT = 5000        # Debe coincidir con el puerto del servidor
BUFFER_SIZE = 4096  # Tamaño del búfer para recibir datos en bloques
NOMBRE_ARCHIVO_SOLICITADO = "archivo_servidor.txt" # El archivo que queremos pedir
NOMBRE_ARCHIVO_RECIBIDO = "archivo_recibido.txt"

def iniciar_cliente():
    """Inicializa y ejecuta el cliente de sockets TCP."""
    
    print(f"--- Cliente TCP ---")
    print(f"[*] Intentando conectar con el servidor en {HOST}:{PORT}...")
    
    try:
        # 1. Creación del Socket
        # AF_INET: para IPv4, SOCK_STREAM: para TCP
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"[+] Socket de cliente creado.")

        # 2. Solicitud de Conexión (Connect)
        # Intenta conectar con el servidor. Si falla, salta al bloque except.
        client_socket.connect((HOST, PORT))
        print(f"[+] Conexión establecida con el servidor.")

        # 3. Envío de la Solicitud de Archivo
        print(f"[*] Solicitando archivo: '{NOMBRE_ARCHIVO_SOLICITADO}'")
        client_socket.sendall(NOMBRE_ARCHIVO_SOLICITADO.encode('utf-8'))

        # 4. Recepción de la Respuesta Inicial (Estado y Tamaño)
        # El cliente espera la respuesta del servidor sobre la disponibilidad del archivo
        response = client_socket.recv(BUFFER_SIZE).decode('utf-8')
        
        # Analizamos la respuesta para ver el estado y el tamaño
        if response.startswith("FILE_EXISTS|"):
            _, file_size_str = response.split("|")
            file_size = int(file_size_str)
            print(f"[+] Archivo encontrado en el servidor. Tamaño total: {file_size} bytes.")
            print(f"[*] Comenzando la recepción del archivo...")

            # 5. Recepción y Escritura del Archivo
            received_bytes = 0
            
            # Abrimos el archivo local en modo binario ('wb') para escribir los datos recibidos
            with open(NOMBRE_ARCHIVO_RECIBIDO, 'wb') as f:
                while received_bytes < file_size:
                    # Recibimos el siguiente bloque de datos
                    chunk = client_socket.recv(BUFFER_SIZE)
                    if not chunk:
                        # Si no hay más datos antes de alcanzar el tamaño esperado, es un error
                        print(f"[!] ERROR: Conexión cerrada inesperadamente. Datos recibidos: {received_bytes}/{file_size}")
                        break
                        
                    f.write(chunk)
                    received_bytes += len(chunk)
                    
                    # Opcional: mostrar progreso
                    # print(f"  Recibido {received_bytes}/{file_size} bytes...")

            if received_bytes == file_size:
                print(f"\n[+] Transferencia exitosa.")
                print(f"[+] Archivo guardado como: '{NOMBRE_ARCHIVO_RECIBIDO}' ({file_size} bytes)")
            
        elif response == "FILE_NOT_FOUND":
            # 5. Notificación de Falla (Archivo no encontrado)
            print(f"\n[!] FALLA: El servidor no encontró el archivo '{NOMBRE_ARCHIVO_SOLICITADO}'.")
        
        else:
            print(f"\n[!] FALLA: Respuesta desconocida del servidor: {response}")


    except ConnectionRefusedError:
        # 5. Notificación de Falla (No conexión)
        print("\n[!] FALLA: No se pudo establecer la conexión.")
        print("    Asegúrate de que el servidor (servidor.py) esté ejecutándose y en escucha.")
    except socket.gaierror:
        # Error al resolver la dirección (problema de DNS, aunque aquí usamos IP)
        print("\n[!] FALLA: Error de dirección. Verifica la IP y el Puerto.")
    except Exception as e:
        # Cualquier otro error, como un problema de lectura/escritura de archivo.
        print(f"\n[!] Ocurrió un error inesperado: {e}")
        
    finally:
        # 6. Cierre de la Sesión
        if 'client_socket' in locals():
            client_socket.close()
            print("\n[+] Cierre de sesión y socket del cliente realizado.")
            
if __name__ == "__main__":
    iniciar_cliente()
