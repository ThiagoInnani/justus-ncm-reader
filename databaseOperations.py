import json
import csv
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
        """Inicializa as tabelas no banco de dados"""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS Nomenclaturas (
                    id VARCHAR(8) PRIMARY KEY,
                    description TEXT
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
                    value VARCHAR(255) NOT NULL,
                    FOREIGN KEY (filter_id) REFERENCES Filter(id)
                );
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS CFOP (
                    id VARCHAR(4) PRIMARY KEY,
                    equivalent VARCHAR(4) NOT NULL,
                    description TEXT
                );
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS CST (
                    id VARCHAR(3) PRIMARY KEY,
                    description TEXT
                );
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS CSOSN (
                    id VARCHAR(3) PRIMARY KEY,
                    description TEXT
                );
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS FederativeUnits (
                    id VARCHAR(2) PRIMARY KEY,
                    state_name VARCHAR(30)
                );
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS BaseIcms (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    value FLOAT NOT NULL,
                    nomenclatura_id VARCHAR(8) NOT NULL,
                    cst_id VARCHAR(3),
                    csosn_id VARCHAR(3),
                    federative_unit_id VARCHAR(2) NOT NULL,
                    FOREIGN KEY (nomenclatura_id) REFERENCES Nomenclaturas(id),
                    FOREIGN KEY (cst_id) REFERENCES CST(id),
                    FOREIGN KEY (csosn_id) REFERENCES CSOSN(id),
                    FOREIGN KEY (federative_unit_id) REFERENCES FederativeUnits(id)
                );
            ''')
            print("Tabelas criadas ou já existentes.")
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

class DatabaseFill:
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
                descricao_corrigida = DatabaseFill.replace_multiple(nomenclatura['Descricao'], ['-', '<i>', '</i>'])

                self.db_operations.cursor.execute('''
                    INSERT INTO Nomenclaturas (id, description)
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

    def insert_cst_in_table(self):
        with open("./data/CST.csv", "r") as file:
            reader = csv.reader(file)

            for row in reader:
                self.db_operations.cursor.execute('''
                INSERT INTO CST (id, description)
                VALUES (%s, %s)
                ''', row)
        self.db_operations._save_connection()
        
    def insert_csosn_in_table(self):
        with open("./data/CSOSN.csv", "r") as file:
            reader = csv.reader(file)

            for row in reader:
                self.db_operations.cursor.execute('''
                INSERT INTO CSOSN (id, description)
                VALUES (%s, %s)
                ''', row)
        self.db_operations._save_connection()

    def insert_uf_in_table(self):
        with open("./data/UF.csv", "r") as file:
            reader = csv.reader(file)

            for row in reader:
                self.db_operations.cursor.execute('''
                INSERT INTO FederativeUnits (id, state_name)
                VALUES (%s, %s)
                ''', row)
        self.db_operations._save_connection()
    
    def insert_cfop_in_table(self):
        with open("./data/CFOP.csv", "r") as file:
            reader = csv.reader(file, delimiter=";")

            for row in reader:
                self.db_operations.cursor.execute('''
                INSERT INTO CFOP (id, equivalent, description)
                VALUES (%s, %s, %s)
                ''', row)
        self.db_operations._save_connection()    