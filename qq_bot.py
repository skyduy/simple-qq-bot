#!/usr/bin/env python
# coding:utf-8

from flask import Flask, request
import traceback, logging
from msg_proc import QQMessage
from model import init_db

app = Flask(__name__)
db = init_db(app)
with app.app_context():
    db.create_all()


def qqbot_main(data):
    QQMessage(data).proc_message()


@app.route("/bot", methods=['POST'])
def qqbot():
    try:
        qqbot_main(request.data)
    except:
        print traceback.format_exc()
    finally:
        return ''

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(host='127.0.0.1', port=60002, debug=True, threaded=True)
