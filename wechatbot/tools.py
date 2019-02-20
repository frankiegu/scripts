import requests
import json
from hashlib import md5

url = 'http://openapi.tuling123.com/openapi/api/v2'
api_key = '52837f9663554bb081c301b743c481b7'

# 图灵机器人接口, 根据 text 内容回复, 用于识别的 userId 可选
def get_reply(text, userId='default'):
    if not text:
        return ''
    data = {
        "reqType":0,
        "perception": {
            "inputText": {
                "text": text
            },
        },
        "userInfo": {
            "apiKey": api_key,
            "userId": userId
        }
    }

    # 转为 json 字符串并发起请求
    resp = requests.post(url, data=json.dumps(data))

    # 网络和接口的错误排查
    if resp.status_code != 200:
        print('http err, code: {}'.format(resp.status_code))
        return ''
    res = resp.json()
    if 0 < res['intent']['code'] < 10000:
        print('tuling123 err, code: {}'.format(res['intent']['code']))
        return ''

    # 返回结果
    return res['results'][0]['values']['text']

# 根据用户名返回散列 id
def get_userid(name):
    return md5(name.encode()).hexdigest()