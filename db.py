import hashlib
import md5
import random

import MySQLdb
import pymongo
import sys

import time

from config import *
from rss import RSS


class DB(object):
    @classmethod
    def init_mysql(cls, engine='innodb'):
        db = cls.mysql_connection()
        cursor = db.cursor()
        # try:
        #     cursor.execute("use " + MYSQL_DATABASE)
        # except:
        #     cursor.execute("CREATE DATABASE IF NOT EXISTS " + MYSQL_DATABASE)
        cursor.execute("DROP TABLE IF EXISTS userdata")
        cursor.execute("DROP TABLE IF EXISTS newsdata")
        cursor.execute("DROP TABLE IF EXISTS user_read_news")
        cursor.execute("""CREATE TABLE userdata (id int AUTO_INCREMENT PRIMARY KEY,
                                                            uname VARCHAR (255),
                                                            password VARCHAR (255))
                                                engine=%s""" % engine)
        cursor.execute("""CREATE TABLE newsdata (id int AUTO_INCREMENT PRIMARY KEY,
                                                            title VARCHAR (255),
                                                           link VARCHAR (512))
                                                engine=%s""" % engine)
        cursor.execute("""CREATE TABLE user_read_news (user_id int, news_id int)
                                                       engine=%s""" % engine)
        cursor.close()

    @staticmethod
    def mysql_connection():
        return MySQLdb.connect(MYSQL_HOST, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DATABASE)

    @classmethod
    def mysql_created(cls):
        try:
            cls.mysql_connection()
            return True
        except:
            return False

    @classmethod
    def mysql_stat(cls):
        db = cls.mysql_connection()
        cursor = db.cursor()
        try:
            cursor.execute("select count(*) from newsdata")
            result = {'news': cursor.fetchone()[0]}
            return result
        except:
            return {'news': 0}
        finally:
            cursor.close()
            db.close()

    @classmethod
    def mysql_users(cls):
        db = cls.mysql_connection()
        cursor = db.cursor()
        try:
            cursor.execute("select id, uname from userdata limit 5")
            result = []
            while True:
                data = cursor.fetchone()
                if not data: break
                user_id, username = data
                result.append({'id': user_id, 'username': username})
            return result
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def init_mongo():
        db = DB.mongodb_connection()
        db.drop_collection('newsdata')
        db.drop_collection('userdata')
        db.create_collection('newsdata')
        db.create_collection('userdata')
        db.get_collection('userdata').create_index('id')

    @staticmethod
    def mongodb_connection():
        client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
        db = client.get_database(MONGO_DATABASE)
        return db

    @classmethod
    def store_data_into_mysql(cls, news, progress_callback=None):
        db = cls.mysql_connection()
        cursor = db.cursor()
        try:
            for row in news:
                if progress_callback and not progress_callback():
                    break
                try:
                    cursor.execute("insert into newsdata (title, link) values (%(title)s, %(link)s)", row)
                    row['id'] = cursor.lastrowid
                except BaseException as e:
                    pass
                    # sys.stderr.write("Could not store " + link + "\n" + e.message)
            db.commit()
        finally:
            cursor.close()
        return news

    @classmethod
    def store_data_into_mongodb(cls, news, progress_callback=None):
        db = cls.mongodb_connection()
        newsdata = db.get_collection('newsdata')
        id = 1
        for row in news:
            if progress_callback and not progress_callback():
                break
            newsdata.insert({"id": row.get('id', id), "link": row['link'], "title": row['title']})
            id += 1

    @classmethod
    def generate_users(cls, count=5000):
        result = [{"id": i, "uname": str(i), "password": str(i)} for i in range(1, count + 1)]
        return result

    @classmethod
    def store_users_in_mysql(cls, users, progress_callback=None):
        db = cls.mysql_connection()
        cursor = db.cursor()
        try:
            for user in users:
                cursor.execute("insert into userdata (id, uname, password) values (%(id)s, %(uname)s, %(password)s)",
                               {"id": user['id'], "uname": user['uname'], "password": user['password']})
                user_id = cursor.lastrowid
                for news in user['news']:
                    if progress_callback and not progress_callback():
                        return
                    if 'id' not in news: continue
                    news_id = news['id']
                    cursor.execute("insert into user_read_news (user_id, news_id) values (%(user_id)s, %(news_id)s)",
                                   {"user_id": user_id, "news_id": news_id})
            db.commit()
        finally:
            cursor.close()

    @classmethod
    def store_users_into_mongodb(cls, users, progress_callback):
        db = cls.mongodb_connection()
        userdata = db.get_collection('userdata')
        current = 0
        for user in users:
            current += len(user['news'])
            if progress_callback and not progress_callback(current):
                break
            userdata.insert(user)

    @classmethod
    def assign_news_to_users_randomly(cls, news, users):
        result = 0
        for user in users:
            user['news'] = random.sample(news, random.randrange(50))
            result += len(user['news'])
        return result

    @classmethod
    def select_users_mysql(cls, count, progress_callback):
        db = cls.mysql_connection()
        cursor = db.cursor()
        try:
            cursor.execute("select max(id) from userdata")
            max_user_id,  = cursor.fetchone()
            for i in range(count):
                if progress_callback and not progress_callback():
                    break
                user_id = random.randrange(1, max_user_id)
                cursor.execute("""Select * from userdata u
                                join user_read_news rn on u.id = rn.user_id
                                join newsdata n on rn.news_id = n.id
                                where u.id = %(user_id)s""", {'user_id': user_id})
        finally:
            db.close()

    @classmethod
    def select_users_mongo(cls, count, progress_callback):
        db = cls.mongodb_connection()
        max_user_id = db.userdata.find_one(sort=[("id", pymongo.DESCENDING)])['id']
        for i in range(count):
            if progress_callback and not progress_callback():
                break
            user_id = random.randrange(1, max_user_id)
            db.userdata.find_one({'id': user_id})

    @classmethod
    def mysql_change_engine(cls, engine):
        db = cls.mysql_connection()
        try:
            cursor = db.cursor()
            cursor.execute("alter table userdata engine=%s" % engine)
            cursor.execute("alter table newsdata engine=%s" % engine)
            cursor.execute("alter table user_read_news engine=%s" % engine)
            db.commit()
        finally:
            db.close()

    @classmethod
    def update_users_reading_news_mysql(cls, count, progress_callback):
        db = cls.mysql_connection()
        cursor = db.cursor()
        try:
            cursor.execute("select max(id) from userdata")
            max_user_id,  = cursor.fetchone()
            cursor.execute("select max(id) from newsdata")
            max_news_id,  = cursor.fetchone()
            for i in range(count):
                if progress_callback and not progress_callback():
                    break
                user_id = random.randrange(1, max_user_id)
                news_id = random.randrange(1, max_news_id)
                cursor.execute("insert into user_read_news (user_id, news_id) values (%(user_id)s, %(news_id)s)",
                               {"user_id": user_id, "news_id": news_id})
                db.commit()
        finally:
            db.close()

    @classmethod
    def update_users_reading_news_mongo(cls, count, progress_callback):
        db = cls.mongodb_connection()
        try:
            max_user_id = db.userdata.find_one(sort=[("id", pymongo.DESCENDING)])['id']
            max_news_id = db.newsdata.find_one(sort=[("id", pymongo.DESCENDING)])['id']
            for i in range(count):
                if progress_callback and not progress_callback():
                    break
                user_id = random.randrange(1, max_user_id)
                news_id = random.randrange(1, max_news_id)
                news = db.newsdata.find_one({'id': news_id})
                user = db.userdata.find_one({'id': user_id})
                if not user:
                    print user_id
                    continue
                user.get('news', []).append(news)
                db.userdata.update({'id': user_id}, {'news': news})
        finally:
            pass
            # db.close()


if __name__ == '__main__':
    news = RSS.load_all_news_as_array()
    users = DB.generate_users(5000)
    mysql_time = time.time()
    DB.init_mysql()
    news = DB.store_data_into_mysql(news)
    DB.assign_news_to_users_randomly(news, users)
    DB.store_users_in_mysql(users)
    print "MySQL Time:", time.time() - mysql_time
    mongo_time = time.time()
    DB.init_mongo()
    DB.store_data_into_mongodb(news)
    DB.store_users_into_mongodb(users)
    print "Mongo Time:", time.time() - mongo_time


class MySQLCursor:

    def __init__(self):
        pass

    def __enter__(self):
        self.db = DB.mysql_connection()
        self.cursor = self.db.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.db.close()


class MongoDBConnection:

    def __init__(self):
        pass

    def __enter__(self):
        self.db = DB.mongodb_connection()
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
