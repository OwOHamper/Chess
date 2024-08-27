from pygame import mixer




class Audio:
    def __init__(self):
        mixer.init()
        # self.sounds = ["game-start", "game-end", "capture", "castle", "premove", "move-self", "move-check", "move-opponent", "promote", "notify", "tenseconds", "illegal"]
        # for sound in self.sounds:
            # mixer.music.load(f"./assets/audio/{sound}.wav")

    def play(self, sound):
        mixer.music.load(f"./assets/audio/{sound}.mp3")
        mixer.music.play()