import os
import sys
from pyglet import resource, app, media
from mutagen.easyid3 import EasyID3
import random
import time
from threading import Thread

class player:
    def __init__(self, playList):
        self.playList = playList
        self.activePlayer = media.Player()
        self.activePlayer.eos_action = self.activePlayer.EOS_PAUSE
        self.paused = False
        
        mediaHandler = playList.nextSong()
        print "Now playing "+mediaHandler.id3Tags["title"][0]+" by "+mediaHandler.id3Tags["artist"][0]
        self.activePlayer.queue(mediaHandler.songFile)
        self.play()

    def play(self):
        self.activePlayer.play()
        self.paused = False

    def pause(self):        
        self.activePlayer.pause()
        self.paused = True

    def next(self):
        if len(self.playList.playListSongs) <= 0:
            print "End of playlist"
            return

        mediaHandler = self.playList.nextSong()
        print "Now playing "+mediaHandler.id3Tags["title"][0]+" by "+mediaHandler.id3Tags["artist"][0]
        self.activePlayer.queue(mediaHandler.songFile)
        self.activePlayer.next()
        self.activePlayer.play()

    def changePlaylist(self, newPlaylist):
        self.playList = newPlaylist
        self.next()

    def shuffle():
        self.playList.shuffle()

    def repeat():
        self.playList.repeat()

class play_list:
    def __init__(self, criteria):
        allSongs = [song(path) for path in os.listdir(sys.argv[1])]
        self.playListSongs = self.songFilter(allSongs, criteria)
        self.playMode = {"shuffle":False, "repeat":False}

    def shuffle(self):
        self.playMode["shuffle"] = not self.playMode["shuffle"]

    def repeat(self):
        self.playMode["repeat"] = not self.playMode["repeat"]

    def songFilter(self, allSongs, criteria):
        filteredList = allSongs
        criteria = criteria.lower()
        criteria = criteria.strip()
        if criteria.find("by") > 0:
            artist = criteria.split("by")[-1]
            filteredList = [aSong for aSong in allSongs if self.artistCompare(aSong.id3Tags['artist'], artist)]
        
        if not criteria.find("songs") >= 0:
            title = criteria.split("by")[0]
            filteredList = [aSong for aSong in allSongs if self.titleCompare(aSong.id3Tags['title'], title)]
            

        if len(filteredList) > 0:
            return filteredList

        
        print "Can't find "+criteria
        return False

    def artistCompare(self, songArtist, artistName):
        formattedArtist = songArtist[0].upper()
        artistName = artistName.strip()
        artistName = artistName.upper()
        if formattedArtist.find(artistName) >= 0:
            return True

        return False

    def titleCompare(self, songTitle, titleName):
        formattedTitle = songTitle[0].upper()
        titleName = titleName.strip()
        titleName = titleName.upper()
        if formattedTitle.find(titleName) >= 0:
            return True

        return False
    
    def nextSong(self):
        playListSongs = self.playListSongs
        if not playListSongs:
            return

        if self.playMode["shuffle"] and not self.playMode["repeat"]:
            aSong = random.choice(playListSongs)
            playListSongs.remove(aSong)
            return aSong

        if self.playMode["shuffle"] and self.playMode["repeat"]:
            return random.choice(playListSongs)
            

        if not self.playMode["shuffle"] and self.playMode["repeat"]:
            aSong = playListSongs.pop(0)
            playListSongs.append(aSong)
            return aSong

        return playListSongs.pop(0)


class song:
    def __init__(self, path):
        self.songFile = media.load(sys.argv[1]+path)
        self.id3Tags = EasyID3(sys.argv[1]+path)

class appThread(Thread):
    def run(self):
        app.run()

class runThread(Thread):
    def run(self):
        while True:
            print "lol"
            if not myPlayer.activePlayer.playing and not myPlayer.paused and len(myPlayer.playList.playListSongs) > 0:
                myPlayer.next()

started = False

while True:
    line = raw_input()
    if line.upper() == "NEXT":
        myPlayer.next()
    if line.upper() == "PAUSE":
        myPlayer.pause()
    if line.upper() == "RESUME":
        myPlayer.play()
    if line.upper() == "PLAYLIST":
        if started:
            for s in myPlayer.playList.playListSongs:
                print s.id3Tags["title"][0]+" by "+s.id3Tags["artist"][0]
        else:
            print "No current playlist"

    if line.upper().find("PLAY") >= 0:
        line = line.upper().split("PLAY")[1:][0]
        aNewPlayList = play_list(line)
        if aNewPlayList.playListSongs:
            if not started:
                myPlayer = player(aNewPlayList)
                appThread().start()
                started = True
            else:
                myPlayer.changePlaylist(aNewPlayList)
