# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from twisted.enterprise import adbapi


# 同步（默认）
class JianshuSpiderPipeline(object):
    def __init__(self):
        dbparams = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': 'mysql123',
            'database': 'jianshu',
            'charset': 'utf8'
        }
        self.conn = pymysql.connect(**dbparams)
        self.cursor = self.conn.cursor()
        self._sql = None

    def process_item(self, item, spider):
        self.cursor.execute(self.sql,
                            (item['title'], item['content'], item['article_id'], item['origin_url'], item['author'],
                             item['avatar'], item['pub_time'], item['word_count'], item['view_count'],
                             item['comment_count'], item['like_count'], item['subjects']))
        self.conn.commit()
        return item

    @property
    def sql(self):
        if not self._sql:
            self._sql = """
            insert into articles(id,title,content,article_id,origin_url,author,avatar,pub_time,word_count,view_count,comment_count,like_count,subjects)
            values (null, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            return self._sql
        return self._sql


# 异步保存到数据库（基于twisted）

class JianshuTwistedPipeline(object):
    def __init__(self):
        dbparams = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': 'mysql123',
            'database': 'jianshu',
            'charset': 'utf8',
            'cursorclass': pymysql.cursors.DictCursor
        }
        self.dbpool = adbapi.ConnectionPool('pymysql', **dbparams)
        self._sql = None

    @property
    def sql(self):
        if not self._sql:
            self._sql = """
            insert into articles(id,title,content,article_id,origin_url,author,avatar,pub_time,word_count,view_count,comment_count,like_count,subjects)
            values (null, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """
            return self._sql
        return self._sql

    def process_item(self, item, spider):
        # runInteraction将同步转化为异步处理
        defer = self.dbpool.runInteraction(self.insert_item, item)
        # 错误处理
        defer.addErrback(self.handle_error, item, spider)

    def insert_item(self, cursor, item):
        cursor.execute(self.sql,
                       (item['title'], item['content'], item['article_id'], item['origin_url'], item['author'],
                        item['avatar'], item['pub_time'], item['word_count'], item['view_count'],
                        item['comment_count'], item['like_count'], item['subjects']))

    def handle_error(self, error, item, spider):
        print("=" * 20 + "error" + "=" * 20)
        print(error)
        print("=" * 20 + "error" + "=" * 20)
