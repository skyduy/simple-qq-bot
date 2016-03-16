#!/usr/bin/env python
# coding:utf-8


class Credentials:
    qq = "2404865065"
    comm_url = "http://127.0.0.1:60001"
    database_account = ("bot", "bot")
    database = ("localhost", "qqbot")


class ReplyStrings:
    learn_commands = [u'学习', u'learn']
    success_messages = [u'真白学到了哦~\n', u'又学会了一句话~\n']
    not_found_messages = [u'啊哦,抱歉真白酱还不知道怎么回答...\n麻烦回复"学习"教教我吧!']
    waiting_answer = [u'请输入对应回答~']
    waiting_ask = [u'请输入对应问题']
    admin_welcome_message = u'欢迎您,管理员'
    admin_help_command = u'当前支持的管理指令:帮助、排行、查询、删除'
    say_no_to_blocked_words = u'不要说脏话啦~'
    feedback_user_submit = u"问题: %s\n回答: %s"
    block_user = u'用户%s已屏蔽'
    block_group = u'群%s已屏蔽'
    unblock_user = u'用户%s已解除屏蔽'
    unblock_group = u'群%s已解除屏蔽'
    invalid_command = u'指令格式不正确233333'
    about_message = u'This is an simple and open-source chat bot.\n' \
                    u'Developed by ihciah, inspired by StoneMoe and QQ515912540\n' \
                    u'Github repo: https://github.com/ihciah/simple-qq-bot\n' \
                    u'Contact c@ihc.im if you need some help:)'
    about = [u'about', u'关于', u'你是谁']
    lotty = [u'乐透', u'抽奖']
    insufficient_coin = u'啊哦...抽奖需要消耗%d个金币,但是你只有%d个\n(多和我聊天或者教我可以获得金币哦~'
    lotty_win = u'你抽中了%d个金币！人品好的话最高可赢%d哦'
    unknown_error = u'未知错误...'
    delete_success = u'相关词条已删除'
    qq = u'QQ'
    coin = u'金币'
    user_line = u'QQ%d 金币%d'
    talk_line = u'Q:%s\nA:%s\nUSER:%d\nTIME:%s'
    information_about = u'有关%s的所有消息:\n'
    users_about = u'有关用户%d的所有消息:\n'
    query_coin = [u'金币', u'硬币', u'查询金币', u'coin']
    coin_count = u'您当前有%d个硬币~\n和我聊天或教我可以增加金币哦!'
    help = [u'帮助', u'help']
    user_help = u'现在支持的指令: 学习、抽奖、金币、帮助'
    disable_group = [u'disable', u'关闭群聊', u'关闭群功能']
    enable_group = [u'enable', u'开启群聊', u'开启群功能']
    group_admin_info = [u'对不起,你不是群管理员,无法操作群设置哦', u'后台出错啦~找不到群信息...稍后再试试吧!',
                        u'后台出错啦~找不到用户信息...可能你是新加的成员?稍后再试试吧!']  # This is not random choice!
    group_enable = u'群功能已开启~@我就可以和我对话啦~'
    group_disable = u'群功能已关闭.\n只有群管理员@我并发送"开启群功能"后我才会参与对话哦~\拜~'


class FuncSettings:
    enable_group = True
    admin_list = [287280953]


class AdvancedSettings:
    remove_words_list = [u'。', u'？', u'\n', u'\r']  # Ignore some word
    blocked_words_list = [u'封禁词语']
    trunk_list = [u'a', u'ad', u'ag', u'an', u'r', u'rr', u'vi', u'vn']  # Refer to: https://gist.github.com/luw2007/6016931
    same_response_limit = 5


class Coin:
    learn = 10
    chat = 1
    lotty_max = 150
    lotty_avg = 25
    lotty_min = 2
    lotty_price = 30
    lotty_mu = 25
    lotty_sigma = 5
