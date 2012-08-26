'''
Created on 19 Aug 2012
@license: MIT License <http://opensource.org/licenses/MIT>
@copyright: 2012 Will Bickerstaff
@author: Will Bickerstaff
@email: will.bickerstaff@gmail.com
'''


from Tkinter import (Button, Listbox, Label, Entry, Frame, Scrollbar, DISABLED,
                     NORMAL, END, N, S, E, W, VERTICAL, HORIZONTAL, SUNKEN,
                     SINGLE, Text, WORD)
import tkMessageBox
import string
import lib.yt.search
import lib.markdown
import lib.trackSelect
from urllib2 import HTTPError
from time import sleep


class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.padx = 3
        self.pady = 3
        self.grid()
        self.results = []
        self.playlists = []
        self.vids = []
        self.__createWidgets()

    def __createWidgets(self):
        self.__searchFields()
        self.__resultArea()
        self.__buttons()
        self.__markdownArea()
        self.bind('<Return>', self.search_button)

    def __buttons(self):
        self.resultSelect = Button(text='OK', state=DISABLED)
        self.resultSelect.grid(row=5, column=4, sticky=E,
                               padx=self.padx, pady=self.pady)
        self.status = Label(text="", bd=1, relief=SUNKEN, anchor=W)
        self.status.grid(row=9, column=0, columnspan=10, sticky=N + E + S + W)
        self.__vidButtons()
        self.__rmVidButtons()
        self.resultSelect.grid_forget()

    def __searchFields(self):
        Label(text="User", anchor=E).grid(row=0, column=0,
                                          padx=self.padx, pady=self.pady,
                                          sticky=W)
        self.user_entry = Entry()
        self.user_entry.grid(row=0, column=1, padx=self.padx, pady=self.pady,
                             sticky=W)
        Label(text="Search terms").grid(row=0, column=3,
                                        padx=self.padx, pady=self.pady,
                                        sticky=W)
        self.search_terms = Entry()
        self.search_terms.grid(row=0, column=4,
                               padx=self.padx, pady=self.pady,
                               sticky=W)
        Label(text="playlist id").grid(row=1, column=3,
                                       padx=self.padx, pady=self.pady,
                                       sticky=W)
        self.playlist_id = Entry()
        self.playlist_id.grid(row=1, column=4, padx=self.padx, pady=self.pady,
                              sticky=W)
        self.search_button = Button(text="Search", command=self.__search)
        self.search_button.grid(row=2, column=4,
                                padx=self.padx, pady=self.pady, sticky=E)

    def __resultArea(self):
        self.result_label = Label(text="Results")
        self.result_label.grid(row=2, column=0,
                               padx=self.padx, pady=self.pady,
                               sticky=W)
        self.resultshowbut = Button(text="View", command=self.__showResults)
        self.resultshowbut.grid(row=2, column=1, sticky=W)
        self.yScroll = Scrollbar(orient=VERTICAL)
        self.xScroll = Scrollbar(orient=HORIZONTAL)
        self.listbox = Listbox(xscrollcommand=self.xScroll.set,
                                yscrollcommand=self.yScroll.set,
                                selectmode=SINGLE)
        self.xScroll.config(command=self.listbox.xview)
        self.yScroll.config(command=self.listbox.yview)

    def __showResults(self):
        self.resultshowbut.config(text="Hide", command=self.__hideResults)
        self.yScroll.grid(row=3, column=5, sticky=N + S)
        self.xScroll.grid(row=4, column=0, sticky=E + W, columnspan=5)
        self.listbox.grid(row=3, column=0, sticky=N + S + E + W, columnspan=5)
        self.markdownarea.config(height=10)

    def __hideResults(self):
        self.resultshowbut.config(text="View", command=self.__showResults)
        self.yScroll.grid_forget()
        self.xScroll.grid_forget()
        self.listbox.grid_forget()
        self.markdownarea.config(height=30)

    def __markdownArea(self):
        self.markdownlabel = Label(text="Markdown")
        self.mdyScroll = Scrollbar(orient=VERTICAL)
        self.mdxScroll = Scrollbar(orient=HORIZONTAL)
        self.markdownarea = Text(wrap=WORD, height=10,
                                 yscrollcommand=self.mdyScroll.set,
                                 xscrollcommand=self.mdxScroll.set)
        self.copymarkdown = Button(text="Copy To Clipboard",
                                  command=self.__copyMarkdown)
        self.mdxScroll.config(command=self.markdownarea.xview)
        self.mdyScroll.config(command=self.markdownarea.yview)

    def __vidButtons(self):
        self.modtitle = Button(text='Modify titles', command=self.__modTitles)
        #self.modtitle.grid(row=5, column=0, sticky=W, columnspan=2,
        #                   padx=self.padx, pady=self.pady)
        self.getcaps = Button(text="Get captions", command=self.__getCaptions)
        self.getcaps.grid(row=5, column=2, columnspan=3, sticky=E,
                          padx=self.padx, pady=self.pady)

    def __rmVidButtons(self):
        self.modtitle.grid_remove()
        self.getcaps.grid_remove()
        self.bind('<Return>', self.search_button)

    def __search(self):
        user = self.user_entry.get()
        playlist = self.playlist_id.get()
        searchterms = self.search_terms.get()
        self.__showResults()
        self.resultSelect.config(state=DISABLED)
        self.__rmVidButtons()
        self.__rmMarkdown()
        if not self.__validparams(user, searchterms, playlist):
            return False

        if len(playlist) > 0:
            self.__searchPlaylist(playlist)
            return

        self.__searchUser(user, searchterms)

    def __showMarkdown(self):
        self.markdownlabel.grid(row=5, column=0,
                                    padx=self.padx, pady=self.pady,
                                    sticky=W)
        self.markdownarea.grid(row=6, column=0, columnspan=5,
                               padx=self.padx, pady=self.pady,
                               sticky=N + S + E + W)
        self.mdyScroll.grid(row=6, column=5, sticky=N + S)
        self.mdxScroll.grid(row=7, column=0, sticky=E + W, columnspan=5)
        self.copymarkdown.grid(row=8, column=2, columnspan=3, sticky=E,
                          padx=self.padx, pady=self.pady)

    def __rmMarkdown(self):
        self.markdownarea.grid_forget()
        self.markdownlabel.grid_forget()
        self.copymarkdown.grid_forget()
        self.mdyScroll.grid_forget()
        self.mdxScroll.grid_forget()

    def __searchPlaylist(self, playlistid):
        self.__getvids(playlistid)

    def __searchUser(self, user, searchterms):
        self.listbox.delete(0, END)
        self.__status("Searching for%splaylists by user \"%s\"" % (
                      " \"%s\" " % searchterms if len(searchterms) else " ",
                      user))
        self.playlists = []
        try:
            self.playlists = lib.yt.search.PlaylistSearch(user=user,
                                                 search=searchterms).query()
        except HTTPError:
            self.__status("User %s does not exist at youtube" % user)
            return
        if self.playlists is None or len(self.playlists) == 0:
            self.__status("Search returned no results")
            return
        self.__populateResults([v['title'] for v in self.playlists])
        self.resultSelect.config(command=self.__getVidsFromSelected,
                                 state=NORMAL)
        self.__status("")
        self.resultSelect.grid(row=5, column=4, sticky=E,
                               padx=self.padx, pady=self.pady)

    def __populateResults(self, values):
        self.listbox.delete(0, END)
        for i, val in enumerate(values):
            self.listbox.insert(i, val)
        self.listbox.activate(0)
        self.listbox.selection_set(0)

    def __getVidsFromSelected(self):
        selected = int(self.listbox.curselection()[0])
        self.__getvids(self.playlists[selected]['id'])

    def __getvids(self, playlistid):
        self.playlist_id.delete(0, END)
        self.playlist_id.insert(0, playlistid)
        self.resultSelect.grid_forget()
        title = playlistid
        if len(self.playlists) > 0:
            for playlist in self.playlists:
                if playlist['id'] == playlistid:
                    title = playlist['title']
                    break

        self.__status("Getting videos for %s" % title)
        self.listbox.delete(0, END)
        try:
            self.vids = lib.yt.search.PlaylistVideoSearch(
                                                    id=playlistid).query()
            self.__populateResults([v['title'] for v in self.vids])
            self.__status("%d Videos found" % len(self.vids))
            self.__vidButtons()
            self.bind('<Return>', self.getcaps)
        except HTTPError:
            self.__status("No videos found! is %s a valid playlist?" %
                          playlistid)

    def __status(self, msg):
        if len(msg) > 75:
            msg = msg[:70] + '...'
        self.status.config(text=msg)
        self.status.update_idletasks()

    def __trackSelect(self, vid, tracks, preftrack=None):
        pref = self.__prefAvailable(preftrack, tracks)
        if pref is None:
            sel = lib.trackSelect.TrackSelect(self, vid=vid,
                                              tracks=tracks)
            if sel.result is None:
                self.__status("skipped")
                tracks = None
            else:
                tracks = [sel.result[0]]
                if sel.preflang is not None:
                    preftrack['lang'] = sel.preflang
                if sel.prefname is not None:
                    preftrack['name'] = sel.prefname
        else:
            tracks = pref
        return tracks, preftrack

    def __getCaptions(self):
        preftrack = {'name': None, 'lang': None}
        self.listbox.delete(0, END)
        self.markdownarea.delete(1.0, END)
        self.__showMarkdown()
        for i, vid in enumerate(self.vids):
            nocapmsg = '[%02d] --NO CAPTIONS-- %s' % (i + 1, vid['title'])
            tracks = lib.yt.search.CaptionSearch(id=vid['id']).query()
            self.vids[i]['text'] = ''
            if len(tracks) == 0:
                self.__status('No captions available for %s' %
                              self.vids[i]['title'])
                self.listbox.insert(END, nocapmsg)

            elif len(tracks) > 1:
                sel = self.__trackSelect(vid, tracks, preftrack)
                if sel[0] is None:
                    msg = '[%02d] --SKIPPED-- %s' % (i + 1, vid['title'])
                    self.listbox.insert(END, msg)
                    self.listbox.see(END)
                    continue
                tracks = sel[0]

            if len(tracks) == 1:
                self.__trackCaps(i, tracks, nocapmsg)
        self.__status('')
        self.__hideResults()

    def __trackCaps(self, vidIndex, tracks, nocapmsg):
        i = vidIndex
        vid = self.vids[i]
        msg = '%02d of %02d Getting captions for %s' % (
                        i + 1, len(self.vids), self.vids[i]['title'])
        self.__status(msg)
        self.listbox.insert(END, msg)
        self.vids[i]['text'] = lib.markdown.heading(vid['title'])
        captiontext = lib.yt.search.GetCaptions(id=vid['id'],
                                lang=tracks[0]['lang'],
                                name=tracks[0]['name']).query()
        sleep(0.2)
        msg = nocapmsg
        if captiontext is not None and len(captiontext) > 0:
            self.vids[i]['text'] += (lib.markdown.to_utf8(captiontext)
                                     + '\n\n')
            msg = '[%02d] --DONE-- %s' % (i + 1, vid['title'])
        self.listbox.delete(END, END)
        self.listbox.insert(END, msg)
        self.listbox.see(END)
        self.markdownarea.insert(END, self.vids[i]['text'])
        self.markdownarea.see(END)

    def __prefAvailable(self, preftrack, tracks):
        if preftrack['lang'] is None:
            return None

        pref = None
        for track in tracks:
            if (track['lang'] == preftrack['lang'] and
                track['name'] == preftrack['name']):
                return [track]
            if track['lang'] == preftrack['lang'] and pref is None:
                pref = [track]

        return pref

    def __modTitles(self):
        pass

    def __validparams(self, user, searchterms, playlist):
        if len(user) == 0 and len(playlist) == 0:
            msg = "Either a valid youtube user or playlist id must be given."
            tkMessageBox.showwarning("missing information", msg)
            return False

        if len(user) > 0 and not self.__validstring(user):
            msg = "The user given contains invalid characters"
            tkMessageBox.showwarning('Bad user', msg)
            return False

        if len(playlist) > 0 and not self.__validstring(playlist):
            msg = "The playlist given contains invalid characters"
            tkMessageBox.showwarning('Bad playlist', msg)
            return False

        if len(searchterms) > 0 and not self.__validstring(searchterms, True):
            msg = "The search terms given contain invalid characters"
            tkMessageBox.showwarning('Bad search', msg)
            return False

        return True

    def __validstring(self, s, spacechar=False):
        validchars = string.letters + string.digits + string.punctuation
        if spacechar:
            validchars += ' '
        for c in s:
            if c not in validchars:
                return False
        return True

    def __copyMarkdown(self):
        self.markdownarea.clipboard_clear()
        self.markdownarea.clipboard_append(self.markdownarea.get(1.0, END))
