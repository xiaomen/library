# -*- coding: utf-8 -*-

import urllib
import urllib2
import logging
from sgmllib import SGMLParser

logger = logging.getLogger(__name__)

class BookParser(SGMLParser):
    inputs = []
    books = []
    find_table = 0
    find_tr = 0
    find_td = 0
    td_count = 0
    book = {}
    def start_table(self, attrs):
        if ('bgcolor', '#008080') in attrs : 
            self.find_table = 1
            self.books = []
            self.inputs = []
    def start_tr(self, attrs):
        if self.find_table == 1:
            self.find_tr = 1
            self.td_count = 0
            self.book = {}
    def start_td(self, attrs):
        if self.find_table == 1 and self.find_tr == 1:
            self.find_td = 1
            self.td_count += 1
    def start_a(self, attrs):
        if self.td_count == 7 :
            href = [v for k, v in attrs if k == 'href']
            self.book['detail_url'] = href[0][href[0].find('?') + 1:]
    def handle_data(self, text):
        if self.find_table == 1 and self.find_tr == 1 and self.find_td == 1 \
        and self.td_count > 0 and self.td_count < 7:
            properties_mapping = ['title', 'author', 'publisher', 'page_count', 'price', 'lib_number']
            self.book[properties_mapping[self.td_count - 1]] = text.decode('GB18030').encode('utf-8')
    def end_td(self):
        if self.find_td == 1:
            self.find_td = 0
    def end_tr(self):
        if self.find_tr == 1:
            self.find_tr = 0
            self.td_count = 0
            self.books.append(self.book)
    def end_table(self):
        if self.find_table == 1 : self.find_table = 0
    def start_input(self, attrs):
        if ('type', 'hidden') in attrs:
            try:
                self.inputs.append(([v for k, v in attrs if k == 'name'][0], [v for k, v in attrs if k == 'value'][0].decode('GB18030').encode('utf-8')))
            except:
                logger.debug(attrs)

def search_book(p):
    p['v_pagenum'] = '10'
    p['v_value'] = p['v_value'].encode('GB18030')
    if p.has_key('v_curkey') : p['v_curkey'] = p['v_curkey'].encode('GB18030')
    req = urllib2.Request(url='http://opac.lib.hnu.cn/cgi-bin/IlaswebBib', data=urllib.urlencode(p))
    res = urllib2.urlopen(req)
    html = res.read()
    res.close()
    bookParser = BookParser()
    bookParser.feed(html)
    return {'book_list' : bookParser.books, 'input_list' : bookParser.inputs, 'is_end' : html.find('document.nextpage.submit()')}

def new_search_book(p):
    url = 'http://202.197.107.27/opac/websearch/bookSearch'
    p['filter'] = p['filter'].encode('utf-8')
    p['bookType'] = p['bookType'].encode('utf-8')
    p['marcType'] = p['marcType'].encode('utf-8')
    p['val1'] = p['val1'].encode('utf-8')
    req = urllib2.Request(url + '?' + urllib.urlencode(p))
    res = urllib2.urlopen(req)
    xml = res.read()
    res.close()
    print xml
    return xml
def get_book_detail(p):
    req = urllib2.Request(url = 'http://opac.lib.hnu.cn/cgi-bin/DispBibDetail?v_recno=%s&v_curdbno=%s' % (p['v_recno'], p['v_curdbno']))
    res = urllib2.urlopen(req)
    html = res.read()
    return html
if __name__ == '__main__':
    print search_book(u'政治')
