from Tkinter import (Scrollbar, Listbox, Checkbutton, Label, N, S, E, W,
                     HORIZONTAL, VERTICAL, Button, END, IntVar, SINGLE,
                     Frame, LEFT, ACTIVE)
import tkSimpleDialog


class TrackSelect(tkSimpleDialog.Dialog):

    def __init__(self, master, **kwargs):
        self.vid = {'title': "this video"}
        self.tracks = []
        for k in kwargs:
            k = k.lower()
            if k == "master":
                self.master = kwargs[k]
                continue
            if k == "vid":
                self.vid = kwargs[k]
                continue
            if k == "tracks":
                self.tracks = kwargs[k]
                continue

        self.padx = 3
        self.pady = 3
        self.prefl = IntVar()
        self.preft = IntVar()
        self.preflang = None
        self.prefname = None
        tkSimpleDialog.Dialog.__init__(self, master, "Select caption track")

    def body(self, master):
        Label(master, text="%s contains multiple caption tracks" %
              self.vid['title']).grid(row=0, padx=self.padx, pady=self.pady,
                                      sticky=W, columnspan=5)
        self.__langlist(master)
        self.chosenlangbut = Button(master, text="->",
                                    command=self.__chooselang)
        self.chosenlangbut.grid(row=1, column=2, padx=self.padx,
                                pady=self.pady)
        self.__tracklist(master)
        self.__fillLangs()
        return self.langsel  # initial focus

    def __tracklist(self, master):
        self.trackYscroll = Scrollbar(master, orient=HORIZONTAL)
        self.trackXscroll = Scrollbar(master, orient=VERTICAL)
        self.tracksel = Listbox(master,
                               xscrollcommand=self.trackXscroll.set,
                               yscrollcommand=self.trackYscroll.set,
                               selectmode=SINGLE)
        self.tracksel.grid(row=1, column=3, sticky=N + S + E + W)
        self.trackXscroll.grid(row=1, column=4, sticky=W + N + S)
        self.trackYscroll.grid(row=2, column=3, stick=N + E + W)
        self.trackXscroll.config(command=self.tracksel.xview)
        self.trackYscroll.config(command=self.tracksel.yview)
        self.preftracksel = Checkbutton(master,
                                        variable=self.preft,
                                        text="Set default track name")
        self.preftracksel.grid(row=3, column=3, sticky=W)

    def __langlist(self, master):
        self.langYscroll = Scrollbar(master, orient=HORIZONTAL)
        self.langXscroll = Scrollbar(master, orient=VERTICAL)
        self.langsel = Listbox(master,
                               xscrollcommand=self.langXscroll.set,
                               yscrollcommand=self.langYscroll.set,
                               selectmode=SINGLE, width=6)
        self.langsel.grid(row=1, column=0, sticky=N + S + E + W)
        self.langXscroll.grid(row=1, column=1, sticky=W + N + S)
        self.langYscroll.grid(row=2, column=0, stick=N + E + W)
        self.langXscroll.config(command=self.langsel.xview)
        self.langYscroll.config(command=self.langsel.yview)
        self.preflangsel = Checkbutton(master,
                                       variable=self.prefl,
                                       text="Set default language")
        self.preflangsel.grid(row=3, column=0, sticky=W)

    def __fillLangs(self):
        self.langsadded = []
        for track in self.tracks:
            lang = track['lang']
            if lang not in self.langsadded:
                self.langsel.insert(END, lang)
                self.langsadded.append(lang)

    def __chooselang(self):
        lang = self.langsadded[int(self.langsel.curselection()[0])]
        self.langselected = lang
        self.trackoptions = []
        self.tracksel.delete(0, END)
        for track in self.tracks:
            if track['lang'] == lang:
                name = 'Default' if len(track['name']) == 0 else track['name']
                self.tracksel.insert(END, name)
                self.trackoptions.append(track)
        self.tracksel.activate(0)
        self.tracksel.selection_set(0)

    def apply(self):
        selected = int(self.tracksel.curselection()[0])
        self.result = [self.trackoptions[selected]]
        if int(self.prefl.get()) == 1:
            self.preflang = self.langselected
        if int(self.preft.get()) == 1:
            self.prefname = self.trackoptions[
                    int(self.tracksel.curselection()[0])]['name']

    def buttonbox(self):
        box = Frame(self)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Skip", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()
