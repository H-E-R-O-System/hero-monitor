import os
import time
import pygame as pg
import math
import pyaudio
from consultation.screen import Screen, BlitLocation, Fonts, Colours
from consultation.avatar import Avatar
from scipy.io.wavfile import write, read
import wave
from consultation.ConsultDisplay import ConsultDisplay
import warnings
import gtts
import speech_recognition as sr

class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age

class ConsultConfig:
    def __init__(self, speech=True):
        self.speech = speech
        self.text = True
        self.output_lang = 'en'
        self.input_lang = 'en'

class Question:
    def __init__(self, text, hints):
        self.text = text
        self.hints = hints[:5]  # restrict to 5 hints per question
        self.hint_count = len(self.hints)

class Consultation:
    def __init__(self, p, user=None, info_width=0, enable_speech=True):
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
        questions = ["How are you feeling today?",
                     "How were your tremors over the past few days?",
                     "How is your mood?"]
        hints = [["has today been overall positive or negative", "has you felt any physical pain"],
                 ["has today been overall positive or negative", "has you felt any physical pain"],
                 ["has today been overall positive or negative", "has you felt any physical pain"]]

        self.questions = [Question(question, hint) for question, hint in zip(questions, hints)]

        self.question_idx = 0
        self.running = True


        # Visual helper attributes
        self.action = "None"
        self.instruction = None
        self.avatar.state = 0

        audio = gtts.gTTS(text=self.questions[0].text, lang='en', slow=False)
        self.next_question_audio = audio
        self.prev_answer_audio = None
        self.prev_answer_text = None

        self.update_info_screen()
        self.update_consult_screen(instruction="Press Q to start")
        self.update_display()

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

        # Question will always be given as an english text string
        question = self.questions[self.question_idx]
        self.update_consult_screen(instruction="Press N to finish recording")
        if self.config.text:
            self.update_consult_screen(question=question)
            self.update_display()

        if self.config.speech:
            self.action = "speaking"
            self.update_info_screen()
            self.update_display()

            self.next_question_audio = gtts.gTTS(text=question.text, lang='en', slow=False)
            question_audio_file = 'consultation/question_audio/tempsave_question_' + str(self.question_idx) + '.mp3'
            self.next_question_audio.save(question_audio_file)

            pg.mixer.music.load(question_audio_file)
            pg.mixer.music.play()

            # Keep in idle loop while speaking
            self.avatar.state = 1
            print(self.question_idx)

            if self.question_idx != len(self.questions) - 1:
                self.question_idx = self.question_idx + 1

            self.consult_screen.avatar.state = 1
            start = time.monotonic()
            while pg.mixer.music.get_busy():
                if time.monotonic() - start > 0.15:
                    self.update_consult_screen(question=question)
                    self.update_display()
                    self.consult_screen.avatar.speak_state = (self.consult_screen.avatar.speak_state + 1) % 2
                    start = time.monotonic()

            self.consult_screen.avatar.state = 0
            self.update_consult_screen(question=question)
            self.update_display()

    def record_answer(self, path, max_time=20, chunk=1024):
        def check_next_question():
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_n:
                        return True

            return False

        device_info = pyaud.get_default_input_device_info()
        rate = int(device_info["defaultSampleRate"])

        stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=rate,
                             input=True, frames_per_buffer=chunk)

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

        t1 = time.monotonic()

        print(f"Backend run time {time.monotonic() - t1} seconds")

        _, data = read(path)
        self.prev_answer_audio = data
        print(data)
        return data

    def transcribe_answer(self, audio_path):
        self.action = 'Transcribing'
        self.update_info_screen()
        self.update_consult_screen(instruction='Transcribing audio file')
        self.update_display()
        
        # convert audio file to text
        r = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = r.record(source)
            response_text = r.recognize_google(audio)
        
        # write response text to file
        response_text_path = 'consultation/response_data/response_text.txt'

        # if new consultation, clear text data
        if self.question_idx == 1:
            with open(response_text_path, "w"):
                pass
        with open(response_text_path, 'a') as f:
            print(response_text)
            f.write(response_text)
            f.write('\n')

    def loop(self):
        while self.running:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    # start the consultation
                    if event.key == pg.K_q:
                        
                        audio_path = f"consultation/response_data/response_audio/answer_{self.question_idx}.wav"

                        self.ask_question()
                        self.record_answer(audio_path)
                        t1 = time.monotonic()
                        self.transcribe_answer(audio_path)
                        print(f"Transcribed in {time.monotonic() - t1} seconds")

                        self.action = "None"
                        self.update_info_screen()
                        self.update_consult_screen(instruction="Press Q to ask next question")
                        self.update_display()

                elif event.type == pg.QUIT:
                    self.running = False


if __name__ == '__main__':
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
    warnings.simplefilter(action='ignore', category=FutureWarning)

    # os.chdir('/Users/might/Documents/rosemary/hero-lightweight')
    os.chdir('/Users/benhoskings/Documents/Projects/hero-monitor')

    pg.init()
    pg.event.pump()
    pyaud = pyaudio.PyAudio()

    consultation = Consultation(pyaud, info_width=0, enable_speech=True)
    consultation.loop()
