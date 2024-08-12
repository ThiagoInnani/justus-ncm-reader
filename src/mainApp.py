import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
import customtkinter

import xml.etree.ElementTree as ET
import os
#from PIL import Image, ImageTk


#Class Import
import fileAlteration
import buildWidgets

class App(customtkinter.CTk):
    def __init__(self):
        def openXmlFile(self):
            diretorio = fileAlteration.FileAlteration.selectFileExplorer()
            if not diretorio:
                return
            
            arquivos_xml = [os.path.join(diretorio, f) for f in os.listdir(diretorio) if f.endswith('.xml')]

            self.tableData = []

            ns = {"": "http://www.portalfiscal.inf.br/nfe"}


            for arquivo in arquivos_xml:
                tree = ET.parse(arquivo)
                root = tree.getroot()

                nota_num = root.find('.//nNF', ns)
                ncm_list = [ncm.text for ncm in root.findall('.//NCM', ns)]
                ncm = ', '.join(ncm_list)
                try:
                    self.tableData.append([nota_num.text, ncm])
                except:
                    continue    
            self.tableFrame.clean_table()
            self.tableFrame.add_item(self.tableData)
        
        def reviewXmlFile(self):
            filter_values = self.filter_frame.get_values()
            print(filter_values)
            filter_values = [value for value in filter_values if value]  # Remove campos vazios

            if not filter_values:  # Se todos os campos estiverem vazios, mostra todos os dados
                filtered_data = self.tableData
            else:
                filtered_data = []
                for row in self.tableData:
                    ncm_values = row[1].split(', ')
                    if not any(ncm in filter_values for ncm in ncm_values):
                        filtered_data.append(row)

            self.tableFrame.clean_table()
            self.tableFrame.add_item(filtered_data)

        def changeTheme(self):
            if self.theme == 1:
                customtkinter.set_appearance_mode("light")
                themeToLight(self)
                self.theme = 0

            else:
                customtkinter.set_appearance_mode("dark")
                themeToDark(self)
                self.barraDeMenus.configure()
                self.theme = 1
            self.barraDeMenus.config(background=self.menuBarColor, foreground=self.menuFontColor)
            self.configure(bg=self.backgroundColor)
            self.style = ttk.Style()
            #self.style.theme_use("default")
            self.style.configure("Treeview",
                                 background=self.tableValueColor,
                                 foreground=self.tableValueFont,
                                 fieldbackground = self.tableValueColor)
            self.style.configure("Treeview.Heading", background=self.tableHeaderColor, foreground=self.tableHeaderFont, font="bold")
            self.style.map('Treeview', background=[("selected", self.tableHeaderColor)])

        def themeToDark(self):
            self.menuBarColor = '#3B3E45'
            self.menuFontColor = "#FFFFFF"
            self.backgroundColor = '#242424'
            self.tableHeaderColor = '#1F6AA5'
            self.tableHeaderFont = "#FFFFFF"
            self.tableHeaderHover = "#fc0093"
            self.tableValueColor = '#242424'
            self.tableValueFont = "#FFFFFF"
            customtkinter.set_default_color_theme("blue")

        def themeToLight(self):
            self.menuBarColor = "#FFFFFF"
            self.menuFontColor = "#000000"
            self.backgroundColor = '#DBDBDB'
            self.tableHeaderColor = '#1F6AA5'
            self.tableHeaderFont = "#FFFFFF"
            self.tableHeaderHover = "#fc0093" #325882
            self.tableValueColor = "#FFFFFF"
            self.tableValueFont = "#000000"
            customtkinter.set_default_color_theme("dark-blue")
        
        super().__init__()
        pastaApp=os.path.dirname(__file__)
        self.title("Filtrador de NCMs Justus")
        self.geometry("1200x800")
        self.grid_columnconfigure((0,1,2), weight=1)
        self.grid_rowconfigure((0,1,2), weight=1)
        self.tk.call('wm', 'iconphoto', self._w, PhotoImage(file=pastaApp+'/src/icon.png'))
        self.style = ttk.Style()

        if customtkinter.get_appearance_mode() == 1:
            print("O sistema está no modo escuro")
            self.theme = 1
            customtkinter.set_appearance_mode("dark")
            themeToDark(self)
        else:
            self.theme = 0
            print("O sistema está no modo de luz")
            customtkinter.set_appearance_mode("light")
            themeToLight(self)
        

        self.barraDeMenus = Menu(self, background= self.menuBarColor)
        menuArquivos = Menu(self.barraDeMenus, tearoff=0)
        menuOpcoes = Menu(self.barraDeMenus, tearoff=0)
        menuArquivos.add_command(label="Importar Arquivo XML",command=lambda: openXmlFile(self))
        menuArquivos.add_separator()
        menuArquivos.add_command(label="Fechar", command=self.quit)
        menuOpcoes.add_command(label="Trocar de Tema", command = lambda: changeTheme(self))
        self.barraDeMenus.add_cascade(label="Arquivos", menu=menuArquivos)
        self.barraDeMenus.add_cascade(label="Opções", menu=menuOpcoes)
        self.config(menu=self.barraDeMenus)

        self.toplevel_window = None

        #Declaração de Frames
        self.button_frame = buildWidgets.MainButtonFrame(self, text=["Importar XMLs","Filtrar XMLs"])
        self.tableFrame = buildWidgets.BuildTable(self, titles=['N° da nota', 'NCM(s)'], values=[], height=40)
        self.filter_frame = buildWidgets.Filter(self)
        #Declaração de Widgets
        self.button_frame.buttons[0].configure(command=lambda: openXmlFile(self))
        self.button_frame.buttons[1].configure(command=lambda: reviewXmlFile(self))

        #Atribuição GRID
        self.filter_frame.grid(row=0, column=3, padx=40, pady=(20, 0), sticky="WN")
        self.button_frame.grid(row=2, column=3, padx=40, pady=(20,0), sticky="W")
        self.tableFrame.grid(row=0, column=0, rowspan=3, columnspan=3, sticky="NWSE")
        #self.image_label.grid()
        
        changeTheme(self)

app = App()
print(app)
app.mainloop()