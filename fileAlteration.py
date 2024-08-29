from tkinter import *
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo

class FileAlteration():
    def __init__():
        super().__init__()
        
    def selectFileExplorer():
        directory = fd.askdirectory(
            title='Selecione o diretório',
            initialdir='',
            )
        
        if not directory:  # Verifica se o diretório está vazio ou foi cancelado
            showinfo(
                title='Aviso',
                message='Nenhuma pasta selecionada.'
            )
            return None
        
        showinfo(
            title='Pasta selecionada',
            message=directory
        )
        
        return directory
