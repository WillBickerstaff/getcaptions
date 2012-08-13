import urllib2
import os
import sys
import argparse
import datetime
import time
from xml.dom.minidom import parseString
from string import Template

PlaylistFeed = Template('http://gdata.youtube.com/feeds/api/users/$user/'
                        'playlists?v=2&start-index=$start_index'
                        '&max-results=$max_results')
AvailCaptions = Template('http://www.youtube.com/api/timedtext?'
                         'type=list&v=$videoid')
CaptionTrack = Template('http://video.google.com/timedtext?'
                        'lang=$lang&v=$videoid&name=$name')
VideoList = Template('http://gdata.youtube.com/feeds/api/playlists/'
                     '$playlist?v=2&start-index=$start_index'
                     '&max-results=$max_results')

Messages = {'NotAPlaylist': Template('$playlist is not a valid '
                                     'youtube playlist.'),
            'NoResults': Template('No results were found for $search.'),
            'NoCaptions': Template('No captions are available for $track'),
            'PartMacth': Template('These $type matched your search for: '
                                  '$search_match.'),
            'ShowList': Template('Enter $print_key to print the list again '
                                 'or $giveup_key to give up!'),
            'NumberOpt': Template('Enter a number between $low_num and '
                                  '$high_num: '),
            'MissingResult': Template('No $missing found for $search.'),
            'Getting': Template('Retriving $get for $item.'),
            'BadForm': Template('$param is not valid, a valid form for '
                                '$param is $valid.'),
            'Invalid': Template('$value is not a valid option.'),
            'Retrieving': Template('$number Retrieving $media, for $source.')
            }

defaults = {'max_results': 20, 'rev': 1, 'reprint_key': 'p'}

scriptName = os.path.splitext(os.path.basename(sys.argv[0]))[0]
errorlog = os.path.join(os.getcwd(), scriptName + '_error.log')

nicerequests = 0.0  # period of time between requests
lastrequest = time.time() - (nicerequests + 1)


class HTTPGETError(object):
    def __init__(self):
        self.code = 0
        self.msg = ''
        self.url = ''


def wikilinks(course, unit, rev):
    """ Make links to the previous and next unit wiki pages """
    links = ''
    prevwiki = 1 if unit < 2 else unit - 1
    nextwiki = 7 if unit > 6 else unit + 1

    for i in range(prevwiki, nextwiki + 1):
        links += ("[%(course)s Unit %(unit)d]"
                  "(/wiki/%(course)s Unit %(unit)d) |" % {'course': course,
                                                        'unit': i})
    return links


def header(course, unit, rev=1):
    """ Make a header containing various links """
    return ("[Back to course page](/wiki/%(course)s) | "
            "%(wikilinks)s "
            "[Overview](/overview/Course/%(course)s/%(rev)s) | "
            "[Classroom](/view#Course/%(course)s/%(rev)s) | "
            "[Discussion](http://forums.udacity.com/%(course)s) | "
            "[Wiki](/wiki/%(course)s) | "
            "[Announcements](/announcements#Course/%(course)s/%(rev)s) | "
            "[Progress](/progress#Course/%(course)s/%(rev)s) | "
            "[Print this page](/wiki/%(course)s Unit %(unit)d?action=print) | "
            "[Save as PDF](/wiki/%(course)s "
                "Unit (unit)d?action=CreatePdfDocument)\n\n"
            "#%(course)s Unit %(unit)d#\n\n"
            "**These are draft notes from subtitles, please help improving "
            "them. Thank you!**\n\n"
            "[TOC]" % {'course': course,
                     'unit': unit,
                     'wikilinks': wikilinks(course, unit, rev),
                     'rev': "CourseRev/%d" % rev})


def setnicerequests(numresults=0):
    """Slow down the HTTP Request rate if there looks like there are lots
of results so as we don't hammer the server
"""
    global nicerequests

    if numresults > 50:
        nicerequests = 1.0
    else:
        nicerequests = 0.5


def findPlaylist(user, search):
    """ Search for a playlist """
    setnicerequests()
    start = 1
    possiblelists = []
    total_results = 0

    print Messages['Retrieving'].substitute(
                                      {'number': '',
                                       'media': 'playlists',
                                       'source': '%s (%s)' % (user, search)})
    while True:
        requesturl = PlaylistFeed.substitute({
                                       'user': user,
                                       'start_index': start,
                                       'max_results': defaults['max_results']})
        data = HTTPGET(requesturl)

        if len(possiblelists) == 0 and (data is None or len(data) == 0):
            print Messages['NoResults'].substitute(
                                      {'search': 'User %s' % user})
            sys.exit(0)

        dom = parseString(data)
        if start == 1:
            total_results = getmaxsetnice(dom)

        entries = dom.getElementsByTagName('entry')

        for x in entries:
            title = x.getElementsByTagName('title')[0].childNodes[0].data
            listid = (x.getElementsByTagName('yt:playlistId')[0].
                                                           childNodes[0].data)
            if len(title) == 0 or len(listid) == 0:
                continue
            matchscore = insearch(title, search)
            if matchscore > 0:
                possiblelists.append(tuple([title, listid, matchscore]))

        start += defaults['max_results']
        if start > total_results:
            break

    if len(possiblelists) < 1:
        print Messages['NoResults'].substitute(
                    {'search': 'user %s matching "%s"' % (user, search)})
        sys.exit(0)
    elif len(possiblelists) == 1:
        return possiblelists[0]

    possiblelists = removedups(possiblelists, 1, 2)
    possiblelists = toppercentage(possiblelists, 2, 25)
    possiblelists.sort(key=lambda x: x[2], reverse=True)

    assert len(possiblelists) > 0

    return suggestlists(possiblelists)


def getmaxsetnice(dom):
    total_results = int(
        dom.getElementsByTagName('openSearch:totalResults')[0].
                                                           childNodes[0].data)
    setnicerequests(total_results)
    return total_results


def insearch(haystack, needles):
    """Search within a string"""
    score = 0
    search_terms = needles.split()
    max_term_score = len(search_terms)
    for item_score, term in enumerate(search_terms):
        if term.lower() in haystack.lower():
            score += (max_term_score - item_score)
    return score


def removedups(lists, key, score_index=-1):
    """ remove duplicates from a list of lists based on a single unique
    element"""
    new_list = []
    for item in lists:
        add_item = True
        for i, new_item in enumerate(new_list):
            if item[key] == new_item[key]:
                if score_index >= 0 and (new_item[score_index] >
                                         item[score_index]):
                    new_list.pop(i)
                    new_list.append(item)
                add_item = False
                break
        if add_item:
            new_list.append(item)
    return new_list


def toppercentage(lists, score_index, percentage=10):
    """Strip everything but the given percentage amount from a list"""
    scores = [s[score_index] for s in lists]
    top_score = max(scores)
    accept_score = top_score - ((top_score / 100.0) * percentage)
    new_list = [i for i in lists if i[score_index] > accept_score]
    assert len(new_list) > 0
    return new_list


def printlists(lists, maxresults=-1):
    """Print a list with numbers """
    for n, lst in enumerate(lists):
        print"[%2d] %s" % (n + 1, lst[0])
        if n > maxresults > 0:
            break


def suggestlists(playlists):
    """Suggest playlists that might match the search """
    return playlists[listselect(playlists)]


def listselect(lists, otherchars=None):
    """Select an item from a list """
    termWidth = os.popen('stty size', 'r').read().split()[0]
    printlists(lists, int(termWidth) - 4)
    print_key = defaults['reprint_key']
    print Messages['ShowList'].substitute({'print_key': print_key,
                                            'giveup_key': '0'})
    maxnum = len(lists)
    sel = -1
    while sel < 0:
        print Messages['NumberOpt'].substitute({'low_num': 1,
                                                 'high_num': maxnum}),
        sel = numberselect(1, maxnum, [print_key])
        try:
            sel = int(sel)
        except ValueError:
            if sel == print_key:
                printlists(lists)
                sel = -1
        return sel - 1


def numberselect(minnum, maxnum, otherchars=None):
    """Check a number given in response to a question is valid """
    sel = -1

    while sel < 0:
        sel = sys.stdin.readline()
        print ''
        sel = sel.strip()
        if otherchars and sel in otherchars:
            return sel
        try:
            sel = int(sel)
            if maxnum >= sel > 0:
                return sel
            elif sel == 0:
                sys.exit(2)
            print Messages['NumberOpt'].substitute({'low_num': minnum,
                                                 'high_num': maxnum})
            sel = -1
        except ValueError:
            print Messages['NumberOpt'].substitute({'low_num': minnum,
                                                 'high_num': maxnum})
            sel = -1
            continue


def getvids(playlistid):
    """Get the list of videos in a playlist"""
    total_results = 0
    start = 1
    numresults = defaults['max_results']
    vids = []

    while True:
        requesturl = VideoList.substitute({'playlist': playlistid,
                                           'start_index': start,
                                           'max_results': numresults})
        data = HTTPGET(requesturl)
        if data is None:
            break
        dom = parseString(data)
        if start == 1:
            total_results = getmaxsetnice(dom)
        v = getvidinf(dom)
        for vid in v:
            vids.append(vid)
        start += numresults
        if start > total_results:
            break

    return vids


def getvidinf(dom):
    """Get the video id and title from the playlist"""
    entries = dom.getElementsByTagName('entry')
    vids = []

    for vid in entries:
        title = vid.getElementsByTagName('title')[0].childNodes[0].data
        vidid = vid.getElementsByTagName('yt:videoid')[0].childNodes[0].data
        assert all([vidid is not None, len(vidid) > 0])
        if title is None or len(title) == 0:
            title = vidid
        vids.append([title, vidid])

    return vids


def getcaptions(title, vidid, vidno=0, vidof=0):
    """Retrieve the captions for a video"""
    captracks = getcaptiontracks(vidid)

    if captracks is None:
        logError(Messages['NoCaptions'].substitute({'track': '%s (%s)'
                                                    % (title, vidid)}))
        return '\n**No captions available**\n'

    lang = captracks[0][0]
    name = captracks[0][1]

    if len(captracks) > 1:
        preferredcap = selectcaptions(captracks)
        lang = captracks[preferredcap][0]
        name = captracks[preferredcap][1]

    vidnums = ''
    if vidno > 0:
        vidnums = "%2d%s" % (vidno, " of %2d - " % vidof if vidof > 0 else ' ')
    source = "%s (%s)" % (title, vidid)
    print Messages['Retrieving'].substitute({'number': vidnums,
                                             'media': 'captions',
                                             'source': source})

    requesturl = CaptionTrack.substitute({'lang': lang,
                                          'name': name,
                                          'videoid': vidid})
    data = HTTPGET(requesturl)

    if data is None or len(data) == 0:
        logError(Messages['NoCaptions'].substitute({'track': '%s (%s)'
                                                    % (title, vidid)}))
        return '\n**No captions available**\n'

    dom = parseString(data)
    return textonly(dom)


def selectcaptions(tracks):
    """Select a caption track if multiple tracks exist """
    print "Lang\tName"
    nicelist = [x[0] + '\t' + x[1] for x in tracks]

    return tracks[listselect(nicelist)]


def getcaptiontracks(vidid):
    """Get the list of caption tracks"""
    requesturl = AvailCaptions.substitute({'videoid': vidid})
    data = HTTPGET(requesturl)

    if data is None or len(data) == 0:
        return None

    dom = parseString(data)
    tracks = dom.getElementsByTagName('track')
    availtracks = []

    for captiontrack in tracks:
        trackinf = [None, None]

        if captiontrack.hasAttribute('name'):
            trackinf[1] = captiontrack.getAttribute('name')
        if captiontrack.hasAttribute('lang_code'):
            trackinf[0] = captiontrack.getAttribute('lang_code')
        if trackinf[0] and trackinf[1]:
            availtracks.append(trackinf)

    if len(availtracks) > 0:
        return availtracks

    return None


def textonly(xml):
    """Remove the time coding elements from the caption track and return
only the text
"""
    textnodes = xml.getElementsByTagName('text')
    text = ''

    for node in textnodes:
        text += node.childNodes[0].data + ' '

    while text.find('  ') != -1:
        text = text.replace('  ', ' ')

    return text


def urlreplacespaces(url):
    """Replace any space in urls with %20, we get bad requests without this
"""
    return url.replace(' ', '%20')


def HTTPGET(url, supresserrors=False):
    """Fetch a url, and honour nicerequests"""
    url = urlreplacespaces(url)
    lastrequest = time.time()

    while time.time() - lastrequest < nicerequests:
        time.sleep(0.1)
    try:
        feed = urllib2.urlopen(url)
    except urllib2.URLError as e:
        feed = HTTPGETError()
        feed.msg = e.msg
        if not supresserrors:
            feed.url = url
            logHTTPError(feed)
        return None

    except Exception as error:
        raise error

    if 200 <= feed.code < 300:
        data = feed.read()
        feed.close()
        return data
    else:
        logHTTPError(feed)
        return None


def logHTTPError(error):
    """Log any HTTP errors"""
    msg = "%d - %s; %s\n" % (error.code, error.msg, error.url)
    logError(msg)


def logError(message):
    """Write something to the error log """
    with open(errorlog, 'a') as logfile:
        line = "%s\n" % message
        logfile.write('[%s] : %s' % (datetime.datetime.now(), line))
        print line


def cleantitle(title, pos, sep):
    """Get the module title text from the video title """
    t = title.split(sep)[pos]
    return t.strip()


def markdown(vid):
    """Convert the caption text to markdown """
    return asciireplace('\n\n##%s##\n%s' % (vid[0], vid[2]))


def asciireplace(md):
    """Replace some odd unicode characters with ascii or mathjax
representations """
    charactermap = [["&#39;", "'"],
                    [u"\u2014", "-"],
                    [u"\xb5", "u"],
                    [u"\u2019", "'"],
                    [u"\u2295", "$% \oplus $%"],
                    [u"\xb7", "$% \cdot $%"],
                    [u"\u2192", "$% \to $%"],
                    [u"\xe9", "e"],
                    [u"\xe4", "a"]
                   ]

    for c in charactermap:
        md = md.replace(c[0], c[1])
    return md


def selecttitletext(vidlist):
    """Ask the user which part of the video title best represents the
module title """
    maxlen, minlen = printvids(vidlist)
    print "----",

    for x in range(1, maxlen + 1):
        print "-" * 21,
    print '\n    |',

    for x in range(1, maxlen + 1):
        print "{:^19s}| ".format("%d" % x if x <= minlen else ''),
    print "\n----",

    for x in range(1, maxlen + 1):
        print "-" * 21,

    print"\n\nSelect which field best represents most modules titles: "
    print Messages['NumberOpt'].substitute({'low_num': 1,
                                            'high_num': minlen}),
    sel = numberselect(1, minlen) - 1

    return sel


def titleelements(vidlist):
    """Print the video list"""
    splitvids = []

    for vid in vidlist:
        fields = vid[0].split(' - ')
        fields.append(vid[1])
        splitvids.append(fields)

    maxlen = max([len(x)for x in splitvids])
    minlen = min([len(x)for x in splitvids])
    return splitvids, maxlen, minlen


def printvids(vidlist):
    splitvids = titleelements(vidlist)

    for i, v in enumerate(splitvids[0]):
        print "[{:2d}] ".format(i + 1),

        for v in v:
            if len(v) >= 18:
                v = v[:15] + '...'
            print"{:<19s}| ".format(v),
        print ''

    return splitvids[1:]


def parseArgs():
    parser = argparse.ArgumentParser(
        description=("""A utility to download caption files from all videos in
 a youtube playlist and convert them to markdown"""))
    parser.add_argument('-s', '--search', dest='search',
            help=("""Search term, if a playlist id is provided with -p or
 --playlist, then this option is ignored."""))
    parser.add_argument('-p', '--playlist', dest='playlist',
            help=("""A valid youtube playlist id, if given user and search
 will be ignored."""))
    parser.add_argument('-t', '--titlepos', dest='titlepos', type=int,
            help=("""If the video title has a number of commonly separated
 elements e.g. "Something - Title - Something" This argument specifies at
 which position the module title can be found (1 being the first element), use
 --sep to specify how to break up the video title. If omitted you will be
 asked to pick a field from that best represents the title from the matching
 video titles unless attempts to split the title result in only 1 element"""))
    parser.add_argument('--sep', dest='sep',
            default=' - ',
            help=("""Specifies a string that will be used to break up the
 video title into fields, this can help with long video titles, that have
 commonly separated elements and only one is required for titling the caption
 text, position 1 indicates the first element in the split string. The
 element at the given position will be converetd to a level 2 heading in the
 resulting markdown."""))
    parser.add_argument('--user', '-u', dest='user',
            default='Udacity',
            help=("""Username of the youtube user whose playlists will be
 searched"""))
    return parser.parse_args()


def main():
    global args
    args = parseArgs()
    outputfile = None
    playlist = None
    titlepos = None
    if vars(args)['playlist'] is not None:
        playlist = args['playlist']
    elif vars(args)['user'] is not None and vars(args)['search'] is not None:
        playlistinf = findPlaylist(vars(args)['user'], vars(args)['search'])
        playlist = playlistinf[1]
        assert playlist is not None
        outputfile = os.path.join(os.getcwd(), playlistinf[0] + '.md')

    playlistvids = getvids(playlist)
    numvids = len(playlistvids)
    md = ''
    if vars(args)['titlepos'] is None:
        titlepos = selecttitletext(playlistvids)
    else:
        titlepos = vars(args)['titlepos']

    for i, vid in enumerate(playlistvids):
        playlistvids[i][0] = cleantitle(vid[0] + vars(args)['sep'] + vid[1],
                                        titlepos,
                                        vars(args)['sep'])
        playlistvids[i].append(getcaptions(vid[0], vid[1], i + 1, numvids))
        playlistvids[i][2] = markdown(vid)
        md += playlistvids[i][2]

    with open(outputfile, 'w') as out:
        out.write(md)
        print "\nMarkdown has been written to:\n\t%s" % outputfile

if __name__ == "__main__":
    main()
