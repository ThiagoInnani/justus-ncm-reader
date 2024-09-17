from tkinter import messagebox
from tkinter import ttk
import tkinter as tk
from tkinter import *
import customtkinter

import databaseOperations

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
        self.ncm_combobox = AutoSuggestCombobox(self, width=9)
        AutoSuggestCombobox.set_completion_list(self.ncm_combobox, completion_list=ncm_data)
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

class AutoSuggestCombobox(ttk.Combobox):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._completion_list = []
        self._hits = []
        self._hit_index = 0
        self.position = 0
        self.bind('<KeyRelease>', self._handle_keyrelease)
        self.bind('<FocusOut>', self._handle_focusout)
        self.bind('<FocusIn>', self._handle_focusin)
        self.bind('<Tab>', self._handle_return)  # bind Enter key
        self.bind('<Down>', self._down_arrow)  # bind Up arrow key
        self.bind('<Up>', self._up_arrow)
        self.bind('<Button-1>', self._handle_click)  # bind mouse click
        master.bind("<Button-1>", self._handle_root_click)  # bind mouse click on root window
        self._popup_menu = None

    def set_completion_list(self, completion_list):
        """Set the list of possible completions."""
        self._completion_list = sorted(completion_list)
        self['values'] = self._completion_list

    def _handle_keyrelease(self, event):
        """Handle key release events."""
        value = self.get()
        cursor_index = self.index(tk.INSERT)

        if value == '':
            self._hits = self._completion_list
        else:
            # Determine the word before the cursor
            before_cursor = value[:cursor_index].rsplit(' ', 1)[-1]

            # Filter suggestions based on the word before the cursor
            self._hits = [item for item in self._completion_list if item.lower().startswith(before_cursor.lower())]

        # Ignore Down and Up arrow key presses
        if event.keysym in ['Down', 'Up', 'Return']:
            return

        if self._hits:
            self._show_popup(self._hits)


    def _show_popup(self, values):
        """Display the popup listbox."""
        if self._popup_menu:
            self._popup_menu.destroy()

        self._popup_menu = tk.Toplevel(self)
        self._popup_menu.wm_overrideredirect(True)
        self._popup_menu.config(bg='black')

        # Add a frame with a black background to create the border effect
        popup_frame = tk.Frame(self._popup_menu, bg='gray10', borderwidth=0.1)
        popup_frame.pack(padx=1, pady=(1, 1), fill='both', expand=True)

        listbox = tk.Listbox(popup_frame, borderwidth=0, relief=tk.FLAT, bg='white', selectbackground='#0078d4', bd=0, highlightbackground='black')
        scrollbar = ttk.Scrollbar(popup_frame, orient=tk.VERTICAL, command=listbox.yview)
        listbox.config(yscrollcommand=scrollbar.set)

        for value in values:
            listbox.insert(tk.END, value)

        listbox.bind("<ButtonRelease-1>", self._on_listbox_select)
        listbox.bind("<FocusOut>", self._on_listbox_focusout)
        listbox.bind("<Motion>", self._on_mouse_motion)

        # Automatically select the first entry if no mouse hover has occurred yet
        if not listbox.curselection():
            listbox.selection_set(0)

        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Adjust popup width to match entry box
        popup_width = self.winfo_width()
        self._popup_menu.geometry(f"{popup_width}x165")

        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self._popup_menu.geometry(f"+{x}+{y}")

    def _on_listbox_select(self, event):
        """Select a value from the listbox."""
        widget = event.widget
        selection = widget.curselection()
        if selection:
            value = widget.get(selection[0])
            self._select_value(value)

    def _on_mouse_motion(self, event):
        """Handle mouse motion over the listbox."""
        widget = event.widget
        index = widget.nearest(event.y)
        widget.selection_clear(0, tk.END)
        widget.selection_set(index)

    def _on_listbox_focusout(self, event):
        """Handle listbox losing focus."""
        if self._popup_menu:
            self._popup_menu.destroy()
            self._popup_menu = None

    def _select_value(self, value):
        """Select a value from the popup listbox."""
        self.set(value)
        self.icursor(tk.END)  # Move cursor to the end
        self.selection_range(0, tk.END)  # Select entire text
        if self._popup_menu:
            self._popup_menu.destroy()
            self._popup_menu = None

    def _handle_focusout(self, event):
        """Handle focus out events."""
        if self._popup_menu:
            try:
                if not self._popup_menu.winfo_containing(event.x_root, event.y_root):
                    self._popup_menu.destroy()
                    self._popup_menu = None
            except tk.TclError:
                pass

    def _handle_focusin(self, event):
        """Handle focus in events."""
        if self._popup_menu:
            self._popup_menu.destroy()
            self._popup_menu = None

    def _handle_return(self, event):
        """Handle Enter key press."""
        if self._popup_menu:
            listbox = self._popup_menu.winfo_children()[0].winfo_children()[0]
            current_selection = listbox.curselection()
            if current_selection:
                value = listbox.get(current_selection[0])
                self._select_value(value)

    def _down_arrow(self, event):
        """Handle down arrow key press."""
        if self._popup_menu:
            listbox = self._popup_menu.winfo_children()[0].winfo_children()[0]
            current_selection = listbox.curselection()
            if current_selection:
                current_index = current_selection[0]
                next_index = (current_index + 1) % len(self._hits)
                listbox.selection_clear(0, tk.END)
                listbox.selection_set(next_index)
                listbox.activate(next_index)
                return 'break'  # prevent default behavior

    def _up_arrow(self, event):
        """Handle up arrow key press."""
        if self._popup_menu:
            listbox = self._popup_menu.winfo_children()[0].winfo_children()[0]
            current_selection = listbox.curselection()
            if current_selection:
                current_index = current_selection[0]
                next_index = (current_index - 1) % len(self._hits)
                listbox.selection_clear(0, tk.END)
                listbox.selection_set(next_index)
                listbox.activate(next_index)
                return 'break'  # prevent default behavior



    def _handle_click(self, event):
        """Handle mouse click events."""
        value = self.get()
        if value == '':
            self._hits = self._completion_list
        else:
            self._hits = [item for item in self._completion_list if item.lower().startswith(value.lower())]

        if self._hits:
            self._show_popup(self._hits)


    def _handle_root_click(self, event):
        """Handle mouse click events on root window."""
        if self._popup_menu:
            x, y = event.x_root, event.y_root
            x0, y0, x1, y1 = self.winfo_rootx(), self.winfo_rooty(), self.winfo_rootx() + self.winfo_width(), self.winfo_rooty() + self.winfo_height()
            if not (x0 <= x <= x1 and y0 <= y <= y1):
                self._popup_menu.destroy()
                self._popup_menu = None
