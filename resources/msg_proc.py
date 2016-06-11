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

    def proc_message(self):
        if self.msg[u'type'] == u'group_message':
            processor = MessageProcessor(self.msg)
            reply = processor.process()
            if reply is not None:
                self.send_group_message(reply)
        else:
            logging.info('Not supported message，the type is:  %s' % self.msg[u'type'])

    def send_group_message(self, message):
        gid, msg = self.msg[u'group_id'], u'@' + self.msg[u'sender'] + u' ' + message
        params = {"gid": gid, "content": msg}
        url = "%s/openqq/send_group_message" % comm_url
        res = json.loads(requests.post(url, params).content)
        logging.info("Send group message:")
        logging.info(str(res))
