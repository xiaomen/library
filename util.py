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
    if (a % b == 0):
        return a / b
    return a / b + 1


