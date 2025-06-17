# gui/startup_window.py
from customtkinter import CTkImage, CTkLabel, CTkFrame, CTkButton, CTkEntry, CTkProgressBar
from tensorflow.keras.models import Sequential 
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
import mediapipe as mp
from mediapipe import ImageFormat, solutions
from PIL import Image
from gui.components.word_selector import WordSelector
import cv2
import numpy as np
from utils.data_imputator import ImputeData
import socket
import pickle
import csv
from datetime import datetime

class PostprocessingWindow(CTkFrame):
    def __init__(self, parent, controller, head_angle, nao_ip, sign_type):
        super().__init__(parent)
        self.configure(fg_color='#182C36')
        self.controller = controller
        self.parent = parent
        self.nao_ip = nao_ip
        self.head_angle = head_angle
        self.sign_type = sign_type
        self.msg_server = None
        self.cam_server = None
        self.start_dectection = False
        self.stream = True
        self.frame_count = 0
        self.current_sign_index = 0
        self.previous_result = {'pose':[], 'r_hand':[], 'l_hand':[]}
        self.correct_signs = 0

        self.nn_predict = []
        self.eye_sequence = ['FaceLed0','FaceLed1','FaceLed2','FaceLed3','FaceLed4','FaceLed5','FaceLed6','FaceLed7']
        clases_dict = {'Colores':['amarillo', 'azul', 'blanco', 'cafe', 'gris', 'morado', 'naranja', 'negro', 'rojo', 'rosado', 'verde'],
                       'Numeros':['cinco', 'cuatro', 'dies', 'dos', 'nueve', 'ocho', 'seis', 'siete', 'tres', 'uno'],
                       'Coordialidad':['Ayudar','Bien','BuenasNoches','BuenasTardes','BuenosDias','Chao','Denada','Hola','Mal','Perdon','Por favor']}
        self.clases = clases_dict[sign_type]
        self.rgb_colors = {'amarillo': [1, 1, 0], 'azul': [0, 0, 1], 'blanco': [1, 1, 1], 'cafe': [0.65, 0.16, 0.16],
                           'gris': [0.7, 0.7, 0.7], 'morado': [0.5, 0, 0.5], 'naranja': [1, 0.65, 0], 'negro': [0, 0, 0],
                           'rojo': [1, 0, 0], 'rosado': [1, 0.55, 0.85], 'verde': [0, 1, 0]}
        self.imputator = ImputeData()
        self.grid_columnconfigure(1, weight=1)  # Expande la columna 0
        for i in range(2):  # Expande las filas 0 a 3
            self.grid_rowconfigure(i, weight=1)

        self.setup_models(sign_type)

        self.camera_img = CTkImage(light_image=Image.open("assets/images/camera_not.png"), size=(350*16//9, 350))
        self.return_btn = CTkImage(light_image=Image.open("assets/images/previous.png"), size=(50, 50))
        self.img_position = CTkImage(light_image=Image.open("assets/images/user_position.png"), size=(202, 180))
        self.nao_free = CTkImage(light_image=Image.open("assets/images/nao_free_obj.png"), size=(200, 200))
        self.logo_usab = CTkImage(light_image=Image.open("assets/images/logo_unisabana.png"), size=(450*40//130, 40))
        self.logo_app = CTkImage(light_image=Image.open("assets/images/logo_final.png"), size=(950*120//623, 120)) # 950:623
        self.logo_capsab = CTkImage(light_image=Image.open("assets/images/logo_capsab.png"), size=(853*40//1098, 40)) # 853:1098
        
        # Configuración de la ventana
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de usuario."""
        
        self.cam_container = CTkFrame(self, fg_color='#8BB5CA', border_color='#000000', border_width=2)
        self.cam_container.grid(row=0, column=0, rowspan=2, sticky='NS', padx=30, pady=20)
        self.cam_container.grid_rowconfigure(0, weight=1)
        self.cam_container.grid_columnconfigure(1, weight=1)

        self.container_1 = CTkFrame(self, fg_color='#8BB5CA', border_color='#000000', border_width=2)
        self.container_1.grid(row=0, column=1, sticky='NSEW', padx=30, pady=20)
        self.container_1.grid_columnconfigure(0, weight=1)
        
        self.container_2 = CTkFrame(self, fg_color='#8BB5CA', border_color='#000000', border_width=2)
        self.container_2.grid(row=1, column=1, sticky='NSEW', padx=30, pady=20)
        self.container_2.grid_rowconfigure((0,1), weight=1)
        self.container_2.grid_columnconfigure(0, weight=1)

        CTkButton(self.cam_container, 
                  image=self.return_btn, 
                  command=self.return_menu, 
                  fg_color='transparent',
                  hover_color='#4a4a4a',
                  text='',
                  width=50,
                  height=50).grid(row=0, column=0, padx=10, pady=10, sticky='NW')
        
        CTkLabel(self.cam_container, text='', image=self.logo_usab).grid(row=0, column=2, padx=10, pady=10, sticky='NE')
        CTkLabel(self.cam_container, text='', image=self.logo_capsab).grid(row=0, column=1, padx=10, pady=10, sticky='NE')
        CTkLabel(self.cam_container, text='', image=self.logo_app).grid(row=0, column=1, padx=30, pady=20, sticky='S')
        
        CTkLabel(self.cam_container, text='ID Usuario', font=('Arial', 25), text_color='#000000').grid(row=1, column=0, pady=10, padx=10, sticky='w')
        self.id_user = CTkEntry(self.cam_container, fg_color='#8898A0', text_color='#000000')
        self.id_user.grid(row=1, column=1, pady=10, padx=10, columnspan=2, sticky='ew')

        self.nao_vid = CTkLabel(self.cam_container, text='', image=self.camera_img)
        self.nao_vid.grid(row=2, column=0, columnspan=3, pady=10, padx=10)

        CTkLabel(self.container_1, text='Escoja los colores que desea:', font=('Arial', 25), text_color='#000000').grid(row=0, column=0, pady=20, padx=10, sticky='W')
        self.word_selector = WordSelector(self.container_1, self.clases)
        self.word_selector.grid(row=1, column=0, pady=10, padx=10, sticky='NSEW')
        
        self.detect_btn = CTkButton(self.container_1,
                  command=self.sign_detection,
                  hover_color='#4a4a4a',
                  text='Iniciar detección',
                  font=('Arial', 20), 
                  height=55,
                  corner_radius=10,
                  state='disabled',
                  text_color_disabled='#6e6e6e',
                  fg_color='#566173')
        self.detect_btn.grid(row=2, column=0, padx=50, pady=10, sticky='EW')
        
        self.sign_label = CTkLabel(self.container_2, text='Progreso de la seña: Amarillo', font=('Arial', 25), text_color='#000000')
        self.sign_label.grid(row=0, column=0, pady=20, padx=10, sticky='W')
        self.prog_bar = CTkProgressBar(self.container_2, height=20, fg_color='#2E414B')
        self.prog_bar.grid(row=1, column=0, padx=10, pady=10, sticky='NSEW')
        self.prog_bar.set(0.0)

        self.prog_label = CTkLabel(self.container_2, text='0 %', font=('Arial', 20), text_color='#000000')
        self.prog_label.grid(row=1, column=1, padx=10, pady=10)

        self.correct_label = CTkLabel(self.container_2, text=f'Señas correctas: 0 de 11', font=('Arial', 20), text_color='#000000')
        self.correct_label.grid(row=2, column=0, padx=10, pady=10)

        self.cam_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.msg_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.cam_server.bind((socket.gethostbyname(socket.gethostname()), 6666))
        #self.cam_server.bind(('127.0.0.1', 6666))
        print(self.id_user.cget('border_color'))
        self.play_camera()

    def play_camera(self):
        if self.stream:
            self.sign_label.configure(text=f'Progreso de la seña: {self.word_selector.get_selected_words()[self.current_sign_index].capitalize()}')
            self.correct_label.configure(text=f'Señas correctas: {self.correct_signs} de {len(self.word_selector.get_selected_words())}')
            x = self.cam_server.recvfrom(1000000)
            data = x[0]
            data = pickle.loads(data, encoding='bytes')

            frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
            cv2.flip(frame, 1, frame)  # Voltea la imagen horizontalmente
            
            if self.frame_count == 3:
                if self.start_dectection:
                    self.pred_frame = frame.copy()
                    self.sign_prediction()
                self.frame_count = 0
            self.frame_count += 1

            # Convertir a formato para CustomTkinter
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            ctk_image = CTkImage(light_image=img, size=(350*16//9, 350))
            
            # Actualizar el label
            self.nao_vid.configure(image=ctk_image)
            self.nao_vid.image = ctk_image  # Mantener referencia

            if len(self.id_user.get()) > 3:
                self.detect_btn.configure(state='normal', fg_color='#182C36')
            else:
                self.detect_btn.configure(state='disabled', text_color_disabled='#6e6e6e', fg_color='#566173')

            self.parent.after(1, self.play_camera)

    def sign_detection(self):
        
        self.selected_colors = self.word_selector.get_selected_words().copy()

        if self.current_sign_index == 0:
            self.move_nao(f'say Hola;{self.id_user.get()},;haz;la;sena;{self.selected_colors[self.current_sign_index]}') 
            self.informe = {'ID':self.id_user.get(),
                            'Fecha':datetime.now().strftime("%d/%m/%Y"),
                            'Hora':datetime.now().strftime("%H:%M:%S")}
        else:
            self.move_nao(f'say Haz;la;sena;{self.selected_colors[self.current_sign_index]}') 
        
        self.current_iteration = 0  # Contador de iteraciones
        self.detect_btn.configure(state='disabled')
        self.move_nao('animation hi')
        self.parent.after(5000, self.flash_leds)  # Iniciar el proceso


    def flash_leds(self):

        color = self.selected_colors[self.current_sign_index]
        max_iter = 20

        if 0 <= self.current_iteration <= max_iter:

            if self.current_iteration%2 == 0:
                if self.sign_type == 'Colores':
                    msg = f'led fade FaceLeds {' '.join(map(str, self.rgb_colors[color]))} 0'
                else:
                    msg = f'led fade FaceLeds {' '.join(map(str, self.rgb_colors['blanco']))} 0'
                self.move_nao(msg)
                
                if self.current_iteration == 0:
                    self.move_nao('posture stand')
                elif self.current_iteration == 20:
                    self.start_dectection = True
                    self.move_nao(msg)
                    self.move_nao('say Grabando')
                
                self.parent.after(200, self.flash_leds)
            
            elif self.current_iteration%2 == 1:
                msg = f'led fade FaceLeds {' '.join(map(str, self.rgb_colors['negro']))} 0'
                self.move_nao(msg)
                
                if self.current_iteration == 1:
                    self.move_nao(f'setHead {self.head_angle}')
                
                self.parent.after(int(1000*2**(-0.4*((self.current_iteration-1)/2))), self.flash_leds)

            self.current_iteration += 1
    
    def sign_prediction(self):
        # Convertir a formato de MediaPipe
        mp_image = mp.Image(image_format=ImageFormat.SRGB,
                            data=cv2.cvtColor(self.pred_frame, cv2.COLOR_BGR2RGB))

        # Detección de landmarks
        self.hand_result = self.hand_landmarker.detect(mp_image)
        self.pose_result = self.pose_landmarker.detect(mp_image)
        self.frame_count = 0   

        self.result = {'pose': self.pose_result.pose_landmarks}
        self.result = self.hand_array(self.hand_result, self.result)

        self.imputator.main(self.result, self.previous_result)
        if self.sign_type == 'Colores':
            temp = self.imputator.nn_input[:162]
            # En colores va primero hand y despues pose, mala mia
            self.nn_predict.append(np.concatenate((temp[99:162], temp[0:99]), axis=0))
        if self.sign_type == 'Coordialidad':
            self.nn_predict.append(self.imputator.nn_input)
        if self.sign_type == 'Numeros':
            self.nn_predict.append(self.imputator.nn_input[99:162])

        self.previous_result = self.result

        self.prog_bar.set(len(self.nn_predict)/30)
        self.move_nao(f'led off {self.eye_sequence[int(7*len(self.nn_predict)/30)]}')
        
        if len(self.nn_predict) == 30:
            print('El tamaño de la entrada es:', np.array([self.nn_predict]).shape)
            prediction = self.model.predict(np.array([self.nn_predict]))
            np.save('models/last_sign.npy', self.nn_predict)
            self.predicted_color = self.clases[np.argmax(prediction)]
            self.nn_predict = []
            self.prog_bar.set(0.0)

            if self.sign_type == 'Colores': # Si es modo colores prende los ojos del color predicho
                self.move_nao(f'led fade FaceLeds {' '.join(map(str, self.rgb_colors[self.predicted_color]))} 0')
            
            self.start_dectection = False
            if self.predicted_color == self.selected_colors[self.current_sign_index]:
                if self.sign_type != 'Colores': # Si es modo colores prende los ojos del color predicho
                    self.move_nao(f'led fade FaceLeds {' '.join(map(str, self.rgb_colors['verde']))} 0')

                self.move_nao('animation correct')
                self.move_nao('animation correct')
                self.move_nao('animation correct')
                self.move_nao(f'say Hiciste;bien;la;seña')

                self.informe[self.selected_colors[self.current_sign_index]] = 'Correcta'
                self.correct_signs += 1
            else:
                if self.sign_type != 'Colores': # Si es modo colores prende los ojos del color predicho
                    self.move_nao(f'led fade FaceLeds {' '.join(map(str, self.rgb_colors['rojo']))} 0')

                self.move_nao('animation incorrect')
                self.move_nao(f'say Así;no;se;hace;la;seña;{self.selected_colors[self.current_sign_index]}')
                self.informe[self.selected_colors[self.current_sign_index]] = 'Incorrecta'

            self.current_sign_index += 1
            
            if self.current_sign_index == len(self.selected_colors):
                self.agregar_fila_csv(self.informe)
                self.return_menu()
            else:
                self.parent.after(4000, self.sign_detection)            
                

    def move_nao(self, command):
        self.msg_server.sendto(command.encode('utf-8'), (self.nao_ip, 6667))

    def setup_models(self, sign_type):
        # Configurar Hand Landmarker
        hand_options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path='models/hand_landmarker.task'),
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            num_hands=2)
        
        # Configurar Pose Landmarker
        pose_options = mp.tasks.vision.PoseLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path='models/pose_landmarker_full.task'),
            running_mode=mp.tasks.vision.RunningMode.IMAGE)
        
        # Crear los detectores
        self.hand_landmarker = mp.tasks.vision.HandLandmarker.create_from_options(hand_options)
        self.pose_landmarker = mp.tasks.vision.PoseLandmarker.create_from_options(pose_options)

        #Configurar arquitectura de red neuronal
        self.model = Sequential()

        if sign_type == 'Colores':
            self.model.add(Input((30,162)))
        elif sign_type == 'Numeros':
            self.model.add(Input((30,63)))
        elif sign_type == 'Coordialidad':
            self.model.add(Input((30,225)))
        
        self.model.add(LSTM(256, return_sequences=True, activation='relu'))
        self.model.add(LSTM(128, return_sequences=True, activation='relu'))
        self.model.add(LSTM(64, return_sequences=False, activation='relu'))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(64, activation='relu'))
        self.model.add(Dense(32, activation='relu'))

        if sign_type == 'Colores':
            self.model.add(Dense(11, activation='softmax'))
            self.model.load_weights('models/color_nn.h5')
        elif sign_type == 'Coordialidad':
            self.model.add(Dense(11, activation='softmax'))
            self.model.load_weights('models/coor_nn.keras')
        elif sign_type == 'Numeros':
            self.model.add(Dense(10, activation='softmax'))
            self.model.load_weights('models/num_nn.keras')
    
    def agregar_fila_csv(self, datos):
        # Leer los encabezados del archivo
        with open('assets/data.csv', 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            encabezados = next(reader)

        # Crear la nueva fila en orden de los encabezados
        nueva_fila = [datos.get(col, 'NA') for col in encabezados]

        # Escribir la nueva fila al final del archivo
        with open('assets/data.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(nueva_fila)

    def return_menu(self):
        self.stream = False
        self.controller.show_startup_window(True, self.nao_ip)
        if self.cam_server is not None:
            self.msg_server.close()
            self.cam_server.close()

    def hand_array(self, prediction, results):

        wrist_coords_pose = [(results['pose'][0][15].x, results['pose'][0][15].y),
                             (results['pose'][0][16].x, results['pose'][0][16].y)]
        
        if not prediction.hand_landmarks:
                results['r_hand'] = []
                results['l_hand'] = []

        elif len(prediction.hand_landmarks) == 1:
                wrist_coords = [prediction.hand_landmarks[0][0].x, 
                                prediction.hand_landmarks[0][0].y]
                
                euc_dist = [((wrist_coords[0] - wrist[0])**2 + (wrist_coords[1] - wrist[1])**2)**0.5 for wrist in wrist_coords_pose]

                indice = euc_dist.index(min(euc_dist))

                if indice:
                        results['l_hand'] = prediction.hand_landmarks
                        results['r_hand'] = []
                else:
                        results['l_hand'] = []
                        results['r_hand'] = prediction.hand_landmarks

        else:
                wrist_coords = [[prediction.hand_landmarks[0][0].x, prediction.hand_landmarks[0][0].y],
                                [prediction.hand_landmarks[1][0].x, prediction.hand_landmarks[1][0].y]]
                
                euc_dist = [[((wrist_hand[0] - wrist[0])**2 + (wrist_hand[1] - wrist[1])**2)**0.5 for wrist in wrist_coords_pose] for wrist_hand in wrist_coords]

                indices = [euc.index(min(euc)) for euc in euc_dist]
                
                min_idx = [min(euc) for euc in euc_dist].index(min([min(euc) for euc in euc_dist]))

                if indices == [0, 1]:
                        results['l_hand'] = [prediction.hand_landmarks[1]]
                        results['r_hand'] = [prediction.hand_landmarks[0]]
                elif indices == [1, 0]:
                        results['l_hand'] = [prediction.hand_landmarks[0]]
                        results['r_hand'] = [prediction.hand_landmarks[1]]

                # Si ambas están cerca de solo una muñeca se toma la mas cercana
                elif indices == [0, 0]:
                        results['l_hand'] = [prediction.hand_landmarks[min_idx]]
                        results['r_hand'] = []
                else:
                        results['l_hand'] = []
                        results['r_hand'] = [prediction.hand_landmarks[min_idx]]

        return results