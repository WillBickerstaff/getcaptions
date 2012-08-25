def heading(text, level=2):
    return "{0} {1} {0}\n".format('#' * level, text)


def to_utf8(text):
    md = text
    md.encode('utf-8', 'xmlcharrefreplace')
    return md
