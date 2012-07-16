import json
import urllib2

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;"}

def html_escape(text):
    return "".join(html_escape_table.get(c, c) for c in text)

def html_unescape(s):
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    s = s.replace("&apos;", "'")
    s = s.replace("&quot;", "\"")
    s = s.replace("&amp;", "&")
    return s

def int_ceil(a, b):
    if b == 0:
        return 0
    return int((a + b - 1) / b)

def get_user(uid):
    url = 'http://open.xiaomen.co/api/people/' + str(uid)
    req = urllib2.Request(url)
    req.add_header('X-APP-NAME', 'account')
    res = urllib2.urlopen(req, timeout=15)
    return json.loads(res.read())
