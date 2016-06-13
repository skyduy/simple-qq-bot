#!/usr/bin/env python
# coding:utf-8

import json
import logging
import requests

from utils import MessageProcessor
from config import comm_url


class QQMessage:
    def __init__(self, raw):
        self.msg = json.loads(raw)
        self.msg[u'content'] = self.msg[u'content'].strip()
        self.msg_type = self.msg[u'type']
        self.gid = self.msg[u'group_id']

    def proc_message(self):
        print self
        if self.msg_type == u'group_message':
            processor = MessageProcessor(self.msg)
            reply = processor.process()
            if reply is not None:
                self.send_message(reply, too_long=processor.too_long)
        else:
            logging.info(u'Not supported message，the type is:  %s' % self.msg_type)

    def send_message(self, message, too_long=False):
        msg = u'@' + self.msg[u'sender'] + u' ' + message
        if too_long:
            msg += u'\n[Tip: 消息太长，部分可能被截取]'
        params = {"gid": self.gid, "content": msg}
        url = "%s/openqq/send_group_message" % comm_url
        requests.post(url, params)
