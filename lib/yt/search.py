import urllib, urllib2
import time
from string import Template
from xml.dom.minidom import parseString

class Search(object):
    MAXRESULTS = 20
    API = 2


    def __init__(self):
        self.reset()


    def reset(self):
        self.hits = 0
        self.start = 1
        self.results = []
        self.totalresults = 10


    def query(self, url, data={}):
        if self.start < self.totalresults > 0:
            data['start-index'] = self.start
            data['max-results'] = Search.MAXRESULTS
            querydata = urllib.urlencode(data)
            request = urllib2.Request('%s?%s' % (url, querydata))
            content = urllib2.urlopen(request).read()
            if self.__hascontent(content):
                content = parseString(content)
                self.__setTotalResults(content)
                self.start += Search.MAXRESULTS
                return content


    def __setTotalResults(self, content):
        if self.start == 1:
            self.totalresults = int(content.getElementsByTagName(
                            'openSearch:totalResults')[0].childNodes[0].data)

    def __hascontent(self, content):
        if content is not None and len(content) > 1:
            return True
        return False


class PlaylistSearch(Search):
    URL = Template('http://gdata.youtube.com/feeds/api/users/$user/playlists')
    

    def __init__(self, **kwargs):
        super(PlaylistSearch, self).__init__()
        self.user = ''
        self.searchterms = ''

        self.__checkkwargs(**kwargs)

    def __checkkwargs(self, **kwargs):
        for k in kwargs:
            k = k.lower()
            if k == 'user':
                self.user = kwargs[k]
                continue
            if k in ['search', 'searchterms']:
                if self.searchterms != kwargs[k]:
                    self.reset()
                self.searchterms = kwargs[k]
                continue


    def query(self, **kwargs):
        self.__checkkwargs(**kwargs)
        url = PlaylistSearch.URL.substitute({'user': self.user})

        if not self.user:
            raise Valuerror('A valid youtube user must be given to search for '
                            'playlists.')
        
        self.hits = 0
        self.results = []
        while ((self.hits < super(PlaylistSearch, self).MAXRESULTS)
                          and (self.totalresults > self.start)):
              dom = super(PlaylistSearch, self).query(url, {'v': Search.API})
              self.__matchLists(dom)
              self.hits = len(self.results)
              if self.hits < super(PlaylistSearch, self).MAXRESULTS:
                  time.sleep(0.2)  # Lets not hammer the yt servers
        if len(self.results) > 0:
            self.results.sort(key=lambda x: x['score'], reverse=True)
            return self.results


    def __matchLists(self, dom):
        playlists = dom.getElementsByTagName('entry')
        for playlist in playlists:
            listdict = self.__matchSearch(playlist)
            if listdict['score'] > 0:
                self.results.append(listdict)

    def __matchSearch(self, playlist):
        listdict = self.__parseList(playlist)
        assert all([len(listdict['title']) > 0, len(listdict['id']) > 0])
        listdict['score'] = self.__score(listdict['title'])
        return listdict

    def __score(self, title):
        if self.searchterms is None or len(self.searchterms) == 0:
            return 1
        title = title.lower()
        terms = self.__createSearchTerms()
        score = 0
        multiplier = 0
        for term in terms:
            term = term.lower()
            if term in title:
                if score == 0:
                    score = 1
                multiplier += 1
        return score * multiplier

    
    def __createSearchTerms(self):
        """ Join single characters in to the preceeding term """
        terms = self.searchterms.split()
        retTerms = []
        for i, term in enumerate(terms):
            if len(terms[i+1]) == 1:
                retTerms.append("%s %s" % (term, terms[i+1]))
                terms.pop(i+1)
            else:
                retTerms.append(term)
        return retTerms


    def __parseList(self, playlist):
        listdict = {}
        listdict['title'] = (playlist.getElementsByTagName('title')[0].
                                                        childNodes[0].data)
        listdict['id'] = (playlist.getElementsByTagName('yt:playlistId')[0].
                                                        childNodes[0].data)
        return listdict
                                                           

class CaptionSearch(Search):
    URL = 'http://www.youtube.com/api/timedtext'


    def __init__(self, **kwargs):
        super(CaptionSearch, self).__init__()


    def query(self, videoid):
        dom = super(CaptionSearch, self).query(CaptionSearch.URL,
                                               {'type': 'list', 'v': videoid})


class CaptionTrackSearch(Search):
    URL =  'http://video.google.com/timedtext'


    def __init__(self, **kwargs):
        super(CaptionTrackSearch, self).__init__()
        

    def query(self, videoid, name, lang):
        dom =super(CaptionTrackSearch, self).query(CaptionTrackSearch.URL,
                                                   {'lang': lang,
                                                    'v': videoid,
                                                    'name': name})

class PlaylistVideoSearch(Search):
    URL = Template('http://gdata.youtube.com/feeds/api/playlists/$playlist')


    def __init__(self, **kwargs):
        super(PlaylistVideoSearch, self).__init__()


    def query(self, playlistid):
        url = PlaylistVideoSearch.URL.substitute({'playlist': playlistid})
        dom = super(PlaylistVideoSearch, self).query(url)

x = PlaylistSearch(user='udacity', search='cs101 unit 4')
y = x.query()
for z in y: print z
