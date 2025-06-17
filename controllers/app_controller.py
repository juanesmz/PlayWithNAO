# controllers/app_controller.py
import customtkinter as ctk
from gui.startup_window import StartupWindow
from gui.postprocessing_window import PostprocessingWindow
from tkinter import messagebox 
from PIL import Image

class AppController:
    def __init__(self):
        self.root = ctk.CTk()
        
        # Configuración de pantalla completa
        self.root.state('zoomed')
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.current_window = None
        self.loading_window = None  

        self.loading_image = ctk.CTkImage(light_image=Image.open("assets/images/loading.png"), size=(200, 200))

    def show_loading(self):
        """Muestra una ventana de carga simplificada"""
        if self.loading_window:
            try:
                self.loading_window.destroy()
            except:
                pass
            
        self.loading_window = ctk.CTkFrame(self.root, fg_color="gray20", corner_radius=0)
        self.loading_window.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.loading_window.lift()
        
        # Contenido de carga centrado
        content_frame = ctk.CTkFrame(self.loading_window, fg_color="transparent")
        content_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(content_frame, image=self.loading_image, text="").pack(pady=10)
        ctk.CTkLabel(content_frame, 
                    text='Cargando ...',
                    font=("Arial", 16)).pack(pady=10)
        
        self.root.update()

    def hide_loading(self):
        """Oculta la ventana de carga de manera segura"""
        if self.loading_window:
            try:
                self.loading_window.destroy()
            except:
                pass
            self.loading_window = None
            self.root.update()

    def _safe_window_change(self, window_class, *args, **kwargs):
        """Cambia de ventana de manera segura con pantalla de carga"""
        self.show_loading()
        self.root.update()
        
        # Destruir ventana actual si existe
        if self.current_window:
            self.current_window.destroy()

        # Crear nueva ventana
        self.current_window = window_class(self.root, self, *args, **kwargs)
        self.current_window.grid(row=0, column=0, sticky='nsew')
        
        '''if hasattr(self.current_window, 'update_texts'):
            self.current_window.update_texts()'''

        self.hide_loading()

    def show_startup_window(self, from_post, nao_ip):
        """Muestra la ventana de inicio"""
        self._safe_window_change(StartupWindow, from_post, nao_ip)
        

    def show_postprocessing_window(self, head_angles, nao_ip, sign_type):
        """Muestra la ventana de postprocesamiento"""
        self._safe_window_change(PostprocessingWindow, head_angles, nao_ip, sign_type)

    def run(self):
        """Inicia la aplicación"""
        self.show_startup_window(False, '127.0.0.1') #No importa la ip que se ponga acá
        #self.show_postprocessing_window(0.25,'127.0.0.1')
        self.root.mainloop()
    
    def on_close(self, msg_server, cam_server):
        """Maneja el cierre de la aplicación"""
        if messagebox.askokcancel("Salir", "¿Seguro que quieres salir?"):
            if cam_server is not None:
                msg_server.close()
                cam_server.close()
            self.root.destroy()
