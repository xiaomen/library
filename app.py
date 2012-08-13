# -*- coding: utf-8 -*-

import os
import web
import json
import urllib
import logging
from datetime import datetime
from sheep.api.statics import static_files
from sheep.api.sessions import SessionMiddleware, FilesystemSessionStore
from sheep.api.users import *

from jinja2 import Environment, FileSystemLoader

from functools import wraps
from werkzeug.useragents import UserAgent
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import func

import hnulib
import util

from models import *

logger = logging.getLogger(__name__)

params = {
        "col1": "marc",
        "marcformat": "all",
        "booktype": "all",
        "raws": "10",
        "cmdACT": "list",
        "xsl": "BOOK_list.xsl",
        "mod": "oneXSL",
        "columnID": "1",
        "searchSign": "",
        "libNUM": "1",
        "ISFASTSEARCH": "true",
        "matching": "radiobutton",
        "multiSelectLibcode": "",
        "orderSign": "true",
        "startPubdate": "",
        "endPubdate": "",
        "hasholdingCheckbox": "1",
        "hasholding": "y",
        "sortSign": "score_sort"
    }

urls = (
    '/Query/(.*)/(.*)', 'Query',
    '/Query', 'Query',
    '/QueryDetail/(.*)', 'QueryDetail',
    '/QueryDetail', 'QueryDetail',
    '/current_user', 'UserSample',
    '/hot_keys', 'HotKeySample',
    '/api/keywords/(.*)', 'UserKeyword',
    '/.*', 'QueryPage',
)

jinja_env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__),
                            'templates')),
    extensions=[])
jinja_env.globals['generate_user_url'] = generate_user_url
jinja_env.globals['generate_login_url'] = generate_login_url
jinja_env.globals['generate_logout_url'] = generate_logout_url
jinja_env.globals['generate_register_url'] = generate_register_url
jinja_env.globals['generate_mail_url'] = generate_mail_url
jinja_env.filters['s_files'] = static_files

def check_ua(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        ua = UserAgent(web.ctx.env['HTTP_USER_AGENT'])
        if ua.browser == 'msie':
            try:
                if int(float(ua.version)) < 8:
                    return jinja_env.get_template("noie.html").render()
            except:
                return jinja_env.get_template("noie.html").render()
        return method(self, *args, **kwargs) 
    return wrapper

def ismobile():
    ua = UserAgent(web.ctx.env['HTTP_USER_AGENT'])
    if ua.platform.lower() in ["android", "iphone"]:
        return True
    return False


def get_page_nav(pages, now, query_val):
    now = now - 1
    dotdot = lambda a: "<li class=\"disabled\"><a href=\"#\">...</a></li>"
    button = lambda page: "<li><a href=\"/Query?pageNo=%d&val1=%s\">%d</a></li>" % (page + 1, query_val, page + 1)
    activebutton = lambda page: "<li class=\"active\"><a href=\"/Query?pageNo=%d&val1=%s\">%d</a></li>" % (page + 1, query_val, page + 1)
    result = []
    for i in range(pages if pages <= 4 else 4):
        if i == now:
            result.append(activebutton(i))
        else:
            result.append(button(i))
    if now == 3 and pages > 4:
        result.append(button(4))
    if now > 3:
        if now > 4:
            result.append(dotdot(1))
            result.append(button(now - 1))
        result.append(activebutton(now))
        if now + 1 < pages:
            result.append(button(now + 1))
    if pages - 1 > 3 and now + 1 < pages - 1:
        result.append(dotdot(1))
        result.append(button(pages - 1))
    return result

def check_state(state):
    if state == u'在馆':
        return u'<span class="green-sign">在馆</span>'
    elif state == u'借出':
        return u'<span class="red-sign">借出</span>'
    return u'<span class="green-sign">%s</span>' % state

jinja_env.filters['get_page_nav'] = get_page_nav
jinja_env.filters['check_state'] = check_state

web.config.debug = False
app = web.application(urls, globals())
wsgi_app = SessionMiddleware(app.wsgifunc(), \
        FilesystemSessionStore(), \
        cookie_name="xid", cookie_path="/", \
        cookie_domain=".xiaomen.co")


def insert_search_record(uid, value):
    session = scoped_session(sessionmaker(bind=engine))
    records = session.query(SearchRecord).filter_by(uid=uid).\
            order_by(SearchRecord.time)
    if records.count() == 15:
        session.delete(records.first())
    session.add(SearchRecord(uid, value, datetime.now()))
    session.commit()
    session.close()

def get_hot_keys(top):
    session = scoped_session(sessionmaker(bind=engine))
    records = session.query(SearchRecord.record, func.count('*').\
            label('record_count')).\
            group_by(SearchRecord.record).\
            order_by('record_count desc')
    count = session.query(SearchRecord).group_by(SearchRecord.record).count()
    ret = records[:min(top, count)]
    session.close()
    return ret

def get_keywords_by_uid(uid):
    session = scoped_session(sessionmaker(bind=engine))
    records = session.query(SearchRecord).filter_by(uid=uid).\
            order_by(SearchRecord.time).all()
    session.close()
    return records

class Query:
    @check_ua
    def GET(self, keyword='', page_no=''):
        user_data = web.input()
        user_data = dict(user_data, **params) 
        if len(keyword) * len(page_no) > 0:
            user_data['val1'] = keyword
            user_data['pageNo'] = page_no

        uid = web.ctx.user.uid
        if uid != None:
            insert_search_record(uid, user_data['val1'])

        user_data['filter'] = self.calc_filter_value(user_data)
        user_data['bookType'] = self.calc_book_type_value(user_data)
        user_data['marcType'] = self.calc_marc_type_value(user_data)
        user_data['val1'] = util.html_unescape(user_data['val1'])
        if user_data['marcformat'] != 'all':
            user_data['marcformat'] = 'radiobutton'
        try:
            query_result = hnulib.new_search_book(user_data)
            if len(keyword) * len(page_no) > 0:
                return json.dumps(query_result)
            if ismobile():
                return jinja_env.get_template('mobile/result.html').render(
                    query_result=query_result,
                    val1=urllib.quote(user_data['val1']), 
                    query_val=user_data['val1'].decode("utf-8"), 
                    pageNo=user_data['pageNo'])
            else:
                return jinja_env.get_template('result.html').render(
                    query_result=query_result,
                    val1=urllib.quote(user_data['val1']), 
                    query_val=user_data['val1'].decode("utf-8"), 
                    pageNo=user_data['pageNo'])
        except:
            return jinja_env.get_template('500.html').render()

    def calc_book_type_value(self, user_data):
        words = {'1': u'图书', '2': u'期刊', '3': u'非书资料',
                 '4': u'古籍', '6': u'临时书目库', 'all': 'undefined'}
        return user_data['booktype'] + ':' + words[user_data['booktype']]

    def calc_marc_type_value(self, user_data):
        words = {'CNMARC': u'CNMARC:中文',
                 'USMARC': u'USMARK:英文',
                 'all': u'undefined:全部'}
        return words[user_data['marcformat']]

    def calc_filter_value(self, user_data):
        q = '(' + user_data['col1'] + ':' + user_data['val1'] + ')'
        if user_data['marcformat'] != 'all':
            q = q + ' AND (marcformat:' + user_data['marcformat'] + '*)'
        if user_data['booktype'] != 'all':
            q = q + ' AND (booktype:' + user_data['booktype'] + '*)'
        if user_data['hasholding'] == 'y':
            q = q + ' AND (hasholding:y)'
        return q

class UserSample:
    def GET(self):
        user = web.ctx.user
        if not user:
            return 'No user in session'
        return '%s %s' % (user.get('name', ''), user.get('uid', 0))

class HotKeySample:
    def GET(self):
        keys = get_hot_keys(5)
        return '\n'.join(['{0} {1}'.format(k.record, k.record_count) for k in keys])

class UserKeyword:
    def GET(self, uid):
        records = get_keywords_by_uid(int(uid))
        return '\n'.join([r.record for r in records])

class QueryPage:
    @check_ua
    def GET(self):
        if ismobile():
            return jinja_env.get_template('mobile/index.html').render()
        else:
            return jinja_env.get_template('index.html').render()

detail_params = {'cmdACT': 'detailmarc', 'xsl': 'listdetailmarc.xsl'}

class QueryDetail:
    @check_ua
    def GET(self, book_rec_no=''):
        user_data = web.input()
        user_data = dict(user_data, **detail_params) 
        if len(book_rec_no) > 0:
            user_data['bookrecno'] = book_rec_no
        book = hnulib.get_book_detail_info(user_data)
        if len(book_rec_no) > 0:
            return json.dumps(book)
        book['borrow_count'] = 0
        for d in book['detail_list']:
            if d['STATE'] == u'在馆':
                book['borrow_count'] = book['borrow_count'] + 1
        if ismobile():
            return jinja_env.get_template('mobile/detail.html').render(
                    book=book,
                    pageNo=user_data['pageNo'],
                    query_val=user_data['val1'].decode("utf-8"), 
                    val1=urllib.quote(user_data['val1']))
        else:
            return jinja_env.get_template('detail.html').render(
                    book=book,
                    pageNo=user_data['pageNo'],
                    query_val=user_data['val1'].decode("utf-8"), 
                    val1=urllib.quote(user_data['val1']))

def before_request(handle):
    web.ctx.session = web.ctx.env['xiaomen.session']
    web.ctx.user = get_current_user(web.ctx.session)
    if web.ctx.user:
        web.ctx.unread_mail_count = lambda: get_unread_mail_count(web.ctx.user.uid)
    jinja_env.globals['ctx'] = web.ctx

    return handle()

app.add_processor(before_request)

if __name__ == "__main__":
    app.run()
