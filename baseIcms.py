from tkinter import messagebox
from tkinter import ttk
from tkinter import *
import customtkinter

import databaseOperations

class BaseICMS(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("800x150")
        self.maxsize(800, 150)
        self.minsize(800, 150)
        self.title("Cadastro de Alíquota de ICMS")
        self.create_widgets()
        self.grid()

    def create_widgets(self):
            self.ncm_label = customtkinter.CTkLabel(self, text="NCM")
            ncm_data = list(self.get_data('Nomenclaturas'))
            #self.ncm_combobox = customtkinter.CTkComboBox(self, values=list(self.get_data('Nomenclaturas')))
            self.ncm_combobox = ttk.Combobox(self, values=ncm_data, width=9)
            self.ncm_combobox.set(ncm_data[0])
            self.ncm_combobox.bind("<<ComboboxSelected>>", self.comboboxes_callback)

            self.uf_label = customtkinter.CTkLabel(self, text="UF")
            self.uf_combobox = customtkinter.CTkComboBox(self,
                                    command=self.comboboxes_callback,
                                    values=list(self.get_data('FederativeUnits')),
                                    width=80
                                    )
            self.uf_combobox.set(list(self.get_data('FederativeUnits'))[0])
            
            self.cst_csosn_label = customtkinter.CTkLabel(self, text="CST/CSOSN")
            self.cst_csosn_combobox = customtkinter.CTkComboBox(self,
                                    command=self.comboboxes_callback,
                                    values=(list(self.get_data('CST')) + list(self.get_data('CSOSN'))),
                                    width=80
                                    )
            self.cst_csosn_combobox.set(list(self.get_data('CST'))[0])
            
            cfop_data = list(self.get_data('CFOP'))
            self.cfop_label = customtkinter.CTkLabel(self, text="CFOP")
            self.cfop_combobox = ttk.Combobox(self, values=cfop_data, width=5)
            self.cfop_combobox.set(cfop_data[0])
            self.cfop_combobox.bind("<<ComboboxSelected>>", self.comboboxes_callback)
            
            self.taxrate_label = customtkinter.CTkLabel(self, text="Alíquota ICMS")
            self.taxrate_entry = customtkinter.CTkEntry(self, width=50)
            self.taxrate_percent = customtkinter.CTkLabel(self, text="%")
            
            self.base_icms_buttons_frame = BaseIcmsButtonsFrame(self)
            
            self.base_icms_buttons_frame.buttons[0].configure(command=self.save_base_icms())
            self.base_icms_buttons_frame.buttons[1].configure(command=self.delete_base_icms())
            self.base_icms_buttons_frame.buttons[2].configure(command=self.destroy)

    def grid(self):
            self.ncm_label.grid(row=0, column=0, padx=10, pady = 20)
            self.ncm_combobox.grid(row=1, column=0, padx=10, pady = 20)

            self.uf_label.grid(row=0, column=1, padx=10, pady = 20)
            self.uf_combobox.grid(row=1, column=1, padx=10, pady = 20)

            self.cst_csosn_label.grid(row=0, column=2, padx=10, pady = 20)
            self.cst_csosn_combobox.grid(row=1, column=2, padx=10, pady = 20)

            self.cfop_label.grid(row=0, column=3, padx=10, pady = 20)
            self.cfop_combobox.grid(row=1, column=3, padx=10, pady = 20)

            self.taxrate_label.grid(row=0, column=4, padx=10, pady=20)
            self.taxrate_entry.grid(row=1, column=4, padx=10, pady= 20)
            self.taxrate_percent.grid(row=1, column=5, pady= 20)

            self.base_icms_buttons_frame.grid(row=0, column=6, rowspan=2, padx=40, pady=20)

    def get_data(self, database):
        db_ops = databaseOperations.DatabaseOperations()
        db_ops.connect_to_database()
        query = f'SELECT * FROM {database}'
        filtered_data = db_ops.execute_command(query)
        db_ops._close_connection()
        return [item[0] for item in filtered_data]
    
    def comboboxes_callback(self, choice):
        db_ops = databaseOperations.DatabaseOperations()

        ncm_value = self.ncm_combobox.get()
        uf_value = self.uf_combobox.get()
        cst_csosn_value = self.cst_csosn_combobox.get()
        cfop_value = self.cfop_combobox.get()

        db_ops.connect_to_database()
        query = f'''SELECT value FROM BaseIcms 
        WHERE nomenclatura_id={ncm_value} 
        AND cfop_id={cfop_value} 
        AND federative_unit_id="{uf_value}" 
        AND (cst_id={cst_csosn_value} OR csosn_id={cst_csosn_value})'''
        filtered_data = db_ops.execute_command(query)
        db_ops._close_connection

        print(f'NCM: {ncm_value}, CFOP: {cfop_value}, UF: {uf_value}, CST/CSOSN: {cst_csosn_value}, ICMS: {filtered_data}')

        if filtered_data:
            word = self.taxrate_entry.get()
            self.taxrate_entry.delete(first_index=0, last_index=len(word))
            self.taxrate_entry.insert(0, filtered_data)

    def save_base_icms(self):
         pass

    def delete_base_icms(self):
         pass


class BaseIcmsButtonsFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.save_button = customtkinter.CTkButton(self, text= "Salvar Base de ICMS")
        self.delete_button = customtkinter.CTkButton(self, fg_color='#cc0000', hover_color='#8e0000', text= "Excluir Base de ICMS")
        self.cancel_button = customtkinter.CTkButton(self, text= "Cancelar")

        self.save_button.grid(row=0, column=0, pady=5)
        self.delete_button.grid(row=1, column=0, pady=5)
        self.cancel_button.grid(row=2, column=0, pady=5)

        self.buttons = [self.save_button, self.delete_button, self.cancel_button]