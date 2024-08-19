import tkinter as tk
from tkinter import simpledialog
import json
import customtkinter
import databaseOperations

class Filter:
    def __init__(self, db_operations):
        self.db_operations = db_operations

    def save_filter(self, filter_values):
        # Abre a janela de diálogo para perguntar o nome do filtro
        filter_name = simpledialog.askstring("Salvar Filtro", "Qual nome você quer colocar para este filtro?")
        if not filter_name:
            return

        # Serializa os valores do filtro para salvar no banco de dados
        filter_json = json.dumps(filter_values)

        # Insere o filtro no banco de dados
        query = "INSERT INTO Filtros (Nome, Valores) VALUES (%s, %s)"
        self.db_operations.cursor.execute(query, (filter_name, filter_json))
        self.db_operations.save_and_close()
        print(f"Filtro '{filter_name}' salvo com sucesso.")

    def load_filters(self):
        # Consulta todos os filtros salvos no banco de dados
        query = "SELECT Nome, Valores FROM Filtros"
        filters = self.db_operations.execute_command(query)
        return filters if filters else []

    def get_filter_by_name(self, name):
        # Consulta um filtro específico pelo nome
        query = f"SELECT Valores FROM Filtros WHERE Nome = '{name}'"
        result = self.db_operations.execute_command(query)
        return json.loads(result[0][0]) if result else None
