from tkinter import *
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo

class FileAlteration():
    def __init__():
        super().__init__()
        
    def selectFileExplorer():
        print("Chegou no select")
        directory = fd.askdirectory(
            title='Selecione o diretório',
            initialdir='',
            )
        showinfo(
            title='Pasta selecionada',
            message=directory
        )
        if directory is None:
            return
        
        return directory
