# coding: utf-8
import re
from collections import defaultdict


class BSFilter(object):

    """Filter Messages from keywords

    Use Back Sorted Mapping to reduce replacement times

    >>> f = BSFilter()
    >>> f.add("sexy")
    >>> f.filter("hello sexy baby")
    hello **** baby
    """

    def __init__(self, path):
        self.keywords = []
        self.kwsets = set([])
        self.bsdict = defaultdict(set)
        self.pat_en = re.compile(r'^[0-9a-zA-Z]+$')  # english phrase or not
        self.parse(path)

    def add(self, keyword):
        if not isinstance(keyword, unicode):
            keyword = keyword.decode('utf-8')
        keyword = keyword.lower()
        if keyword not in self.kwsets:
            self.keywords.append(keyword)
            self.kwsets.add(keyword)
            index = len(self.keywords) - 1
            for word in keyword.split():
                if self.pat_en.search(word):
                    self.bsdict[word].add(index)
                else:
                    for char in word:
                        self.bsdict[char].add(index)

    def parse(self, path):
        with open(path, "r") as f:
            for keyword in f:
                self.add(keyword.strip())

    def filter(self, message, repl="*"):
        if not isinstance(message, unicode):
            message = message.decode('utf-8')
        message = message.lower()
        for word in message.split():
            if self.pat_en.search(word):
                for index in self.bsdict[word]:
                    message = message.replace(self.keywords[index], repl)
            else:
                for char in word:
                    for index in self.bsdict[char]:
                        message = message.replace(self.keywords[index], repl)
        return message


class DFAFilter(object):

    """
        Filter Messages from keywords

        Use DFA to keep algorithm perform constantly

        >>> f = DFAFilter()
        >>> f.add("sexy")
        >>> f.filter("hello sexy baby")
        hello **** baby
    """

    def __init__(self, path):
        self.keyword_chains = {}
        self.delimit = '\x00'
        self.parse(path)

    def add(self, keyword):
        if not isinstance(keyword, unicode):
            keyword = keyword.decode('utf-8')
        keyword = keyword.lower()
        chars = keyword.strip()
        if not chars:
            return
        level = self.keyword_chains
        for i in range(len(chars)):
            if chars[i] in level:
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):
                    # 防止添加'123\x00AA'这样的过滤词出现错误,但又不影响对该词的过滤,因为前面肯定有了敏感词'123'了
                    break
                for j in range(i, len(chars)):
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: 0}
                break
        if i == len(chars) - 1:
            level[self.delimit] = 0

    def parse(self, path):
        with open(path) as f:
            for keyword in f:
                self.add(keyword.strip())

    def included_in(self, message):
        if not isinstance(message, unicode):
            message = message.decode('utf-8')
        message = message.lower()
        for start in xrange(len(message)):
            level = self.keyword_chains
            for char in message[start:]:
                if char in level:
                    if self.delimit in level[char]:
                        return True
                    else:
                        level = level[char]
                else:
                    break
        return False

    def filter(self, message, repl="*"):
        if not isinstance(message, unicode):
            message = message.decode('utf-8')
        message = message.lower()
        ret = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        ret.append(repl * step_ins)
                        start += step_ins - 1
                        break
                else:
                    ret.append(message[start])
                    break
            else:
                ret.append(message[start])
            start += 1

        return ''.join(ret)


# class DFATree(object):
#     class Node(object):
#         def __init__(self):
#             self.children = None
#
#     def __init__(self):
#         self.root = self.Node()
#
#     def add(self, keyword):
#         if not isinstance(keyword, unicode):
#             keyword = keyword.decode('utf-8')
#         keyword = keyword.lower()
#         node = self.root
#         end_index = len(keyword) - 1
#         for i in xrange(len(keyword)):
#             if node.children is None:
#                 node.children = {}
#                 if i != end_index:
#                     node.children[keyword[i]] = (self.Node(), False)
#                 else:
#                     node.children[keyword[i]] = (self.Node(), True)
#             elif keyword[i] not in node.children:
#                 if i != end_index:
#                     node.children[keyword[i]] = (self.Node(), False)
#                 else:
#                     node.children[keyword[i]] = (self.Node(), True)
#             else:
#                 if i == end_index:
#                     key, flag = node.children[keyword[i]]
#                     node.children[keyword[i]] = (key, True)
#             node = node.children[keyword[i]][0]
#
#     def parse(self, path):
#         with open(path) as f:
#             for keyword in f:
#                 self.add(keyword.strip())
#
#     def included_in(self, message):
#         root = self.root
#         message_len = len(message)
#         for i in xrange(message_len):
#             node = root
#             j = i
#             while j < message_len and node.children is not None and message[j] in node.children:
#                 node, end_flag = node.children[message[j]]
#                 if end_flag is True:
#                     return True
#                 j += 1
#         return False
#
#     def filter(self, message):
#         new_message = []
#         root = self.root
#         msg_len = len(message)
#         i = 0
#         back_continue = False
#         while i < msg_len:
#             node = root
#             j = i
#             while j < msg_len and node.children is not None and message[j] in node.children:
#                 node, flag = node.children[message[j]]
#                 if flag is True:
#                     new_message.append(u'*'*(j-i+1))
#                     i = j + 1
#                     back_continue = True
#                     break
#                 j += 1
#             if back_continue:
#                 back_continue = False
#                 continue
#             new_message.append(message[i])
#             i += 1
#         return ''.join(new_message)


