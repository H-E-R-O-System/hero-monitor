import os
import time
from transformers import AutoProcessor, SeamlessM4TModel, SeamlessM4TForTextToSpeech
import pygame as pg
import math
import pyaudio
from consultation.screen import Screen, BlitLocation, Fonts, Colours
from avatar import Avatar
import multiprocessing
from multiprocessing.connection import Connection

language_codes = {"English": "eng", "German": "deu"}
from scipy.io.wavfile import write, read
import wave


class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age


class ConsultConfig:
    def __init__(self):
        self.speech = True
        self.text = True
        self.output_lang = language_codes["English"]
        self.input_lang = language_codes["English"]


def load_models(sender_connection: Connection):
    processor = AutoProcessor.from_pretrained("facebook/hf-seamless-m4t-medium")
    model = SeamlessM4TModel.from_pretrained("facebook/hf-seamless-m4t-medium")
    t2s = SeamlessM4TForTextToSpeech.from_pretrained("facebook/hf-seamless-m4t-medium")

    sender_connection.send([processor, model, t2s])
    return None


class Consultation:
    def __init__(self, p, user=None, load_on_startup=True):
        """
        Object for running the consultation

        :param p: initialised PyAudio object
        :param user: user data with name, age, etc.
        :param load_models: load language models on start-up or not. Will be loaded when needed if set to False.
        """

        if user:
            self.user = user
        else:
            # create demo user
            self.user = User("Demo", 65)

        self.config = ConsultConfig()

        self.display_size = pg.Vector2(1024, 600)

        # load all attributes which utilise any pygame surfaces!

        self.window = pg.display.set_mode(self.display_size, pg.SRCALPHA)
        self.main_panel = self.window.subsurface(((0, 0), (math.floor(self.display_size.x * 0.6), self.display_size.y)))
        self.info_panel = self.window.subsurface(((self.main_panel.get_size()[0], 0),
                                                  (self.display_size.x - self.main_panel.get_size()[0],
                                                   self.display_size.y)))

        self.fonts = Fonts()
        self.main_screen = Screen(self.main_panel.get_size(), self.fonts.normal, colour=Colours.white.value)
        self.info_screen = Screen(self.info_panel.get_size(), self.fonts.normal, colour=Colours.lightGrey.value)

        # add unchanging items to info screen
        self.info_screen.add_text(f"Name: {self.user.name}", (10, 30), base=True)
        self.info_screen.add_text(f"Age: {self.user.age}", (10, 80), base=True)

        self.avatar = Avatar(size=(256, 256 * 1.125))

        self.action = "Initialising"

        self.p = p
        self.questions = ["how are you feeling today?",
                          "How were your tremors over the past few days?",
                          "how is your mood?"]
        self.question_idx = 0
        self.running = True

        self.processor = None
        self.model = None
        self.t2s = None
        self.models_loaded = False

        if load_on_startup:
            process = multiprocessing.Process(target=load_models, args=(sender,))
            process.daemon = True
            process.start()
            self.processor, self.model, self.t2s = self.loading_screen(receiver, "Loading language models")
            self.models_loaded = True

        self.action = "None"
        self.avatar.state = 0
        self.update_info_screen()
        self.update_main_screen("Press Q to start")
        self.update_display()

    def loading_screen(self, receiver_connection, text=None):
        start_time = time.monotonic()
        self.action = "Loading models"
        self.avatar.state = 2
        self.update_info_screen()
        self.update_main_screen(text)
        self.update_display()

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    quit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        quit()

            if receiver_connection.poll():
                return receiver_connection.recv()

            if (time.monotonic() - start_time) > 2:
                self.update_main_screen("Loading language models")
                self.update_display()
                self.avatar.whistle_state = (self.avatar.whistle_state + 1) % 2
                start_time = time.monotonic()

    def update_display(self):
        self.main_panel.blit(self.main_screen.surface, (0, 0))
        self.info_panel.blit(self.info_screen.surface, (0, 0))
        pg.display.flip()

    def update_info_screen(self, time_left=None):
        # clear info screen
        self.info_screen.refresh()
        self.info_screen.add_text(f"Current Job: {self.action}", (10, 150))

        if time_left:
            self.info_screen.add_text(f"Time left: {time_left}", (10, 200))

    def update_main_screen(self, text=None):
        self.main_screen.refresh()
        self.main_screen.add_surf(self.avatar.get_surface(),
                                  pos=(self.main_screen.size.x / 2, self.main_screen.size.x / 3),
                                  location=BlitLocation.centre)

        if text:
            self.main_screen.add_text(text, (self.main_screen.size.x / 2, 500), location=BlitLocation.centre)

    def ask_question(self):
        if not self.models_loaded:
            process = multiprocessing.Process(target=load_models, args=(sender,))
            process.daemon = True
            process.start()
            self.processor, self.model, self.t2s = self.loading_screen(receiver, "Loading language models")
            self.models_loaded = True

        # Question will always be given as an english text string
        question = self.questions[self.question_idx]
        if self.config.text:
            self.update_main_screen(question)
            self.update_display()

        if self.config.speech:
            self.action = "speaking"
            self.update_info_screen()
            self.update_display()

            tokens = self.processor(text=question, src_lang="eng", return_tensors="pt")
            audio = self.t2s.generate(**tokens, tgt_lang=self.config.output_lang)[0].cpu().numpy().squeeze()

            # maybe use pygame sound
            write("tempsave_question.wav", 16000, audio)
            pg.mixer.music.load("tempsave_question.wav")
            pg.mixer.music.play()

            time.sleep(0.5)
            # Keep in idle loop while speaking
            self.avatar.state = 1
            while pg.mixer.music.get_busy():
                self.update_main_screen(question)
                self.update_display()
                self.avatar.speak_state = (self.avatar.speak_state + 1) % 2
                time.sleep(0.15)

            self.avatar.state = 0
            self.update_main_screen(question)
            self.update_display()

            os.remove("tempsave_question.wav")

    def record_answer(self, path, max_time=10, rate=16000, chunk=1024):
        def check_next_question():
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_n:
                        return True

            return False

        # try:
        stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=rate,
                             input=True, frames_per_buffer=chunk)
        # except OSError:
        #     pg.quit()
        #     raise SystemError("No Microphone detected!")

        frames = []
        self.action = "recording"
        self.update_info_screen()
        self.update_display()
        iter_per_second = int((rate / chunk))
        for i in range(0, iter_per_second * max_time):
            if i % iter_per_second == 0:
                self.update_info_screen(max_time - (i / iter_per_second))
                self.update_display()

            data = stream.read(chunk)
            # data is a raw bytes object
            frames.append(data)
            if check_next_question():
                break

        stream.stop_stream()
        stream.close()

        self.update_info_screen(f"{0}")
        self.update_display()
        time.sleep(0.5)

        self.action = "Writing file"
        self.update_info_screen()
        self.update_main_screen("Writing audio file")
        self.update_display()

        wf = wave.open(path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
        wf.close()

        _, data = read(path)
        return data

    def transcribe_answer(self, response, path):
        self.action = "Transcribing"
        self.update_info_screen()
        self.update_main_screen("Transcribing audio file")
        self.update_display()

        input_tokens = self.processor(audios=[response], return_tensors="pt", sampling_rate=16000)
        output_tokens = self.model.generate(**input_tokens, tgt_lang=self.config.output_lang, generate_speech=False)
        response_text = self.processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)
        with open(path, 'w') as f:
            f.write(response_text)

        return response_text

    def loop(self):
        while self.running:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    # start the consultation
                    if event.key == pg.K_q:
                        audio_file = f"response-data/answer_{self.question_idx}.wav"
                        text_file = f"response-data/answer_{self.question_idx}.txt"

                        self.ask_question()
                        audio_data = self.record_answer(audio_file)
                        response = self.transcribe_answer(audio_data, text_file)

                        self.action = "None"
                        self.update_info_screen()
                        self.update_main_screen("Press Q to ask next question")
                        self.update_display()

                        print(self.questions[self.question_idx])
                        print(response)

                        self.question_idx = (self.question_idx + 1) % len(self.questions)

                elif event.type == pg.QUIT:
                    self.running = False


if __name__ == "__main__":
    pg.init()
    pg.event.pump()
    audio = pyaudio.PyAudio()
    receiver, sender = multiprocessing.Pipe(duplex=False)

    consultation = Consultation(audio, load_on_startup=True)
    consultation.loop()
