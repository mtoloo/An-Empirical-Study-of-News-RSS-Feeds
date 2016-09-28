import MySQLdb
import pymongo

from config import *


class DB(object):
    @staticmethod
    def init_mysql():
        db = MySQLdb.connect(MYSQL_HOST, MYSQL_USERNAME, MYSQL_PASSWORD)
        cursor = db.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS " + MYSQL_DATABASE)
        cursor.execute("use " + MYSQL_DATABASE)
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (id int AUTO_INCREMENT PRIMARY KEY,
                                                            uname VARCHAR (255),
                                                            password VARCHAR (255))""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS news (id int AUTO_INCREMENT PRIMARY KEY,
                                                            title VARCHAR (255),
                                                           link VARCHAR (255))""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS user_read_news (user_id int, news_id int)""")
        cursor.close()

    @staticmethod
    def init_mongo():
        client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
        db = client.get_database(MONGO_DATABASE)
        print db.name
        print db.userdata
        print db.newsdata

DB.init_mysql()
DB.init_mongo()
