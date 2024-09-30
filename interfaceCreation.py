import tkinter as tk
from tkinter import ttk, filedialog as fd, PhotoImage, Menu
from tkinter import messagebox
import customtkinter
import xml.etree.ElementTree as ET
import os

#Classes
import processArchives
import baseIcms
import cfopEquivalent

class Interface:
    def __init__(self, master):
        self.pasta_app = os.path.dirname(__file__)
        self._setup_window_icon(master)
        self._setup_menu(master)
        self._setup_theme(master)
        self._change_theme(master)

    def _setup_window_icon(self, master):
        """Configura o ícone da janela"""
        icon_path = os.path.join(self.pasta_app, 'src/icon.png')
        master.tk.call('wm', 'iconphoto', master._w, PhotoImage(file=icon_path))

    def _setup_menu(self, master):
        """Configura a barra de menus"""
        self.menu_bar = Menu(master)
        self._create_file_menu(master)
        self._create_registry_menu(master)
        self._create_options_menu(master)
        master.config(menu=self.menu_bar)

    def _create_file_menu(self, master):
        """Cria o menu Arquivos"""
        file_menu = Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Importar Arquivo XML", command=lambda: master.process_archive.openXmlFile())
        file_menu.add_separator()
        file_menu.add_command(label="Fechar", command=master.quit)
        self.menu_bar.add_cascade(label="Arquivos", menu=file_menu)

    def _create_registry_menu(self, master):
        """Cria o menu de Bases de ICMS"""
        icms_menu = Menu(self.menu_bar, tearoff=0)
        icms_menu.add_command(label="Cadastrar Base de ICMS", command= lambda: self.open_toplevel_base_icms(master))
        icms_menu.add_command(label="Cadastrar CFOP", command= lambda: self.open_toplevel_cfop(master))
        self.menu_bar.add_cascade(label="Cadastrar", menu=icms_menu)

    def _create_options_menu(self, master):
        """Cria o menu Opções"""
        options_menu = Menu(self.menu_bar, tearoff=0)
        options_menu.add_command(label="Trocar de Tema", command=lambda: self._change_theme(master))
        self.menu_bar.add_cascade(label="Opções", menu=options_menu)
    
    def _setup_theme(self, master):
        """Configura o tema inicial da aplicação"""
        current_theme = customtkinter.get_appearance_mode()
        self.theme = 1 if current_theme == "dark" else 0
        customtkinter.set_appearance_mode("dark" if self.theme == 1 else "light")
        self._apply_theme(master)
        
    def _change_theme(self, master):
        """Alterna entre os temas claro e escuro"""
        self.theme = 1 - self.theme
        customtkinter.set_appearance_mode("dark" if self.theme == 1 else "light")
        self._apply_theme(master)

    def _apply_theme(self, master):
        """Aplica o tema configurado"""
        master.configure(bg=self.background_color)
        master.style = ttk.Style()
        master.style.configure("Treeview",
                             background=self.table_value_color,
                             foreground=self.table_value_font,
                             fieldbackground=self.table_value_color)
        master.style.configure("Treeview.Heading",
                             background=self.table_header_color,
                             foreground=self.table_header_font,
                             font="bold")
        master.style.map('Treeview', background=[("selected", self.table_header_color)])
        master.style.configure("TCombobox",
                             fieldbackground=self.background_color, # Cor de fundo da área de seleção
                             background=self.dropdown_button,       # Cor de fundo do combobox
                             foreground=self.menu_font_color,       # Cor do texto
                             selectbackground=self.dropdown_button) # Cor do fundo da seleção
        
        self.menu_bar.config(background=self.menu_bar_color, foreground=self.menu_font_color)
        
    
    def open_toplevel_base_icms(self, master):
        if master.toplevel_window is None or not master.toplevel_window.winfo_exists():
            master.toplevel_window = baseIcms.BaseICMS(master)  # create window if its None or destroyed
        else:
            master.toplevel_window.focus()  # if window exists focus it
    
    def open_toplevel_cfop(self, master):
        if master.toplevel_window is None or not master.toplevel_window.winfo_exists():
            master.toplevel_window = cfopEquivalent.CFOPEquivalent(master)  # create window if its None or destroyed
        else:
            master.toplevel_window.focus()  # if window exists focus it

    @property
    def menu_bar_color(self):
        return '#3B3E45' if self.theme == 1 else '#FFFFFF'

    @property
    def menu_font_color(self):
        return "#FFFFFF" if self.theme == 1 else "#000000"

    @property
    def background_color(self):
        return '#242424' if self.theme == 1 else '#DBDBDB'

    @property
    def table_header_color(self):
        return '#1F6AA5'

    @property
    def table_header_font(self):
        return "#FFFFFF"

    @property
    def table_value_color(self):
        return '#242424' if self.theme == 1 else "#FFFFFF"

    @property
    def table_value_font(self):
        return "#FFFFFF" if self.theme == 1 else "#000000"

    @property
    def button_color(self):
        return '#1F6AA5'
    
    @property
    def dropdown_button(self):
        return '#565b5e'
    

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
