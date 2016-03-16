#!/usr/bin/env python
# coding:utf-8

import json, logging, requests, plugin
from config import Credentials, FuncSettings, ReplyStrings
from utils import MyDB


class BotManage:
    @staticmethod
    def help(message, sender_qq, sender, msg):
        help_msg = ReplyStrings.admin_welcome_message + u'%s!\n' % sender
        return help_msg + ReplyStrings.admin_help_command

    @staticmethod
    def top(message, sender_qq, sender, msg):
        db = MyDB()
        users = [ReplyStrings.user_line % (user[0], user[1]) for user in db.top_user()]
        return ReplyStrings.users_about % sender_qq + u"\n".join(users)

    @staticmethod
    def querytalk(message, sender_qq, sender, msg):
        db = MyDB()
        mt = msg[u'content'].split(' ')[0]
        content = msg[u'content'][(len(mt) + 1):]
        res = db.query_admin(content)
        lines = [ReplyStrings.talk_line % (line[0][:50], line[1][:50], line[2], str(line[5])) for line in res]
        return ReplyStrings.information_about % content + u"\n".join(lines)

    @staticmethod
    def deletetalk(message, sender_qq, sender, msg):
        db = MyDB()
        mt = msg[u'content'].split(' ')[0]
        content = msg[u'content'][(len(mt) + 1):]
        db.delete_talk(sender_qq, content, is_super=True)
        return ReplyStrings.delete_successful

    @staticmethod
    def blockuser(message, sender_qq, sender, msg):
        if len(message) == 0:
            return ReplyStrings.invalid_command
        db = MyDB()
        db.block_user(message[0])
        return ReplyStrings.block_user % message[0]

    @staticmethod
    def unblockuser(message, sender_qq, sender, msg):
        if len(message) == 0:
            return ReplyStrings.invalid_command
        db = MyDB()
        db.block_user(message[0], unblock=True)
        return ReplyStrings.unblock_user % message[0]

    @staticmethod
    def blockgroup(message, sender_qq, sender, msg):
        if len(message) == 0:
            return ReplyStrings.invalid_command
        db = MyDB()
        db.block_group(message[0])
        return ReplyStrings.block_group % message[0]

    @staticmethod
    def unblockgroup(message, sender_qq, sender, msg):
        if len(message) == 0:
            return ReplyStrings.invalid_command
        db = MyDB()
        db.block_group(message[0], unblock=True)
        return ReplyStrings.unblock_group % message[0]


class QQMessage:
    def __init__(self, raw):
        self.msg = json.loads(raw)
        self.msg[u'content'] = self.msg[u'content'].strip()
        logging.info(str(self.msg))

    @staticmethod
    def send_single_message(qid, msg):
        params = {"id": qid, "content": msg}
        url = "%s/openqq/send_message" % Credentials.comm_url
        res = json.loads(requests.post(url, params).content)
        logging.info("Send message:")
        logging.info(str(res))
        return res

    @staticmethod
    def send_group_message(gid, msg):
        params = {"gid": gid, "content": msg}
        url = "%s/openqq/send_group_message" % Credentials.comm_url
        res = json.loads(requests.post(url, params).content)
        logging.info("Send group message:")
        logging.info(str(res))
        return res

    @staticmethod
    def proc_discuss_message():
        logging.info("Not supported by the Mojo-API")

    def send_message(self, message, is_at_sender=True):
        if self.msg[u'type'] == u'message':
            self.send_single_message(self.msg[u'sender_id'], message)
        elif self.msg[u'type'] == u'group_message':
            if is_at_sender:
                self.send_group_message(self.msg[u'group_id'], u'@' + self.msg[u'sender'] + u' ' + message)
            else:
                self.send_group_message(self.msg[u'group_id'], message)
        else:
            logging.info("Cannot send message.")
            logging.info('Type:', self.msg[u'type'], "Message:", self.msg[u'content'])

    def proc_message(self):
        if self.msg[u'type'] == u'message':
            self.proc_single_message()
        elif self.msg[u'type'] == u'group_message':
            self.proc_group_message()
        else:
            logging.info('Not supported message')
            logging.info(str(self.msg))

    def proc_single_message(self):
        message = self.msg[u'content']
        sender_qq = self.msg[u'sender_qq']
        sender_nickname = self.msg[u'sender']

        # -----Basic management-----
        if message.startswith(u'!') or message.startswith(u'！') and sender_qq in FuncSettings.admin_list:
            ret = self.manage(self.msg)
            if ret != u'':
                self.send_message(ret)
                return

        # -----Extensions-----
        # plugin_list = dir(__import__("plugin"))
        plugin_list = plugin.all_func_single
        for f in plugin_list:
            if not f.startswith("_"):
                (if_end, msg) = eval('plugin.%s' % f)(self.msg)
                if msg != '':
                    self.send_message(msg)
                if if_end:
                    break

    def proc_group_message(self):
        # -----Extensions-----
        # plugin_list = dir(__import__("plugin"))
        plugin_list = plugin.all_func_group
        for f in plugin_list:
            if not f.startswith("_"):
                (if_end, msg) = eval('plugin.%s' % f)(self.msg)
                if msg != '':
                    self.send_message(msg)
                if if_end:
                    break

    def manage(self, msg):
        message = msg[u'content'][1:].split(u' ')
        sender_qq = msg[u'sender_qq']
        sender = msg[u'sender']
        func = {u'帮助': BotManage.help,
                u'HELP': BotManage.help,
                u'排行': BotManage.top,
                u'TOP': BotManage.top,
                u'查询对话': BotManage.querytalk,
                u'QUERYTALK': BotManage.querytalk,
                u'删除对话': BotManage.deletetalk,
                u'DELETETALK': BotManage.deletetalk,
                u'封禁用户': BotManage.blockuser,
                u'BLOCKUSER': BotManage.blockuser,
                u'封禁群': BotManage.blockgroup,
                u'BLOCKGROUP': BotManage.blockgroup,
                u'解封用户': BotManage.unblockuser,
                u'UNBLOCKUSER': BotManage.unblockuser,
                u'解封群': BotManage.unblockgroup,
                u'UNBLOCKGROUP': BotManage.unblockgroup,
                }
        if message[0].upper() in func.keys():
            return func[message[0].upper()](message[1:], sender_qq, sender, msg)
        return u""
