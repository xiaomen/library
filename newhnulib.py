# -*- coding: utf-8 -*-

import re
import urllib
import urllib2
import xml.etree.ElementTree as etree
import string

book_attr = ['BOOKRECNO', 'AUTHOR', 'ISBN', 'PAGE', 'PRICE', 
'PUBLISHER', 'PUBDATE', 'TITLE', 'SUBJECT', 'BOOKTYPE']

navbar_attr = 'NAVBAR'
session_attr = 'SESSION'

url = 'http://deploy2.xiaom.co:8998/opac/websearch/bookSearch'

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

def new_search_book(p):
    p['filter'] = p['filter'].encode('utf-8')
    p['bookType'] = p['bookType'].encode('utf-8')
    p['marcType'] = p['marcType'].encode('utf-8')
    p['val1'] = p['val1'].encode('utf-8')
    req = urllib2.Request(url + '?' + urllib.urlencode(p))
    res = urllib2.urlopen(req)
    xml = res.read()
    res.close()
    return get_book_list_from_xml(xml)

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
            if key != '999' : ret_dict[key] = value
     
    return ret_dict

def get_book_detail_from_xml(xml):
    
    new_xml = re.compile('<HEAD>(.*)</HEAD>').sub('', xml)
    tree = etree.fromstring(new_xml)

    #get some meta info of library
    hold_state_dict = get_hold_state(tree)
    book_type_dict = get_book_type(tree)
    lib_local_dict = get_lib_local(tree)
    lib_dict = get_lib(tree)

    detail_list = []

    rows = tree.findall('ROWSET1/ROW')
    loanrows = tree.findall('ROWSET2/ROW')
    if rows == None:
        return detail_list

    for row in rows:
        detail = {}
        detail['BARCODE'] = barcode = get_value_from_xml_node(row, 'BARCODE', '')
        detail['CALLNO']  = get_value_from_xml_node(row, 'CALLNO', '')
        detail['TOTALLOANNUM']  = get_value_from_xml_node(row, 'TOTALLOANNUM', '')
        detail['TOTALRENEWNUM']  = get_value_from_xml_node(row, 'TOTALRENEWNUM', '')

        if loanrows != None:
            for loan in loanrows:
                bar = get_value_from_xml_node(loan, 'BARCODE', '')
                if len(bar) > 0 and bar == barcode:
                    detail['LOANDATE'] = get_value_from_xml_node(loan, 'LOANDATE', '')
                    detail['RETURNDATE'] = get_value_from_xml_node(loan, 'RETURNDATE', '')

        state = get_value_from_xml_node(row, 'STATE', '')
        detail['STATE'] = hold_state_dict.get(state, '')

        curlib = get_value_from_xml_node(row, 'CURLIB', '')
        detail['CURLIB'] = lib_dict.get(curlib, '')

        cirtype = get_value_from_xml_node(row,'CIRTYPE', '')
        detail['CIRTYPE'] = book_type_dict.get(cirtype, '')

        curlocal = get_value_from_xml_node(row, 'CURLOCAL', '')
        detail['CURLOCAL'] = lib_local_dict.get(curlocal, '')

        detail_list.append(detail)
    return detail_list

def get_book_detail_info(p):
    req = urllib2.Request(url + '?' + urllib.urlencode(p))
    res = urllib2.urlopen(req)
    xml = res.read()
    res.close()
    return get_book_detail_from_xml(xml)
