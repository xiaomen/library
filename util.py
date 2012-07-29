import web
import json
import urllib2
from sheep.api.open import rpc

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
    response_str = rpc('account', 'api/people/{0}'.format(uid))
    user = json.loads(response_str)
    if user.get('status', '') == 'ok':
        return user
    return None

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
