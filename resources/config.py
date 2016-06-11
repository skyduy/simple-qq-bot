#!/usr/bin/env python
# coding:utf-8


MYSQL_HOST = 'localhost'
MYSQL_PORT = '3306'
MYSQL_USER = 'username'  # your username
MYSQL_PASS = 'password'  # your password
MYSQL_DB = 'wechat'


comm_url = "http://127.0.0.1:60001"
filter_path = 'path/to/simple-qq-bot/resources/text_filter/keywords'  # 绝对路径


class ReplyStrings(object):
    disable_group = [u'disable', u'关闭群聊', u'关闭群功能', u'关掉群功能']
    group_admin_info = [u'对不起,你不是群管理员,无法操作群设置哦', u'后台出错啦~找不到群信息...稍后再试试吧!',
                        u'后台出错啦~找不到用户信息...可能你是新加的成员?稍后再试试吧!']  # This is not random choice!
    group_disable = u'群功能已关闭.\n群管理员发送"/开启群功能"后我就会回来的 :)'

    enable_group = [u'enable', u'开启群聊', u'开启群功能', u'打开群功能']
    group_enable = u'群功能已开启~ 支持回复\'/\'开头的信息~'

    about = [u'about', u'关于', u'你是谁']
    about_message = u'这是一个开源的并没有什么技术含量的聊天机器人\n' \
                    u'你可以在这里找到源代码: https://github.com/skyduy/simple-qq-bot\n' \
                    u'如果你在搭建或继续开发的过程中遇到什么问题,可以直接发邮件到 i@skyduy.me'

    help = [u'帮助']
    user_help = u'\n/学习\n/段子\n/豆子\n/排行\n/乐透\n/帮助\n发送指令消息即可执行。'

    query_coin = [u'我的豆子', u'余额', u'豆子']
    get_joke = [u'段子', u'笑话']
    get_ranking = [u'排行', u'排行榜']
    lotto = [u'乐透', u'抽奖']
    learn = [u'学习']

    instruction = learn
