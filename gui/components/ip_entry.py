import customtkinter as ctk
from tkinter import StringVar

class IPEntry(ctk.CTkFrame):
    def __init__(self, master, connect_command=None, **kwargs):
        super().__init__(master, **kwargs)
        
        default_ip = ["192", "168", "0", "109"]
        self.configure(fg_color='transparent')
        self.octet_vars = [StringVar(value=ip) for ip in default_ip]
        self.entries = []
        
        # Configuración del grid
        self.grid_columnconfigure((0, 2, 4, 6), weight=0)
        self.grid_columnconfigure((1, 3, 5, 7), weight=1)
        
        for i in range(4):
            entry = ctk.CTkEntry(
                self,
                width=50,
                fg_color='#8898A0',
                textvariable=self.octet_vars[i],
                justify='center',
                validate='key',
                text_color='#000000'
            )
            entry.configure(validatecommand=(
                entry.register(self.validate_octet), 
                '%P', '%W', '%d', '%i'
            ))
            entry.grid(row=0, column=i*2, padx=2, sticky="nsew")
            self.entries.append(entry)
            
            entry.bind('<KeyRelease>', lambda e, idx=i: self.auto_tab(e, idx))
            entry.bind('<FocusIn>', lambda e, idx=i: self.select_all(e, idx))
            
            if i < 3:
                dot = ctk.CTkLabel(self, text="·", font=("Arial", 16), text_color='#000000')
                dot.grid(row=0, column=i*2+1, padx=2, pady=2)
        
        self.connect_btn = ctk.CTkButton(
            self, 
            fg_color='#182C36',
            text="Conectar",
            command=connect_command
        )
        self.connect_btn.grid(row=0, column=7, padx=(10, 2), sticky="ns")
    
    def set_ip(self, ip_str):
        """Establece la IP desde un string"""
        octets = ip_str.split('.')
        if len(octets) != 4:
            raise ValueError("La dirección IP debe tener 4 octetos separados por puntos")
        
        for i, octet in enumerate(octets):
            if not octet.isdigit() or not 0 <= int(octet) <= 255:
                raise ValueError(f"Octeto inválido: {octet}")
            
            self.octet_vars[i].set(octet)
            self.entries[i].delete(0, 'end')
            self.entries[i].insert(0, octet)
    
    # Resto de los métodos permanecen igual...
    def validate_octet(self, new_value, widget_name, action_type, char_index):
        if action_type == '0': return True
        if not new_value.isdigit(): return False
        if len(new_value) > 3: return False
        if new_value and int(new_value) > 255: return False
        return True
    
    def auto_tab(self, event, current_idx):
        entry = self.entries[current_idx]
        text = entry.get()
        
        if len(text) == 3 and current_idx < 3:
            self.entries[current_idx + 1].focus()
            self.entries[current_idx + 1].select_range(0, 'end')
        
        if event.keysym == 'BackSpace' and not text and current_idx > 0:
            self.entries[current_idx - 1].focus()
            self.entries[current_idx - 1].select_range(0, 'end')
    
    def select_all(self, event, idx):
        self.entries[idx].select_range(0, 'end')
    
    def get_ip(self):
        return ".".join([var.get() for var in self.octet_vars])
    
    def enable(self):
        for entry in self.entries:
            entry.configure(state='normal')
        self.connect_btn.configure(state='normal')
    
    def disable(self):
        for entry in self.entries:
            entry.configure(state='disabled')
        self.connect_btn.configure(state='disabled')