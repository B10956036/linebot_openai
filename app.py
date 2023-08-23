from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *

#======python的函數庫==========
import tempfile, os, re, pyimgur, requests, json
import datetime
import openai
import time
#======python的函數庫==========

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    #imgur的CLIENT_ID
    CLIENT_ID = "9a88f1e57a71f9b"
    PATH = "ch/image_0.jpg"      #要改檔名
    title = "image_0.jpg"        #要改檔名
    im = pyimgur.Imgur(CLIENT_ID)
    #上傳圖片並取得網址
    uploaded_image = im.upload_image(PATH, title=title)
    
    #上傳影片並取得網址
    import requests
    url = "https://api.imgur.com/3/upload"
    payload = {'album': 'ALBUMID', 'type': 'file', 'disable_audio': '0'}
    files = [('video', open('ch/output_1.mp4','rb'))]     #要改檔名
    headers = {'Authorization': 'Bearer BEARERTOKENHERE'}
    response = requests.request("POST", url, headers=headers, data = payload, files = files)
    if response.status_code == 200:
        # 解析 JSON 響應
        response_data = json.loads(response.text)
        # 獲取影片link
        link = response_data.get("data", {}).get("link")
        if link:
            print("Link:", link)
        else:
            print("Link not found in the response.")
    else:
        print("Request failed with status code:", response.status_code)
    #傳送訊息
    message = event.message.text
    if re.match('影片',message):
        video_message = VideoSendMessage(
            original_content_url = link,
            preview_image_url = uploaded_image.link
        )
        line_bot_api.reply_message(event.reply_token, video_message)
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(message))
          
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
