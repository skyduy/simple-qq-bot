#!/usr/bin/env python
# coding:utf-8
from __future__ import unicode_literals
import requests
import json
import re
import urllib2
import collections
from config import Credentials
import redis
import jieba
from collections import Counter
jieba.initialize()
redis_store = redis.Redis('localhost', 6379, db=1)


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


def id_from_redis(content):
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

    keys = redis_store.keys()
    kv = {}
    for key in keys:
        questions = redis_store.hgetall(key)
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


def content_to_redis(questions, qa_id):
    return redis_store.hmset(qa_id, Counter(jieba.cut(questions)))


def convert(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data


def fetch_jokes():
    page = 1
    results = []
    while len(results) < 40:
        url = 'http://www.qiushibaike.com/text/page/%s/' % page
        headers = {
            'UserHost': 'www.qiushibaike.com',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/42.0.2311.90 Safari/537.36',
            'DNT': 1,
            'Accept-Encoding': 'unicode, utf-8, gb2312, gbk',
            'Accept-Language': 'zh-CN,zh;q=0.8',
        }
        request = urllib2.Request(url, headers=convert(headers))
        response = urllib2.urlopen(request)
        content = response.read().decode('utf-8', 'ignore')
        pattern = re.compile(
            '<div class="content">(.*?)</div>',
            re.S
        )
        items = re.findall(pattern, content)
        for item in items:
            joke = item.strip().replace('<br/>', '\n').replace('&quot;', '"')
            results.append(joke)
        page += 1
    return results
