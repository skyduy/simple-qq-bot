#!/usr/bin/env python
# coding:utf-8

import logging

from flask import Flask, request
from model import init_db
from msg_proc import QQMessage

app = Flask(__name__)
db = init_db(app)
with app.app_context():
    db.create_all()


@app.route("/bot", methods=['POST'])
def qqbot():
    try:
        qq_msg = QQMessage(request.data)
        qq_msg.proc_message()
    except Exception as e:
        print 'Error occor:    %s' % e
    finally:
        return ''

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(host='127.0.0.1', port=60002, debug=True, threaded=True)
