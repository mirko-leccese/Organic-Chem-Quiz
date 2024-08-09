import sqlite3

class Utils:
    '''
    Python class with util functions 
    '''

    @staticmethod
    def get_db_connection(db_path: str):
        '''
        Method to establish a connection with a SQLite3 Db 

        :params db_path: absolute path of the database file
        '''
        connection = sqlite3.connect(db_path)
        connection.row_factory = sqlite3.Row 

        return connection