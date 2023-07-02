import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mysql.connector
from mysql.connector import pooling

from configs.config import DEVELOPMENT, LLP_DEV, PRODUCTION

# 判断当前环境
if os.environ.get("PRODUCTION"):
    config = PRODUCTION
elif os.environ.get("DEVELOPMENT"):
    config = DEVELOPMENT
elif os.environ.get("LLP_DEV"):
    config = LLP_DEV
else:
    config= DEVELOPMENT
    
class MySQLDAO:
    def __init__(self, pool_name, pool_size, **kwargs):
        self.pool = pooling.MySQLConnectionPool(pool_name=pool_name,
                                                pool_size=pool_size,
                                                **kwargs)

    def execute_query(self, query, params=None, conditions=None):
        if conditions:
            conditions_str = ' AND '.join(conditions)
            query += f" WHERE {conditions_str}"
            
        connection = self.pool.get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(query, params)
            columns = cursor.column_names
            result = []
            
            for row in cursor.fetchall():
                row_data = dict(zip(columns, row))
                result.append(row_data)
            
            return result
        finally:
            cursor.close()
            connection.close()
            
    def execute_update(self, query, params=None):
        connection = self.pool.get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(query, params)
            connection.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            connection.close()

    def insert_data(self, table, data):
        columns = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({values})"
        params = tuple(data.values())

        return self.execute_update(query, params)

    def update_data(self, table, data, condition):
        columns = ', '.join([f"{column} = %s" for column in data.keys()])
        query = f"UPDATE {table} SET {columns} WHERE {condition}"
        params = tuple(data.values())

        return self.execute_update(query, params)

    def delete_data(self, table, condition):
        query = f"DELETE FROM {table} WHERE {condition}"

        return self.execute_update(query)

    @classmethod
    def get_dao(cls):
        dao = MySQLDAO(pool_name='my_pool',
                pool_size=5, 
                host=config.MYSQL_HOST, 
                database=config.MYSQL_DATABASE,
                user=config.MYSQL_USER, 
                password=config.MYSQL_PWD)
        return dao
  

if __name__ == '__main__':
    dao = MySQLDAO.get_dao()
    # 插入数据
    # data = {'collection_name': 'A1', 
    #         'doc_name': 'A1.pdf', 
    #         'doc_type': 'pdf',
    #         'state': 0,
    #         'size': 0,
    #         'create_at':0,
    #         'update_at':0
    #         }
    # affected_rows = dao.insert_data('docs', data)
    # print(f"Affected rows: {affected_rows}")
    
    # 查询数据
    # result = dao.execute_query("SELECT * FROM docs")
    # print(result)
    
    # 更新数据
    # data = {'collection_name': 'A1', 
    #         'doc_name': 'A2.pdf', 
    #         'doc_type': 'pdf',
    #         'state': 0,
    #         'size': 0,
    #         'create_at':0,
    #         'update_at':0
    #         }
    # condition = "collection_name = 'A1' and doc_name = 'A2.pdf'"
    # affected_rows = dao.update_data('docs', data, condition)
    # print(f"Affected rows: {affected_rows}")
    
    # 查询数据
    condition = conditions = ["collection_name = 'A1'", "doc_name = 'A1.pdf'"]
    result = dao.execute_query("SELECT * FROM docs", conditions = condition)
    print(result)