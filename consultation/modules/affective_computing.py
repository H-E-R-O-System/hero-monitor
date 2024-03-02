import pygame as pg
import pygame.camera
from consultation.touch_screen import TouchScreen, GameButton, GameObjects
from consultation.display_screen import DisplayScreen
from consultation.screen import Colours, BlitLocation
import os
import cv2
import time
import wave
import pyaudio


class AffectiveModule:
    def __init__(self, size=(1024, 600), parent=None):
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

        self.display_screen.instruction = "I'm listening ..."

        # Additional class properties
        self.listening = False

        self.running = False

        try:
            # pygame.camera.init()
            # self.face_cam = pygame.camera.Camera(size=(1280, 720))
            # self.face_cam.start()
            # self.cam_size = self.face_cam.get_size()

            self.pyaud = pyaudio.PyAudio()
            device_info = self.pyaud.get_default_input_device_info()
            self.audio_rate = int(device_info["defaultSampleRate"])
        except ValueError:
            self.face_cam = None
            self.cam_size = None
            self.pyaud = None
            self.audio_rate = None

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

    def question_loop(self, ):
        self.listening = True
        self.update_display()

        chunk = 1024

        stream = self.pyaud.open(
            format=pyaudio.paInt16, channels=1, rate=self.audio_rate, input=True, frames_per_buffer=chunk)

        image_size = (1280, 720)
        cap = cv2.VideoCapture(0)
        cap.set(3, image_size[0])
        cap.set(4, image_size[1])

        fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        out = cv2.VideoWriter('affective_video.mp4', fourcc, 20, image_size)
        frames = []

        start = time.monotonic()
        # t1 = start
        t2 = time.monotonic()
        while t2 - start < 10:
            data = stream.read(chunk, exception_on_overflow=False)
            # data is a raw bytes object
            frames.append(data)

            ret, frame = cap.read()
            out.write(frame)

            t2 = time.monotonic()

        stream.stop_stream()
        stream.close()

        cap.release()
        out.release()

        wf = wave.open("affective_audio.wav", 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.pyaud.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.audio_rate)
        wf.writeframes(b''.join(frames))
        wf.close()

        print("question complete")

    def exit_sequence(self):
        # post-loop completion section
        # maybe add short thank you for completing the section?

        # only OPTIONAL and can leave blank
        ...

    def loop(self):
        self.entry_sequence()
        while self.running:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_s:
                        if self.parent:
                            self.parent.take_screenshot()
                        else:
                            img_array = pg.surfarray.array3d(self.window)
                            img_array = cv2.transpose(img_array)
                            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                            cv2.imwrite("screenshots/affective.png", img_array)
                        ...
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
                            self.display_screen.instruction = "Press the button to start"
                            self.main_button.text = "I'm finished"
                            self.question_loop()

                        self.update_display()
                    ...

                elif event.type == pg.QUIT:
                    # break the running loop
                    self.running = False

        self.exit_sequence()


if __name__ == "__main__":
    os.chdir("/Users/benhoskings/Documents/Pycharm/Hero_Monitor")

    pg.init()
    # Module Testing
    module_name = AffectiveModule()
    module_name.loop()
    print("Module run successfully")
