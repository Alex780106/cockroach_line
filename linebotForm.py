from flask import Flask
app = Flask(__name__)

from flask import request, abort
from flask_sqlalchemy import SQLAlchemy
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

line_bot_api = LineBotApi('U1kChmbPoKBBA9wIU93e8pFSPpbCQN0+29DViLGSHHFu6zurME8j4HYG7JbpgQZrJO1FVuJctYKzCTiNbcyVV62bHFboNvIGuEp4+1/0qZm484jqR4mPTpuKY0ErD+KDflPMiXuMGEv/eC2QRzBERgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('b29cd2e3e645cbd4357008e8ef316838')

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:123456@127.0.0.1:5432/hotel'
db = SQLAlchemy(app)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    userid = event.source.user_id
    sql_cmd = "select * from formuser where uid='" + userid + "'"
    query_data = db.engine.execute(sql_cmd)
    if len(list(query_data)) == 0:
        sql_cmd = "insert into formuser (uid) values('" + userid + "');"
        db.engine.execute(sql_cmd)

    mtext = event.message.text
    if mtext[:6] == '123456' and len(mtext) > 6:  #推播給所有顧客
        pushMessage(event, mtext)

def pushMessage(event, mtext):  ##推播訊息給所有顧客
    try:
        msg = mtext[6:]  #取得訊息
        sql_cmd = "select * from formuser"
        query_data = db.engine.execute(sql_cmd)
        userall = list(query_data)
        for user in userall:  #逐一推播
            message = TextSendMessage(
                text = msg
            )
            line_bot_api.push_message(to=user[1], messages=[message])  #推播訊息
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

if __name__ == '__main__':
    app.run()