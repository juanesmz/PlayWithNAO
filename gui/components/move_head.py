from customtkinter import CTkImage, CTkButton, CTkFrame, CTkLabel
from PIL import Image

class MoveHead(CTkFrame):
    def __init__(self, master, move_command=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(fg_color='transparent')
        self.nao_head_img = CTkImage(light_image=Image.open("assets/images/nao_head.png"), size=(70, 70))
        self.up_img = CTkImage(light_image=Image.open("assets/images/up_on.png"), size=(30,30))
        self.down_img = CTkImage(light_image=Image.open("assets/images/down_on.png"), size=(30,30))
        self.rigth_img = CTkImage(light_image=Image.open("assets/images/rigth_on.png"), size=(30,30))
        self.left_img = CTkImage(light_image=Image.open("assets/images/left_on.png"), size=(30,30))

        self.up_img_off = CTkImage(light_image=Image.open("assets/images/up_off.png"), size=(30,30))
        self.down_img_off = CTkImage(light_image=Image.open("assets/images/down_off.png"), size=(30,30))
        self.rigth_img_off = CTkImage(light_image=Image.open("assets/images/rigth_off.png"), size=(30,30))
        self.left_img_off = CTkImage(light_image=Image.open("assets/images/left_off.png"), size=(30,30))
        
        CTkLabel(self, text='', image=self.nao_head_img).grid(row=1, column=1, padx=10, pady=2)
        self.btn_up = CTkButton(self, text="", command=lambda: move_command('motion negative HeadPitch'), image= self.up_img_off, width=35, height=35, state='disabled', fg_color='#566173')
        self.btn_down = CTkButton(self, text="", command=lambda: move_command('motion positive HeadPitch'), image= self.down_img_off, width=35, height=35, state='disabled', fg_color='#566173')
        self.btn_rigth = CTkButton(self, text="", command=lambda: move_command('motion positive HeadYaw'), image= self.rigth_img_off, width=35, height=35, state='disabled', fg_color='#566173')
        self.btn_left = CTkButton(self, text="", command=lambda: move_command('motion negative HeadYaw'), image= self.left_img_off, width=35, height=35, state='disabled', fg_color='#566173')

        self.btn_up.grid(row=0, column=1, padx=2, pady=2)
        self.btn_down.grid(row=2, column=1, padx=2, pady=2)
        self.btn_rigth.grid(row=1, column=2, padx=2, pady=2)
        self.btn_left.grid(row=1, column=0, padx=2, pady=2)
    
    def enable_buttons(self):
        """Habilita los botones de movimiento de la cabeza."""
        self.btn_up.configure(state='normal', fg_color='#182C36', image= self.up_img)
        self.btn_down.configure(state='normal', fg_color='#182C36', image= self.down_img)
        self.btn_rigth.configure(state='normal', fg_color='#182C36', image= self.rigth_img)
        self.btn_left.configure(state='normal', fg_color='#182C36', image= self.left_img)
