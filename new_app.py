# -*- coding: utf-8 -*-
import web
import newhnulib
import os
from jinja2 import Environment, FileSystemLoader

urls = (
    '/Query', 'Query',
    '/QueryDetail', 'QueryDetail',
    '/.*', 'QueryPage',
)

def render_template(template_name, **context):
    extensions = context.pop('extensions', [])
    globals = context.pop('globals', {})
    jinja_env = Environment(
        loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
        extensions=extensions)
    jinja_env.globals.update(globals)
    return jinja_env.get_template(template_name).render(context)

class Query:
    def POST(self):
        user_data = web.input()
        user_data['hasholding'] = 'y' if user_data['hasholdingCheckbox'] == 'on' else 'n'
        user_data['filter'] = self.calc_filter_value(user_data)
        user_data['bookType'] = self.calc_book_type_value(user_data)
        user_data['marcType'] = self.calc_marc_type_value(user_data)
        user_data['val1'] = newhnulib.html_unescape(user_data['val1'])
        if user_data['marcformat'] != 'all':
            user_data['marcformat'] = 'radiobutton'
        query_result = newhnulib.new_search_book(user_data)
        return render_template('result.html', query_result=query_result, 
                                              val1=newhnulib.html_escape(user_data['val1'].decode('utf-8')),
                                              sortSign=user_data['sortSign'],
                                              hasholdingCheckbox=user_data['hasholdingCheckbox'])

    def calc_book_type_value(self, user_data):
        words = {'1' : u'图书', '2' : u'期刊', '3' : u'非书资料', '4' : u'古籍', '6' : u'临时书目库', 'all' : 'undefined'}
        return user_data['booktype'] + ':' + words[user_data['booktype']]

    def calc_marc_type_value(self, user_data):
        words = {'CNMARC' : u'CNMARC:中文', 'USMARC' : u'USMARK:英文', 'all' : u'undefined:全部'}
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
    def GET(self):
        return render_template('index.html')

class QueryDetail:
    def GET(self):
        user_data = web.input()
        detail_list = newhnulib.get_book_detail_info(user_data)
        return render_template('details.html', detail_list=detail_list)
app = web.application(urls, globals())
wsgi_app = app.wsgifunc()

if __name__ == "__main__": 
    app.run()
