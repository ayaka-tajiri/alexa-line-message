# -*- coding: utf-8 -*-

import logging
import datetime

from boto3.session import Session

from linebot import (
    LineBotApi, WebhookHandler, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError,LineBotApiError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,ButtonsTemplate,URITemplateAction,LocationSendMessage
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

region = "ap-northeast-1"
session = Session(
    region_name=region
)
dynamodb = session.resource('dynamodb')

table = dynamodb.Table('LineMassageTable')


def line(event, context):

    # イベントデータの表示
    logger.info('headers:' + str(event['headers']['X-Line-Signature']))
    logger.info('body:' + str(event['body']))

    # リクエスト本体と、X-LINE-Signatureヘッダを取出す
    body = event['body']
    signature = event['headers']['X-Line-Signature']

    # Channel Secretを使って入力が正しいかを確認する
    secret = 'ここにシークレットを入力'
    parser = WebhookParser(secret)

    try:
        events = parser.parse(body,signature)
    except InvalidSignatureError:
        logger.error('InvalidSignatureError')
        return {"stautsCode" : 400,"body" : ""};

    # LineBotAPIオブジェクトを作成する
    token = 'ここにトークンを入力'
    line_bot_api = LineBotApi(token)

    try:
        events = parser.parse(body,signature)
    except InvalidSignatureError:
        return {"stautsCode" : 400,"body" : ""};

    # for event in events:
    logger.info('events:' + str(events))

    # DBにメッセージを保存
    user_id = events[0].source.user_id
    line_message = events[0].message.text

    put_response = table.put_item(
        Item={
            'timestamp': int(datetime.datetime.now().timestamp()),
            'id': user_id,
            'message': line_message
        }
    )

    reply_token = events[0].reply_token
    success_message = TextSendMessage(
        text='メッセージを登録しました！\n\n'
             'メッセージを修正する場合はもう一度メッセージを送ってください\n\n'
             'メッセージにはあなたのお名前がわかるようにしてください'
    )

    try:
        line_bot_api.reply_message(reply_token,success_message)
    except LineBotApiError as e:
        print(e.status_code)
        print(e.error.message)
        print(e.error.details)

    return {"stautsCode" : 200,"body" : "OK"};
