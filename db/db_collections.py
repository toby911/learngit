import calendar
import os
import sqlite3
import time
import uuid

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

class Collections:
    def __init__(self):
        pass

    # 将对象插入到数据库中
    def insert(self, dao, collection_name):
        data = {'collection_name': collection_name,
                'collection': "k" + str(uuid.uuid4())[-12:],
                'status': 0
            }
        try:
            affected_rows = dao.insert_data('collections', data)
        except Exception as e:
            print("inseret collection error!",e)

    # 从数据库中删除对象
    def delete(self, dao, collection_name):
        pass
 
    # 更新对象在数据库中的信息
    def update(self, collection_name, status):
       pass

    # 从数据库中获取所有对象
    def get_all(self, dao):
        return dao.execute_query("SELECT * FROM collections", conditions = None)

    def get_by_collection_name(self, dao, collection_name):
        condition = ["collection_name = '" + collection_name+ "'"]
        return dao.execute_query("SELECT * FROM collections", conditions = condition)

    def del_by_collection_name(self, collection_name):
        pass
         
    def del_all(self):
        pass

    def __str__(self):
        return f"Collection(collection_name='{self.collection_name}', status='{self.status}', create_at={self.create_at}, update_at={self.update_at})"

if __name__ == '__main__':
    from MySQLDAO import MySQLDAO
    dao = MySQLDAO(pool_name='my_pool', 
                pool_size=5, 
                host= config.MYSQL_HOST, 
                database= config.MYSQL_DATABASE,
                user= config.MYSQL_USER, 
                password= config.MYSQL_PWD)
    collections = Collections(dao)
    collections.insert("B1")
    print(collections.get_by_collection_name("B1"))
        