import pygame as pg
from consultation.touch_screen import TouchScreen, GameButton, GameObjects
from consultation.display_screen import DisplayScreen
from consultation.screen import Colours, BlitLocation
from consultation.utils import take_screenshot
import cv2
import wave
import pyaudio
import os

import shutil

class AffectiveModulePi:
    def __init__(self, size=(1024, 600), parent=None, pi=True, cleanse_files=True):

        self.parent = parent
        if parent is not None:
            self.display_size = parent.display_size
            self.bottom_screen = parent.bottom_screen
            self.top_screen = parent.top_screen
            self.display_screen = DisplayScreen(self.display_size, avatar=parent.avatar)

        else:
            self.display_size = pg.Vector2(size)
            self.window = pg.display.set_mode((self.display_size.x, self.display_size.y * 2), pg.SRCALPHA)

            self.top_screen = self.window.subsurface(((0, 0), self.display_size))
            self.bottom_screen = self.window.subsurface((0, self.display_size.y), self.display_size)
            self.display_screen = DisplayScreen(self.display_size)

        self.touch_screen = TouchScreen(self.display_size)

        self.display_screen.speech_text = "Have you noticed anything this past week?"

        button_size = pg.Vector2(self.display_size.x*0.9, self.display_size.y*0.15)
        self.main_button = GameButton(pg.Vector2(0.5*self.display_size.x, 0.85*self.display_size.y) - button_size / 2,
                                      button_size, id=1, text="Begin", colour=Colours.hero_blue)
        self.touch_screen.sprites = GameObjects([self.main_button])

        # Additional class properties
        self.listening = False

        self.running = False
        self.pi = pi

        self.question_idx = 0

        if pi:
            picamera = __import__('picamera2')
            self.picam = picamera.Picamera2()
            config = self.picam.create_preview_configuration()
            self.picam.configure(config)
            self.cv2_cam = None

        else:
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # this is the magic!

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

            self.cv2_cam = cv2.VideoCapture(0)
            self.picam = None
            print("pi not specified, will use cv2 instead")

        if not os.path.isdir("data/affective_images"):
            os.mkdir("data/affective_images")

        if not os.path.isdir("data/nlp_audio"):
            os.mkdir("data/nlp_audio")

        try:
            self.pyaud = pyaudio.PyAudio()
            device_info = self.pyaud.get_default_input_device_info()
            self.audio_rate = int(device_info["defaultSampleRate"])

        except ValueError:
            print("Microphone error")
            self.pyaud = None
            self.audio_rate = None

        self.cleanse_files = cleanse_files

    def update_display(self):
        self.touch_screen.refresh()

        if self.listening:
            self.touch_screen.load_image("consultation/graphics/listening.png", size=pg.Vector2(300, 300),
                                         pos=pg.Vector2(self.display_size.x*0.5, self.display_size.y*0.4),
                                         location=BlitLocation.centre)

        self.top_screen.blit(self.display_screen.get_surface(), (0, 0))
        self.bottom_screen.blit(self.touch_screen.get_surface(), (0, 0))
        pg.display.flip()

    def entry_sequence(self):
        # pre-loop initialisation section
        # add everything needed to introduce your module and explain
        # what the users are expected to do (e.g. game rules, aim, etc.)
        self.running = True
        self.display_screen.instruction = "Press the button to start"
        self.update_display()  # render graphics to main consult
        # add code below

    def question_loop(self, max_time=10):
        self.display_screen.instruction = "Press the button to stop"
        self.main_button.text = "I'm finished"
        self.display_screen.refresh()
        self.update_display()

        if not os.path.isdir(f"data/affective_images/question_{self.question_idx}"):
            os.mkdir(f"data/affective_images/question_{self.question_idx}")

        self.listening = True
        self.update_display()

        chunk_size = 1024
        stream = self.pyaud.open(format=pyaudio.paInt16, channels=1, rate=int(self.audio_rate), input=True, frames_per_buffer=chunk_size)
        frames = []

        iter_per_second = int((self.audio_rate / chunk_size))
        for i in range(0, iter_per_second * max_time):
            data = stream.read(chunk_size, exception_on_overflow=False)
            # data is a raw bytes object
            frames.append(data)

            if self.picam:
                self.picam.capture_file(f"data/affective_images/question_{self.question_idx}/im_{i}.png")

            elif self.cv2_cam:
                ret, frame = self.cv2_cam.read()
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
                cv2.imwrite(f"data/affective_images/question_{self.question_idx}/im_{i}.png", frame)

        stream.stop_stream()
        stream.close()

        wf = wave.open(f"data/nlp_audio/question_{self.question_idx}.wav", 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.pyaud.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.audio_rate)
        wf.writeframes(b''.join(frames))
        wf.close()

        if self.picam:
            self.picam.stop()

        if self.cv2_cam:
            self.cv2_cam.release()

        print("question complete")

        self.display_screen.instruction = "Press the button to start"
        self.main_button.text = "begin"
        self.display_screen.refresh()
        self.update_display()

    def exit_sequence(self):
        # post-loop completion section
        # maybe add short thank you for completing the section?

        # only OPTIONAL and can leave blank
        if self.cleanse_files:
            print("cleansing files")
            shutil.rmtree("data/affective_images")
            shutil.rmtree("data/nlp_audio")
            print(f"successfully cleansed files")

    def loop(self):
        self.entry_sequence()
        while self.running:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_s:
                        if self.parent:
                            take_screenshot(self.parent.window)
                        else:
                            take_screenshot(self.window, "affective_module")

                    elif event.key == pg.K_ESCAPE:
                        self.running = False

                elif event.type == pg.MOUSEBUTTONDOWN:
                    # do something with mouse click
                    if self.parent:
                        pos = self.parent.get_relative_mose_pos()
                    else:
                        pos = pg.Vector2(pg.mouse.get_pos()) - pg.Vector2(0, self.display_size.y)

                    button_id = self.touch_screen.click_test(pos)
                    if button_id is not None:
                        if button_id:
                            self.question_loop()

                        # self.update_display()

                elif event.type == pg.QUIT:
                    # break the running loop
                    self.running = False

        self.exit_sequence()


if __name__ == "__main__":
    os.chdir("/Users/benhoskings/Documents/Pycharm/Hero_Monitor")

    pg.init()
    # Module Testing
    module_name = AffectiveModulePi(pi=False)
    module_name.loop()
    print("Module run successfully")
