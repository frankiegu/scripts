from collections import OrderedDict
from datetime import datetime
from pprint import pprint

import re

import itchat
from itchat.content import TEXT, MAP, CARD, NOTE, SHARING, PICTURE, RECORDING, VOICE, ATTACHMENT, VIDEO, FRIENDS, SYSTEM

# 消息缓存字典与最大存储量
msgs = OrderedDict()
MAX_MSG_COUNT = 20

# 直接回复名单
reply_list = ['卓卓', '天王', '我给大家吐个槽']

# 用户和群组的文本消息记录
@itchat.msg_register(TEXT, isFriendChat=True, isGroupChat=True)
def record_msg(msg):
    pprint(msg['Content'])
    msg_id = msg['MsgId']
    # 区分用户和群组
    is_user = msg['User']['MemberCount'] == 0
    tmp_msg = {
        'time': str(datetime.now()),
        'from': msg['User']['NickName'] if is_user else msg['User']['NickName'] + '_' + msg['ActualNickName'],
        'from_id': msg['User']['UserName'],
        'content': msg['Text']
    }
    pprint(tmp_msg)
    msgs[msg_id] = tmp_msg
    if len(msgs) > MAX_MSG_COUNT:
        msgs.popitem(last=False)


# 撤回NOTE时查找id并在缓存字典中取出
@itchat.msg_register(NOTE, isFriendChat=True, isGroupChat=True)
def send_backed_msg(msg):
    if re.search(r"\<\!\[CDATA\[.*撤回了一条消息\]\]\>", msg['Content']) is not None:
        backed_msg_id = re.search("\<msgid\>(.*?)\<\/msgid\>", msg['Content']).group(1)
        backed_msg = msgs.get(backed_msg_id, {})
        # 有可能发生消息太多而被挤出缓存的情况
        if not backed_msg:
            tmp_msg = '检测到有消息撤回, 但未在缓存中找到'
        else:
            tmp_msg = '{} 于 {} 撤回了一条文本消息: \n{}'.format(
                    backed_msg['from'],
                    backed_msg['time'],
                    backed_msg['content'],
                )
        # 匹配直接回复名单
        if any(x in backed_msg['from'] for x in reply_list) :
            itchat.send(tmp_msg, toUserName=backed_msg['from_id'])
        # 发到文件助手
        itchat.send(tmp_msg, toUserName='filehelper')


itchat.auto_login(hotReload=True)
itchat.send('login via itchat at {}'.format(datetime.now()), toUserName='filehelper')
itchat.run()