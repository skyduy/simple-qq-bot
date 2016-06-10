#!/usr/bin/env python
# coding:utf-8

import json
import logging
import requests
import plugin
from config import Credentials


class QQMessage:
    def __init__(self, raw):
        self.msg = json.loads(raw)
        self.msg[u'content'] = self.msg[u'content'].strip()
        logging.info(str(self.msg))

    @staticmethod
    def send_group_message(gid, msg):
        params = {"gid": gid, "content": msg}
        url = "%s/openqq/send_group_message" % Credentials.comm_url
        res = json.loads(requests.post(url, params).content)
        logging.info("Send group message:")
        logging.info(str(res))
        return res

    def proc_message(self):
        if self.msg[u'type'] == u'group_message':
            self.proc_group_message()
        else:
            logging.info('Not supported message，the type is:  %s' % self.msg[u'type'])
            logging.info(str(self.msg))

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

    def send_message(self, message):
        if self.msg[u'type'] == u'group_message':
            self.send_group_message(self.msg[u'group_id'], u'@' + self.msg[u'sender'] + u' ' + message)
        else:
            logging.info("Cannot send message.")
            logging.info('Type:', self.msg[u'type'], "Message:", self.msg[u'content'])
