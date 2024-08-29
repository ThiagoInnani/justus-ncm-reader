import json
import mysql.connector
from mysql.connector import errorcode
from ncm.client import FetchNcm

class DatabaseOperations:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = 'D1k1xs5j#!'
        self.database_name = "ncmreader"
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
            return False
        return True

    def _select_database(self):
        try:
            self.connection.database = self.database_name
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
            self.cursor.execute(f"CREATE DATABASE {self.database_name}")
            self.connection.database = self.database_name
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
                );
                ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS Filter (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL
                );
                ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS FilterLine (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    filter_id INT,
                    logical_operator VARCHAR(10),
                    field VARCHAR(255),
                    operation VARCHAR(10),
                    value VARCHAR(255),
                    FOREIGN KEY (filter_id) REFERENCES Filter(id)
                );
                ''')
            print("Tabela 'Nomenclaturas', 'Filters', 'FilterLine' criadas ou já existentes.")
            self._save_connection()
        except mysql.connector.Error as err:
            print(f"Erro ao criar a tabela: {err}")
            self._close_connection()
            exit(1)

    def _save_connection(self):
        """Salva as mudanças e fecha a conexão"""
        try:
            if self.connection:
                self.connection.commit()
                print("Alteração salva.")
        except mysql.connector.Error as err:
            print(f"Erro ao salvar no banco de dados: {err}")

    def execute_command(self, command):
        """Executa um comando SQL e retorna os resultados"""
        try:
            if command == "lastrowid":
                return self.cursor.lastrowid
            else:
                self.cursor.execute(command)
                return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Erro ao executar o comando: {err}")
            return None

    def _close_connection(self):
        """Fecha a conexão com o banco de dados"""
        if self.connection:
            self.connection.close()
            print("Conexão com banco fechada")


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
        print("Inserindo dados NCM na tabela")
        data = self.download_ncm_table()
        try:
            for nomenclatura in data['Nomenclaturas']:
                codigo_sem_pontos = nomenclatura['Codigo'].replace('.', '')
                descricao_corrigida = DatabaseNcm.replace_multiple(nomenclatura['Descricao'], ['-', '<i>', '</i>'])

                self.db_operations.cursor.execute('''
                    INSERT INTO Nomenclaturas (Codigo, Descricao)
                    VALUES (%s, %s)
                ''', (codigo_sem_pontos, descricao_corrigida))
            self.db_operations._save_connection()
        except mysql.connector.Error as err:
            print(f"Erro ao inserir dados na tabela: {err}")
            self.db_operations._close_connection()
        
    def replace_multiple(text, words_to_replace):
        for word in words_to_replace:
            text = text.replace(word, "")
        return text


