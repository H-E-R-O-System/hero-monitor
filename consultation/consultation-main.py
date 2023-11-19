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
from scipy.io.wavfile import write, read
import wave
from consultation.ConsultDisplay import ConsultDisplay

language_codes = {"English": "eng", "German": "deu"}


class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age


class ConsultConfig:
    def __init__(self, speech=True):
        self.speech = speech
        self.text = True
        self.output_lang = language_codes["English"]
        self.input_lang = language_codes["English"]


class Question:
    def __init__(self, text, hints):
        self.text = text
        self.hints = hints[:5] # restrict to 5 hints per question
        self.hint_count = len(self.hints)


def load_models(sender_connection: Connection):
    processor = AutoProcessor.from_pretrained("facebook/hf-seamless-m4t-medium")
    model = SeamlessM4TModel.from_pretrained("facebook/hf-seamless-m4t-medium")
    t2s = SeamlessM4TForTextToSpeech.from_pretrained("facebook/hf-seamless-m4t-medium")

    sender_connection.send([processor, model, t2s])
    return None


class Consultation:
    def __init__(self, p, user=None, load_on_startup=True, info_width=0, enable_speech=True):
        """
        Object for running the consultation

        :param p: initialised PyAudio object
        :param user: user data with name, age, etc.
        :param load_on_startup: load language models on start-up or not. Will be loaded when needed if set to False.
        :param info_width: ratio of screen to assign to helper screen for backend debugging
        """

        if user:
            self.user = user
        else:
            # create demo user
            self.user = User("Demo", 65)

        self.config = ConsultConfig(speech=enable_speech)

        self.display_size = pg.Vector2(1024, 600)

        # load all attributes which utilise any pygame surfaces!

        self.window = pg.display.set_mode(self.display_size, pg.SRCALPHA)
        self.main_panel = self.window.subsurface(((0, 0), (math.floor(self.display_size.x * (1 - info_width)),
                                                           self.display_size.y)))
        self.backend_panel = self.window.subsurface(((self.main_panel.get_size()[0], 0),
                                                     (self.display_size.x - self.main_panel.get_size()[0],
                                                      self.display_size.y)))

        self.fonts = Fonts()
        self.consult_screen = ConsultDisplay(self.main_panel.get_size())
        self.backend_screen = Screen(self.backend_panel.get_size(), self.fonts.normal, colour=Colours.lightGrey.value)

        # add unchanging items to info screen
        self.backend_screen.add_text(f"Name: {self.user.name}", (10, 30), base=True)
        self.backend_screen.add_text(f"Age: {self.user.age}", (10, 80), base=True)

        self.avatar = Avatar(size=(256, 256 * 1.125))

        self.action = "Initialising"

        self.p = p
        questions = ["how are you feeling today?",
                     "How were your tremors over the past few days?",
                     "how is your mood?"]
        hints = [["has today been overall positive or negative", "has you felt any physical pain"],
                 ["has today been overall positive or negative", "has you felt any physical pain"]]

        self.questions = [Question(question, hint) for question, hint in zip(questions, hints)]

        self.question_idx = 0
        self.running = True

        self.processor = None
        self.model = None
        self.t2s = None
        self.models_loaded = False

        # Visual helper attributes
        self.action = "None"
        self.instruction = None
        self.avatar.state = 0

        if load_on_startup:
            process = multiprocessing.Process(target=load_models, args=(sender,))
            process.daemon = True
            process.start()
            self.processor, self.model, self.t2s = self.loading_screen(receiver, "Loading language models")
            self.models_loaded = True

        self.update_info_screen()
        self.update_consult_screen(instruction="Press Q to start")
        self.update_display()

    def loading_screen(self, receiver_connection, text=None):
        """
        Loading screen while background functions are being carried out

        ADD SLEEPING DOCTOR and maybe time changing

        :param receiver_connection:
        :param text:
        :return:
        """
        start_time = time.monotonic()
        self.action = "Loading models"
        self.avatar.state = 2
        self.consult_screen.avatar_display.state = 1

        self.update_info_screen()
        self.update_consult_screen(instruction=text)
        self.update_display()

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    quit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        quit()

            if receiver_connection.poll():
                self.consult_screen.avatar_display.state = 0
                return receiver_connection.recv()

            if (time.monotonic() - start_time) > 0.2:
                self.consult_screen.avatar_display.time = (self.consult_screen.avatar_display.time + 1) % 24
                self.update_consult_screen(instruction="Loading language models")
                self.update_display()
                start_time = time.monotonic()

    def update_display(self, main=True, backend=True):
        if main:
            # update instruction text
            self.backend_screen.refresh()
            if self.instruction:
                self.backend_screen.add_text(self.instruction,
                                               pos=self.backend_screen.size / 2,
                                               location=BlitLocation.centre)
            # update doctor screen

            self.main_panel.blit(self.consult_screen.get_surface(), (0, 0))

        if backend:
            self.backend_panel.blit(self.backend_screen.surface, (0, 0))

        pg.display.flip()

    def update_info_screen(self, time_left=None):
        # clear info screen
        self.backend_screen.refresh()
        self.backend_screen.add_text(f"Job: {self.action}", (10, 150))

        if time_left:
            self.backend_screen.add_text(f"Time left: {time_left}", (10, 200))

    def update_consult_screen(self, instruction=None, question=None):
        if instruction:
            self.consult_screen.instruction = instruction
        # add update main text screen and doctor screen
        self.consult_screen.update(question)

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
            self.update_consult_screen(question=question)
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
                self.update_consult_screen(question=question)
                self.update_display()
                self.avatar.speak_state = (self.avatar.speak_state + 1) % 2
                time.sleep(0.15)

            self.avatar.state = 0
            self.update_consult_screen(question=question)
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
        self.update_consult_screen(instruction="Writing audio file")
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
        self.update_consult_screen(instruction="Transcribing audio file")
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
                        audio_file = f"consultation/response-data/answer_{self.question_idx}.wav"
                        text_file = f"consultation/response-data/answer_{self.question_idx}.txt"

                        self.ask_question()
                        audio_data = self.record_answer(audio_file)
                        response = self.transcribe_answer(audio_data, text_file)

                        self.action = "None"
                        self.update_info_screen()
                        self.update_consult_screen(instruction="Press Q to ask next question")
                        self.update_display()

                        print(self.questions[self.question_idx])
                        print(response)

                        self.question_idx = (self.question_idx + 1) % len(self.questions)

                elif event.type == pg.QUIT:
                    self.running = False


if __name__ == "__main__":
    os.chdir('/Users/benhoskings/Documents/Projects/hero-monitor')

    pg.init()
    pg.event.pump()
    audio = pyaudio.PyAudio()
    receiver, sender = multiprocessing.Pipe(duplex=False)

    consultation = Consultation(audio, load_on_startup=True, info_width=0, enable_speech=False)
    consultation.loop()
