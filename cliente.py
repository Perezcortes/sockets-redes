import socket
import os

#La indicaccion del host y puerto se hace desde la interfaz
BUFFER_SIZE = 4096

class LogicaCliente:

    #Lo mismo de iniciar cliente
    def __init__(self):
        """ Inicializa las variables."""
        self.client_socket = None

    def conectar(self, host, port):
        """
        Intentar establecer una conexión con el servidor.
        """
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host, port))
        except Exception as e:
            self.client_socket = None
            raise ConnectionError(f"No se pudo conectar a {host}:{port}. Detalles: {e}")

    def desconectar(self):
        """Cerrar la conexion."""
        if self.client_socket:
            try:
                self.client_socket.close()
            except Exception as e:
                print(f"Error al cerrar el socket: {e}")
            finally:
                self.client_socket = None

    def listar_archivos(self, file_type):
        """
        Pedir archivos de un tipo segun lo seleccionado en la interfaz.
        """
        if not self.client_socket:
            raise ConnectionError("No estás conectado a ningún servidor.")
        
        try:
            # Enviar comando para listar archivos 
            request = f"LIST|{file_type}"
            self.client_socket.sendall(request.encode('utf-8'))
            
            # Recibir la lista de archivos
            response = self.client_socket.recv(BUFFER_SIZE).decode('utf-8')
            
            if response:
                return response.split(',') # Devuelve una lista de nombres de archivo
            return [] # Devuelve una lista vacía si no hay archivos
            
        except Exception as e:
            raise IOError(f"Error al obtener la lista de archivos: {e}")


    def solicitar_archivo(self, nombre_archivo, ruta_guardado, progress_callback, status_callback):

        if not self.client_socket:
            raise ConnectionError("No estás conectado a ningún servidor.")

        try:
            # 1. Enviar solicitud de archivo 
            request = f"GET|{nombre_archivo}"
            self.client_socket.sendall(request.encode('utf-8'))
            
            # 2. Recibir respuesta del servidor (estado y tamaño)
            response = self.client_socket.recv(BUFFER_SIZE).decode('utf-8')
            
            if response.startswith("FILE_EXISTS|"):
                _, file_size_str = response.split("|")
                file_size = int(file_size_str)
                
                status_callback(f"Descargando... Tamaño: {file_size/1024:.2f} KB",False)

                # 3. Recibir y guardar el archivo en disco
                received_bytes = 0
                with open(ruta_guardado, 'wb') as f:
                    while received_bytes < file_size:
                        remaining = file_size - received_bytes
                        to_receive = min(BUFFER_SIZE, remaining)
                        chunk = self.client_socket.recv(to_receive)
                        if not chunk:
                            raise Exception("La conexión se cerró inesperadamente.")
                        f.write(chunk)
                        received_bytes += len(chunk)
                        
                        progress = (received_bytes / file_size) * 100
                        progress_callback(progress)

                if received_bytes != file_size:
                    raise Exception("Transferencia incompleta.")

            elif response == "FILE_NOT_FOUND":
                raise FileNotFoundError(f"El archivo '{nombre_archivo}' no fue encontrado en el servidor.")
            
            else:
                raise Exception(f"Respuesta desconocida del servidor: {response}")

        except Exception as e:
            status_callback(f"Error: {e}", True)
            raise e

