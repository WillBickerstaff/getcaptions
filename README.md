pyPlaylistCap
=============

pyPlaylistCap is a utility to retrieve captions from all youtube videos within a playlist and convert them to markdown.


Tkinter branch
==============

This Branch contains a tkInter implementation, It is not yet complete, so far
only searching playlists, and retrieving videos.

##Known Issues##

 - The caption track selection dialog will cause the utility to error and freeze 
if no track is selected and OK is pressed.
 - This dialog is also V.V. annoying with large playlists, need to work on choosing 
a default language / track so we don't keep getting asked.

###TODO###

 - Modify titles
 - Save output / open in external editor
 

###/lib/yt/search.py###
This file contains 5 classes for retrieving playlist information from youtube

###/lib/markdown.py###
Some simple markdown / mathjax conversion of unicode characters