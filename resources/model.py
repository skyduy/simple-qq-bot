# coding: utf-8

"""
    ...
    ~~~~~~~~~~

    :author Skyduy <cuteuy@gmail.com> <http://skyduy.me>

"""
from flask_sqlalchemy import SQLAlchemy
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASS, MYSQL_DB

db = SQLAlchemy()


class SessionMixin(object):
    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Record(db.Model, SessionMixin):
    __tablename__ = 'chat_record'
    id = db.Column(db.INT, primary_key=True)
    content = db.Column(db.TEXT, nullable=False)
    post_user = db.Column(db.VARCHAR(30), nullable=False)
    chat_time = db.Column(db.TIMESTAMP, nullable=False)

    def __init__(self, content, post_user):
        self.content = content
        self.post_user = post_user


class QA(db.Model, SessionMixin):
    __tablename__ = 'question_answer'
    id = db.Column(db.INT, primary_key=True)
    question = db.Column(db.TEXT, nullable=False)
    answer = db.Column(db.TEXT, nullable=False)
    post_user = db.Column(db.VARCHAR(30), nullable=False)
    post_time = db.Column(db.TIMESTAMP, nullable=False)

    def __init__(self, question, answer, post_user):
        self.question = question
        self.answer = answer
        self.post_user = post_user


class SensitiveQA(db.Model, SessionMixin):
    __tablename__ = 'Sensitive_QA'
    id = db.Column(db.INT, primary_key=True)
    question = db.Column(db.TEXT, nullable=False)
    answer = db.Column(db.TEXT, nullable=False)
    post_user = db.Column(db.VARCHAR(30), nullable=False)
    post_time = db.Column(db.TIMESTAMP, nullable=False)

    def __init__(self, question, answer, post_user):
        self.question = question
        self.answer = answer
        self.post_user = post_user


def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        'mysql://%s:%s@%s:%s/%s' % (MYSQL_USER, MYSQL_PASS, MYSQL_HOST, MYSQL_PORT, MYSQL_DB)
    app.config['SQLALCHEMY_POOL_SIZE'] = 100
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 300
    db.init_app(app)
    return db
