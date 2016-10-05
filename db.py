import MySQLdb
import pymongo
import sys

from config import *
from rss import RSS


class DB(object):
    @classmethod
    def init_mysql(cls):
        db = cls.mysql_connection()
        cursor = db.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS " + MYSQL_DATABASE)
        cursor.execute("use " + MYSQL_DATABASE)
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("DROP TABLE IF EXISTS news")
        cursor.execute("DROP TABLE IF EXISTS user_read_news")
        cursor.execute("""CREATE TABLE userdata (id int AUTO_INCREMENT PRIMARY KEY,
                                                            uname VARCHAR (255),
                                                            password VARCHAR (255))""")
        cursor.execute("""CREATE TABLE newsdata (id int AUTO_INCREMENT PRIMARY KEY,
                                                            title VARCHAR (255),
                                                           link VARCHAR (255))""")
        cursor.execute("""CREATE TABLE user_read_news (user_id int, news_id int)""")
        cursor.close()

    @staticmethod
    def mysql_connection():
        return MySQLdb.connect(MYSQL_HOST, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DATABASE)

    @staticmethod
    def init_mongo():
        db = DB.mongodb_connection()
        db.drop_collection('newsdata')
        db.drop_collection('userdata')
        db.create_collection('newsdata')
        db.create_collection('userdata')

    @staticmethod
    def mongodb_connection():
        client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
        db = client.get_database(MONGO_DATABASE)
        return db

    @classmethod
    def store_data_into_mysql(cls):
        db = cls.mysql_connection()
        cursor = db.cursor()
        try:
            for file_name in RSS.stored_files():
                data = RSS.load_file_data(file_name)
                for link, title in data.iteritems():
                    try:
                        cursor.execute("insert into newsdata (title, link) values (%(title)s, %(link)s)", {'title': title, 'link': link})
                    except BaseException as e:
                        sys.stderr.write("Could not store " + link + "\n" + e.message)
                db.commit()
        finally:
            cursor.close()

    @classmethod
    def store_data_into_mongodb(cls):
        db = cls.mongodb_connection()
        newsdata = db.get_collection('newsdata')
        for file_name in RSS.stored_files():
            data = RSS.load_file_data(file_name)
            for link, title in data.iteritems():
                newsdata.insert({"link": link, "title": title})


if __name__ == '__main__':
    DB.init_mysql()
    DB.init_mongo()
    DB.store_data_into_mysql()
    DB.store_data_into_mongodb()