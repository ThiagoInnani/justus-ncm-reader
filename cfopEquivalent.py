from tkinter import messagebox
from tkinter import ttk
from tkinter import *
import customtkinter

import databaseOperations
import interfaceCreation

class CFOPEquivalent(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("500x300")
        self.maxsize(500, 300)
        self.minsize(500, 300)
        self.attributes('-topmost', True)
        self.title("Cadastro de CFOP")
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

        #CFOP Widgets
        self.cfop_label = customtkinter.CTkLabel(self, text="CFOP", font=("Arial",16))
        cfop_data = list(self.get_data('CFOP', 1)) #1 é o index da variável cfop na tabela cfop
        self.cfop_combobox = interfaceCreation.AutoSuggestCombobox(self, width=9, height=6, font="Arial 16")
        interfaceCreation.AutoSuggestCombobox.set_completion_list(self.cfop_combobox, completion_list=cfop_data)
        self.cfop_combobox.set(cfop_data[0])
        self.cfop_combobox.bind("<<ComboboxSelected>>", self.comboboxes_callback)
        self.cfop_combobox.bind("<FocusOut>", self.comboboxes_callback)
        self.cfop_combobox.tk.eval('[ttk::combobox::PopdownWindow %s].f.l configure -foreground white -background #343638 -selectforeground #424548 -selectbackground #343638' % self.cfop_combobox)
  
        #CST/CSOSN Widgets
        self.cst_csosn_label = customtkinter.CTkLabel(self, text="CST/CSOSN", font=("Arial",16))
        cst_csosn_data = (list(self.get_data('CST', 0)) + list(self.get_data('CSOSN', 0)))
        self.cst_csosn_combobox = interfaceCreation.AutoSuggestCombobox(self, width=9, height=6, font="Arial 16")
        interfaceCreation.AutoSuggestCombobox.set_completion_list(self.cst_csosn_combobox, completion_list=cst_csosn_data)
        self.cst_csosn_combobox.set(list(self.get_data('CST', 0))[0])
        self.cst_csosn_combobox.bind("<<ComboboxSelected>>", self.comboboxes_callback)
        self.cst_csosn_combobox.bind("<FocusOut>", self.comboboxes_callback)
        self.cst_csosn_combobox.tk.eval('[ttk::combobox::PopdownWindow %s].f.l configure -foreground white -background #343638 -selectforeground #424548 -selectbackground #343638' % self.cst_csosn_combobox)
  
        #CFOP Equivalent Widgets
        self.cfop_equivalent_label = customtkinter.CTkLabel(self, text="CFOP Equivalente", font=("Arial",16))
        validation = self.register(self.entry_validate)
        self.cfop_equivalent_entry = customtkinter.CTkEntry(self, width=50, height=30, validate='key', validatecommand=(validation, '%P'), font=('Arial', 16))

        #Buttons
        self.cfop_equivalent_buttons_frame = CfopEquivalentButtonsFrame(self)
        self.cfop_equivalent_buttons_frame.buttons[0].configure(command=lambda: self.save_cfop())
        self.cfop_equivalent_buttons_frame.buttons[1].configure(command=self.destroy)
        
        # Vincular Tab para navegar pelos botões
        for button in self.cfop_equivalent_buttons_frame.buttons:
            button.bind("<Shift-Tab>", focus_prev_widget)

        # Vincular Enter para acionar os botões
        self.cfop_equivalent_buttons_frame.buttons[0].bind("<Return>", lambda event: button_execute(event, self.cfop_equivalent_buttons_frame.buttons[0]))
        self.cfop_equivalent_buttons_frame.buttons[1].bind("<Return>", lambda event: button_execute(event, self.cfop_equivalent_buttons_frame.buttons[1]))

        for button in self.cfop_equivalent_buttons_frame.buttons:
            apply_focus_effect(button)
        self.grid()

    def grid(self):
            self.cfop_label.grid(row=0, column=0, padx=(50,10), pady = 10)
            self.cfop_combobox.grid(row=1, column=0, padx=(50,10), pady = (10, 30))

            self.cst_csosn_label.grid(row=2, column=0, padx=(50,10), pady = (30, 10))
            self.cst_csosn_combobox.grid(row=3, column=0, padx=(50,10), pady = 10)

            self.cfop_equivalent_label.grid(row=0, column=1, padx=(50,10), pady = 10)
            self.cfop_equivalent_entry.grid(row=1, column=1, padx=(50,10), pady = (10, 30))

            self.cfop_equivalent_buttons_frame.grid(row=3, column=1, columnspan=2, padx=20)

    def get_data(self, database, index):
        db_ops = databaseOperations.DatabaseOperations()
        db_ops.connect_to_database()
        query = f'SELECT * FROM {database}'
        filtered_data = db_ops.execute_command(query)
        db_ops._close_connection()
        return [item[index] for item in filtered_data]

    def get_cfop_equivalent(self, cfop, cst_csosn):
        """
        Recebe duas listas: uma com os IDs de CFOPs e outra com os IDs de CST ou CSOSN.
        Deve devolver uma lista com os CFOPs equivalentes correspondentes.
        """

        db_ops = databaseOperations.DatabaseOperations()
        db_ops.connect_to_database()

        # Cria placeholders para as listas de CFOP e CST/CSOSN
        placeholders_cfop = ', '.join(['%s'] * len(cfop))  # Placeholder para CFOP
        placeholders_cst_csosn = ', '.join(['%s'] * len(cst_csosn))  # Placeholder para CST ou CSOSN

        # Ajuste da query para verificar os IDs de CFOP e de CST ou CSOSN
        query = f'''
            SELECT cfop, equivalent, cst_id, csosn_id
            FROM CFOP
            WHERE cfop IN ({placeholders_cfop})
            AND (cst_id IN ({placeholders_cst_csosn}) OR csosn_id IN ({placeholders_cst_csosn}))
        '''

        print(f'query: {query}')
        
        # Combine os parâmetros para passar à execução da query
        params = cfop + cst_csosn + cst_csosn  # cst_csosn é duplicado, pois é usado duas vezes na query (cst e csosn)
        
        db_ops.cursor.execute(query, params)  # Execute a query com os parâmetros corretos
        filtered_data = db_ops.cursor.fetchall()
        db_ops._close_connection()

        # Cria um dicionário para mapear cada CFOP para o seu equivalente
        cfop_map = {cfop_id: equivalent for cfop_id, equivalent, cst, csosn in filtered_data}

        # Constrói uma nova lista mapeando os CFOPs da lista original para os equivalentes
        cfop_equivalents = [cfop_map[cfop_id] for cfop_id in cfop if cfop_id in cfop_map]

        return cfop_equivalents
    
    def comboboxes_callback(self, event):
        cfop_value = self.cfop_combobox.get()
        cst_csosn_value = self.cst_csosn_combobox.get()

        cfop_equivalent = self.get_cfop_equivalent(cfop_value, cst_csosn_value)
        self.cfop_equivalent_entry.configure(Text=cfop_equivalent)
    
    def save_cfop(self):
        return

    def entry_validate(self, P):
        if (P == "" or P.replace('.', '', 1).isdigit()) and len(P) <= 4:
            return True
        else:
            return False

class CfopEquivalentButtonsFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.save_button = customtkinter.CTkButton(self, text= "Salvar CFOP")
        self.cancel_button = customtkinter.CTkButton(self, text= "Cancelar")

        self.save_button.grid(row=0, column=0, padx=(0,5))
        self.cancel_button.grid(row=0, column=1, padx=(5,0))

        self.buttons = [self.save_button, self.cancel_button]