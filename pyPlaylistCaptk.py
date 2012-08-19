from Tkinter import (Button, Listbox, Label, Entry, Frame, Scrollbar, DISABLED,
                     NORMAL, END, N, S, E, W, VERTICAL, HORIZONTAL, SUNKEN,
                     SINGLE)
import tkMessageBox
import string
import lib.yt.search
from urllib2 import HTTPError


class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.padx = 3
        self.pady = 3
        self.grid()
        self.results = []
        self.playlists = []
        self.vids = []
        self.createWidgets()

    def createWidgets(self):
        self.__userEntryFields()
        self.__resultArea()
        self.__buttons()

    def __buttons(self):
        self.search_button = Button(text="Search", command=self.__search)
        self.search_button.grid(row=2, column=4,
                                padx=self.padx, pady=self.pady, sticky=E)

        self.resultSelect = Button(text='OK', state=DISABLED)
        self.resultSelect.grid(row=5, column=4, sticky=E,
                               padx=self.padx, pady=self.pady)
        self.status = Label(text="", bd=1, relief=SUNKEN, anchor=W)
        self.status.grid(row=9, column=0, columnspan=10, sticky=N + E + S + W)
        self.__vidButtons()
        self.__rmVidButtons()
        self.resultSelect.grid_forget()

    def __userEntryFields(self):
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

    def __resultArea(self):
        self.result_label = Label(text="Results")
        self.result_label.grid(row=2, column=0,
                               padx=self.padx, pady=self.pady,
                               sticky=W)
        self.yScroll = Scrollbar(orient=VERTICAL)
        self.yScroll.grid(row=3, column=5, sticky=N + S)

        self.xScroll = Scrollbar(orient=HORIZONTAL)
        self.xScroll.grid(row=4, column=0, sticky=E + W, columnspan=5)

        self.listbox = Listbox(xscrollcommand=self.xScroll.set,
                                yscrollcommand=self.yScroll.set,
                                selectmode=SINGLE)
        self.listbox.grid(row=3, column=0, sticky=N + S + E + W, columnspan=5)
        self.xScroll["command"] = self.listbox.xview
        self.yScroll["command"] = self.listbox.yview

    def __vidButtons(self):
        self.modtitle = Button(text='Modify titles', command=self.__modTitles)
        self.modtitle.grid(row=5, column=0, sticky=W, columnspan=2,
                           padx=self.padx, pady=self.pady)
        self.getcaps = Button(text="Get captions", command=self.__getCaptions)
        self.getcaps.grid(row=5, column=2, columnspan=3, sticky=E,
                          padx=self.padx, pady=self.pady)

    def __rmVidButtons(self):
        self.modtitle.grid_remove()
        self.getcaps.grid_remove()

    def __search(self):
        user = self.user_entry.get()
        playlist = self.playlist_id.get()
        searchterms = self.search_terms.get()
        self.resultSelect.config(state=DISABLED)
        self.__rmVidButtons()
        if not self.__validparams(user, searchterms, playlist):
            return False

        if len(playlist) > 0:
            self.__searchPlaylist(playlist)
            return

        self.__searchUser(user, searchterms)

    def __searchPlaylist(self):
        self.__getvids(self.playlist_id.get())

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
        self.status.config(text="")
        self.status.update_idletasks()
        self.resultSelect.grid(row=5, column=4, sticky=E,
                               padx=self.padx, pady=self.pady)

    def __populateResults(self, values):
        self.listbox.delete(0, END)
        for i, val in enumerate(values):
            self.listbox.insert(i, val)
        self.listbox.activate(0)

    def __getVidsFromSelected(self):
        selected = int(self.listbox.curselection()[0])
        self.__getvids(self.playlists[selected]['id'])

    def __getvids(self, playlistid):
        self.resultSelect.grid_forget()
        title = playlistid
        if len(self.playlists) > 0:
            for playlist in self.playlists:
                if playlist['id'] == playlistid:
                    title = playlist['title']
                    break

        self.__status.config("Getting videos for %s" % title)
        self.listbox.delete(0, END)
        self.vids = lib.yt.search.PlaylistVideoSearch(id=playlistid).query()
        self.__populateResults([v['title'] for v in self.vids])
        self.__status.config("%d Videos found" % len(self.vids))
        self.__vidButtons()

    def __status(self, msg):
        self.status.config(text=msg)
        self.status.update_idletasks()

    def __getCaptions(self):
        pass

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

app = Application()
app.master.title("pyPlaylistCaptk")
app.mainloop()
