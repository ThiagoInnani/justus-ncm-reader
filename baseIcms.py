from tkinter import messagebox
from tkinter import ttk
import tkinter as tk
from tkinter import *
import customtkinter

import databaseOperations
import interfaceCreation

class BaseICMS(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("700x150")
        self.maxsize(700, 150)
        self.minsize(700, 150)
        self.attributes('-topmost', True)
        self.title("Cadastro de Alíquota de ICMS")
        self.create_widgets()
        self.bind('<Escape>', lambda event: self.destroy())

    def create_widgets(self):

        def focus_prev_widget(event):
            event.widget.tk_focusPrev().focus()
            return("break")

        def button_execute(event, button):
            button.invoke()
        
        def apply_focus_effect(button):
            # Altera a borda quando o botão recebe o foco
            def on_focus_in(event):
                #event.widget.configure(border_color="red")
                button.configure(border_width=2, border_color="white")

            # Restaura a borda original quando o foco é perdido
            def on_focus_out(event):
                button.configure(border_width=0, border_color="")

            # Vincula os eventos de foco ao botão
            button.bind("<FocusIn>", on_focus_in)
            button.bind("<FocusOut>", on_focus_out)

        #NCM Widgets
        self.ncm_label = customtkinter.CTkLabel(self, text="NCM")
        ncm_data = list(self.get_data('Nomenclaturas'))
        self.ncm_combobox = interfaceCreation.AutoSuggestCombobox(self, width=9, height=6, font='Arial 16')
        interfaceCreation.AutoSuggestCombobox.set_completion_list(self.ncm_combobox, completion_list=ncm_data)
        self.ncm_combobox.set(ncm_data[0])
        self.ncm_combobox.bind("<<ComboboxSelected>>", self.comboboxes_callback)
        self.ncm_combobox.bind("<FocusOut>", self.comboboxes_callback)
        self.ncm_combobox.tk.eval('[ttk::combobox::PopdownWindow %s].f.l configure -foreground white -background #343638 -selectforeground #424548 -selectbackground #343638' % self.ncm_combobox)
        #UF Widgets
        self.uf_label = customtkinter.CTkLabel(self, text="UF")
        self.uf_combobox = customtkinter.CTkComboBox(self,
                                command=self.comboboxes_callback,
                                values=list(self.get_data('FederativeUnits')),
                                width=80
                                )
        self.uf_combobox.set(list(self.get_data('FederativeUnits'))[0])
        self.uf_combobox.bind("<FocusOut>", self.comboboxes_callback)
        
        #CST/CSOSN Widgets
        self.cst_csosn_label = customtkinter.CTkLabel(self, text="CST/CSOSN")
        self.cst_csosn_combobox = customtkinter.CTkComboBox(self,
                                command=self.comboboxes_callback,
                                values=(list(self.get_data('CST')) + list(self.get_data('CSOSN'))),
                                width=80
                                )
        self.cst_csosn_combobox.set(list(self.get_data('CST'))[0])
        self.cst_csosn_combobox.bind("<FocusOut>", self.comboboxes_callback)
        
        #Base de ICMS Widgets 
        self.taxrate_label = customtkinter.CTkLabel(self, text="Alíquota ICMS")
        validation = self.register(self.entry_validate)
        self.taxrate_entry = customtkinter.CTkEntry(self, width=50, validate='key', validatecommand=(validation, '%P'))
        self.taxrate_percent = customtkinter.CTkLabel(self, text="%")
        self.taxrate_entry.bind('<KeyRelease>', self.replace_comma)
        self.comboboxes_callback(0)
        #Buttons
        self.base_icms_buttons_frame = BaseIcmsButtonsFrame(self)
        self.base_icms_buttons_frame.buttons[0].configure(command=lambda: self.save_base_icms())
        self.base_icms_buttons_frame.buttons[1].configure(command=lambda: self.delete_base_icms())
        self.base_icms_buttons_frame.buttons[2].configure(command=self.destroy)
        
        # Vincular Tab para navegar pelos botões
        for button in self.base_icms_buttons_frame.buttons:
            #button.bind("<Tab>", focus_next_widget)
            button.bind("<Shift-Tab>", focus_prev_widget)

        # Vincular Enter para acionar os botões
        self.base_icms_buttons_frame.buttons[0].bind("<Return>", lambda event: button_execute(event, self.base_icms_buttons_frame.buttons[0]))
        self.base_icms_buttons_frame.buttons[1].bind("<Return>", lambda event: button_execute(event, self.base_icms_buttons_frame.buttons[1]))
        self.base_icms_buttons_frame.buttons[2].bind("<Return>", lambda event: button_execute(event, self.base_icms_buttons_frame.buttons[2]))

        for button in self.base_icms_buttons_frame.buttons:
            apply_focus_effect(button)
        self.grid()

    def grid(self):
            self.ncm_label.grid(row=0, column=0, padx=(50,10), pady = 20)
            self.ncm_combobox.grid(row=1, column=0, padx=(50,10), pady = 20)

            self.uf_label.grid(row=0, column=1, padx=10, pady = 20)
            self.uf_combobox.grid(row=1, column=1, padx=10, pady = 20)

            self.cst_csosn_label.grid(row=0, column=2, padx=10, pady = 20)
            self.cst_csosn_combobox.grid(row=1, column=2, padx=10, pady = 20)

            self.taxrate_label.grid(row=0, column=4, padx=10, pady=20)
            self.taxrate_entry.grid(row=1, column=4, padx=10, pady= 20)
            self.taxrate_percent.grid(row=1, column=5, pady= 20)

            self.base_icms_buttons_frame.grid(row=0, column=6, rowspan=2, padx=50, pady=20)

    def get_data(self, database):
        db_ops = databaseOperations.DatabaseOperations()
        db_ops.connect_to_database()

        if database == 'Nomenclaturas':
            query = f'SELECT id FROM {database} WHERE LENGTH(id) = 8'
        else:
            query = f'SELECT * FROM {database}'
        filtered_data = db_ops.execute_command(query)
        print(f'Filtered Data: {filtered_data}')
        db_ops._close_connection()
        return [item[0] for item in filtered_data]
    
    def comboboxes_callback(self, event):
        ncm_value = self.ncm_combobox.get()
        uf_value = self.uf_combobox.get()
        cst_csosn_value = self.cst_csosn_combobox.get()

        base_icms_value = BaseICMS.get_base_icms(ncm_value, uf_value, cst_csosn_value)

        print(f'NCM: {ncm_value}, UF: {uf_value}, CST/CSOSN: {cst_csosn_value}, ICMS: {base_icms_value}')
        
        word = self.taxrate_entry.get()
        self.taxrate_entry.delete(first_index=0, last_index=len(word))
        
        if base_icms_value:
            self.taxrate_entry.insert(0, base_icms_value)

        self.validate_data()

    def validate_data(self):
         if not (self.ncm_combobox.get() in self.ncm_combobox["values"]):
              messagebox.showerror('ERRO: dado incorreto', f'Erro: Insira um NCM que existe', parent=self)
              self.ncm_combobox.set(self.ncm_combobox["values"][0])

         if not (self.uf_combobox.get() in self.uf_combobox.cget('values')):
              messagebox.showerror('ERRO: dado incorreto', f'Erro: Insira uma UF que existe', parent=self)
              self.uf_combobox.set(self.uf_combobox.cget("values")[0])

         if not (self.cst_csosn_combobox.get() in self.cst_csosn_combobox.cget('values')):
              messagebox.showerror('ERRO: dado incorreto', f'Erro: Insira uma CST/CSOSN que existe', parent=self)
              self.cst_csosn_combobox.set(self.cst_csosn_combobox.cget("values")[0])

    def entry_validate(self, P):
        P = P.replace(',', '.')

        if (P == "" or P.replace('.', '', 1).isdigit()) and len(P) <= 5:
            return True
        else:
            return False

    def replace_comma(self, event):
        # Get the current value of the entry
        value = self.taxrate_entry.get()
        # Replace comma with dot
        if ',' in value:
            self.taxrate_entry.delete(0, 'end')
            self.taxrate_entry.insert(0, value.replace(',', '.'))

    def save_base_icms(self):
        def insert_into_db():
            if cst:
                query = f'''INSERT INTO BaseIcms (value, nomenclatura_id, cst_id, federative_unit_id) 
                VALUES ({icms_value}, '{ncm_value}', '{cst_csosn_value}', '{uf_value}')'''
            else:
                query = f'''INSERT INTO BaseIcms (value, nomenclatura_id, csosn_id, federative_unit_id) 
                VALUES ({icms_value}, '{ncm_value}', '{cst_csosn_value}', '{uf_value}')'''
            db_ops.execute_command(query)
            db_ops._save_connection()
            messagebox.showinfo('Base de ICMS salva', f'A base de ICMS foi salva com sucesso.', parent=self)
         
        db_ops = databaseOperations.DatabaseOperations()
         
        icms_value = self.taxrate_entry.get()
        ncm_value = self.ncm_combobox.get()
        uf_value = self.uf_combobox.get()
        cst_csosn_value = self.cst_csosn_combobox.get()

        if icms_value:
            cst = True if int(cst_csosn_value) < 100 else False
            db_ops.connect_to_database()
            filtered_data = BaseICMS.get_base_icms(ncm_value, uf_value, cst_csosn_value)

            if filtered_data:
                answer = messagebox.askquestion('SOBRESCREVER BASE DE ICMS', f'Tem certeza que deseja sobrescrever essa base de ICMS?', parent=self)
                if answer == 'yes':
                        if cst:
                            db_ops.execute_command(f'''DELETE FROM BaseIcms 
                                WHERE nomenclatura_id={ncm_value} 
                                AND federative_unit_id="{uf_value}" 
                                AND cst_id={cst_csosn_value}''')
                        else:
                            db_ops.execute_command(f'''DELETE FROM BaseIcms 
                                WHERE nomenclatura_id={ncm_value} 
                                AND federative_unit_id="{uf_value}" 
                                AND csosn_id={cst_csosn_value}''')
                        insert_into_db()
            else:
                insert_into_db()
        else:
            messagebox.showerror('ERRO: dado incorreto', f'Erro: Insira um valor no campo de Alíquota de ICMS', parent=self)
        db_ops._close_connection()

    def delete_base_icms(self):
         answer = messagebox.askquestion('EXCLUIR BASE DE ICMS', f'Tem certeza que deseja excluir essa base de ICMS?', parent=self)
         if answer == 'yes':
            db_ops = databaseOperations.DatabaseOperations()

            icms_value = self.taxrate_entry.get()
            ncm_value = self.ncm_combobox.get()
            uf_value = self.uf_combobox.get()
            cst_csosn_value = self.cst_csosn_combobox.get()

            db_ops.connect_to_database()

            #Define se é CST ou CSOSN
            cst = True if int(cst_csosn_value)<100 else False

            if icms_value:
               if cst:
                   query = f'''DELETE FROM BaseIcms 
                   WHERE nomenclatura_id={ncm_value} 
                   AND federative_unit_id="{uf_value}" 
                   AND cst_id={cst_csosn_value}'''
               else:
                   query = f'''DELETE FROM BaseIcms 
                   WHERE nomenclatura_id={ncm_value} 
                   AND federative_unit_id="{uf_value}" 
                   AND csosn_id={cst_csosn_value}'''

            db_ops.execute_command(query)
            db_ops._save_connection()
            db_ops._close_connection()
            self.comboboxes_callback(0)

    def get_base_icms(ncm_value, uf_value, cst_csosn_value):
        db_ops = databaseOperations.DatabaseOperations()
        cst = True if int(cst_csosn_value)<100 else False
        db_ops.connect_to_database()

        if cst:
            query = f'''SELECT value FROM BaseIcms 
            WHERE nomenclatura_id={ncm_value} 
            AND federative_unit_id="{uf_value}" 
            AND cst_id={cst_csosn_value}'''
        else:
            query = f'''SELECT value FROM BaseIcms 
            WHERE nomenclatura_id={ncm_value} 
            AND federative_unit_id="{uf_value}" 
            AND csosn_id={cst_csosn_value}'''

        filtered_data = db_ops.execute_command(query)
        db_ops._close_connection
        return filtered_data

    def get_cst_csosn(ncm_value, uf_value):
        db_ops = databaseOperations.DatabaseOperations()
        db_ops.connect_to_database()
        query = f'''SELECT CONCAT_WS('', cst_id, csosn_id) 
        FROM BaseIcms 
        WHERE nomenclatura_id={ncm_value}
        AND federative_unit_id="{uf_value}"
        '''
        filtered_data = db_ops.execute_command(query)
        db_ops._close_connection
        print(f"CST/CSOSN: {filtered_data}")
        return filtered_data

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