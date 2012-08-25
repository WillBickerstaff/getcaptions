import urllib
import urllib2
import time
from string import Template
from xml.dom.minidom import parseString


class Search(object):

    """Generic  definitions for search classes"""

    MAXRESULTS = 20
    API = 2

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset to the just created state

        Resets the public attributes of the Search class:
        hits -> 0
        start -> 1
        results -> empty list
        totalresults -> 10"""
        self.hits = 0
        self.start = 1
        self.results = []
        self.totalresults = 10

    def query(self, url, data={}):
        """Query a url with the data parameters

        query takes a search url and data to query with. Query data is
        encoded with urllib.encode and so should be provided in an appropriate
        format.

        A maximum set of 20 results per Query call is returned as
        xml.dom.minidom document object. A subsequent call t query will return
        the next 20 results until no more results are available in which case
        None is returned or reset is called after which the first 20 results
        are again returned."""
        if self.start < self.totalresults > 0:
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
            if len(
                content.getElementsByTagName('openSearch:totalResults')) > 0:
                self.totalresults = int(content.getElementsByTagName(
                            'openSearch:totalResults')[0].childNodes[0].data)
            else:
                self.totalresults = 1000

    def __hascontent(self, content):
        if content is not None and len(content) > 1:
            return True
        return False


class PlaylistSearch(Search):

    """Find youtube playlists

    Matching playists will be available in the attribute results[]. If
    search terms is provided either when creating the class instance or
    calling query then results[] will be sorted with the highest scoring
    match appearing first in the list."""

    URL = Template('http://gdata.youtube.com/feeds/api/users/$user/playlists')

    def __init__(self, **kwargs):
        """To find a playlist at least a username must be given, in the form
        of a user="someuser" argument either when createing the class instance
        or calling the query method. Optionally searchterms="some terms" can
        also be given to reduce the number of results.

        Calling reset() will not reset either of these arguments, it will
        clear all existing search results and restart the search with the
        same arguments."""

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
        """To find a playlist at least a username must be given, in the form
        of a user="someuser" argument either when createing the class instance
        or calling the query method. Optionally searchterms="some terms" can
        also be given to reduce the number of results.

        Calling reset() will not reset either of these arguments, it will
        clear all existing search results and restart the search with the
        same arguments.

        query returns the contents of results or None if there are no
        matching results."""

        self.__checkkwargs(**kwargs)
        url = PlaylistSearch.URL.substitute({'user': self.user})

        if not self.user:
            raise ValueError('A valid youtube user must be given to search '
                             'for playlists.')

        self.hits = 0
        self.results = []
        while ((self.hits < super(PlaylistSearch, self).MAXRESULTS)
                          and (self.totalresults > self.start)):
            dom = super(PlaylistSearch, self).query(url,
                                            {'v': Search.API,
                                             'start-index': self.start,
                                             'max-results': Search.MAXRESULTS,
                                             'v': Search.API})
            if dom is None:
                return
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
        """Join single/double character trms  in to the preceeding term."""
        terms = self.searchterms.split()
        retTerms = []
        for i, term in enumerate(terms):
            if i + 1 < len(terms) and len(terms[i + 1]) < 3:
                retTerms.append("%s %s" % (term, terms[i + 1]))
                terms.pop(i + 1)
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

    """Find all available caption tracks for a video.

    All found caption tracks will be in results[], which will be sorted
    alphabetically by language.

    reset() does not clear the videoid, it clears all results and resets
    the search back to the beginning."""

    URL = 'http://www.youtube.com/api/timedtext'

    def __init__(self, **kwargs):
        """To retrieve caption tracks a valid video id must be given
        as id="somevideoid" or videoid="somevideid" either when creating
        the class instance or calling the query method."""

        super(CaptionSearch, self).__init__()
        self.videoid = None
        self.__checkkwargs(**kwargs)

    def __checkkwargs(self, **kwargs):
        for k in kwargs:
            k = k.lower()
            if k in ['id', 'videoid']:
                self.videoid = kwargs[k]
                continue

    def query(self, **kwargs):
        """To retrieve caption tracks a valid video id must be given
        as id="somevideoid" or videoid="somevideid" either when creating
        the class instance or calling the query method.

        query returns the contents off results[]"""

        self.__checkkwargs(**kwargs)
        if self.videoid is None or len(self.videoid) == 0:
            raise ValueError('A valid videoid must be given to find '
                             'caption tracks.')
        dom = super(CaptionSearch, self).query(CaptionSearch.URL,
                                               {'type': 'list',
                                                'v': self.videoid})
        if dom is None:
            return
        self.__parseList(dom)
        return self.results

    def __parseList(self, queryresult):
        tracks = queryresult.getElementsByTagName('track')
        for track in tracks:
            captiontrack = {'videoid': self.videoid}
            captiontrack['name'] = track.getAttribute('name')
            captiontrack['lang'] = track.getAttribute('lang_code')
            captiontrack['lang_orig'] = track.getAttribute('lang_original')
            captiontrack['lang_trans'] = track.getAttribute('lang_translated')
            captiontrack['track_id'] = track.getAttribute('id')
            self.results.append(captiontrack)
            self.results.sort(key=lambda x: x['lang'], reverse=False)


class GetCaptions(Search):

    """Retrieve captions from a youtube video

    The retrieved captions will be stored in results as a UTF-8 encoded
    string, with characters replaced with xml entity reference if needed.

    reset() does not clear lang, name or id. It clears the results
    and resets the search to the beginning."""

    URL = 'http://video.google.com/timedtext'

    def __init__(self, **kwargs):
        """To retrieve captions all of the following must be given:
        lang="language"
        name="trcakname"
        id="somevideoid" or videoid="somevideoid"
        either when creating the class instance or calling query. All of
        this can be obtained with the CaptionSearch class."""

        super(GetCaptions, self).__init__()
        self.reset()
        self.__checkkwargs(**kwargs)

    def __checkkwargs(self, **kwargs):
        for k in kwargs:
            k = k.lower()
            if 'lang' in k:
                self.lang = kwargs[k]
                continue
            if k in ['videoid', 'id']:
                self.videoid = kwargs[k]
                continue
            if k == 'name':
                self.name = kwargs[k]
                continue

    def query(self, **kwargs):
        """To retrieve captions all of the following must be given:
        lang="language"
        name="trcakname"
        id="somevideoid" or videoid="somevideoid"
        either when creating the class instance or calling query. All of
        this can be obtained with the CaptionSearch class.

        returns a string containing the text content of the caption track."""

        self.__checkkwargs(**kwargs)
        if all([self.videoid is None or len(self.videoid) == 0,
                self.lang is None or len(self.lang) == 0,
                self.name is None]):
            print self.videoid, self.lang, self.name
            raise ValueError('videoid, lang and name must all be '
                             'provided to retrieve captions.')

        dom = super(GetCaptions, self).query(GetCaptions.URL,
                                             {'lang': self.lang,
                                              'v': self.videoid,
                                              'name': self.name})
        self.__parseList(dom)
        return self.results

    def __parseList(self, queryresult):
        captiontext = []
        captions = queryresult.getElementsByTagName('text')
        for line in captions:
            captiontext.append(line.childNodes[0].data)
        self.results = ' '.join(captiontext)


class PlaylistVideoSearch(Search):

    """Get the videoids of all videos in a playlist.

    reset() does not clear the playlistid, instead it clears the results
    and resets the search to the beginning."""

    URL = Template('http://gdata.youtube.com/feeds/api/playlists/$playlist')

    def __init__(self, **kwargs):
        """To retrieve videos in a playlist the playlist id must be given as
        id="someplaylistid" or playlistid="someplaylistid" either when
        creating the class instance or calling query(). The list of videos
        will be stored in results[] sorted by the video order in the
        playlist (first video, first in the list)."""

        super(PlaylistVideoSearch, self).__init__()
        self.reset()
        self.__checkkwargs(**kwargs)

    def __checkkwargs(self, **kwargs):
        for k in kwargs:
            k = k.lower()
            if k in ['id', 'playlistid']:
                self.playlistid = kwargs[k]

    def query(self, **kwargs):
        """To retrieve videos in a playlist the playlist id must be given as
        id="someplaylistid" or playlistid="someplaylistid" either when
        creating the class instance or calling query(). The list of videos
        will be stored in results[] sorted by the video order in the
        playlist (first video, first in the list).

        query() returns the contents of results[]"""
        url = PlaylistVideoSearch.URL.substitute({'playlist': self.playlistid})

        self.__checkkwargs(**kwargs)
        if self.playlistid is None or len(self.playlistid) == 0:
            raise ValueError('A valid playlist id must be given to retrieve '
                             'videos.')
        while True:
            dom = super(PlaylistVideoSearch, self).query(url,
                                            {'v': Search.API,
                                             'start-index': self.start,
                                             'max-results': Search.MAXRESULTS})
            if dom is None:
                break
            self.__parseList(dom)
            time.sleep(0.2)  # Lets not hammer the yt servers
        self.results.sort(key=lambda x: x['position'], reverse=False)
        return self.results

    def __parseList(self, queryresult):
        vids = queryresult.getElementsByTagName('entry')
        for vid in vids:
            video = {}
            video['id'] = (vid.getElementsByTagName('yt:videoid')[0].
                                                            childNodes[0].data)
            video['title'] = (vid.getElementsByTagName('title')[0].
                                                            childNodes[0].data)
            video['position'] = int(vid.getElementsByTagName('yt:position')[0].
                                                            childNodes[0].data)
            self.results.append(video)
