# -*- coding: utf-8 -*-
import web
import hnulib

urls = (
    '/QueryDetail', 'QueryBookDetail',
    '/Query', 'LibraryQuery',
    '/.*', 'LibraryQueryForm',
)

render = web.template.render('templates')

class LibraryQueryForm:
    form = web.form.Form(
        web.form.Radio('v_index', [('TITLE','题名（刊名）'),
                                   ('AUTHOR', '作者'),
                                   ('SUBJECT', '主题词'),
                                   ('CLASSNO', '分类号'),
                                   ('ISBN', '国际标准书/刊号')], description = '查找途径'),
        web.form.Textbox('v_value', web.form.notnull,
            description = "Book's Name"),
        web.form.Radio('v_seldatabase', [('0','书和刊'),
                                   ('1', '图书'),
                                   ('2', '期刊')], description = '检索库'),
        web.form.Radio('v_LogicSrch', [('0','前方一致'),
                                   ('1', '模糊检索')], description = '检索方式'),
    )
    def GET(self):
        """ Show Page """
        form = self.form
        return render.query(form)

class QueryBookDetail:
    def GET(self):
       user_data = web.input()
       print user_data
       return hnulib.get_book_detail(user_data)
    def POST(self):
        pass

class LibraryQuery:
    def GET(self):
        return "Do not use GET request"
    def POST(self):
        user_data = web.input()
        result = hnulib.search_book(user_data)
        book_list = result['book_list']
        input_list = result['input_list']
        is_end = result['is_end']
        return render.query_result(book_list[1:], input_list, is_end >= 0)

app = web.application(urls, globals())
wsgi_app = app.wsgifunc()

if __name__ == "__main__": 
    app.run()
