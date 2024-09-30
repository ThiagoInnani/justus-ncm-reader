from tkinter import *
from tkinter import ttk
import customtkinter
from PIL import Image
from PIL import ImageTk
import pyperclip

import filter
import processArchives

class TableFrame(customtkinter.CTkFrame):
    def __init__(self, master, titles, values, height):
        super().__init__(master)
        self.grid_columnconfigure(index=0, weight=1)
        self.grid_rowconfigure(index=0, weight=1)
        self.titles = titles
        self.values = values
        self.height = height
        self.create_tree()
    
    def create_tree(self):
        # Add a Treeview widget
        self.tree = ttk.Treeview(self, column=self.titles, show='headings', height=self.height)

        for i in range(len(self.titles)):
            self.tree.column("# "+str(i+1), anchor=CENTER, width=450 if i==5 else 200 if i==6 else 100)
            self.tree.heading("# "+str(i+1), text=self.titles[i])
        
        # Insert the data in Treeview widget
        for i in range(len(self.values)):
            self.tree.insert('', 'end', text=i+1, values=self.values[i])

        self.tree.bind("<<TreeviewSelect>>", lambda x: on_tree_select(self.tree, x))
        self.tree.bind("<Control-Key-c>", lambda x: copy_from_treeview(self.tree, x))

        self.tree.grid(row=0, column=0, padx=10, pady=5, sticky="WSEN")

        def copy_from_treeview(tree, event):
            selection = tree.selection()
            column = tree.identify_column(event.x)
            column_no = int(column.replace("#", "")) - 1
                    
            copy_values = []
            for each in selection:
                try:
                    value = tree.item(each)["values"][column_no]
                    copy_values.append(str(value))
                except:
                    pass
                
            copy_string = "\n".join(copy_values)
            pyperclip.copy(copy_string)
        
        def on_tree_select(tree, event):
                print("selected items:")
                for item in tree.selection():
                    item_text = tree.item(item,"text")
                    print(item_text)

    def clean_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def remove_item(self):
        selected_items = self.tree.selection()        
        for selected_item in selected_items:          
            self.tree.delete(selected_item)

    def add_item(self, values):
        for i in range(len(values)):
            self.tree.insert('', 'end', text=i+1, values=values[i])

    def get_tree(self, index):
        values = []
        for item in self.tree.get_children():
            values.append(self.tree.item(item, "values")[index].rstrip(","))
        #print("Values: ",values)
        return values

class FilterFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.text_fields = []
        self.add_text_field()

    def fill_filter(self, choice):
        filter_lines = filter.Filter.get_filterlines(self)
        filters = filter.Filter.get_filters(self)
        filter_id = None

        for line in filters:
            print(f'Linha de filtros: {line}, choice: {choice}')
            if line[1] == choice:
                filter_id = line[0]
                break


        self.clear_filter()
        
        index = 0
        for line in filter_lines:
            print(f'Linha de linhas de filtros: {line}')
            if line[1] == filter_id:
                if index > 0:
                    self.add_text_field()
                    self.logic_combo.set(line[2])
                self.field_combo.set(line[3])
                self.operation_combo.set(line[4])
                self.entry.insert(0, line[5]) 
                index+=1
        processArchives.ProcessXmls.reviewXmlFile(self.master)
                
    def add_text_field(self):
        index = len(self.text_fields)
        frame = customtkinter.CTkFrame(self)
        frame.grid(row=index, column=0, pady=5, sticky="ewn")

        if index > 0:
            self.logic_combo = customtkinter.CTkOptionMenu(frame, values=["E", "OU"], width=50)
            self.logic_combo.grid(row=0, column=0, padx=(0, 10))
        else:
            self.logic_combo = None

        self.field_combo = customtkinter.CTkOptionMenu(frame, values=["N° da nota", "Produto", "NCM(s)", "CFOP", "CST/CSOSN", "Descrição"], width=150)
        self.field_combo.grid(row=0, column=1, padx=(0, 10))

        self.operation_combo = customtkinter.CTkOptionMenu(frame, values=["é igual a", "é diferente de", "maior que", "menor que", "contém"], width=150)
        self.operation_combo.grid(row=0, column=2, padx=(0, 10))

        self.entry = customtkinter.CTkEntry(frame, placeholder_text="Valor", width=200)
        self.entry.grid(row=0, column=3, padx=(0, 10))

        self.btn_add = customtkinter.CTkButton(frame, text="+", width=30, command=self.add_text_field)
        self.btn_add.grid(row=0, column=4, padx=(0, 10))

        self.btn_remove = customtkinter.CTkButton(frame, text="-", width=30, command=lambda f=frame: self.remove_text_field(f))
        self.btn_remove.grid(row=0, column=5)

        if index > 0 and self.text_fields[-1][4].winfo_exists():
            self.text_fields[-1][4].grid_forget()


        self.text_fields.append((self.logic_combo, self.field_combo, self.operation_combo, self.entry, self.btn_add, self.btn_remove, frame))

    def remove_text_field(self, frame):
        if len(self.text_fields) > 1:
            # Remove a frame correspondente
            print(f"Frame: {frame}")
            for widgets in frame.winfo_children():
                widgets.destroy()
            frame.grid_forget()
            self.text_fields = [tf for tf in self.text_fields if tf[6] != frame]

            # Atualiza os índices das linhas restantes
            for index, (logic_combo, field_combo, operation_combo, entry, btn_add, btn_remove, frame) in enumerate(self.text_fields):
                frame.grid(row=index, column=0, pady=5, sticky="ewn")
                if index == 0:
                    if logic_combo:
                        logic_combo.grid_forget()
                else:
                    if not logic_combo:
                        logic_combo = customtkinter.CTkComboBox(frame, values=["E", "OU"], width=50)
                        logic_combo.grid(row=0, column=0, padx=(0, 10))
                        self.text_fields[index] = (logic_combo, field_combo, operation_combo, entry, btn_add, btn_remove, frame)

            # Reexibir o botão "+" na última linha
            self.text_fields[-1][4].grid(row=0, column=4, padx=(0, 10))

    def get_values(self):
        return [
            (logic_combo.get() if logic_combo else None, field_combo.get(), operation_combo.get(), entry.get())
            for logic_combo, field_combo, operation_combo, entry, _, _, _ in self.text_fields
        ]

    def clear_filter(self):
        for _, _, _, _, _, _, frame in self.text_fields:
            self.remove_text_field(frame)
        palavra = self.entry.get()
        self.entry.delete(first_index=0, last_index=len(palavra))
        
class MainButtonFrame(customtkinter.CTkFrame):
    def combobox_callback(self, choice):
        if choice != 'Filtro Novo':
             self.master.filter_frame.fill_filter(choice)
        else:
            self.master.filter_frame.clear_filter()
            processArchives.ProcessXmls.reviewXmlFile(self.master)

    def update_combobox(self):
        self.combobox.configure(values=['Filtro Novo'] + list(filter.Filter.get_filters(self)))
        self.combobox.set("Filtro Novo")  # set initial value
    
    def get_current_filter(self):
        print(f'Current filter: {self.combobox.get()}')
        return self.combobox.get()
    
    def __init__(self, master, **kwargs):
        super().__init__(master)
        self.grid_columnconfigure((0,2), weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure((0,1,2,3,4), weight=1)

        self.import_button = customtkinter.CTkButton(self, text="Importar XMLs", font=('Arial', 16))
        self.process_button = customtkinter.CTkButton(self, text="Filtrar XMLs", font=('Arial', 16))

        clear_filter_image = Image.open('./src/clear_filter.png')
        clear_filter_image_ctk = customtkinter.CTkImage(light_image=clear_filter_image,
                                                  dark_image=clear_filter_image,
                                                  size=(20,20))
        self.clear_filters_button = customtkinter.CTkButton(self,text="", image=clear_filter_image_ctk, width=20)

        self.separatorUp = ttk.Separator(self, orient='horizontal')

        self.save_button = customtkinter.CTkButton(self, text="Salvar Filtro Atual", font=('Arial', 16))

        delete_image = Image.open('./src/delete_icon.png')
        delete_image_ctk = customtkinter.CTkImage(light_image=delete_image,
                                                  dark_image=delete_image,
                                                  size=(20,20))
        self.delete_filter_button = customtkinter.CTkButton(self,text="", image=delete_image_ctk, width=20, fg_color='#cc0000', hover_color='#8e0000')

        combobox_var = customtkinter.StringVar(value="Filtro Novo")  # set initial value
        self.combobox = customtkinter.CTkOptionMenu(self,
                                     values=['Filtro Novo'],
                                     command=self.combobox_callback,
                                     variable=combobox_var,
                                     font=('Arial', 16)
                                     )
        #grid
        self.import_button.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky="ew")
        self.process_button.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky="ew")
        self.clear_filters_button.grid(row=1, column=2, padx=(10,0), pady=(0, 10), sticky="ew")


        self.separatorUp.grid(row=2, column=0, columnspan=3, pady=(5, 15), sticky="ew")
        
        self.save_button.grid(row=3, column=0, columnspan=3, pady=(0, 10), sticky="ew")

        
        self.delete_filter_button.grid(row=4, column=0, pady=(0, 10), padx=(0, 10), sticky="ew")
        
        self.combobox.grid(row=4, column=1, columnspan=2, pady=(0, 10), sticky="ew")

class AnalyzeButtonFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master)
        self.grid_columnconfigure((0,2), weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure((0,1,2), weight=1)

        self.analyzer = customtkinter.CTkButton(self, text="Analisador", font=('Arial', 16))

        self.entries_label = customtkinter.CTkLabel(self, text="Entradas", font=("Arial", 16), anchor='e')
        self.equivalent_switch = customtkinter.CTkSwitch(self, text="Saídas", onvalue='on', offvalue='off', 
                                                         switch_width=50, switch_height=20, font=('Arial', 16)
                                                        )
        
        self.credited_money_label = customtkinter.CTkLabel(self, text="Imposto Creditado: ", font=("Arial", 16), anchor='w')
        self.due_money_label = customtkinter.CTkLabel(self, text="Imposto Devido : ", font=("Arial", 16), anchor='w')
        self.credit_money_value = customtkinter.CTkLabel(self, text="", font=("Arial", 16), anchor='w')
        self.due_money_value = customtkinter.CTkLabel(self, text="", font=("Arial", 16), anchor='w')


        #Grid
        self.analyzer.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky="ew")
        self.entries_label.grid(row=1, column=0, columnspan=1, padx=0, pady=(0,10), sticky="ew")
        self.equivalent_switch.grid(row=1, column=1, columnspan=1, padx=(10,0), pady=(0,10), sticky="ew")
        self.credited_money_label.grid(row=2, column=0, columnspan=2, pady=(0,10), sticky="ew")
        self.due_money_label.grid(row=3, column=0, columnspan=2, pady=(0,10), sticky="ew")
        self.credit_money_value.grid(row=2, column=2, pady=(0,10), sticky='ew')
        self.due_money_value.grid(row=3, column=2, pady=(0,10), sticky='ew')
 
