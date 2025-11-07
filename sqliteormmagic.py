# python3.9.16
# version 0.0.6
"""
The script allows you to access the SQlite3 database 
through a function, which is more convenient than 
the syntax of direct SQL queries. For questions and 
comments, write to the author @Practic_old
"""
import sqlite3
from sqlite3 import Error
import asyncio
import aiosqlite
import pandas as pd

import logger as log


async def execute_query(connection, query, params):
    """ 
    Function for recording
    to sql database
    connection : database connection
    query: str SQLite query string
    params: list request parameters
    """
    res = None
    cursor = await connection.cursor()
    try:

        if len(params) > 0:

            await cursor.execute(query, params)
        else:
            await cursor.execute(query)
            res = await cursor.fetchall()
        await connection.commit()
    except Error as e:
        print(f"The error '{e}' occurred")

    return res


async def del_key_words():
    async with aiosqlite.connect('users.db') as connection:
        query = f"""
                DELETE FROM const 
                """
        await execute_query(connection=connection, query=query, params=[])


async def report_users():
    async with aiosqlite.connect('users.db') as connection:
        query = f"""
                SELECT * FROM users 
                """
        all_records = await execute_query(connection=connection, query=query, params=[])
        len_of_records = len(all_records['from_user_id'])
        all_records.to_excel('report.xlsx', index=False)

        return len_of_records


async def get_user_list():
    async with aiosqlite.connect('users.db') as connection:
        query = f"""
                SELECT * FROM users 
                """
        all_records = await execute_query(connection=connection, query=query, params=[])
        user_list = [user_data[0] for user_data in all_records]

        return user_list


async def execute_query_select(query, params):
    """ 
    Function for reading from sql database
    returns a list of tuples
    connection : database connection
    query: str SQLite query string
    params: list request parameters
    """
    async with aiosqlite.connect('users.db') as connection:
        res = None
        cursor = await connection.cursor()
        try:
            await cursor.execute(query, params)
            res = await cursor.fetchall()

            await connection.commit()
        except Error as e:
            print(f"The error '{e}' occurred")

        return res


async def get_cnt_keyword():
        async with aiosqlite.connect('users.db') as connection:
            query = "SELECT COUNT(*) FROM const"
            key_cnt = await execute_query(connection, query=query, params=[])
            return key_cnt


class SQLiteDB():

    def __init__(self, DBNAME):
        self.DBNAME = DBNAME

    async def create_table(self, table:str, list_query_params:list):
        """
        Function to create a table
        table: str table name
        list_query_params: list query parameters
        An example of how column names are passed to a table by a list of tuples
        list_query_params = [
        ('from_user_id', 'INTEGER UNIQUE'),   must be unique values ​​here
        ('from_user_username', 'TEXT'),
        ('from_user_firstname', 'TEXT'),
        ('regtime', 'INTEGER')
        ]
        """
        async with aiosqlite.connect(self.DBNAME) as connection:
            text_query=''
            for i in list_query_params:
                text_query += f"{i[0]} {i[1]},\n"
            text_query=text_query[:-2]

            query = f"CREATE TABLE IF NOT EXISTS {table} ({text_query});"
            await execute_query(connection=connection, query=query, params=[])

    async def find_table_or_column(self, table_name:str, column_name:str):
        """
        the function is designed to search
        for all values ​​by the column name key
        example: column_name = 'from_user_id'
        if you need to find several columns,
        just specify them separated by commas,
        example: column_name = 'from_user_id, reg_data'
        to search for all columns, specify
        example: column_name = '*'
        """
        async with aiosqlite.connect(self.DBNAME) as connection:
            query = f"""SELECT {column_name} 
                    FROM {table_name}
                    """
            list_of_tuple = await execute_query_select(query=query, params=[])
            return list_of_tuple

    async def find_elements_in_column(self, table_name:str, key_name:str, column_name:str):
        """
        database search function
        by cell value with column name
        returns a list of tuples of one table row
        table_name: str table name
        key_name: str key name
        column_name: str column name
        """
        query = f"""SELECT * 
                FROM {table_name}
                WHERE {column_name} = ?
                """
        list_of_tuple = await execute_query_select(query=query, params=[key_name])
        return list_of_tuple

    async def find_elements_by_keyword(self, table_name:str, key_name:str, column_name:str):
        """
        database search function
        searches for matches in a column line by line
        returns a list of tuples
        table_name: str the name of the table
        key_name: str keyword string
        column_name: str column name
        """
        async with aiosqlite.connect(self.DBNAME) as connection:
            query = f"""SELECT * 
                    FROM {table_name}
                    WHERE {column_name} LIKE '%{key_name}%' 
                    """
            # print(query)
            list_of_tuple = execute_query_select(connection, query=query, params=[])
            return list_of_tuple

    async def upd_element_in_column(self, table_name:str, set_upd_par_name: str, set_key_par_name: str, upd_column_name: str, key_column_name:str):
        """
        database update function
        by cell value with column name
        table_name: str table name
        upd_par_name: str name of the parameter to update
        key_par_name: str name of the parameter to search
        upd_column_name: str name of the column to update
        key_column_name: str name of the column to search
        """
        async with aiosqlite.connect(self.DBNAME) as connection:
            query = f"""
                UPDATE {table_name}
                SET {set_upd_par_name} = ?
                WHERE {upd_column_name} = ?
                """
            # print(query)
            await execute_query(connection, query=query, params=[set_key_par_name, key_column_name])

    async def ins_unique_row(self, table_name:str, list_query_params:list):
        """
        database insertion function
        unique value with column name
        if there was a UNIQUE flag when creating 
        a column in a database table
        table_name: str table name
        list_query_params: list list of tuples of one table row
        Parameter List Loading Example 
        list_query_params = [
        ('from_user_id', '123'),
        ('from_user_username', 'vasya'),
        ('from_user_firstname', 'petrov'),
        ('regtime', '1234568')
        ]   
        """
        async with aiosqlite.connect(self.DBNAME) as connection:
            text_params = ''
            for i in list_query_params:
                text_params += f"{i[0]},\n"
            text_params=text_params[:-2]

            list_value = []
            text_questions = ""
            for i in list_query_params:
                list_value.append(i[1])
                text_questions += f"?,"
            text_questions = text_questions[:-1]

            query = """
            INSERT OR IGNORE INTO {table} ({text_params}) VALUES ({text_questions})
            """.format(table=table_name, text_params=text_params, text_questions=text_questions)

            await execute_query(connection=connection, query=query, params=list_value)

    async def insert_row(self, table_name:str, list_query_params:list):
            """
            database insertion function
            unique value with column name
            if there was a UNIQUE flag when creating
            a column in a database table
            table_name: str table name
            list_query_params: list list of tuples of one table row
            Parameter List Loading Example
            list_query_params = [
            ('from_user_id', '123'),
            ('from_user_username', 'vasya'),
            ('from_user_firstname', 'petrov'),
            ('regtime', '1234568')
            ]
            """
            async with aiosqlite.connect(self.DBNAME) as connection:

                text_params=''
                for i in list_query_params:
                    text_params += f"{i[0]},\n"
                text_params=text_params[:-2]

                list_value = []
                text_questions = ""
                for i in list_query_params:
                    list_value.append(i[1])
                    text_questions += f"?,"
                text_questions=text_questions[:-1]

                query = """
                INSERT INTO {table} ({text_params}) VALUES ({text_questions})
                """.format(table=table_name, text_params=text_params, text_questions=text_questions)

                await execute_query(connection=connection, query=query, params=list_value)

    async def find_one_value_from_row(self, value:str, table_name:str, column_name:str, key_name:str):
            """
            database search function
            by cell value with column name
            returns a list of tuples of one table row
            table_name: str table name
            key_name: str key name
            column_name: str column name
            """
            async with aiosqlite.connect(self.DBNAME) as connection:
                query = f"""SELECT {value} 
                        FROM {table_name}
                        WHERE {column_name} = ?
                        """
                list_of_tuple = await execute_query_select(connection, query=query, params=[key_name])
                return list_of_tuple[0][0]

    async def delete_table(self, table):
            """
            ERASE table
            DELETE all rows from table
            """
            async with aiosqlite.connect(self.DBNAME) as connection:
                query = f"""
                DELETE FROM "{table}"
                        """
                await execute_query(connection, query=query, params=[])

    async def delete_row(self, table:str, key_name:str, column_name:str):
            """
            DELETE rows from table by key 
            """
            async with aiosqlite.connect(self.DBNAME) as connection:
                query = f"""
                DELETE FROM "{table}"
                WHERE {column_name} = ?
                        """
                await execute_query(connection, query=query, params=[key_name])

    async def get_cnt_products(self):
        async with aiosqlite.connect(self.DBNAME) as connection:
            query = "SELECT COUNT(*) FROM tmp_id WHERE price IS NOT NULL"
            products_cnt = await execute_query(connection, query=query, params=[])
            return products_cnt

