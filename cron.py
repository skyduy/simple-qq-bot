# coding: utf-8

"""
    ...
    ~~~~~~~~~~
    
    :author Skyduy <cuteuy@gmail.com> <http://skyduy.me>
    
"""
from __future__ import unicode_literals
import re
import requests
from redis import Redis
redis_store = Redis('localhost', 6379)


def fetch_jokes():
    page = 1
    results = []
    while len(results) < 40:
        url = 'http://www.qiushibaike.com/text/page/%s/' % page
        content = requests.get(url).content.decode('utf-8', 'ignore')
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


def reset():
    key1 = 'daily_active_user'
    active_user = redis_store.smembers(key1)
    for user in active_user:
        redis_store.set(('joke_rank-' + user), 40)
        redis_store.set(('read-' + user), 0)

    key2 = 'daily_active_group'
    active_group = redis_store.smembers(key2)
    for group in active_group:
        redis_store.set(('joke_rank-' + group), 40)
        redis_store.set(('read-' + group), 0)

    redis_store.delete(key)

if __name__ == '__main__':
    jokes = fetch_jokes()
    for index, joke in enumerate(jokes):
        key = 'joke-' + str(index+1)
        redis_store.set(key, joke, 90000)
    reset()
