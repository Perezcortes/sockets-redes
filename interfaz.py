import customtkinter as ctk
from tkinter import messagebox
import time
import threading
import os

# Importar la clase de lógica del otro archivo
from cliente import LogicaCliente

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 5000

# Configurar apariencia de customTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class FileClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Proyecto 2 - Redes")
        self.root.geometry("500x450")
        
        # Colores
        self.bg_color = "#E7DFE9"
        self.button_color = "#B478B9"
        self.button_hover_color = "#a068a5"
        self.button_colorr = "#753E65"
        self.button_hover_colorr = "#491c3e"
        self.text_color = "#572F2F"
        self.button_text_color = "#463E3E"
        self.button_text_colorr = "#C9B3CE"
        self.client_logic = LogicaCliente()

        # Fuentes con CTK
        self.font_titulo = ctk.CTkFont(family='Noto Sans Tamil', size=20, weight='bold')
        self.font_boton_principal = ctk.CTkFont(family='URW Gothic', size=13, weight='bold')
        self.font_normal = ctk.CTkFont(family='Arial', size=12)

        # Frames para cada pantalla de la aplicación
        self.connection_frame = ctk.CTkFrame(root, fg_color=self.bg_color)
        self.selection_frame = ctk.CTkFrame(root, fg_color=self.bg_color)
        self.download_frame = ctk.CTkFrame(root, fg_color=self.bg_color)

        self.create_connection_widgets()
        self.create_selection_widgets()

        # El frame de descarga se crea dinámicamente
        self.connection_frame.pack(expand=True, fill="both", padx=20, pady=20)

    # cada pantalla

    def create_connection_widgets(self):
        ctk.CTkLabel(self.connection_frame, text="Descarga De Archivos", 
                     font=self.font_titulo, text_color=self.text_color).pack(pady=(20, 20))
        
        self.connect_button = ctk.CTkButton(self.connection_frame, 
                                           text="Conectate al servidor", 
                                           font=self.font_boton_principal,
                                           fg_color=self.button_color,
                                           text_color=self.button_text_color,
                                           hover_color=self.button_hover_color,
                                           command=self.start_connection_thread,
                                           corner_radius=20,
                                           border_width=0)
        self.connect_button.pack(pady=20)
        
        self.progress_bar_conn = ctk.CTkProgressBar(self.connection_frame, 
                                                   progress_color="#F26D7D",
                                                   corner_radius=10)
        self.progress_bar_conn.pack(fill='x', pady=10, padx=50)
        self.progress_bar_conn.set(0)
        
        self.status_label_conn = ctk.CTkLabel(self.connection_frame, 
                                             text="Esperando para conectar...",
                                             text_color=self.text_color,
                                             font=self.font_normal)
        self.status_label_conn.pack(pady=5)

    def create_selection_widgets(self):
        ctk.CTkLabel(self.selection_frame, text="SELECCIÓN DE ARCHIVO", 
                     font=self.font_titulo, text_color=self.text_color).pack(pady=(20, 30))
        
        button_options = {"font": self.font_boton_principal, 
                         "fg_color": self.button_color, 
                         "text_color": self.button_text_color,
                         "hover_color": self.button_hover_color,
                         "corner_radius": 15,
                         "border_width": 0,
                         "width": 150,
                         "height": 40}

        ctk.CTkButton(self.selection_frame, text="PDF", 
                     command=lambda: self.show_download_frame('PDF'), 
                     **button_options).pack(pady=10)
        ctk.CTkButton(self.selection_frame, text="IMAGEN", 
                     command=lambda: self.show_download_frame('IMAGEN'), 
                     **button_options).pack(pady=10)
        ctk.CTkButton(self.selection_frame, text="VIDEO", 
                     command=lambda: self.show_download_frame('VIDEO'), 
                     **button_options).pack(pady=10)
        ctk.CTkButton(self.selection_frame, text="OTRO", 
                     command=lambda: self.show_download_frame('OTRO'), 
                     **button_options).pack(pady=10)

    def create_download_widgets(self, file_type, file_list):
        # Limpia el frame de selección anterior
        for widget in self.download_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.download_frame, text=f"Archivos de {file_type}", 
                     font=self.font_titulo, text_color=self.text_color).pack(pady=(20, 10))
        
        # Muestra la lista de archivos
        files_text = "Archivos disponibles:\n" + ("\n".join(file_list) if file_list else "No se encontraron archivos de este tipo.")
        ctk.CTkLabel(self.download_frame, text=files_text, 
                     text_color=self.text_color, 
                     font=self.font_normal,
                     wraplength=450).pack(pady=10)

        # Aqui se introducira el nombre del archivo a descargar
        ctk.CTkLabel(self.download_frame, text="Ingresa el nombre del archivo:",
                    text_color=self.text_color,
                    font=self.font_normal).pack()
        self.filename_entry = ctk.CTkEntry(self.download_frame, 
                                          font=self.font_normal, 
                                          width=300,
                                          corner_radius=15)
        self.filename_entry.pack(pady=5)

        # Botón de descarga
        self.request_button = ctk.CTkButton(self.download_frame, 
                                           text="Descargar", 
                                           font=self.font_boton_principal,
                                           fg_color=self.button_color,
                                           text_color=self.button_text_color,
                                           hover_color=self.button_hover_color,
                                           command=self.start_request_file_thread,
                                           corner_radius=20,
                                           border_width=0)
        self.request_button.pack(pady=25)
        
        # Barra de progreso y estado
        self.progress_bar = ctk.CTkProgressBar(self.download_frame, 
                                              progress_color="#F57584",
                                              corner_radius=10)
        self.progress_bar.pack(fill='x', pady=5, padx=50)
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(self.download_frame, 
                                        text="Estado: Bueno",
                                        text_color=self.text_color,
                                        font=self.font_normal)
        self.status_label.pack(pady=5)
        
        # Botón para volver
        ctk.CTkButton(self.download_frame, text="<- Regresar", 
                     command=self.show_selection_frame,
                     fg_color=self.button_colorr,
                     text_color=self.button_text_colorr,
                     hover_color=self.button_hover_colorr,
                     corner_radius=20,
                     border_width=0,
                     width=100,
                     font=self.font_normal).pack(side="bottom", anchor="sw", pady=10, padx=10)

    # --- Lógica de hilos y comunicación ---

    def start_connection_thread(self):
        self.connect_button.configure(state="disabled")
        self.status_label_conn.configure(text="Conectando...")
        self.progress_bar_conn.start()
        threading.Thread(target=self.connect_task, daemon=True).start()
        
    def connect_task(self):
        try:
            time.sleep(1) 
            self.client_logic.conectar(DEFAULT_HOST, DEFAULT_PORT)
            self.root.after(0, self.on_connection_success)
        except Exception as e:
            self.root.after(0, self.on_connection_error, str(e))

    def start_request_file_thread(self):
        """
        Uso de hilo para la descarga automática del archivo.
        """
        #1.Definir donde se guardara la descarga 
        DOWNLOADS_FOLDER = "./descargas_cliente"
        
        # 2. Obtener el nombre del archivo del campo de texto
        filename = self.filename_entry.get().strip()
        if not filename:
            messagebox.showwarning("Entrada inválida", "Por favor, ingresa un nombre de archivo.")
            return

        # 3. Crear la carpeta de descargas si no existe
        try:
            if not os.path.exists(DOWNLOADS_FOLDER):
                os.makedirs(DOWNLOADS_FOLDER)
        except OSError as e:
            messagebox.showerror("Error de Carpeta", f"No se pudo crear la carpeta de descargas: {e}")
            return
            
        # 4. Construir la ruta completa donde se guardará el archivo
        save_path = os.path.join(DOWNLOADS_FOLDER, filename)

        self.request_button.configure(state="disabled")
        self.progress_bar.set(0)
        self.update_status(f"Preparando descarga de '{filename}'...")
        
        # Iniciar el hilo de descarga con la nueva ruta de guardado automático
        thread = threading.Thread(target=self.request_file_task, args=(filename, save_path), daemon=True)
        thread.start()

    def request_file_task(self, filename, save_path):
        try:
            self.client_logic.solicitar_archivo(
                filename,
                save_path,
                progress_callback=lambda p: self.root.after(0, self.update_progress, p),
                status_callback=lambda msg, err: self.root.after(0, self.update_status, msg)
            )

            success_msg = f"Archivo '{filename}' guardado en la carpeta '{os.path.basename(os.path.dirname(save_path))}'."
            self.root.after(0, lambda: messagebox.showinfo("Éxito", success_msg))
            self.root.after(0, self.update_status, "Descarga completada.")
        except Exception as e:
            # Si la descarga no funciono o algo aqui se muestra.
            self.root.after(0, lambda: messagebox.showerror("Error de Transferencia", str(e)))
        finally:
            # Se resetea la interfaz para otra solicitud
            self.root.after(0, self.reset_request_ui)

    #llamadas de retorno para actualizar la interfaz desde los hilos

    def on_connection_success(self):
        self.progress_bar_conn.stop()
        self.connection_frame.pack_forget()
        self.selection_frame.pack(expand=True, fill="both", padx=20, pady=20)

    def on_connection_error(self, error_message):
        self.progress_bar_conn.stop()
        messagebox.showerror("Error de Conexión", error_message)
        self.status_label_conn.configure(text="Fallo en la conexión.")
        self.connect_button.configure(state="normal")

    def show_download_frame(self, file_type):
        try:
            # Pedir la lista de archivos al servidor
            file_list = self.client_logic.listar_archivos(file_type)
            self.selection_frame.pack_forget()
            self.create_download_widgets(file_type, file_list)
            self.download_frame.pack(expand=True, fill="both", padx=20, pady=20)
        except Exception as e:
            messagebox.showerror("Error de Lista", f"No se pudo obtener la lista de archivos: {e}")

    def show_selection_frame(self):
        self.download_frame.pack_forget()
        self.selection_frame.pack(expand=True, fill="both", padx=20, pady=20)

    def update_progress(self, value):
        # Convertir el valor de 0-100 a 0-1 para CTkProgressBar
        self.progress_bar.set(value / 100)

    def update_status(self, message):
        self.status_label.configure(text=f"Estado: {message}")

    def reset_request_ui(self):
        self.request_button.configure(state="normal")

    def on_closing(self):
        self.client_logic.desconectar()
        self.root.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = FileClientGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()