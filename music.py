import random
import threading
from utils import log
from os import listdir
from pydub import AudioSegment
from pygame import mixer
import config


class MusicPlayer:
    def __init__(self):
        mixer.init()
        self.random_songs = self.find_random_songs()
        self.random_stack = []
        self.ready_to_queue = False
        self.song_queue = []
        self.user_song_currently_playing = None

        # wait before queuing any songs
        if config.wait_to_play:
            time_wait_to_play = config.time_wait_to_play
        else:
            time_wait_to_play = 0
        threading.Timer(interval=time_wait_to_play, function=self.play_song_on_queue).start()

    ## Random songs are currently deprecated. We may want
    ## to add random songs back in, but server-side.
    def find_random_songs(self):
        randomDir = config.audio_dir + config.random_subdir
        random_songs = {}
        for song in listdir(randomDir):
            if not song.startswith('.'):
                random_songs[randomDir+song] = 0
        return random_songs

    ## Random songs are currently deprecated. We may want
    ## to add random songs back in, but server-side.
    def increment_random_song_use(self, song):
        self.random_songs[song] += 1

    ## Random songs are currently deprecated. We may want
    ## to add random songs back in, but server-side.
    def get_random_song(self):
        # generate new random stack, if required
        if len(self.random_stack) == 0:
            min_song_use = float('inf')
            for key, val in self.random_songs.iteritems():
                if val < min_song_use:
                    min_song_use = val
                    random_stack = []
                if val == min_song_use:
                    random_stack.append(key)
            random.shuffle(random_stack)
            self.random_stack = random_stack

        # get next element off of the stack
        song = self.random_stack[0]
        self.random_stack = self.random_stack[1:]
        self.increment_random_song_use(song=song)
        return song

    def play_song_on_queue(self):
        if not self.ready_to_queue:
            self.ready_to_queue = True
            log(message="System now ready to play walk-in songs.")
            self.play_sound(sound_name="activated.wav")
        threading.Timer(interval=config.time_check_queue, function=self.play_song_on_queue).start()

        if not mixer.music.get_busy():
            if self.song_queue:
                # pop the next song off of the front of the queue
                user = self.song_queue[0]
                self.song_queue = self.song_queue[1:]
                # set the user of the currently playing song
                self.user_song_currently_playing = user.name
                # set a timer for long songs
                
                threading.Timer(user.length, self.stop_long_song, [user.name]).start()
                # play the song
                log(message="Playing {name}'s song {song}.".format(name=user.name, song=user.song))
                ## Pygame seems to have issues with MP3 files on certain computers, so this is a hacky way to get around it.
                ## AudioSegment converts it to a wave file so that it will play consistently.
                if user.song.endswith('mp3'):
                    songname=user.song[:-4]
                    mp3song=AudioSegment.from_mp3(user.song)
                    mp3song.export(songname+".wav",format="wav")
                    user.song=user.song[:-4]+".wav"
                mixer.music.load(user.song)
                mixer.music.play()
            else:
                # print "user_song_currently_playing is now None"
                self.user_song_currently_playing = None

    def stop_long_song(self, user_name):
        if self.user_song_currently_playing:
            print 'stopping long song'
            if self.user_song_currently_playing == user_name:
                mixer.music.fadeout(config.time_fadeout_song)           
    
    def queue_song_after_delay(self, user):
        log(message="Queued {name}'s song {song}.".format(name=user.name, song=user.song))
        self.song_queue.append(user)

    def queue_song(self, user):
        if self.ready_to_queue:
            log(message="Waiting delay of {delay} seconds to queue {name}'s song.".format(delay=config.time_delay_to_play_song, name=user.name))
            self.play_sound(sound_name="activity.wav")
            threading.Timer(config.time_delay_to_play_song, self.queue_song_after_delay, [user]).start()

    def play_sound(self, sound_name):
        soundDir = config.audio_dir + config.sound_subdir
        mixer.Sound(soundDir+sound_name).play()
