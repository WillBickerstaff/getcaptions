## /lib/yt/search.py ##

This file contains 5 classes for retrieving playlist information from youtube

### Search ###

The Base class for the other search classes, should not be used directly

*Common Search class useage*
`query()` for everything except GetCaptions returns the first 20 matches.
to retrieve the next 20 matches run `query()` again

The class instances can be created with parameters or they can be set when
calling `query()`:

the most recent results from `query()` are also available in the 
playlist.results attribute.

Calling `reset()` will reset the result list to empty, the search index to the
beginning, which means you will get the first 20 results when you next run
`query()`. Anything passed as an argument when creating the class instance
or running `query()` is left as is.

All classes will raise a ValueError if a required argument is missing when
running `query()` **TODO** Make this do something better

### PlayListSearch ###

This class searches for all playlists, it requires a youtube user name for
the user whose playlists are going to be searched and an optional search
term parameter by which to score the results which is a space separated
list of terms.


    playlists = PlayListSearch(user='someuser', search='some search terms')
    playlists.query()


`query()` returns the result set as list of dicts keyed:

 - 'id' playlist id
 - 'title' playlist title
 - 'score' The search score:

if search terms are given then only playlists whose title match at least one 
search term are returned, without search terms all of the users playlists are
returned with a score of 1.

The results list is ordered by the search score with the highest score first
in the list

### PlaylistVideoSearch ###

PlaylistVideoSearch retrieves all videos in a playlist. The values in the
results list of dicts or return value of `query()` are keyed:

 - 'id' The youtube videoid
 - 'title' The video title
 - 'position' The order the video appears in the playlist

The results list is ordered by position with the first video in the playlist
being the first video in the list.

To perform a `query()` the playlistid must be set either when creating the
class instance or running `query()`


    vids = PlaylistVideoSearch(id='videoid')
    vids.query()


### CaptionSearch ###

CaptionSearch searches for all available caption tracks for a youtube
video. The results list of dicts is keyed:

 - 'videoid' The youtube videoid for which this caption track applies
 - 'lang' The language of the caption track
 - 'name' The name of the caption track

All three of these are required for GetCaptions

The results list is ordered alphapetically by the lang token.

To perform a `query()` the videoid must be set either when creating the class
instance or running `query()`


    caption_tracks = CaptionSearch(id='videoid')
    caption_tracks.query()


### GetCaptions ###

GetCaptions retrieves the text of the caption track. The results attribute
and return value of query are a single string, no encoding or replacement of 
any weird unicode characters is performed. It is returned exactly as it appears
in timedtext, just concatenated into one string with all the time codings removed.

GetCaptions requires lang, name and videoid to be passed either when creating
the class instance or running `query()`. All can be obtained by using a 
CaptionSearch object with the required video.


    captions = GetCaptions(lang='en', name='English', id='videoid')
    captions.query()