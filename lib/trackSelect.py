from Tkinter import *
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
        tkSimpleDialog.Dialog.__init__(self, master, "Select caption track")

    def body(self, master):
        

        Label(master, text="%s contains multiple caption tracks" %
              self.vid['title']).grid(row=0, padx=self.padx, pady=self.pady,
                                      sticky=W, columnspan=5)

        self.langYscroll = Scrollbar(master, orient=HORIZONTAL)
        self.langXscroll = Scrollbar(master, orient=VERTICAL)
        self.langsel = Listbox(master, xscrollcommand=self.langXscroll,
                               yscrollcommand=self.langYscroll,
                               selectmode=SINGLE)
        self.langsel.grid(row=1, column=0, sticky=N + S + E + W)
        self.langXscroll.grid(row=1, column=1, sticky=W + N + S)
        self.langYscroll.grid(row=2, column=0, stick=N + E + W)

        self.chosenlangbut = Button(master, text="->", 
                                    command=self.__chooselang)

        self.chosenlangbut.grid(row=1, column=2, padx=self.padx,
                                pady=self.pady)

        self.trackYscroll = Scrollbar(master, orient=HORIZONTAL)
        self.trackXscroll = Scrollbar(master, orient=VERTICAL)
        self.tracksel = Listbox(master, xscrollcommand=self.trackXscroll,
                               yscrollcommand=self.trackYscroll,
                               selectmode=SINGLE)
        self.tracksel.grid(row=1, column=3, sticky=N + S + E + W)
        self.trackXscroll.grid(row=1, column=4, sticky=W + N + S)
        self.trackYscroll.grid(row=2, column=3, stick=N + E + W)


        self.__fillLangs()

        return self.langsel # initial focus

    def __fillLangs(self):
        self.langsadded = []
        for track in self.tracks:
            lang = track['lang']
            if lang not in self.langsadded:
                self.langsel.insert(END, lang)
                self.langsadded.append(lang)

    def __chooselang(self):
        lang = self.langsadded[int(self.langsel.curselection()[0])]
        self.trackoptions = []
        self.tracksel.delete(0, END)
        for track in self.tracks:
            if track['lang'] == lang:
                name = 'Default' if len(track['name']) == 0 else track['name']
                self.tracksel.insert(END, name)
                self.trackoptions.append(track)
        self.tracksel.activate(0)

    def apply(self):
        selected = int(self.tracksel.curselection()[0])
        if not (len(self.trackoptions) > selected > -1):
            selected = 0
        self.result = self.trackoptions[selected]
