# -*- coding: utf-8 -*-

import re
import string
import urllib
import urllib2
import logging
import xml.etree.ElementTree as etree

import util

book_attr = ['BOOKRECNO', 'AUTHOR', 'ISBN', 'PAGE', 'PRICE',
             'PUBLISHER', 'PUBDATE', 'TITLE', 'SUBJECT', 'BOOKTYPE']
navbar_attr = 'NAVBAR'
session_attr = 'SESSION'
#url = 'http://opac.lib.hnu.cn/opac/websearch/bookSearch'
url = 'http://deploy2.xiaom.co:8998/opac/websearch/bookSearch'

logger = logging.getLogger(__name__)

def get_value_from_xml_node(tree, path, default):
    node = tree.find(path)
    if node == None:
        return default
    return node.text

def get_book_list_from_xml(xml):
    tree = etree.fromstring(xml)
    book_query_result = {}
    book_query_result['book_list'] = []
    book_query_result['CURPAGE'] = string.atoi(get_value_from_xml_node(tree, session_attr + '/CURPAGE', '0'))
    book_query_result['PAGEROWS'] = string.atoi(get_value_from_xml_node(tree, navbar_attr + '/PAGEROWS', '0'))
    book_query_result['TOTALROWS'] = string.atoi(get_value_from_xml_node(tree, navbar_attr + '/TOTALROWS', '0'))
    book_query_result['PAGES'] = util.int_ceil(book_query_result['TOTALROWS'], book_query_result['PAGEROWS'])
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

def get_mapping_from_xml(tree, path, key_name, value_name):
    ret_dict = {}
    rows = tree.findall(path)
    if rows == None:
        return {}
    for row in rows:
        key = row.find(key_name).text
        value = row.find(value_name).text
        ret_dict[key] = value
    return ret_dict

def get_book_from_xml(tree):
    book = {}
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
    return book

def get_detail_dict(tree):
    dict_property_list = [
            ('STATE','HOLDSTATE/ROWSET/ROW', 'STATETYPE', 'STATENAME'),
            ('CURLIB','ROWSET3/ROW', 'LIBCODE', 'SIMPLENAME'),
            ('CURTYPE','ROWSET5/ROW', 'CIRTYPE', 'NAME'),
            ('CURLOCAL','ROWSET4/ROW', 'LOCALCODE', 'NAME')]
    dicts = {}
    for prop in dict_property_list:
        dicts[prop[0]] = get_mapping_from_xml(tree, prop[1], prop[2], prop[3])
    return dicts

def get_detail_list_from_xml(tree):
    detail_list = []
    rows = tree.findall('ROWSET1/ROW')
    loanrows = tree.findall('ROWSET2/ROW')
    if rows == None:
        return [] 
    dicts = get_detail_dict(tree)
    for row in rows:
        detail = {}
        for prop in ['BARCODE', 'CALLNO', 'TOTALLOANNUM', 'TOTALRENEWNUM']:
            detail[prop] = get_value_from_xml_node(row, prop, '')
        if loanrows == None:
            continue
        for loan in loanrows:
            bar = get_value_from_xml_node(loan, 'BARCODE', '')
            if len(bar) < 0 or bar != detail['BARCODE']:
                continue
            for prop in ['LOANDATE', 'RETURNDATE']:
                detail[prop] = get_value_from_xml_node(loan, prop, '')
        for prop in ['STATE', 'CURLIB', 'CURTYPE', 'CURLOCAL']:
            value = get_value_from_xml_node(row, prop, '')
            detail[prop] = dicts[prop].get(value, '')
        detail_list.append(detail)
    return detail_list

def get_book_detail_from_xml(xml):
    new_xml = re.compile('<HEAD>(.*)</HEAD>').sub('', xml)
    tree = etree.fromstring(new_xml)
    

    book = get_book_from_xml(tree) 
    detail_list = get_detail_list_from_xml(tree) 
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

