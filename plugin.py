#!/usr/bin/env python
# coding:utf-8

# Version 1:
# In this file you can write any function to process message.
# def test(msg):
#     return (if_end,ret_msg)
# If if_end == True, all other functions left will not continue to execute.
# If you want to define some functions only used by yourself, you can name it as "_xxx"

# Version 2:
# Register all functions used in `all_func`

from utils import Memcache, MyDB, UserMod, TuringBot
from config import ReplyStrings, AdvancedSettings, Coin, FuncSettings
import random, logging, sys

all_func_single = ['Common.blank_check', 'Common.black_list', 'Common.block_words_check', 'Game.query_coin',
                   'Game.lotty', 'PreDefinedMessage.all', 'Common.chat'
                   ]
all_func_group = ['GroupChat.check_at_me', 'Common.blank_check', 'Common.black_list', 'GroupChat.disable_group',
                  'Game.lotty', 'Game.query_coin', 'PreDefinedMessage.all', 'Common.block_words_check', 'Common.chat'
                  ]


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
    def black_list(msg):
        sender_qq = msg[u'sender_qq']
        mem = Memcache()
        if not mem.check_block_user(sender_qq):
            return True, u""
        return False, u""

    @staticmethod
    def block_words_check(msg):
        message = msg[u'content']
        for word in AdvancedSettings.blocked_words_list:
            if message.find(word) != -1:
                return True, ReplyStrings.say_no_to_blocked_words
        return False, u""

    @staticmethod
    def chat(msg):
        mem = Memcache()
        db = MyDB()
        message = msg[u'content']
        sender_qq = msg[u'sender_qq']
        sender = msg[u'sender']
        type = msg[u'type']
        gid = 0
        if type == u'group_message':
            my_name = msg[u'receiver']
            gid = msg[u'gnumber']
            message = message.replace(u'@' + my_name, u'').strip()

        # ----Check if user send too many same content----
        if not mem.check_last_chat_same(sender_qq, message):
            return True, u""

        history_state, history = mem.check_history(sender_qq, gid=gid)
        # ----In learning mode----
        if history_state is not None:
            if history_state == mem.WAIT_ANSWER:
                mem.clear_state(sender_qq, gid=gid)
                db.insert_chat(history, message, sender_qq, gid=gid)
                success_message = random.choice(ReplyStrings.success_messages)
                success_message += ReplyStrings.feedback_user_submit % (history, message)
                db.mod_coin(sender_qq, Coin.learn)
                return True, success_message
            else:
                mem.set_before_answer(sender_qq, message, gid=gid)
                success_message = random.choice(ReplyStrings.waiting_answer)
                return True, success_message

        # ----Enter learning mode----
        if message.lower() in ReplyStrings.learn_commands:
            mem.set_before_ask(sender_qq, gid=gid)
            success_message = random.choice(ReplyStrings.waiting_ask)
            return True, success_message

        # ----Normal chat mode----
        answer = db.query_question(message)
        logging.info(answer)
        if answer is None:
            if FuncSettings.turing_robot_enabled and AdvancedSettings.turing_robot_api:
                turing_bot = TuringBot(message, sender_qq)
                fail_message = turing_bot.proc_message()
                if fail_message == u'':
                    fail_message = random.choice(ReplyStrings.not_found_messages)
            else:
                fail_message = random.choice(ReplyStrings.not_found_messages)
            return True, fail_message
        db.mod_coin(sender_qq, Coin.chat)
        return True, answer[1]


class Game:
    @staticmethod
    def query_coin(msg):
        message = msg[u'content']
        sender_qq = msg[u'sender_qq']
        db = MyDB()
        if msg[u'type'] == u'group_message':
            my_name = msg[u'receiver']
            message = message.replace(u'@' + my_name, u'').strip()
        if message.lower() in ReplyStrings.query_coin:
            user = db.get_user_info(sender_qq)
            if not user:
                return True, ReplyStrings.unknown_error
            coin = user[1]
            return True, ReplyStrings.coin_count % coin
        return False, u''

    @staticmethod
    def lotty(msg):
        message = msg[u'content']
        sender_qq = msg[u'sender_qq']
        db = MyDB()
        if msg[u'type'] == u'group_message':
            my_name = msg[u'receiver']
            message = message.replace(u'@' + my_name, u'').strip()
        if message in ReplyStrings.lotty:
            user = db.get_user_info(sender_qq)
            if not user:
                return True, ReplyStrings.unknown_error
            coin = user[1]
            if coin < Coin.lotty_price:
                return True, ReplyStrings.insufficient_coin % (Coin.lotty_price, coin)
            got = int(random.normalvariate(Coin.lotty_mu, Coin.lotty_sigma))
            got = max(got, Coin.lotty_min)
            got = min(got, Coin.lotty_max)
            db.mod_coin(sender_qq, got)
            return True, ReplyStrings.lotty_win % (got, Coin.lotty_max)
        return False, u""


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
            my_name = msg[u'receiver']
            message = message.replace(u'@' + my_name, u'').strip()
        if message in ReplyStrings.about:
            return ReplyStrings.about_message

    @staticmethod
    def help_info(msg):
        message = msg[u'content'].lower()
        if msg[u'type'] == u'group_message':
            my_name = msg[u'receiver']
            message = message.replace(u'@' + my_name, u'').strip()
        if message in ReplyStrings.help:
            return ReplyStrings.user_help


class SingleChat:
    @staticmethod
    def test(msg):
        return False, u''


class GroupChat:
    @staticmethod
    def check_at_me(msg):
        message = msg[u'content']
        sender_qq = msg[u'sender_qq']
        sender = msg[u'sender']
        my_name = msg[u'receiver']
        if message.find(u'@' + my_name) == -1:
            return True, u''
        return False, u''

    @staticmethod
    def disable_group(msg):
        message = msg[u'content']
        sender_qq = msg[u'sender_qq']
        sender = msg[u'sender']
        gid = msg[u'gnumber']
        my_name = msg[u'receiver']
        message = message.replace(u'@' + my_name, u'').strip()
        if message in ReplyStrings.disable_group or message in ReplyStrings.enable_group:
            u = UserMod()
            r = u.check_group_admin(gid, sender_qq)
            if r == u.IS_ADMIN:
                db = MyDB()
                if message in ReplyStrings.enable_group:
                    db.disable_group(gid, False)
                    return True, ReplyStrings.group_enable
                else:
                    db.disable_group(gid, True)
                    return True, ReplyStrings.group_disable
            return True, ReplyStrings.group_admin_info[r]
        mem = Memcache()
        if not mem.check_disable_group(gid):
            return True, u''
        return False, u''
