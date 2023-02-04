__author__ = '3eca'
__github__ = 'https://github.com/3eca'
__telegram__ = '@holyNash'

from pyodbc import InterfaceError, OperationalError, connect


SQL_ATTR_CONNECTION_TIMEOUT = 113


class DB:
    __db_string_connect = 'DRIVER={ODBC Driver 17 for SQL Server};' \
                          'SERVER=%s;DATABASE=%s;UID=%s;PWD=%s'

    def __init__(self, server: str, database: str, user: str, password: str):
        self.__server = server
        self.__database = database
        self.__user = user
        self.__password = password
        self.__connect = None

    def __enter__(self):
        try:
            self.__connect = connect(self.__db_string_connect % (
                self.__server,
                self.__database,
                self.__user,
                self.__password
            ),
                                     timeout=3,
                                     attrs_before={
                                     SQL_ATTR_CONNECTION_TIMEOUT: 3}
                                     )
            self.__connect.timeout = 3
            self.__connect.autocommit = True
            return self
        except (InterfaceError, OperationalError) as error:
            self.error = error

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__connect:
            self.__connect.close()

    def __get_cursor(self) -> object:
        return self.__connect.cursor()

    def execute(self, query: str) -> None:
        cursor = self.__get_cursor()
        cursor.execute(query)

    def select(self, query: str) -> list:
        cursor = self.__get_cursor()
        cursor.execute(query)
        return cursor.fetchall()


if __name__ == '__main__':
    pass
