import tkinter as tk
from tkinter import ttk, filedialog as fd, PhotoImage, Menu
from tkinter.messagebox import showinfo
import customtkinter
import xml.etree.ElementTree as ET
import os



# Imports de Classes
import buildWidgets
import processArchives
import databaseOperations

class App(customtkinter.CTk):
    """Classe principal da aplicação"""

    def __init__(self):
        super().__init__()
        self.pasta_app = os.path.dirname(__file__)
        self.title("Filtrador de NCMs Justus")
        self.geometry("1200x800")
        self._setup_window_icon()
        self._setup_grid()
        self._setup_menu()
        self._setup_theme()
        self._connect_database()
        self._create_widgets()
        self._change_theme()

    def _setup_window_icon(self):
        """Configura o ícone da janela"""
        icon_path = os.path.join(self.pasta_app, 'src/icon.png')
        self.tk.call('wm', 'iconphoto', self._w, PhotoImage(file=icon_path))

    def _setup_grid(self):
        """Configura o layout de grid da janela"""
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

    def _setup_theme(self):
        """Configura o tema inicial da aplicação"""
        current_theme = customtkinter.get_appearance_mode()
        self.theme = 1 if current_theme == "dark" else 0
        customtkinter.set_appearance_mode("dark" if self.theme == 1 else "light")
        self._apply_theme()

    def _setup_menu(self):
        """Configura a barra de menus"""
        self.menu_bar = Menu(self)
        self._create_file_menu()
        self._create_options_menu()
        self.config(menu=self.menu_bar)

    def _create_file_menu(self):
        """Cria o menu Arquivos"""
        file_menu = Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Importar Arquivo XML", command=lambda: processArchives.ProcessXmls.openXmlFile(self))
        file_menu.add_separator()
        file_menu.add_command(label="Fechar", command=self.quit)
        self.menu_bar.add_cascade(label="Arquivos", menu=file_menu)

    def _create_options_menu(self):
        """Cria o menu Opções"""
        options_menu = Menu(self.menu_bar, tearoff=0)
        options_menu.add_command(label="Trocar de Tema", command=self._change_theme)
        self.menu_bar.add_cascade(label="Opções", menu=options_menu)

    def _connect_database(self):
        # Uso dos módulos
        self.db_ops = databaseOperations.DatabaseOperations(
            host="localhost",
            user="root",
            password="D1k1xs5j#!",
            database_name="ncmreader"
        )

        if self.db_ops.connect_to_database():
            self.db_ops._initialize_database()
            db_ncm = databaseOperations.DatabaseNcm(self.db_ops)
            db_ncm.insert_ncm_in_table()
    
    def _create_widgets(self):
        """Cria os widgets da aplicação"""
        self.button_frame = buildWidgets.MainButtonFrame(self, text=["Importar XMLs", "Filtrar XMLs"])
        self.table_frame = buildWidgets.TableFrame(self, titles=['N° da nota', 'Produto', 'NCM(s)', 'CFOP', 'Descrição'], values=[], height=40)
        self.filter_frame = buildWidgets.FilterFrame(self)

        self.button_frame.buttons[0].configure(command=lambda: processArchives.ProcessXmls.openXmlFile(self))
        self.button_frame.buttons[1].configure(command=lambda: processArchives.ProcessXmls.reviewXmlFile(self))

        self.filter_frame.grid(row=0, column=3, padx=40, pady=(20, 0), sticky="WN")
        self.button_frame.grid(row=2, column=3, padx=40, pady=(20, 0), sticky="W")
        self.table_frame.grid(row=0, column=0, rowspan=3, columnspan=3, sticky="NWSE")

    def _change_theme(self):
        """Alterna entre os temas claro e escuro"""
        self.theme = 1 - self.theme
        customtkinter.set_appearance_mode("dark" if self.theme == 1 else "light")
        self._apply_theme()

    def _apply_theme(self):
        """Aplica o tema configurado"""
        self.configure(bg=self.background_color)
        self.style = ttk.Style()
        self.style.configure("Treeview",
                             background=self.table_value_color,
                             foreground=self.table_value_font,
                             fieldbackground=self.table_value_color)
        self.style.configure("Treeview.Heading",
                             background=self.table_header_color,
                             foreground=self.table_header_font,
                             font="bold")
        self.style.map('Treeview', background=[("selected", self.table_header_color)])
        self.menu_bar.config(background=self.menu_bar_color, foreground=self.menu_font_color)

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


if __name__ == "__main__":
    app = App()
    app.mainloop()
