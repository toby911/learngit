from db.MySQLDAO import MySQLDAO
from configs.app_config import *


class Users:

    def __init__(self, username:str, password:str):
        self.username = username
        self.password = password

    # 将对象插入到数据库中
    def insert(self, dao):
        user = {
            "user_name": self.username,
            "password": self.password
        }

        try:
            affected_rows = dao.insert_data('users', user)
        except Exception as e:
            print("inseret docs error!",e)
        print(f"Affected rows: {affected_rows}")

    @staticmethod
    def get_by_name(dao, username):
        query = ["user_name = '" + username + "'"]
        return dao.execute_query("SELECT * FROM sys_users", conditions = query)

