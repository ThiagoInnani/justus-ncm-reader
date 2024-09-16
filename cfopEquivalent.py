from tkinter import messagebox
from tkinter import ttk
from tkinter import *
import customtkinter

import databaseOperations

class CFOPEquivalent(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("500x300")
        self.maxsize(500, 300)
        self.minsize(500, 300)
        self.attributes('-topmost', True)
        self.title("Cadastro de CFOP")
        self.create_widgets()
        self.grid()
    
    def create_widgets(self):
            #Widgets de CFOPs Normais / Entrada
            self.entry_label = customtkinter.CTkLabel(self, text="Entrada")
            entry_data = list(self.get_data('CFOP'))
            self.entry_combobox = ttk.Combobox(self, values=entry_data, width=9)
            self.entry_combobox.set(entry_data[0])
            self.entry_combobox.bind("<<ComboboxSelected>>", self.comboboxes_callback)
            self.entry_combobox.bind("<FocusOut>", self.comboboxes_callback)

            #Widgets de CFOPs Equivalentes / Saída
            self.exit_label = customtkinter.CTkLabel(self, text="Saída")
            exit_data = list(self.get_data('CFOP'))
            self.exit_combobox = ttk.Combobox(self, values=exit_data, width=9)
            self.exit_combobox.set(exit_data[1])
            self.exit_combobox.bind("<<ComboboxSelected>>", self.comboboxes_callback)
            self.exit_combobox.bind("<FocusOut>", self.comboboxes_callback)
    def grid(self):
            self.entry_label.grid(row=0, column=0, padx=50, pady = 20)
            self.entry_combobox.grid(row=1, column=0, padx=50, pady = 20)

            self.exit_label.grid(row=0, column=1, padx=50, pady = 20)
            self.exit_combobox.grid(row=1, column=1, padx=50, pady = 20)

    def get_data(self, database):
        db_ops = databaseOperations.DatabaseOperations()
        db_ops.connect_to_database()
        query = f'SELECT * FROM {database}'
        filtered_data = db_ops.execute_command(query)
        db_ops._close_connection()
        return [item[0] for item in filtered_data]

    def get_cfop_equivalent(self, cfop):
        '''Recebe uma lista de CFOPs do ProcessArchives,
        deve devolver uma lista com os CFOPs equivalentes'''

        db_ops = databaseOperations.DatabaseOperations()
        db_ops.connect_to_database()

        placeholders = ', '.join(['%s'] * len(cfop))  # Cria %s para cada CFOP
        query = f'''SELECT id, equivalent FROM CFOP WHERE id IN ({placeholders})'''

        db_ops.cursor.execute(query, cfop)
        filtered_data = db_ops.cursor.fetchall()
        db_ops._close_connection()
        # Cria um dicionário para mapear cada CFOP para o seu equivalente
        cfop_map = {cfop_id: equivalent for cfop_id, equivalent in filtered_data}
        
        # Constrói uma nova lista mapeando os CFOPs da lista original para os equivalentes
        cfop_equivalents = [cfop_map[cfop_id] for cfop_id in cfop]
        return cfop_equivalents
    
    def comboboxes_callback(self, event):
         pass