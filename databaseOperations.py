from ncm.entities import Ncm, NcmList
from ncm.client import FetchNcm

import json
import mysql.connector
from mysql.connector import errorcode

class DatabaseOperations:
    def _connectToDatabase(self):
        """Conecta com o servidor local MySQL"""
        database_name = 'ncmreader'
        try:
            self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="D1k1xs5j#!"
            )
        except:
            print("Erro na conexão com o banco de dados MySQL.")

        self.cursor = self.connection.cursor()
        try:
            self.connection.database = database_name
            print(f"Acessado o banco de dados {database_name}")

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                # Banco de dados não existe, criando-o
                print(f"O banco de dados {database_name} não existe. Criando...")
                self.cursor.execute(f"CREATE DATABASE {database_name}")
                self.connection.database = database_name
                print(f"Banco de dados {database_name} criado e acessado com sucesso")
                DatabaseOperations._initializeDatabase(self, self.cursor)
                DatabaseOperations._saveAndQuit(self, self.connection)
            else:
                print(err)
                exit(1)

    def _initializeDatabase(self, cursor):
        # Criando a tabela 'Nomenclaturas'
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Nomenclaturas (
            Codigo VARCHAR(50),
            Descricao TEXT
        )
        ''')
        DatabaseNcm._insertNcmInTable(self, cursor)

    def _saveAndQuit(self, connection):
        # Salvando as mudanças e fechando a conexão
        connection.commit()
        connection.close()
    
    def _getCommand(self, command):
        self.cursor.execute(command)
        myresult = self.cursor.fetchall()
        return myresult

    
class DatabaseNcm:
    def _downloadNcmTable(self):
        # Download do arquivo
        fetch_ncm = FetchNcm()
        # Ler o arquivo JSON
        with open('ncm.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data

    def _insertNcmInTable(self, cursor):
        # Inserir os dados do JSON na tabela
        data = DatabaseNcm._downloadNcmTable(self)
        for nomenclatura in data['Nomenclaturas']:
            cursor.execute('''
            INSERT INTO Nomenclaturas (Codigo, Descricao)
            VALUES (%s, %s)
            ''', (nomenclatura['Codigo'], nomenclatura['Descricao']))


