# gui/startup_window.py
from customtkinter import CTkImage, CTkLabel, CTkFrame, CTkButton, CTkOptionMenu
from PIL import Image
from gui.components.ip_entry import IPEntry
from gui.components.move_head import MoveHead
import cv2
import socket
import pickle
import webbrowser
from web_server.dashboard import Dashboard
import threading

class StartupWindow(CTkFrame):
    def __init__(self, parent, controller, from_post, nao_ip):
        super().__init__(parent)
        self.configure(fg_color='#182C36')
        self.controller = controller
        self.parent = parent
        self.msg_server = None
        self.cam_server = None
        self.head_angle = 0
        self.stream = True
        self.dash_thread = None
        self.from_post = from_post
        self.nao_ip = nao_ip
        self.grid_columnconfigure(1, weight=1)  # Expande la columna 0
        self.grid_rowconfigure((0,1), weight=1)

        self.camera_img = CTkImage(light_image=Image.open("assets/images/camera_not.png"), size=(350*16//9, 350))
        self.close_btn = CTkImage(light_image=Image.open("assets/images/close.png"), size=(50, 50))
        self.informe_btn = CTkImage(light_image=Image.open("assets/images/informe.png"), size=(35, 35))
        self.ready_btn_img = CTkImage(light_image=Image.open("assets/images/ready.png"), size=(30, 30))
        self.ready_btn_off = CTkImage(light_image=Image.open("assets/images/ready_off.png"), size=(30, 30))
        self.img_position = CTkImage(light_image=Image.open("assets/images/user_position.png"), size=(168, 149)) #101:90 aspect ratio
        self.nao_free = CTkImage(light_image=Image.open("assets/images/nao_free_obj.png"), size=(120, 120))
        self.logo_usab = CTkImage(light_image=Image.open("assets/images/logo_unisabana.png"), size=(450*40//130, 40))
        self.logo_app = CTkImage(light_image=Image.open("assets/images/logo_final.png"), size=(950*120//623, 120)) # 950:623
        self.logo_capsab = CTkImage(light_image=Image.open("assets/images/logo_capsab.png"), size=(853*40//1098, 40)) # 853:1098
        self.ip_btn_img = CTkImage(light_image=Image.open("assets/images/ip_btn.png"), size=(30*90//18, 90)) # 853:1098
        # Configuración de la ventana
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de usuario."""
        
        self.cam_container = CTkFrame(self, fg_color='#8BB5CA', border_color='#000000', border_width=2)
        self.cam_container.grid(row=0, column=0, rowspan=3, sticky='NS', padx=30, pady=20)
        self.cam_container.grid_rowconfigure(0, weight=1)

        self.container_2 = CTkFrame(self, fg_color='#8BB5CA', border_color='#000000', border_width=2)
        self.container_2.grid(row=0, column=1, sticky='NSEW', padx=30, pady=(20, 10))
        self.container_2.grid_columnconfigure((0,1), weight=1)
        #self.container_2.grid_rowconfigure((0,1,2), weight=1)

        self.container_1 = CTkFrame(self, fg_color='#8BB5CA', border_color='#000000', border_width=2)
        self.container_1.grid(row=1, column=1, sticky='NSEW', padx=30, pady=10)
        self.container_1.grid_columnconfigure((0,1), weight=1)
        #self.container_1.grid_rowconfigure((0,1), weight=1)

        self.container_3 = CTkFrame(self, fg_color='#8BB5CA', border_color='#000000', border_width=2)
        self.container_3.grid(row=2, column=1, sticky='NSEW', padx=30, pady=(10, 20))
        self.container_3.grid_columnconfigure((0,1), weight=1)
        self.container_3.grid_rowconfigure((0,1), weight=1)

        CTkButton(self.cam_container, 
                  image=self.close_btn, 
                  command=self.close_app, 
                  fg_color='transparent',
                  hover_color='#4a4a4a',
                  text='',
                  width=50,
                  height=50).grid(row=0, column=0, padx=10, pady=10, sticky='NW')
        
        CTkLabel(self.cam_container, text='', image=self.logo_usab).grid(row=0, column=1, padx=10, pady=10, sticky='NE')
        CTkLabel(self.cam_container, text='', image=self.logo_capsab).grid(row=0, column=1, padx=10, pady=10, sticky='NW')
        CTkLabel(self.cam_container, text='', image=self.logo_app).grid(row=0, column=0, padx=30, pady=20, sticky='ES')
        CTkLabel(self.cam_container, text='', image=self.ip_btn_img).grid(row=1, column=1, rowspan=2, padx=5, pady=5)
        
        CTkLabel(self.cam_container, text='Ingrese la IP del NAO:', font=('Arial', 25), text_color='#000000').grid(row=1, column=0, padx=20, sticky='WS')
        
        self.nao_vid = CTkLabel(self.cam_container, text='', image=self.camera_img)
        self.nao_vid.grid(row=3, column=0, columnspan=2, pady=10, padx=10)

        self.ip_entry = IPEntry(self.cam_container, self.connect_nao)
        self.ip_entry.grid(row=2, column=0, pady=5, sticky='S')
        CTkButton(self.cam_container, 
                  image=self.informe_btn, 
                  command=self.ver_informe, 
                  fg_color='transparent',
                  hover_color='#4a4a4a',
                  border_color="#000000",
                  border_width=3,
                  text='',
                  width=35,
                  height=35).grid(row=0, column=0, padx=18, sticky='W')

        CTkLabel(self.container_1, 
                 text='Mueva la cabeza del NAO asegurando la persona esté enmarcada', 
                 font=('Arial', 25), 
                 text_color='#000000',
                 wraplength=500, justify='left').grid(row=0, column=0, columnspan=2, pady=10, padx=10)
        CTkLabel(self.container_1, text='', image=self.img_position).grid(row=1, column=1, pady=10, padx=10)
        self.move_head = MoveHead(self.container_1, self.move_nao)
        self.move_head.grid(row=1, column=0, padx=10, pady=10)

        CTkLabel(self.container_2, 
                 text='¿El NAO está listo para levantarse?', 
                 font=('Arial', 25), 
                 text_color='#000000',
                 wraplength=250).grid(row=0, column=0, pady=10, padx=10)
        CTkLabel(self.container_2, text='', image=self.nao_free).grid(row=0, column=1, rowspan=3, pady=10, padx=10)
        self.stand_btn = CTkButton(self.container_2, 
                  command=lambda: self.move_nao('posture stand'), 
                  fg_color='#566173',
                  text_color='white',
                  text_color_disabled='#6e6e6e',
                  text='Stand-Up NAO', 
                  font=('Arial', 20),
                  width=200,
                  height=40,
                  state='disabled')
        self.stand_btn.grid(row=1, column=0, padx=10, pady=10, sticky='N')

        CTkLabel(self.container_3, 
                 text='¿Configure como quiere la actividad?', 
                 font=('Arial', 25), 
                 text_color='#000000').grid(row=0, column=0, columnspan=2,pady=10, padx=10)
        self.ready_btn = CTkButton(self.container_3, 
                  command=self.on_closing,
                  image=self.ready_btn_off,
                  fg_color='#566173',
                  text='Iniciar actividad', 
                  text_color_disabled='#6e6e6e',
                  text_color='white',
                  font=('Arial', 20),
                  width=200,
                  height=40,
                  state='disabled')
        self.ready_btn.grid(row=1, column=1, padx=10, pady=10, sticky='N')
        self.sign_opt = CTkOptionMenu(self.container_3, 
                                      fg_color='#182C36', 
                                      font=('Arial', 20),
                                      width=180,
                                      height=40,
                                      values=['Colores', 'Numeros', 'Coordialidad'])
        self.sign_opt.grid(row=1, column=0, padx=10, pady=10, sticky='N')
        
        if self.from_post:
            self.parent.after(500, self.connect_nao)
            

        
    def connect_nao(self):
        self.cam_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.msg_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.msg_server.bind(('0.0.0.0', 6668))

        if not self.from_post:
            self.nao_ip = self.ip_entry.get_ip()
        else:
            self.ip_entry.connect_btn.configure(state='disabled')

        #self.cam_server.bind((socket.gethostbyname(socket.gethostname()), 6666))
        self.cam_server.bind(('0.0.0.0', 6666))
        self.play_camera()

    def play_camera(self):
        if self.stream:
            self.stand_btn.configure(state='normal', fg_color='#182C36')
            self.ready_btn.configure(state='normal', fg_color='#182C36', image=self.ready_btn_img)
            x = self.cam_server.recvfrom(1000000)
            data = x[0]
            data = pickle.loads(data, encoding='bytes')

            frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2.flip(frame, 1, frame)  # Voltea la imagen horizontalmente
            img_ctk = CTkImage(light_image=Image.fromarray(frame), size=(350*16//9, 350))
            self.nao_vid.configure(image=img_ctk)

            self.parent.after(1, self.play_camera)

    def move_nao(self, command):
        self.msg_server.sendto(command.encode('utf-8'), (self.nao_ip, 6667))
        if command == 'posture stand':
            self.move_head.enable_buttons()

    def close_app(self):
        self.controller.on_close(self.msg_server, self.cam_server)

    def on_closing(self):
        self.move_nao('motion angle')
        data, addr = self.msg_server.recvfrom(1024)
        message = str(data.decode('utf-8')).split()
        self.head_angle = message[0][1:-2]

        self.stream = False
        self.parent.after(400, self.go_to_post)

    def ver_informe(self):
        def run_dash():
            app = Dashboard()
            app.run('127.0.0.1', port=8000)  # debug=False evita conflictos en el hilo
            
        self.dash_thread = threading.Thread(target=run_dash, daemon=True)
        self.dash_thread.start()

        url = "http://localhost:8000"
        webbrowser.open(url)

    def go_to_post(self):
        self.cam_server.close()
        self.msg_server.close()
        self.controller.show_postprocessing_window(self.head_angle, self.nao_ip, self.sign_opt.get())