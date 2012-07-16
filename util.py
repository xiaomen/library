import web
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

def get_current_uid():
    web_session = web.ctx.env['xiaomen.session']
    if not web_session or not web_session.get('user_id') or not web_session.get('user_token'):
        return None
    return web_session['user_id']

def get_current_user():
    web_session = web.ctx.env['xiaomen.session']
    if not web_session or not web_session.get('user_id') or not web_session.get('user_token'):
        return None
    return get_user(web_session['user_id'])
