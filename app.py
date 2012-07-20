# -*- coding: utf-8 -*-

import os
import web
import json
import urllib
from sheep.api.statics import static_files
from jinja2 import Environment, FileSystemLoader
from functools import wraps
from werkzeug.useragents import UserAgent

import hnulib
import util

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
    '/.*', 'QueryPage',
)

jinja_env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__),
                            'templates')),
    extensions=[])
jinja_env.globals.update({})
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

jinja_env.filters['get_page_nav'] = get_page_nav

class Query:
    @check_ua
    def GET(self, keyword='', page_no=''):
        user_data = web.input()
        user_data = dict(user_data, **params) 
        if len(keyword) * len(page_no) > 0:
            user_data['val1'] = keyword
            user_data['pageNo'] = page_no
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

class QueryPage:
    @check_ua
    def GET(self):
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
        return jinja_env.get_template('detail.html').render(
                book=book,
                pageNo=user_data['pageNo'],
                query_val=user_data['val1'].decode("utf-8"), 
                val1=urllib.quote(user_data['val1']))

app = web.application(urls, globals())
wsgi_app = app.wsgifunc()

if __name__ == "__main__":
    app.run()
