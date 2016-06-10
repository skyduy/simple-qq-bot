#!/usr/bin/env python
# coding:utf-8

from __future__ import unicode_literals

import random
import sys
from redis import Redis
from utils import UserMod, id_from_redis, content_to_redis
from config import ReplyStrings

all_func_group = [
    'GroupChat.check_at_me', 'Common.blank_check', 'GroupChat.disable_group',
    'Game.query_coin', 'PreDefinedMessage.all', 'Common.chat'
]


class GroupChat:
    @staticmethod
    def check_at_me(msg):
        message = msg[u'content']
        if not message.startswith(u'/'):
            return True, u''
        return False, u''

    @staticmethod
    def disable_group(msg):
        message = msg[u'content']
        sender_qq = msg[u'sender_qq']
        gid = msg[u'gnumber']
        message = message.replace(u'/', u'').strip()
        redis_store = Redis('localhost', 6379, db=2)
        if message in ReplyStrings.disable_group or message in ReplyStrings.enable_group:
            u = UserMod()
            r = u.check_group_admin(gid, sender_qq)
            if r == u.IS_ADMIN:
                if message in ReplyStrings.enable_group:
                    redis_store.set(u'group-%s-enable' % gid, 1)
                    return True, ReplyStrings.group_enable
                else:
                    redis_store.set(u'group-%s-enable' % gid, 0)
                    return True, ReplyStrings.group_disable
            return True, ReplyStrings.group_admin_info[r]
        r = redis_store.get(u'group-%s-enable' % gid)
        if r is not None and int(r) == 1:
            return True, u''
        return False, u''


class Common:
    @staticmethod
    def blank_check(msg):
        message = msg[u'content']
        blank_list = [u' ', u',', u'，', u'\r', u'\n']
        for i in blank_list:
            message = message.replace(i, u'')
        if len(message) == 0:
            return True, u""
        return False, u""

    @staticmethod
    def chat(msg):
        redis_store = Redis('localhost', 6379)
        message = msg[u'content']
        sender_qq = msg[u'sender_qq']
        sender = msg[u'sender']
        type = msg[u'type']
        if type == u'group_message':
            message = message.replace(u'/', u'').strip()
        state = redis_store.get('state-' + sender_qq)
        if state is None:
            redis_store.set('state-' + sender_qq, 0)
            state = '0'

        if state == '0':
            if message == '学习':
                key = 'state-' + sender_qq
                tmp_state = int(redis_store.get(key))
                if not tmp_state:
                    redis_store.set(key, 1, 3600)
                else:
                    tmp_state = (tmp_state + 1) % 3
                    redis_store.set(key, tmp_state, 3600)
                return True, '@%s 输入问题：' % sender
            else:
                from model import Record
                question_answer = Record(message, sender_qq)
                question_answer.save()
                redis_store.incr('money-' + sender_qq)
                ids = id_from_redis(message)
                if not ids:
                    return True, '该问题还没人教呢！回复“学习”教教小D吧！'
                from model import QA
                qa_id = random.choice(ids)
                r = QA.query.filter_by(id=qa_id).first()
                if r is None:
                    return True, '该问题还没人教呢！回复“学习”教教小D吧！'
                return True, r.answer

        if state == '1':
            if message in ['学习', '帮助', '段子', '我的豆子']:
                return 'Tip:指令无法作为问题，请重新输入其他问题。'
            else:
                redis_store.set('question-' + sender_qq, message, 7200)
                key = 'state-' + sender_qq
                tmp_state = int(redis_store.get(key))
                if not tmp_state:
                    redis_store.set(key, 1, 3600)
                else:
                    tmp_state = (tmp_state + 1) % 3
                    redis_store.set(key, tmp_state, 3600)
                return True, '@%s 对于问题：%s\n输入您的答案:' % (sender, message)

        if state == '2':
            key = 'state-' + sender_qq
            tmp_state = int(redis_store.get(key))
            if not tmp_state:
                redis_store.set(key, 1, 3600)
            else:
                tmp_state = (tmp_state + 1) % 3
                redis_store.set(key, tmp_state, 3600)

            question = redis_store.get('question-' + sender_qq)
            if not question:
                return True, '@%s 呜...小D只知道你在一小时或者更久之前问过问题，但是忘记问题是什么了...' % sender
            else:
                from model import QA
                question_answer = QA(question, message, sender_qq)
                r = question_answer.save()
                redis_store.incr('money-' + sender_qq, 10)
                qa_id = r.id
                content_to_redis(question, qa_id)
                return True, '@%s 问题：%s\n答案：%s\n学习成功:)' % (sender, question, message.encode('utf-8'))


class Game:
    @staticmethod
    def query_coin(msg):
        message = msg[u'content']
        sender_qq = msg[u'sender_qq']
        if msg[u'type'] == u'group_message':
            message = message.replace(u'/', u'').strip()
        if message.lower() in ReplyStrings.query_coin:
            redis_store = Redis('localhost', 6379)
            key = 'money-' + sender_qq
            balance = redis_store.get(key)
            if balance is None:
                redis_store.set(key, 40)
                balance = '40'
            return True, ReplyStrings.coin_count % balance
        return False, u''

    @staticmethod
    def get_joke(msg):
        message = msg[u'content']
        gid = msg[u'gnumber']
        sender_qq = msg[u'sender_qq']
        sender = msg[u'sender']
        if msg[u'type'] == u'group_message':
            message = message.replace(u'/', u'').strip()
        if message.lower() in ReplyStrings.get_joke:
            redis_store = Redis('localhost', 6379)
            rank_key = 'joke_rank-' + gid
            rank = redis_store.get(rank_key)
            if not rank:
                redis_store.set(('joke_rank-' + gid), 40)
                rank = '40'
            joke_key = 'joke-' + rank
            joke = redis_store.get(joke_key)
            if not joke:
                from utils import fetch_jokes
                jokes = fetch_jokes()
                for index, joke in enumerate(jokes):
                    key = 'joke-' + str(index+1)
                    redis_store.set(key, joke, 79200)
                joke = redis_store.get('joke-1')
                rank = 40
            joke = joke.decode('utf-8')
            rank = int(rank)
            done = redis_store.get('read-'+gid)
            if done != '1':
                reductions = 1 if 31 <= rank <= 40 else 2 if 26 <= rank <= 30 else \
                    4 if 23 <= rank <= 25 else 8 if 21 <= rank <= 22 else 0

                key = 'money-' + sender_qq
                balance = redis_store.get(key)
                if balance is None:
                    redis_store.set(key, 40)
                    balance = 40
                else:
                    balance = int(balance)
                if balance < reductions:
                    return False, "@%s 你只有%s个豆子了,不够购买价值%s的段子了，快教教我吧，能赚豆子哦！" % \
                           (sender, balance, reductions)
                redis_store.decr(key, reductions)
                balance -= reductions
                if rank > 21:
                    fee = "付费"
                    num = rank - 20
                    tip = "[TIP: @%s 你购买了价值%s豆的段子，还剩下%s颗豆子]" % (sender, reductions, balance)
                elif rank == 21:
                    fee = "付费"
                    num = rank - 20
                    tip = "[TIP: @%s 你购买了价值%s豆的最后一餐付费段子，还剩下%s颗豆子，接下来的20个段子免费哦]" % \
                          (sender, reductions, balance)
                elif rank > 1:
                    fee = '免费'
                    num = rank
                    tip = "[TIP: 本条为免费段子~]"
                else:
                    fee = "免费"
                    num = rank
                    tip = "[TIP: 今天的段子讲完啦~不过可以重温讲给女票！(重温免费)]"
                    redis_store.set('read-'+gid, 1, 86400)
                content = "今日%s段子[%s]:\n%s\n%s" % (fee, str(num), joke, tip)
            else:
                tip = '\n[TIP:此条为免费重温段子，每日更新]'
                content = "今日段子[%s]:\n%s\n%s" % (str(rank), joke, tip)

            key = 'joke_rank-' + gid
            remain = redis_store.get(key)
            if not remain:
                redis_store.set(key, 40)
                remain = '40'
            remain = int(remain)
            if remain == 1:
                redis_store.set(key, 40)
            else:
                redis_store.decr(key)
            return True, content
        return False, u''


class PreDefinedMessage:
    @staticmethod
    def all(msg):
        this_function = sys._getframe().f_code.co_name
        used_functions = filter(lambda func: not (func.startswith('_') or func == this_function), dir(PreDefinedMessage))

        for func in used_functions:
            ret_msg = eval("PreDefinedMessage.%s" % func)(msg)
            if ret_msg and ret_msg != u'':
                return True, ret_msg
        return False, u''

    @staticmethod
    def about_page(msg):
        message = msg[u'content'].lower()
        if msg[u'type'] == u'group_message':
            message = message.replace(u'/', u'').strip()
        if message in ReplyStrings.about:
            return ReplyStrings.about_message

    @staticmethod
    def help_info(msg):
        message = msg[u'content'].lower()
        if msg[u'type'] == u'group_message':
            message = message.replace(u'/', u'').strip()
        if message in ReplyStrings.help:
            return ReplyStrings.user_help
