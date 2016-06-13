#!/usr/bin/env python
# coding:utf-8
from __future__ import unicode_literals

import random
import json
import requests

from redis import Redis
from collections import Counter

import jieba
from config import comm_url, ReplyStrings, filter_path
from model import QA, SensitiveQA, Record
from text_filter import DFAFilter

jieba.initialize()


class UserMod(object):
    IS_ADMIN = 3
    NOT_ADMIN = 0
    NO_GROUP_INFO = 1
    NO_USER_INFO = 2

    def check_group_admin(self, gid, qid):
        url = "%s/openqq/get_group_info" % comm_url
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


class HandlerRedisDB0(object):
    def __init__(self, sender_qq, gid, nickname, enable_filter=False):
        self.redis = Redis('localhost', 6379)
        self.sender_qq = sender_qq
        self.gid = gid
        self.nickname = nickname
        self.filter_enabled = enable_filter

    def active(self):
        self.redis.sadd('daily_active_user', self.sender_qq)
        self.redis.sadd('daily_active_group', self.gid)
        self.redis.sadd('active_group_%s_qq' % self.gid, self.sender_qq)
        self.redis.set(self.sender_qq, self.nickname)

    def get_money_dict(self):
        money_dict = {}
        active_qqs = self.redis.smembers('active_group_%s_qq' % self.gid)
        for qq in active_qqs:
            nickname = self.redis.get(qq)
            money = self.redis.get('money-%s' % qq)
            if money is not None and nickname is not None:
                money_dict[nickname] = int(money)
        return money_dict

    def enable_group_replay(self):
        self.redis.set('group-%s-enable' % self.gid, 1)

    def disable_group_replay(self):
        self.redis.set('group-%s-enable' % self.gid, 0)

    def reply_group(self):
        r = self.redis.get('group-%s-enable' % self.gid)
        if r is not None and r == '0':
            return False
        return True

    def get_state(self):
        r = self.redis.get('state-' + self.sender_qq)
        if r is None:
            self.redis.set('state-' + self.sender_qq, 0)
            r = '0'
        return r

    def chg_state(self):
        key = 'state-' + self.sender_qq
        state = self.get_state()
        state = int(state)
        if not state:
            self.redis.set(key, 1, 3600)
        else:
            state = (state + 1) % 3
            self.redis.set(key, state, 3600)

    def get_joke_rank(self):
        rank_key = 'joke_rank-'+self.gid
        rank = self.redis.get(rank_key)
        if not rank:
            self.redis.set(rank_key, 40)
            rank = '40'
        joke_key = 'joke-' + rank
        joke = self.redis.get(joke_key)
        if not joke:
            joke = ''
        joke = joke.decode('utf-8')
        return joke, rank

    def chg_joke_rank(self):
        key = 'joke_rank-' + self.gid
        remain = self.redis.get(key)
        if not remain:
            self.redis.set(key, 40)
            remain = '40'
        remain = int(remain)
        if remain == 1:
            self.redis.set(key, 40)
        else:
            self.redis.decr(key)

    def read_over(self):
        self.redis.set('read-' + self.gid, 1, 86400)

    def has_read(self):
        done = self.redis.get('read-' + self.gid)
        if done == '1':
            return True
        return False

    def get_money(self):
        key = 'money-' + self.sender_qq
        balance = self.redis.get(key)
        if balance is None:
            self.redis.set(key, 40)
            return 40
        return int(balance)

    def add_money(self, money=1):
        key = 'money-' + self.sender_qq
        self.redis.incr(key, money)

    def reduce_money(self, reductions):
        balance = self.get_money()
        if balance < reductions:
            return False, balance
        self.redis.decr('money-' + self.sender_qq, reductions)
        return True, balance-reductions

    def add_question(self, question):
        self.redis.set('question-' + self.sender_qq, question, 7200)

    def get_question(self):
        question = self.redis.get('question-' + self.sender_qq)
        return question


class HandlerRedisDB1(object):
    def __init__(self):
        self.redis = Redis('localhost', 6379, db=1)

    def content_to_redis(self, questions, qa_id):
        return self.redis.hmset(qa_id, Counter(jieba.cut(questions)))

    # 根据问题content获取在数据库中的id
    def id_from_redis(self, content):
        def get_len(d):
            length = 0
            for i in d.values():
                i = int(i)
                length += i ** 2
            length = pow(length, 0.5)
            return length * 1.0

        contents = {}
        raw_contents = Counter(jieba.cut(content))
        for k, v in raw_contents.iteritems():
            contents[k.encode("utf-8")] = v
        content_keys_set = set(contents.keys())
        len1 = get_len(raw_contents)

        keys = self.redis.keys()
        kv = {}
        for key in keys:
            questions = self.redis.hgetall(key)
            question_keys_set = set(questions.keys())
            common_keys_set = content_keys_set & question_keys_set
            if common_keys_set:
                tmp = 0
                for item in common_keys_set:
                    tmp += contents[item] * int(questions[item])
                len2 = get_len(questions)
                rate = tmp / (len1 * len2)
                if rate > 0.52:
                    kv.setdefault(rate, [])
                    kv[rate].append(key)
        if len(kv) == 0:
            return None
        rate = max(kv.keys())
        ids = kv[rate]
        return ids


class HandlerMySQL(object):
    def __init__(self, user):
        self.redis = Redis('localhost', 6379)
        self.user = user

    def add_chat_record(self, content):
        question_answer = Record(content, self.user)
        question_answer.save()

    def add_sensitive_qa(self, question, answer):
        question_answer = SensitiveQA(question, answer, self.user)
        question_answer.save()

    def add_valid_qa(self, question, answer):
        question_answer = QA(question, answer, self.user)
        r = question_answer.save()
        return r.id

    def get_answer_by_id(self, qa_id):
        r = QA.query.filter_by(id=qa_id).first()
        if r is None:
            return None
        return r.answer


class MessageProcessor(object):
    def __init__(self, msg):
        self.message = msg[u'content'].strip()
        self.sender_qq = str(msg[u'sender_qq'])
        self.gid = str(msg[u'gnumber'])
        self.sender = msg[u'sender']
        self.handler_redis0 = HandlerRedisDB0(self.sender_qq, self.gid, self.sender, enable_filter=False)
        self.handler_redis1 = HandlerRedisDB1()
        self.handler_sql = HandlerMySQL(self.sender_qq)
        self.text_filter = DFAFilter(filter_path)
        self.too_long = False

    def send_to_me(self):
        if self.message.startswith(u'/') or self.message.startswith(u'／'):
            self.message = self.message[1:].strip().lower()
            if len(self.message.encode('utf-8')) >= 690:
                self.too_long = True
            self.handler_redis0.active()
            if not self.handler_redis0.reply_group() and self.message not in ReplyStrings.enable_group:
                return False
            return True
        return False

    def make_static_reply(self):
        if self.message in ReplyStrings.about:
            return ReplyStrings.about_message
        elif self.message in ReplyStrings.help:
            return ReplyStrings.user_help
        else:
            return None

    def change_reply_state(self):
        is_reply_state = self.handler_redis0.reply_group()
        u = UserMod()
        r = u.check_group_admin(self.gid, self.sender_qq)
        if r == u.IS_ADMIN:
            if self.message in ReplyStrings.enable_group:
                if not is_reply_state:
                    self.handler_redis0.enable_group_replay()
                    return ReplyStrings.group_enable
                else:
                    return '已处于群聊开启状态 :)'
            else:
                if is_reply_state:
                    self.handler_redis0.disable_group_replay()
                    return ReplyStrings.group_disable
                else:
                    return None
        return ReplyStrings.group_admin_info[r]

    def query_coin(self):
        balance = self.handler_redis0.get_money()
        return '你还剩%s颗豆子~\n·教我知识+10豆\n·和我聊天+1豆' % balance

    def get_ranking(self):
        money_dict = self.handler_redis0.get_money_dict()
        message = '本群活跃用户豆子排行如下:'
        count = 0
        money_list = sorted(money_dict.iteritems(), key=lambda d: d[1], reverse=True)
        for nickname, money in money_list:
            message += '\n@%s : %s' % (unicode(nickname, 'utf-8'), money)
            count += 1
            if count >= 10:
                break
        return message

    def lotto(self):
        money = self.handler_redis0.get_money()
        if money < 30:
            return '一次消耗30豆！你仅剩颗%s个豆子,不能乐透了！' % money
        self.handler_redis0.reduce_money(30)
        got = int(random.normalvariate(30, 20))
        got = max(got, 2)
        got = min(got, 150)
        self.handler_redis0.add_money(got)
        return '你抽中了%d颗豆子！人品好的话最高可赢150颗哦~' % got

    def get_joke(self):
        joke, rank = self.handler_redis0.get_joke_rank()
        if joke == '':
            return '库存没有段子了！管理员正在运货！'
        rank = int(rank)
        if not self.handler_redis0.has_read():
            reductions = 1 if 31 <= rank <= 40 else 2 if 26 <= rank <= 30 else \
                4 if 23 <= rank <= 25 else 8 if 21 <= rank <= 22 else 0
            enough, balance = self.handler_redis0.reduce_money(reductions)
            if not enough:
                return '你仅剩颗%s个豆子,不能购买价值%s的段子了, 回复"学习"教我知识吧，能赚豆子哦！' \
                       % (balance, reductions)
            elif rank > 21:
                fee = '付费'
                num = rank - 20
                tip = '[你购买了价值%s豆的段子，还剩下%s颗豆子]' % (reductions, balance)
            elif rank == 21:
                fee = '付费'
                num = rank - 20
                tip = '[你购买了价值%s豆的最后一餐付费段子，还剩下%s颗豆子，接下来的20个段子免费哦]' % \
                      (reductions, balance)
            elif rank > 1:
                fee = '免费'
                num = rank
                tip = '[本条为免费段子~]'
            else:
                fee = '免费'
                num = rank
                tip = '[今天的段子讲完啦~不过可以重温讲给女票！(重温免费)]'
                self.handler_redis0.read_over()
            content = '今日%s段子[%s]:\n%s\n\n%s' % (fee, str(num), joke, tip)
        else:
            tip = '\n[此条为免费重温段子，每日更新]'
            content = '今日段子[%s]:\n%s\n\n%s' % (str(rank), joke, tip)
        self.handler_redis0.chg_joke_rank()
        return content

    def chat(self):
        state = self.handler_redis0.get_state()
        if state == '0':
            if self.message in ReplyStrings.learn:
                self.handler_redis0.chg_state()
                return '输入问题：'
            else:
                self.handler_sql.add_chat_record(self.message)
                self.handler_redis0.add_money()
                ids = self.handler_redis1.id_from_redis(self.message)
                if not ids:
                    return '该问题还没人教呢！回复“学习”教教小D吧！'
                qa_id = random.choice(ids)
                answer = self.handler_sql.get_answer_by_id(qa_id)
                if answer is None:
                    return '该问题还没人教呢！回复“学习”教教小D吧！'
                return answer

        if state == '1':
            if self.message in ReplyStrings.instruction:
                return '指令无法作为问题，请重新输入其他问题。'
            else:
                self.handler_redis0.add_question(self.message)
                self.handler_redis0.chg_state()
                return '对于问题：%s\n输入其答案:' % self.message

        if state == '2':
            self.handler_redis0.chg_state()
            question = self.handler_redis0.get_question()
            if not question:
                return '呜...小D只知道你在一小时或者更久之前问过问题，但是忘记问题是什么了...'
            if self.handler_redis0.filter_enabled and self.text_filter.included_in(self.message):
                self.handler_sql.add_sensitive_qa(question, self.message)
                return '(#ﾟДﾟ)！小D检测到您的回答中有敏感词汇，学习失败。'
            else:
                qa_id = self.handler_sql.add_valid_qa(question, self.message)
                self.handler_redis0.add_money(10)
                self.handler_redis1.content_to_redis(question, qa_id)
                reply = '\n问题：%s\n答案：%s\n学习成功:)' % (unicode(question, 'utf-8'), self.message)
                if len(reply.encode('utf-8')) > 698:
                    return '\n学习成功 :)\n[Tip: 消息太长，恕无法给予其它提示]'
                return reply

    def process(self):
        if not self.send_to_me():
            return None

        static_reply = self.make_static_reply()
        if static_reply is not None:
            return static_reply

        if self.message in ReplyStrings.disable_group or self.message in ReplyStrings.enable_group:
            return self.change_reply_state()

        if self.message in ReplyStrings.query_coin:
            return self.query_coin()

        if self.message in ReplyStrings.get_ranking:
            return self.get_ranking()

        if self.message in ReplyStrings.lotto:
            return self.lotto()

        if self.message in ReplyStrings.get_joke:
            return self.get_joke()

        reply = self.chat()
        return reply
