'''

슬랙 봇 프로젝트

> 구조 :
                        ┏ 파이썬 코드 ┓
    이벤트(호출) ┬ request - 처리 - Slacker - 출력
    일반 입력    ┘

> 이벤트
    slack의 event api 사용
    hear() 함수에서 처리

> 텍스트 입력

출력 : Slacker

'''
# -*- coding: utf-8 -*-
import time
from flask import Flask, request, make_response
from slacker import Slacker
import websocket
import re
from threading import Thread
import requests
from bs4 import BeautifulSoup
import json
import urllib.request

app = Flask(__name__)

slack_token = "secret"
slack_client_id = "secret"
slack_client_secret = "secret"
slack_verification = "secret"
slack = Slacker(slack_token)

caller = []
channel_list = []

def get_name(id):
    user = slack.users.info(id)
    name = user.body["user"]["profile"]["display_name"]
    return name


def check_user(user, msg):
    if 'user' in msg and 'text' in msg:
        if user == msg['user']:
            return True
    return False


# 앨리스 호출
def call_elice(event):
    res = slack.rtm.connect()
    endpoint = res.body['url']
    ws = websocket.create_connection(endpoint)

    slack.chat.post_message(event['channel'], "부르셨어요, {}님? \n `응` / `아니`".format(get_name(event['user'])))
    while True:
        msg = json.loads(ws.recv())
        if check_user(event['user'], msg):
            name = get_name(msg['user'])
            channel = event["channel"]
            re_yes = re.compile('((yes))|(응)|(ㅇ)+', re.I)
            re_no = re.compile('((no)|(아니))|(ㄴ)+', re.I)
            if msg['text'] == '<@UEXBA7A0K>':
                slack.chat.post_message(channel, "저 여기 있어요~")
            elif re_yes.match(msg['text']):
                elice(ws, event, msg)
                break;
            elif re_no.match(msg['text']):
                slack.chat.post_message(channel, "필요할때 불러주세요:wink:".format(name))
                break;

            else:
                slack.chat.post_message(channel, "`응` / `아니`로 대답해주세요")
    ws.close()


#앨리스 실행
def elice(ws, event, msg):
    name = get_name(msg['user'])
    channel = event["channel"]
    slack.chat.post_message(channel, "안녕하세요! {}님\n"
                                     "필요하신 기능을 말씀해주세요!\n"
                                     "`넌 누구니?`/`맞춤법검사해줘`/`문법경찰출동`/`번역해줘`/`잘가`".format(name))
    hello_c = 0
    while True:
        msg = json.loads(ws.recv())
        if check_user(event['user'], msg):
            msg = msg['text']
            msg = msg.replace(' ', '').strip()
            if msg == '<@UEXBA7A0K>':
                slack.chat.post_message(channel, "저 여기 있어요~")
            elif '안녕' in msg:
                hi(channel, hello_c, name)
                hello_c +=1
            elif '누구' in msg:
                who_is_elice(channel)
            elif '검사' in msg:
                lets_check(ws, channel, name, event['user'])
            elif '경찰' in msg:
                police(channel)
            elif '번역' in msg:
                trans(ws, channel, name, event['user'])
            elif '잘가' in msg:
                slack.chat.post_message(channel, "필요할때 언제든 다시 불러주세요 :wink: 찡긋찡긋")
                break;
            else:
                slack.chat.post_message(channel, "다시 말해주세요\n")
            slack.chat.post_message(channel,"\n\n" 
                                        "이제 뭘 할까요?\n"
                                         "`넌 누구니?`/`맞춤법검사해줘`/`문법경찰출동`/`번역해줘`/`잘가`")
        else :
            if 'user' in msg and 'text' in msg :
                if event['user'] != msg['user']:
                    slack.chat.post_message(channel, "{}님이랑 작업중이에요! 끝날때까지 기다려주세요!".format(name))

def hi(channel, hello_count, name):
    if hello_count == 0:
        slack.chat.post_message(channel, "하하, {}님! 정말정말 반가워요!:heart_eyes:".format(name))
    elif hello_count == 1:
        slack.chat.post_message(channel, "음? 우리 이미 인사하지 않았었나요?:sweat_smile:")
    elif hello_count == 2:
        slack.chat.post_message(channel, "음? 우리 이미 인사하지 않았었나요?:thinking_face:")
    elif hello_count == 3:
        slack.chat.post_message(channel, "저도 나름 바쁜 봇이에요! 이제 대답 안할거에요!:expressionless:")
    elif hello_count == 10:
        slack.chat.post_message(channel, "ㅎㅎ.. 근성은 인정해드릴게요, 이제 진짜 끝이에요!:kissing_heart:")
    else:
        pass


def who_is_elice(channel):
    slack.chat.post_message(channel, "```저는 앨리스입니다!!\n"
                                     "한국말을 잘 할 수 있게 도와주는 봇이에요\n"
                                     "저를 유용하게 이용해 주셨으면 좋겠네요!\n"
                                     "근데 우리, 인사는 했나요..?```\n")


def lets_check(ws, channel, name, user_id):
    slack.chat.post_message(channel, """지금부터 {}님의 입력을 받을게요!
    입력을 다 하셨으면 {}이라고 말씀해주세요!""".format(name, "<@UEXBA7A0K>"))
    user_text=[]
    while True:
        msg = json.loads(ws.recv())
        if check_user(user_id, msg):
            msg = msg['text']
            if "<@UEXBA7A0K>" in msg:
                user_text.append(msg[:msg.find('<@UEXBA7A0K>')])
                slack.chat.post_message(channel, "입력받았습니다, 잠시만 기다려주세요!")
                break;
            user_text.append(msg)
        elif 'user' in msg and 'text' in msg:
                slack.chat.post_message(channel, "{}님이랑 문법검사중이에요! 끝날때까지 기다려주세요!".format(name))
    befo = '\n'.join(user_text)
    after = spellCorrection(befo)

    slack.chat.post_message(channel, """```수정된 내용은 다음과 같습니다.
    ==수정 전==
    {}
    ==수정 후==
    {}
    ```""".format(befo, after))


def police(channel):
    slack.chat.post_message(channel, "경찰 출동!:rotating_light:")
    time.sleep(0.5)
    slack.chat.post_message(channel, ".")
    time.sleep(0.5)
    slack.chat.post_message(channel, ".")
    time.sleep(0.5)
    slack.chat.post_message(channel, ".")
    time.sleep(0.5)
    slack.chat.post_message(channel, "죄송해요, 아직 기능이 없어요ㅠ")


def spellCorrection(q):
    datas = {'text1': q}
    post_result = requests.post("http://speller.cs.pusan.ac.kr/PnuWebSpeller/lib/check.asp", data=datas)
    if post_result.status_code != 200 :
        return """지금 번역기에 문제가 있어서 검사가 안될것같아요ㅠ
        조금 있다가 다시 시도해주세요!"""
    res = post_result.text
    soup = BeautifulSoup(res, "html.parser")
    tables = soup.find_all("table", class_="tableErrCorrect")
    replaced_list=[]
    for table in tables:
        err = table.find("td", class_="tdErrWord").get_text()
        cor = table.find("td", class_="tdReplace").get_text()
        replaced_list.append([err, cor])
    after = q;
    mody_list = []
    for replace_word in replaced_list:
        after = after.replace(replace_word[0], replace_word[1])
        mody_list.append(replace_word[0]+" -> "+replace_word[1])
    after+= "\n"+'\n'.join(mody_list)
    return after


def trans(ws, channel, name, user_id):
    slack.chat.post_message(channel, """번역하고 싶은 말을 입력해주세요!
입력이 끝나셨으면 {}이라고 말씀해주세요!""".format("<@UEXBA7A0K>"))
    user_text=[]
    while True:
        msg = json.loads(ws.recv())
        if check_user(user_id, msg):
            msg = msg['text']
            if "<@UEXBA7A0K>" in msg:
                user_text.append(msg[:msg.find('<@UEXBA7A0K>')])
                slack.chat.post_message(channel, "입력받았습니다, 잠시만 기다려주세요!")
                break;
            user_text.append(msg)
        elif 'user' in msg and 'text' in msg:
                slack.chat.post_message(channel, "{}님이랑 번역중이에요! 끝날때까지 기다려주세요!".format(name))
    from_text = '\n'.join(user_text)

    slack.chat.post_message(channel, "```{}```".format(trans_naver('\n'.join(user_text))))


def trans_naver(q):
    encText = urllib.parse.quote(q)
    client_id = "secret"
    client_secret = "secret"
    #언어감지
    data = "query=" + encText
    url = "https://openapi.naver.com/v1/papago/detectLangs"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()
    from_type = 'ko'
    to_type = 'en'
    if (rescode == 200):
        response_body = response.read()
        res = json.loads(response_body.decode('utf-8'))
        from_type = res['langCode']
        if from_type == 'en':
            to_type = 'ko'
        elif from_type != 'ko':
            return "번역이 안되는 언어입니다! 죄송해요!"
    else:
        print("Error Code:" + rescode)
        return "Error Code:" + rescode
    #번역
    data = "source={}&target={}&text={}".format(from_type, to_type, encText)
    url = "https://openapi.naver.com/v1/papago/n2mt"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()

    #번역 결과
    if(rescode==200):
        response_body = response.read()
        res = json.loads(response_body.decode('utf-8'))
        from_type = res['message']['result']['srcLangType']
        to_type = res['message']['result']['tarLangType']
        translated = res['message']['result']['translatedText']
        return "== 원문 ==\n{}\n== {} -> {} ==\n{}""".format(q, from_type, to_type, translated)
    else:
        print("Error Code:" + rescode)
        return rescode


# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_response):
    global caller, channel_list
    if event_type == "app_mention":
        channel = slack_response["event"]["channel"]
        if slack_response["event"]["channel"] in channel_list:
            pass
        caller.append(slack_response)
        channel_list.append(channel)
        return make_response("App mention message has been sent", 200, )


    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/event", methods=["GET", "POST"])
def hears():
    slack_response = json.loads(request.data)

    if "challenge" in slack_response:
        return make_response(slack_response["challenge"], 200, {"content_type":"application/json"})

    if slack_verification != slack_response.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_response["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_response:
        event_type = slack_response["event"]["type"]
        return _event_handler(event_type, slack_response)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>앨리스 서버에용! 어떻게 알고 오셨을까?ㅎ_ㅎ</h1>"


def proc(slack_response):
    call_elice(slack_response["event"])


def interact():
    while True:
        if len(caller) > 0:
            res = caller.pop()
            proc(res)
            channel_list.remove(res["event"]["channel"])


if __name__ == '__main__':
    p = Thread(target=interact)
    p.start()
    app.run('127.0.0.1', port=5000)
    p.join()

