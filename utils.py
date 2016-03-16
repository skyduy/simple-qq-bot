#!/usr/bin/env python
# coding:utf-8

import MySQLdb, time, logging, requests, json
import jieba.posseg as pseg
from werkzeug.contrib.cache import MemcachedCache
from config import Credentials, AdvancedSettings


class Word:
    @staticmethod
    def remove_symbols(string):
        for i in AdvancedSettings.remove_words_list:
            string = string.replace(i, u'')
        return string

    @staticmethod
    def gen_trunk(string):
        words = pseg.cut(string)
        trunk = map(lambda y: y.word, filter(lambda x: x.flag in AdvancedSettings.trunk_list, words))
        return trunk


class Memcache:
    WAIT_ASK = 1
    WAIT_ANSWER = 2

    def __init__(self):
        self.cache = MemcachedCache(['127.0.0.1:11211'])

    def get(self, key):
        ret = self.cache.get(key)
        try:
            ret = ret.decode('utf-8')
        except:
            pass
        return ret

    def set(self, key, value):
        try:
            value = value.encode('utf-8')
        except:
            pass
        return self.cache.set(key, value, timeout=600)

    def delete(self, key):
        return self.cache.delete(key)

    def check_history(self, qid, gid=0):
        r = self.get(u'H' + str(qid) + u'G' + str(gid))
        if r is None:
            return r, r
        if r == self.WAIT_ANSWER:
            return self.WAIT_ANSWER, self.get(u'A' + str(qid) + u'G' + str(gid))
        if r == self.WAIT_ASK:
            return self.WAIT_ASK, None
        return None

    def set_before_ask(self, qid, gid=0):
        self.set(u'H' + str(qid) + u'G' + str(gid), self.WAIT_ASK)

    def set_before_answer(self, qid, ask, gid=0):
        self.set(u'A' + str(qid) + u'G' + str(gid), ask)
        self.set(u'H' + str(qid) + u'G' + str(gid), self.WAIT_ANSWER)

    def clear_state(self, qid, gid=0):
        self.delete(u'A' + str(qid) + u'G' + str(gid))
        self.delete(u'H' + str(qid) + u'G' + str(gid))

    def last_warn_time(self, qid):
        self.set(u'W'+str(qid), time.time())

    def check_last_chat_same(self, qid, msg):
        if self.get(u'LC'+str(qid)) and self.get(u'LC'+str(qid)) == msg:
            return self.last_chat_count(qid, add=True)
        self.set(u'LC'+str(qid), msg)
        self.set(u'LCC'+str(qid), 1)
        return True

    def last_chat_count(self, qid, add=False):
        lcc = self.get(u'LCC'+str(qid))
        if not lcc:
            self.set(u'LCC'+str(qid), 1)
            return True
        if add and lcc <= AdvancedSettings.same_response_limit:
            self.cache.inc(u'LCC'+str(qid))
            lcc += 1
        return lcc < AdvancedSettings.same_response_limit

    def check_block_user(self, qid):
        x = self.get(u'BU'+str(qid))
        if x is not None:
            return x
        db = MyDB()
        is_blocked = db.check_blocked(qid, 'user')
        logging.info("is_blocked")
        logging.info(is_blocked)
        self.set(u'BU'+str(qid), is_blocked)
        return is_blocked

    def check_block_group(self, gid):
        x = self.get(u'BG'+str(gid))
        if x is not None:
            return x
        db = MyDB()
        is_blocked = db.check_blocked(gid, 'group')
        self.set(u'BG'+str(gid), is_blocked)
        return is_blocked

    def check_disable_group(self, gid):
        x = self.get(u'BD'+str(gid))
        if x is not None:
            return x
        db = MyDB()
        is_disabled = db.check_disabled(gid)
        self.set(u'BD'+str(gid), is_disabled)
        return is_disabled


class MyDB:
    def __init__(self):
        self.db = MySQLdb.connect(host=Credentials.database[0],
                                  user=Credentials.database_account[0],
                                  passwd=Credentials.database_account[1],
                                  db=Credentials.database[1],
                                  charset='utf8'
                                  )
        self.db.autocommit(True)

    def __del__(self):
        self.db.close()

    def execute(self, sql, params=tuple()):
        cursor = self.db.cursor()
        try:
            cursor.execute(sql, params)
        except:
            pass
        return cursor

    def query_exact_question(self, question):
        # question = Word.remove_symbols(question)
        sql = "SELECT * FROM `chat` WHERE `ask`=%s AND `deleted`!=1 ORDER BY RAND() LIMIT 1"
        return self.execute(sql, (question,)).fetchone()

    def query_admin(self, question):
        sql = "SELECT * FROM `chat` WHERE `ask` LIKE %%s% AND `deleted`!=1 LIMIT 30"
        return self.execute(sql, (question,)).fetchone()

    def query_question(self, question):
        question = Word.remove_symbols(question)
        data = self.query_exact_question(question)
        if data is not None:
            return data
        query_string = u'%'.join(Word.gen_trunk(question))
        sql = "SELECT * FROM `chat` WHERE `ask` LIKE %s AND `deleted`!=1 ORDER BY RAND() LIMIT 1"
        return self.execute(sql, (question,)).fetchone()

    def insert_chat(self, ask, answer, committer, gid=0):
        ask = Word.remove_symbols(ask)
        sql = "INSERT INTO `chat`(`ask`,`answer`,`committer`,`gid`,`time`) VALUES(%s,%s,%s,%s,NOW())"
        self.execute(sql, (ask, answer, committer, gid))

    def get_user_info(self, qid):
        sql = "SELECT * FROM `user` WHERE `uid`=%s"
        return self.execute(sql, (qid,)).fetchone()

    def get_group_info(self, gid):
        sql = "SELECT * FROM `group` WHERE `gid`=%s"
        return self.execute(sql, (gid,)).fetchone()

    def block_user(self, qid, unblock=False):
        sql = "UPDATE `user` SET `blocked`=1 WHERE `uid`=%s"
        if unblock:
            sql = "UPDATE `user` SET `blocked`=0 WHERE `uid`=%s"
        self.execute(sql, (qid,))
        mem = Memcache()
        mem.delete(u'BU'+str(qid))

    def block_group(self, gid, unblock=False):
        sql = "UPDATE `group` SET `blocked`=1 WHERE `gid`=%s"
        if unblock:
            sql = "UPDATE `group` SET `blocked`=1 WHERE `gid`=%s"
        self.execute(sql, (gid,))
        mem = Memcache()
        mem.delete(u'BG'+str(gid))

    def disable_group(self, gid, disable=False):
        sql = "UPDATE `group` SET `disabled`=0 WHERE `gid`=%s"
        if disable:
            sql = "UPDATE `group` SET `disabled`=1 WHERE `gid`=%s"
        self.execute(sql, (gid,))
        mem = Memcache()
        mem.delete(u'BD'+str(gid))

    def top_user(self):
        sql = "SELECT * FROM `user` ORDER BY `coin` DESC LIMIT 15"
        return self.execute(sql).fetchall()

    def delete_talk(self, qid, content, is_super=False):
        if not is_super:
            sql = "UPDATE `chat` SET `deleted`=1 WHERE `uid`=%s AND `ask`=%s"
            self.execute(sql, (qid, content))
        else:
            sql = "UPDATE `chat` SET `deleted`=1 WHERE `ask`=%s"
            self.execute(sql, (content,))


    def init_user(self, qid):
        sql = "INSERT INTO `user`(`uid`) VALUES(%s)"
        self.execute(sql, (qid,))

    def init_group(self, gid):
        sql = "INSERT INTO `group`(`gid`) VALUES(%s)"
        self.execute(sql, (gid,))

    def check_blocked(self, xid, type='user'):
        if type == 'user':
            info = self.get_user_info(xid)
            if not info:
                self.init_user(xid)
                return True
            if info[2] and info[2] == 1:
                return False
            return True
        ginfo = self.get_group_info(xid)
        if not ginfo:
            self.init_group(xid)
            return True
        if ginfo[2] and ginfo[2] == 1:
            return False
        return True

    def check_disabled(self, gid):
        ginfo = self.get_group_info(gid)
        if not ginfo:
            self.init_group(gid)
            return True
        if ginfo[1] and ginfo[1] == 1:
            return False
        return True


    def mod_coin(self, qid, x):
        x = int(x)
        if x < 0:
            x = str(x)
        else:
            x = '+' + str(x)
        sql = "UPDATE `user` SET `coin`=`coin`+" + x + " WHERE `uid`=%s"
        cursor = self.db.cursor()
        self.execute(sql, (qid,))

class UserMod:
    IS_ADMIN = 3
    NOT_ADMIN = 0
    NO_GROUP_INFO = 1
    NO_USER_INFO = 2

    def check_group_admin(self, gid, qid):
        url = "%s/openqq/get_group_info" % Credentials.comm_url
        groups = json.loads(requests.get(url).content)
        gid, qid = int(gid), int(qid)
        group = filter(lambda g: int(g[u'gnumber']) == gid, groups)
        if group:
            group = group[0]
            admins = map(lambda member: int(member[u'qq']),
                         filter(lambda x: x[u'role'] == u'admin' or x[u'role'] == u'owner', group[u'member'])
                         )
            if qid in admins:
                return self.IS_ADMIN
            me = filter(lambda x: int(x[u'qq']) == qid, group[u'member'])
            if me:
                return self.NOT_ADMIN
            return self.NO_USER_INFO
        return self.NO_GROUP_INFO
