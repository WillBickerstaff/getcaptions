'''
Created on 19 Aug 2012
@license: MIT License <http://opensource.org/licenses/MIT>
@copyright: 2012 Will Bickerstaff
@author: Will Bickerstaff
@email: will.bickerstaff@gmail.com
'''


def heading(text, level=2):
    return "{0} {1} {0}\n".format('#' * level, text)


def to_utf8(text):
    md = text
    md.encode('utf-8', 'xmlcharrefreplace')
    return md
