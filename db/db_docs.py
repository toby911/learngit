import calendar
import os
import sqlite3
import time

from configs.config import DEVELOPMENT, LLP_DEV, PRODUCTION
from db.MySQLDAO import MySQLDAO

# 判断当前环境
if os.environ.get("PRODUCTION"):
    config = PRODUCTION
elif os.environ.get("DEVELOPMENT"):
    config = DEVELOPMENT
elif os.environ.get("LLP_DEV"):
    config = LLP_DEV
else:
    config= DEVELOPMENT
class Docs:
    
    def __init__(self, collection_name: str="", doc_id: str="", doc_name: str="", doc_type: str = "pdf", size : int = 0, state : int = 0, create_at: int = 0, update_at: int = 0, id : int = 0):
        self.collection_name = collection_name
        self.doc_id = doc_id
        self.doc_name = doc_name
        self.doc_type = doc_type
        self.state = state
        self.size = size
        self.create_at = create_at
        self.update_at = update_at

        ts = calendar.timegm(time.gmtime())
        if self.create_at == 0:
            self.create_at = ts
        if self.update_at == 0:
            self.update_at = ts


    # 将对象插入到数据库中
    def insert(self, dao):
        # 插入数据
        data = {'collection_name': self.collection_name,
                'doc_id': self.doc_id, 
                'doc_name': self.doc_name, 
                'doc_type': self.doc_type,
                'state': self.state,
                'size': self.size,
                'create_at': self.create_at,
                'update_at': self.update_at
                }
        try:
            affected_rows = dao.insert_data('docs', data)
        except Exception as e:
            print("inseret docs error!",e)
        print(f"Affected rows: {affected_rows}")


    # 更新对象在数据库中的信息
    def update(self, dao):
        # 更新数据
        data = {'collection_name': self.collection_name, 
                'doc_id': self.doc_id,
                'doc_name': self.doc_name, 
                'doc_type': self.doc_type,
                'state': self.state,
                'size': self.size,
                'create_at': self.create_at,
                'update_at': self.update_at
                }
        condition = ["collection_name = " + self.collection_name, "doc_name = " + self.doc_name]
        affected_rows = dao.update_data('docs', data, condition)
        print(f"Affected rows: {affected_rows}")
        return affected_rows
    
    def get_all(self, dao):
        return dao.execute_query("SELECT * FROM docs", condition = None)

    def get_all_by_collection(self, dao, collection_name):
        condition = ["collection_name = '" + collection_name+ "'"]
        return dao.execute_query("SELECT * FROM docs", conditions = condition)
        
    def get_by_doc_name(dao, collection_name, doc_name):
        condition = ["collection_name = '" + collection_name + "'", "doc_name = '" + doc_name + "'"]
        return dao.execute_query("SELECT * FROM docs", conditions = condition)

    def __str__(self):
        return f"Doc(collection_name='{self.collection_name}', doc_id='{self.doc_id}', doc_name='{self.doc_name}', doc_type='{self.doc_type}', state={self.state}, create_at={self.create_at}, update_at={self.update_at})"

    
if __name__ == '__main__':
    from MySQLDAO import MySQLDAO
    dao = MySQLDAO(pool_name='my_pool', 
                pool_size=5, 
                host=config.MYSQL_HOST, 
                database=config.MYSQL_DATABASE,
                user=config.MYSQL_USER, 
                password=config.MYSQL_PWD)
    doc = Docs(dao, 'A1', 'A3.pdf')
    doc.insert()
    print(doc.get_by_doc_name("A1","A3.pdf"))
        