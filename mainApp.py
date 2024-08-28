import tkinter as tk
from tkinter import ttk, filedialog as fd, PhotoImage, Menu
from tkinter import messagebox
import customtkinter
import xml.etree.ElementTree as ET
import os



# Imports de Classes
import buildWidgets
import processArchives
import databaseOperations
import filter

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
        self.grid_rowconfigure((0, 1), weight=1)

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
        self.db_ops = databaseOperations.DatabaseOperations()
    
        if self.db_ops.connect_to_database():
            self.db_ops._initialize_database()
            #Confere se existe uma tabela Nomenclaturas preenchida
            count = self.db_ops.execute_command("SELECT COUNT(*) FROM Nomenclaturas")
            db_ncm = databaseOperations.DatabaseNcm(self.db_ops)
            if count[0][0] == 0:
                db_ncm.insert_ncm_in_table()
            db_filter = filter.Filter(self.db_ops)
    
    def _create_widgets(self):
        def get_current_filter_lines(self):
            self.values = self.filter_frame.get_values()
            return self.values

        def save_button_click_event(self):
            nome_filtro_atual = self.mainButton_frame.get_current_filter()
            # Se for um filtro novo
            if nome_filtro_atual == "Filtro Novo":
                dialog = customtkinter.CTkInputDialog(text="Digite o nome do filtro:", title="Nome do Filtro")
                filter_name = dialog.get_input()
                if filter_name:
                    filter_lines = get_current_filter_lines(self)  # Define how to get the current filter lines
                    filter.Filter.save_filter(self, filter_name, filter_lines)
                    reload_combo_box(self)
            # Se for um filtro já existente
            else:
                answer = messagebox.askquestion('Sobrepor filtro no sistema', f'Tem certeza que deseja sobrescrever o filtro {nome_filtro_atual}?')
                if answer == 'yes':
                    filters = filter.Filter.get_filters(self)
                    for line in filters:
                        if line[1] == nome_filtro_atual:
                            filter_id = line[0]
                            break
                    filter_lines = get_current_filter_lines(self)  # Define how to get the current filter lines
                    filter.Filter.edit_filter(self, filter_id, nome_filtro_atual, filter_lines)
                    reload_combo_box(self)

        def reload_combo_box(self):
            filter_names = [name for id, name in filter.Filter.load_filters(self)]
            print(f'List: {filter_names}')
            self.mainButton_frame.combobox.configure(values = ["Filtro Novo"] + filter_names)


        """Cria os widgets da aplicação"""
        self.table_frame = buildWidgets.TableFrame(self, titles=['N° da nota', 'Produto', 'NCM(s)', 'CFOP', 'Descrição'], values=[], height=25)
        self.filter_frame = buildWidgets.FilterFrame(self)
        self.mainButton_frame = buildWidgets.MainButtonFrame(self)

        reload_combo_box(self)
        self.toplevel_window = None

        self.mainButton_frame.buttons[0].configure(command=lambda: processArchives.ProcessXmls.openXmlFile(self))
        self.mainButton_frame.buttons[1].configure(command=lambda: processArchives.ProcessXmls.reviewXmlFile(self))
        self.mainButton_frame.buttons[2].configure(command=lambda: save_button_click_event(self))


        self.filter_frame.grid(row=0, column=0, padx=40, pady=(20, 0), sticky="WN")
        self.mainButton_frame.grid(row=0, column=1, padx=(40, 0), pady=(20, 0), sticky="NEW")
        self.table_frame.grid(row=2, column=0, columnspan=2, sticky="NWSE")

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
