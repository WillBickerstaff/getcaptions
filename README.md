pyPlaylistCap
=============

A utility to download caption files from all videos in a youtube playlist and convert them to markdown

Useage
======

###s, --search###
Search term, if a playlist id is provided with -p or --playlist, then this option is ignored.
    

###-p, --playlist###
A valid youtube playlist id, if given user and search will be ignored.

###-t, --titlepos###
If the video title has a number of commonly separated elements e.g. "Something - Title - Something" This argument specifies at which position the module title can be found (1 being the first element), use --sep to specify how to break up the video title. If omitted you will be asked to pick a field from that best represents the title from the matching video titles unless attempts to split the title result in only 1 element.

###--sep###
Specifies a string that will be used to break up the video title into fields, this can help with long video titles, that have commonly separated elements and only one is required for titling the caption text, position 1 indicates the first element in the split string. The element at the given position will be converetd to a level 2 heading in the resulting markdown. Default is ' - '.

###--user', '-u'###
Username of the youtube user whose playlists will be searched. Default is 'Udacity'