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
        file_menu.add_command(label="Importar Arquivo XML", command=lambda: processArchives.ProcessXmls.openXmlFile(master))
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