from collections import OrderedDict
from datetime import datetime
from pprint import pprint

import re

import itchat
from itchat.content import TEXT, MAP, CARD, NOTE, SHARING, PICTURE, RECORDING, VOICE, ATTACHMENT, VIDEO, FRIENDS, SYSTEM

from tools import get_userid, get_reply

# 消息缓存字典与最大存储量
msgs = OrderedDict()
MAX_MSG_COUNT = 20

# 直接回复名单
reply_list = list()
# 自动回复
AUTO_REPLY = False

# 用户和群组的文本消息记录
@itchat.msg_register(TEXT, isFriendChat=True, isGroupChat=True)
def record_msg(msg):
    global AUTO_REPLY
    global reply_list
    msg_id = msg['MsgId']
    # 区分用户和群组
    is_user = msg['User']['MemberCount'] == 0
    tmp_msg = {
        # 本地时间戳
        'time': str(datetime.now()),
        # 来自于某用户, 或某群组的某用户
        'from': msg['User']['NickName'] if is_user else msg['User']['NickName'] + '_' + msg['ActualNickName'],
        # 用户 id 或 群组id, 用于直接发回
        'from_id': msg['User']['UserName'],
        # 消息内容
        'content': msg['Text']
    }
    pprint(tmp_msg)
    print()

    # 存至限长缓存字典
    msgs[msg_id] = tmp_msg
    if len(msgs) > MAX_MSG_COUNT:
        msgs.popitem(last=False)

    # 使用 `开启/关闭自动回复 群组名` 来这个格式来开关
    if 'Leo' in tmp_msg['from']:
        if '开启自动回复' in tmp_msg['content']:
            AUTO_REPLY = True
            reply_list.append(tmp_msg['content'].split(' ')[-1])
            print(reply_list)
            print(tmp_msg['content'])
        elif '关闭自动回复' in tmp_msg['content']:
            AUTO_REPLY = False
            reply_list.remove(tmp_msg['content'].split(' ')[-1])
            print(reply_list)
            print(tmp_msg['content'])
        return

    # 特定群组机器人回复
    if any(x in tmp_msg['from'] for x in reply_list) and AUTO_REPLY:
        user_id = get_userid(tmp_msg['from'])
        reply = get_reply(tmp_msg['content'], userId=user_id)
        if not reply:
            itchat.send('[AUTO] 回复失败' + str(tmp_msg), toUserName='filehelper')
        else:
            itchat.send('[AUTO] ' + reply, toUserName=tmp_msg['from_id'])


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
        if any(x in backed_msg['from'] for x in reply_list):
            itchat.send(tmp_msg, toUserName=backed_msg['from_id'])
        # 发到文件助手
        itchat.send(tmp_msg, toUserName='filehelper')


itchat.auto_login(hotReload=True)
itchat.send('login via itchat at {}'.format(datetime.now()), toUserName='filehelper')
itchat.run()