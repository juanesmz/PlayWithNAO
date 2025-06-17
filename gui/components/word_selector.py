import customtkinter as ctk
from typing import List, Dict

class WordSelector(ctk.CTkFrame):
    def __init__(self, parent, words: List[str], **kwargs):
        super().__init__(parent, **kwargs)
        
        self.words = words.copy()
        self.word_vars = [ctk.BooleanVar(value=True) for _ in words]
        
        self.configure(fg_color="transparent")
        
        # Frame para contener los elementos de palabras
        self.words_container = ctk.CTkScrollableFrame(self, fg_color='#333333', border_color='#565B5E')
        self.words_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.labels = [] 
        
        # Inicializar las palabras
        self.initialize_words()
    
    def initialize_words(self):
        """Crea los elementos de la interfaz para cada palabra"""

        for i, word in enumerate(self.words):
            self.add_word_element(word, i)
    
    def add_word_element(self, word: str, word_index: int):
        """Añade un elemento de palabra con checkbox y botones de flecha"""
        
        frame = ctk.CTkFrame(self.words_container, fg_color="#8898A0")
        frame.pack(fill="x", pady=2, padx=2)
        
        # Checkbox
        checkbox = ctk.CTkCheckBox(frame, text="", variable=self.word_vars[word_index], width=20, fg_color='#182C36')
        checkbox.pack(side="left", padx=(5, 0))
        
        # Label con la palabra
        label = ctk.CTkLabel(frame, text=word.capitalize(), fg_color="#8898A0", corner_radius=5, font=('Arial', 20), text_color='#000000')
        label.pack(side="left", fill='both',expand=True, padx=(5, 0), pady=2)
        self.labels.append(label)
        
        # Frame para los botones de flecha
        arrow_frame = ctk.CTkFrame(frame, fg_color="transparent", width=50)
        arrow_frame.pack(side="right", padx=(0, 5), pady=(4,4))
        
        # Botón para subir
        up_btn = ctk.CTkButton(
            arrow_frame,
            text="↑",
            width=20,
            height=20,
            fg_color='#182C36',
            command=lambda i=word_index: self.move_word_up(i)
        )
        up_btn.pack(side="top", fill="x")
        
        # Botón para bajar
        down_btn = ctk.CTkButton(
            arrow_frame, 
            text="↓", 
            width=20, 
            height=20,
            fg_color='#182C36',
            command=lambda i=word_index: self.move_word_down(i)
        )
        down_btn.pack(side="top", fill="x", pady=(2, 0))
    
    def move_word_up(self, index: int):
        """Mueve la palabra una posición arriba en la lista"""
       
        if index > 0:
            # Intercambiar posiciones en la lista
            self.words[index], self.words[index-1] = self.words[index-1], self.words[index]
            # Reconstruir la interfaz
            self.labels[index].configure(text=f'{self.words[index].capitalize()}')
            self.labels[index-1].configure(text=f'{self.words[index-1].capitalize()}')

            old_val =  self.word_vars[index].get()
            self.word_vars[index].set(self.word_vars[index-1].get())
            self.word_vars[index-1].set(old_val)            
    
    def move_word_down(self, index: int):
        """Mueve la palabra una posición abajo en la lista"""
        if index < len(self.words) - 1:
            # Intercambiar posiciones en la lista
            self.words[index], self.words[index+1] = self.words[index+1], self.words[index]
            # Reconstruir la interfaz
            self.labels[index].configure(text=f'{self.words[index].capitalize()}')
            self.labels[index+1].configure(text=f'{self.words[index+1].capitalize()}')

            old_val =  self.word_vars[index].get()
            self.word_vars[index].set(self.word_vars[index+1].get())
            self.word_vars[index+1].set(old_val)  
    
    def get_selected_words(self) -> List[str]:
        """Devuelve las palabras seleccionadas (con checkbox activado) en el orden actual"""
        return [word for i, word in enumerate(self.words) if self.word_vars[i].get()]
    
    def get_ordered_words(self) -> List[str]:
        """Devuelve todas las palabras en el orden actual (seleccionadas o no)"""
        return self.words.copy()