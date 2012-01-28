# -*- coding: utf-8 -*-

import re
import string
import urllib
import urllib2
import logging
import xml.etree.ElementTree as etree

book_attr = ['BOOKRECNO', 'AUTHOR', 'ISBN', 'PAGE', 'PRICE',
             'PUBLISHER', 'PUBDATE', 'TITLE', 'SUBJECT', 'BOOKTYPE']

navbar_attr = 'NAVBAR'
session_attr = 'SESSION'

url = 'http://opac.lib.hnu.cn/opac/websearch/bookSearch'


html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;"}

logger = logging.getLogger(__name__)

def html_escape(text):
    return "".join(html_escape_table.get(c, c) for c in text)

def html_unescape(s):
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    s = s.replace("&apos;", "'")
    s = s.replace("&quot;", "\"")
    s = s.replace("&amp;", "&")
    return s

def get_value_from_xml_node(tree, path, default):
    node = tree.find(path)
    if node == None:
        return default
    return node.text

def int_ceil(a, b):
    if b == 0:
        return 0
    if (a % b == 0):
        return a / b
    return a / b + 1

def get_book_list_from_xml(xml):
    tree = etree.fromstring(xml)
    book_query_result = {}
    book_query_result['book_list'] = []
    book_query_result['CURPAGE'] = string.atoi(get_value_from_xml_node(tree, session_attr + '/CURPAGE', '0'))
    book_query_result['PAGEROWS'] = string.atoi(get_value_from_xml_node(tree, navbar_attr + '/PAGEROWS', '0'))
    book_query_result['TOTALROWS'] = string.atoi(get_value_from_xml_node(tree, navbar_attr + '/TOTALROWS', '0'))
    book_query_result['PAGES'] = int_ceil(book_query_result['TOTALROWS'], book_query_result['PAGEROWS'])
    bookrows = tree.findall('ROW')
    if bookrows == None:
        book_query_result['has_result'] = False
        return book_query_result

    result_length = len(bookrows)
    book_query_result['has_result'] = result_length > 0
    if result_length > 0:
        for row in bookrows:
            book = {}
            for attr in book_attr:
                book[attr] = get_value_from_xml_node(row, attr, '')
            book_query_result['book_list'].append(book)

    return book_query_result

def get_book_loan_info_from_xml(book_list, xml):
    tree = etree.fromstring(xml)
    callno_rows = tree.findall('ROWSET1/ROW')
    loan_rows = tree.findall('ROWSET2/ROW')
    for book in book_list:
        book['CALLNO'] = ''
        for row in callno_rows:
            value = get_value_from_xml_node(row, 'BOOKRECNO', '')
            if book['BOOKRECNO'] == value.strip():
                book['CALLNO'] = get_value_from_xml_node(row, 'CALLNO', '')
                break
        book['BORROW'] = False
        for row in loan_rows:
            value = get_value_from_xml_node(row, 'BOOKRECNO', '')
            if book['BOOKRECNO'] == value.strip():
                book['BORROW'] = True
                break

def get_book_loan_info(book_list):
    p = dict(cmdACT='getbooknum')
    p['fill'] = ''.join([",'" + x['BOOKRECNO'] + "'" for x in book_list])
    print p
    try:
        res = urllib2.urlopen(url + '?' + urllib.urlencode(p), timeout=15)
        xml = res.read()
        res.close()
        get_book_loan_info_from_xml(book_list, xml)
    except:
        logger.info(p)
        logger.exception('error occured when getting book loan info')
        raise

def new_search_book(p):
    #p['filter'] = p['filter'].encode('utf-8')
    #p['bookType'] = p['bookType'].encode('utf-8')
    #p['marcType'] = p['marcType'].encode('utf-8')
    #p['val1'] = p['val1'].encode('utf-8')
    for key in p.keys():
        if isinstance(p[key], unicode):
            p[key] = p[key].encode('utf-8')
    try:
        req = urllib2.Request(url + '?' + urllib.urlencode(p))
        res = urllib2.urlopen(req, timeout=15)
        xml = res.read()
        res.close()
        result = get_book_list_from_xml(xml)
        book_list = result['book_list']
        get_book_loan_info(book_list)
        return result
    except:
        logger.info(p)
        logger.exception('error occured')
        raise

def get_hold_state(tree):
    ret_dict = {}
    rows = tree.findall('HOLDSTATE/ROWSET/ROW')
    if rows != None:
        for row in rows:
            key = row.find('STATETYPE').text
            value = row.find('STATENAME').text
            ret_dict[key] = value
    return ret_dict

def get_book_type(tree):
    ret_dict = {}
    rows = tree.findall('ROWSET5/ROW')
    if rows != None:
        for row in rows:
            key = row.find('CIRTYPE').text
            value = row.find('NAME').text
            ret_dict[key] = value
    return ret_dict

def get_lib_local(tree):
    ret_dict = {}
    rows = tree.findall('ROWSET4/ROW')
    if rows != None:
        for row in rows:
            key = row.find('LOCALCODE').text
            value = row.find('NAME').text
            ret_dict[key] = value
    return ret_dict

def get_lib(tree):
    ret_dict = {}
    rows = tree.findall('ROWSET3/ROW')
    if rows != None:
        for row in rows:
            key = row.find('LIBCODE').text
            value = row.find('SIMPLENAME').text
            if key != '999':
                ret_dict[key] = value
    return ret_dict

def get_book_detail_from_xml(xml):
    new_xml = re.compile('<HEAD>(.*)</HEAD>').sub('', xml)
    tree = etree.fromstring(new_xml)

    #get some meta info of library
    hold_state_dict = get_hold_state(tree)
    book_type_dict = get_book_type(tree)
    lib_local_dict = get_lib_local(tree)
    lib_dict = get_lib(tree)

    book = {}
    detail_list = []
    book_info_prop = [('name', '200', 'suba'),
            ('author', '200', 'subf'),
            ('publisher', '210', 'subc'),
            ('publish_time', '210', 'subd'),
            ('isbn', '010', 'suba'),
            ('callno', '905', 'subf')]
    for prop in book_info_prop:
        node_list = tree.findall("FLD")
        node = None
        for n in node_list:
            m = n.find('FLDNAME')
            if m != None and m.text.strip() == prop[1]:
                node = n.find(prop[2])
        
        if node == None:
            book[prop[0]] = ''
        else:
            book[prop[0]] = node.text.strip()
    rows = tree.findall('ROWSET1/ROW')
    loanrows = tree.findall('ROWSET2/ROW')
    if rows == None:
        return detail_list

    for row in rows:
        detail = {}
        barcode = get_value_from_xml_node(row, 'BARCODE', '')
        detail['BARCODE'] = barcode
        detail['CALLNO'] = get_value_from_xml_node(
            row, 'CALLNO', '')
        detail['TOTALLOANNUM'] = get_value_from_xml_node(
            row, 'TOTALLOANNUM', '')
        detail['TOTALRENEWNUM'] = get_value_from_xml_node(
            row, 'TOTALRENEWNUM', '')

        if loanrows != None:
            for loan in loanrows:
                bar = get_value_from_xml_node(loan, 'BARCODE', '')
                if len(bar) > 0 and bar == barcode:
                    detail['LOANDATE'] = get_value_from_xml_node(
                        loan, 'LOANDATE', '')
                    detail['RETURNDATE'] = get_value_from_xml_node(
                        loan, 'RETURNDATE', '')

        state = get_value_from_xml_node(row, 'STATE', '')
        detail['STATE'] = hold_state_dict.get(state, '')
        curlib = get_value_from_xml_node(row, 'CURLIB', '')
        detail['CURLIB'] = lib_dict.get(curlib, '')
        cirtype = get_value_from_xml_node(row, 'CIRTYPE', '')
        detail['CIRTYPE'] = book_type_dict.get(cirtype, '')
        curlocal = get_value_from_xml_node(row, 'CURLOCAL', '')
        detail['CURLOCAL'] = lib_local_dict.get(curlocal, '')

        detail_list.append(detail)
        book['detail_list'] = detail_list
    return book

def get_book_detail_info(p):
    for key in p.keys():
        if isinstance(p[key], unicode):
            p[key] = p[key].encode('utf-8')
    try:
        req = urllib2.Request(url + '?' + urllib.urlencode(p))
        res = urllib2.urlopen(req, timeout=15)
        xml = res.read()
        res.close()
        return get_book_detail_from_xml(xml)
    except:
        logger.info('error occured when getting detail info')
        logger.exception('error occured')
        raise
