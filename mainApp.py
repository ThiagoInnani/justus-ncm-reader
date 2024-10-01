from tkinter import messagebox
import customtkinter
import os
from tkinter import ttk, filedialog as fd, PhotoImage, Menu



# Imports de Classes
import buildWidgets
import processArchives
import databaseOperations
import filter
import interfaceCreation

class App(customtkinter.CTk):
    """Classe principal da aplicação"""

    def __init__(self):
        super().__init__()
        self.toplevel_window = None
        self.title("Filtrador de NCMs Justus")
        self.geometry("1200x850")
        self.minsize(1200, 850)
        self._setup_grid()
        self._connect_database()
        self._create_widgets()
        self.interface_creation = interfaceCreation.Interface(self)

    def _setup_grid(self):
        """Configura o layout de grid da janela"""
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

    def _connect_database(self):
        # Uso dos módulos
        self.db_ops = databaseOperations.DatabaseOperations()
    
        if self.db_ops.connect_to_database():
            self.db_ops._initialize_database()
            #Confere se existe uma tabela Nomenclaturas preenchida
            count = self.db_ops.execute_command("SELECT COUNT(*) FROM Nomenclaturas")
            db_fill = databaseOperations.DatabaseFill(self.db_ops)
            if count[0][0] == 0:
                db_fill.insert_ncm_in_table()
                db_fill.insert_cst_in_table()
                db_fill.insert_csosn_in_table()
                db_fill.insert_uf_in_table()
                db_fill.insert_cfop_in_table()
            db_filter = filter.Filter(self.db_ops)
    
    def _create_widgets(self):
        def get_current_filter_lines(self):
            self.values = self.filter_frame.get_values()
            return self.values

        def save_button_click_event(self):
            nome_filtro_atual = self.main_button_frame.get_current_filter()
            # Se for um filtro novo
            if nome_filtro_atual == "Filtro Novo":
                dialog = customtkinter.CTkInputDialog(text="Digite o nome do filtro:", title="Nome do Filtro")
                filter_name = dialog.get_input()
                if filter_name:
                    filter_lines = get_current_filter_lines(self)  # Define how to get the current filter lines
                    filter.Filter.save_filter(self, filter_name, filter_lines)
                    reload_combo_box(self)
                    self.main_button_frame.combobox.set(f"{filter_name}")
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
                    self.main_button_frame.combobox.set(f'{nome_filtro_atual}')

        def delete_button_click_event(self):
            nome_filtro_atual = self.main_button_frame.get_current_filter()
            if nome_filtro_atual != 'Filtro Novo':
                answer = messagebox.askquestion('Deletar filtro do sistema', f'Tem certeza que deseja excluir o filtro {nome_filtro_atual}?')
                if answer == 'yes':
                    filters = filter.Filter.get_filters(self)
                    for line in filters:
                        if line[1] == nome_filtro_atual:
                            filter_id = line[0]
                            break
                    filter.Filter.delete_filter(self, filter_id)
                    reload_combo_box(self)
                    self.main_button_frame.combobox.set("Filtro Novo")
            else:
                messagebox.showerror('ERRO: filtro não excluível', f'ERRO: não é possível excluir o filtro {nome_filtro_atual}')            
        
        def reload_combo_box(self):
            filter_names = [name for id, name in filter.Filter.load_filters(self)]
            print(f'List: {filter_names}')
            self.main_button_frame.combobox.configure(values = ["Filtro Novo"] + filter_names)

        """Cria os widgets da aplicação"""
        self.tabview = customtkinter.CTkTabview(master=self, width=400)
        tab_filter = self.tabview.add('Filtros')
        tab_analysis = self.tabview.add('Análise')
        tab_filter.grid_columnconfigure(0, weight=1)
        tab_filter.grid_rowconfigure(0, weight=1)
        tab_analysis.grid_columnconfigure(0, weight=1)
        tab_analysis.grid_rowconfigure(0, weight=1)

        self.table_frame = buildWidgets.TableFrame(self, titles=['N° da nota', 'Produto', 'NCM(s)', 'CFOP', 'CST/CSOSN',
                                                                 'Descrição', 'Status', 'Crédito (R$)', 'Débito (R$)', 'Diferença (R$)'
                                                                ], values=[], height=25)
        self.filter_frame = buildWidgets.FilterFrame(self)
        self.main_button_frame = buildWidgets.MainButtonFrame(tab_filter)
        self.analyze_button_frame = buildWidgets.AnalyzeButtonFrame(tab_analysis)
        self.process_archive = processArchives.ProcessXmls(self)

        reload_combo_box(self)
        self.toplevel_window = None

        '''Conecta os botões do main_button_frame, process_archive e analyze_button_frame com suas funcionalidades'''
        self.main_button_frame.import_button.configure(command=lambda: self.process_archive.openXmlFile())
        self.main_button_frame.process_button.configure(command=lambda: self.process_archive.reviewXmlFile())
        self.main_button_frame.save_button.configure(command=lambda: save_button_click_event(self))
        self.main_button_frame.delete_filter_button.configure(command=lambda: delete_button_click_event(self))
        self.main_button_frame.clear_filters_button.configure(command=lambda: self.filter_frame.clear_filter())
        self.analyze_button_frame.analyzer.configure(command=lambda: self.process_archive.analyze_button_click_event())
        self.analyze_button_frame.equivalent_switch.configure(command=lambda: self.process_archive.cfop_swap())

        self.tabview.grid(row=0, column=1, sticky="NES")
        self.tabview._segmented_button.grid(sticky="W")

        self.filter_frame.grid(row=0, column=0, padx=40, pady=(20, 0), sticky="WN")
        self.table_frame.grid(row=2, column=0, columnspan=2, sticky="NWSE")
        self.main_button_frame.grid(row=0, column=0, padx=20, pady=10, sticky="NEWS")
        self.analyze_button_frame.grid(row=0, column=0, padx=20, pady=10, sticky="NEWS")

if __name__ == "__main__":
    app = App()
    app.mainloop()
