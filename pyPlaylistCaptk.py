from Tkinter import *
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
        self.createWidgets()
        self.results = []
        self.playlists = []
        self.vids = []
        

    def createWidgets(self):

        Label(text="User", anchor=E).grid(row=0, column=0,
                                          padx=self.padx, pady=self.pady, 
                                          sticky=W)
        self.user_entry = Entry()
        self.user_entry.grid(row=0,column=1, padx=self.padx, pady=self.pady, 
                             sticky=W)
        Label(text="Search terms").grid(row=0, column=3, 
                                        padx=self.padx, pady=self.pady,
                                        sticky=W)
        self.search_terms = Entry()
        self.search_terms.grid(row=0, column=4, padx=self.padx, pady=self.pady,
                               sticky=W)
        Label(text="playlist id").grid(row=1, column=3, 
                                       padx=self.padx, pady=self.pady,sticky=W)
        self.playlist_id = Entry()
        self.playlist_id.grid(row=1, column=4, padx=self.padx, pady=self.pady,
                              sticky=W)
        self.result_label = Label(text="Results")
        self.result_label.grid(row=2,column=0, padx=self.padx, pady=self.pady,
                               sticky=W)
        self.showResultBox()
        self.search_button = Button(text="Search", command=self.search)
        self.search_button.grid(row=2, column=4, 
                                padx=self.padx, pady=self.pady, sticky=E)

        
        self.resultSelect = Button(text='OK', state=DISABLED)
        self.resultSelect.grid(row=5,column=4, sticky=E, 
                               padx=self.padx, pady=self.pady)
        self.status = Label(text="", bd=1, relief=SUNKEN, anchor=W)
        self.status.grid(row=9, column=0, columnspan=10, sticky=N+E+S+W)
        self.addvidcommands()
        self.modtitle.grid_forget()
        self.getcaps.grid_forget()
        self.resultSelect.grid_forget()

    def search(self):
        user = self.user_entry.get()
        playlist = self.playlist_id.get()
        searchterms = self.search_terms.get()
        self.resultSelect.config(state=DISABLED)
        self.modtitle.grid_forget()
        self.getcaps.grid_forget()
        if not self.validparams(user, searchterms, playlist):
            return False

        if len(playlist) > 0:
            self.searchPlaylist(playlist)
            return
        
        self.searchUser(user, searchterms)
        
    def showResultBox(self):
        self.yScroll  =  Scrollbar (orient=VERTICAL )
        self.yScroll.grid ( row=3, column=5, sticky=N+S, )

        self.xScroll  =  Scrollbar (orient=HORIZONTAL )
        self.xScroll.grid ( row=4, column=0, sticky=E+W, columnspan=5 )

        self.listbox = Listbox (xscrollcommand=self.xScroll.set,
                                yscrollcommand=self.yScroll.set,
                                selectmode=SINGLE   )
        self.listbox.grid (row=3, column=0, sticky=N+S+E+W, columnspan=5)
        self.xScroll["command"]  =  self.listbox.xview
        self.yScroll["command"]  =  self.listbox.yview

    def searchPlaylist(self):
        self.getvids(self.playlist_id.get())
    
    def searchUser(self, user, searchterms):
        self.listbox.delete(0,END)
        self.status.config(text="Searching for%splaylists by user \"%s\"" %(
                        " \"%s\" " % searchterms if len(searchterms) else " ",
                        user))
        self.status.update_idletasks()
        usrsearch = lib.yt.search.PlaylistSearch(user=user, search=searchterms)
        self.playlists = []
        try:
            self.playlists = usrsearch.query()
        except HTTPError as e:
            self.status.config(text="User %s does not exist at youtube" % user)
            self.status.update_idletasks()
            return
        if self.playlists is None or len(self.playlists) == 0:
            self.status.config(text="Search returned no results")
            self.status.update_idletasks()
            return
        for i,playlist in enumerate(self.playlists):
            self.listbox.insert(i, playlist['title'])
        self.listbox.activate(0)
        self.resultSelect.config(command=self.getVidsFromSelected,
                                 state=NORMAL)
        self.status.config(text="")
        self.status.update_idletasks()
        self.resultSelect.grid(row=5,column=4, sticky=E, 
                               padx=self.padx, pady=self.pady)
    
    def getVidsFromSelected(self):
        selected = int(self.listbox.curselection()[0])        
        self.getvids(self.playlists[selected]['id'])
        
    def getvids(self, playlistid):
        self.resultSelect.grid_forget()
        vidsearch = lib.yt.search.PlaylistVideoSearch(id=playlistid)
        title = playlistid
        if len(self.playlists) > 0:
            for playlist in self.playlists:
                if playlist['id'] == playlistid:
                    title = playlist['title']
                    break
        
        self.status.config(text="Getting videos for %s" % title)
        self.status.update_idletasks()
        self.listbox.delete(0,END)
        self.vids = vidsearch.query()
        for i,vid in enumerate(self.vids):
            self.listbox.insert(i,vid['title'])
        self.status.config(text="%d Videos found" % len(self.vids))
        self.status.update_idletasks()
        self.addvidcommands()
        
    def addvidcommands(self):
        self.modtitle = Button(text='Modify titles', command=self.modTitles)
        self.modtitle.grid(row=5, column=0, sticky=W, columnspan=2, 
                           padx=self.padx, pady=self.pady)
        self.getcaps = Button(text="Get captions", command=self.getCaptions)
        self.getcaps.grid(row=5, column=2, columnspan=3, sticky=E,
                          padx=self.padx, pady=self.pady)
        
    def getCaptions(self):
        pass
    
    def modTitles(self):
        pass
    
    def validparams(self, user, searchterms, playlist):
        if len(user) == 0 and len(playlist) == 0:
            msg = "Either a valid youtube user or playlist id must be given."
            tkMessageBox.showwarning("missing information", msg)
            return False

        if len(user) > 0 and not self.validstring(user):
            msg = "The user given contains invalid characters"
            tkMessageBox.showwarning('Bad user', msg)
            return False

        if len(playlist) > 0 and not self.validstring(playlist):
            msg = "The playlist given contains invalid characters"
            tkMessageBox.showwarning('Bad playlist', msg)
            return False
        
        if len(searchterms) > 0 and not self.validstring(searchterms, True):
            msg = "The search terms given contain invalid characters"
            tkMessageBox.showwarning('Bad search', msg)        
            return False

        return True

    def validstring(self, s, spacechar=False):
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
