import json
import mysql.connector
from mysql.connector import errorcode
from ncm.client import FetchNcm

class DatabaseOperations:
    def __init__(self, host, user, password, database_name):
        self.host = host
        self.user = user
        self.password = password
        self.database_name = database_name
        self.connection = None
        self.cursor = None

    def connect_to_database(self):
        """Conecta com o servidor local MySQL e ao banco de dados especificado"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            self.cursor = self.connection.cursor()
            self._select_database()
        except mysql.connector.Error as err:
            print(f"Erro na conexão com o banco de dados MySQL: {err}")
            return False
        return True

    def _select_database(self):
        try:
            self.connection.database = self.database_name
            print(f"Acessado o banco de dados {self.database_name}")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                self._create_database()
            else:
                print(err)
                self._close_connection()
                exit(1)

    def _create_database(self):
        """Cria o banco de dados se não existir"""
        try:
            print(f"O banco de dados {self.database_name} não existe. Criando...")
            self.cursor.execute(f"CREATE DATABASE {self.database_name}")
            self.connection.database = self.database_name
            print(f"Banco de dados {self.database_name} criado e acessado com sucesso")
            self._initialize_database()
        except mysql.connector.Error as err:
            print(f"Erro ao criar o banco de dados: {err}")
            self._close_connection()
            exit(1)

    def _initialize_database(self):
        """Inicializa a tabela 'Nomenclaturas'"""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS Nomenclaturas (
                    Codigo VARCHAR(50),
                    Descricao TEXT
                )
            ''')
            print("Tabela 'Nomenclaturas' criada ou já existente.")
        except mysql.connector.Error as err:
            print(f"Erro ao criar a tabela: {err}")
            self._close_connection()
            exit(1)

    def save_and_close(self):
        """Salva as mudanças e fecha a conexão"""
        try:
            if self.connection:
                self.connection.commit()
                self.connection.close()
                print("Conexão com o banco de dados fechada.")
        except mysql.connector.Error as err:
            print(f"Erro ao fechar a conexão: {err}")

    def execute_command(self, command):
        """Executa um comando SQL e retorna os resultados"""
        try:
            self.cursor.execute(command)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Erro ao executar o comando: {err}")
            return None

    def _close_connection(self):
        """Fecha a conexão com o banco de dados"""
        if self.connection:
            self.connection.close()


class DatabaseNcm:
    def __init__(self, db_operations):
        self.db_operations = db_operations

    def download_ncm_table(self):
        """Faz o download do arquivo JSON contendo as Nomenclaturas"""
        fetch_ncm = FetchNcm()
        # Ler o arquivo JSON
        with open('ncm.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data

    def insert_ncm_in_table(self):
        """Insere os dados do JSON na tabela 'Nomenclaturas'"""
        data = self.download_ncm_table()
        try:
            for nomenclatura in data['Nomenclaturas']:
                codigo_sem_pontos = nomenclatura['Codigo'].replace('.', '')
                self.db_operations.cursor.execute('''
                    INSERT INTO Nomenclaturas (Codigo, Descricao)
                    VALUES (%s, %s)
                ''', (codigo_sem_pontos, nomenclatura['Descricao']))
            self.db_operations.save_and_close()
        except mysql.connector.Error as err:
            print(f"Erro ao inserir dados na tabela: {err}")
            self.db_operations._close_connection()



