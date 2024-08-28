import mysql.connector
import customtkinter

import databaseOperations

class Filter:
    def __init__(self, db_operations):
        self.db_ops = db_operations
        self.load_filters()
        

    def load_filters(self):
        print("Chegou em load_filters")
        query = f"SELECT id, name FROM Filter"
        result = self.db_ops.execute_command(query)
        print(f'Result: {result}')
        return result

    def save_filter(self, filter_name, filter_lines):
        # Save filter
        query = f"INSERT INTO Filter (name) VALUES ('{filter_name}')"
        print(f'Query em save_filter: {query}')
        self.db_ops.execute_command(query)
        self.db_ops._save_connection()

        filter_id = self.db_ops.execute_command('lastrowid')

        # Save filter lines
        for line in filter_lines:
            print(f'Filter ID: {filter_id}, Linha atual: {line}')
            query = f"INSERT INTO FilterLine (filter_id, logical_operator, field, operation, value) VALUES ({filter_id}, '{line[0]}', '{line[1]}', '{line[2]}', '{line[3]}')"
            self.db_ops.execute_command(query)
        self.db_ops._save_connection()

    def edit_filter(self, filter_id, new_name, new_lines):
        # Edit filter name
        db_ops = databaseOperations.DatabaseOperations()
        db_ops.connect_to_database()

        db_ops.execute_command(f"UPDATE Filter SET name = '{new_name}' WHERE id = {filter_id}")
        db_ops._save_connection()

        # Delete old filter lines
        db_ops.execute_command(f"DELETE FROM FilterLine WHERE filter_id = {filter_id}")
        db_ops._save_connection()

        # Save new filter lines
        for line in new_lines:
            db_ops.execute_command(
                f"INSERT INTO FilterLine (filter_id, logical_operator, field, operation, value) VALUES ({filter_id}, '{line[0]}', '{line[1]}', '{line[2]}', '{line[3]}')"
            )
        db_ops._save_connection()
        db_ops._close_connection()

    def delete_filter(self, filter_id):
        # Delete filter lines
        self.cursor.execute("DELETE FROM FilterLine WHERE filter_id = %s", (filter_id,))
        self.connection.commit()

        # Delete filter
        self.cursor.execute("DELETE FROM Filter WHERE id = %s", (filter_id,))
        self.connection.commit()
        self.load_filters()  # Reload filters after deleting

    def get_filters(self):
        db_ops = databaseOperations.DatabaseOperations()
        db_ops.connect_to_database()
        query = f'SELECT * FROM Filter'
        filter_lines = db_ops.execute_command(query)
        print(f'Filtros filtradas: {filter_lines}')
        db_ops._close_connection()
        return filter_lines

    def get_filterlines(self):
        db_ops = databaseOperations.DatabaseOperations()
        db_ops.connect_to_database()
        query = f'SELECT * FROM FilterLine'
        filter_lines = db_ops.execute_command(query)
        #print(f'Linhas filtradas: {filter_lines}')
        db_ops._close_connection()
        return filter_lines
        