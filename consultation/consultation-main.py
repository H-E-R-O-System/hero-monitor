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
import warnings

language_codes = {"English": "eng", "German": "deu"}


# Multiprocessing Functions
def load_models(sender_connection: Connection):
    processor = AutoProcessor.from_pretrained("facebook/hf-seamless-m4t-medium")
    model = SeamlessM4TModel.from_pretrained("facebook/hf-seamless-m4t-medium")
    t2s = SeamlessM4TForTextToSpeech.from_pretrained("facebook/hf-seamless-m4t-medium")

    sender_connection.send([processor, model, t2s])
    return None


def consult_backend(sender_connection, processor, speech_model, text_model, text=None, response=None):
    audio, response_text = None, None

    if text is not None:
        text_tokens = processor(text=text, src_lang="eng", return_tensors="pt")
        audio = speech_model.generate(**text_tokens, tgt_lang="eng")[0].cpu().numpy().squeeze()

    if response is not None:
        response_tokens = processor(audios=[response], return_tensors="pt", sampling_rate=16000)
        output_tokens = text_model.generate(**response_tokens, tgt_lang="eng", generate_speech=False)
        response_text = processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)

    sender_connection.send([audio, response_text])

    return None


def generate_question_speech(sender_connection, text, processor, model):
    """
    Function for turing text based question into speech

    :param sender_connection: the multiprocessing sender connection
    :param text: the text that will be turned into audio
    :param processor: the tokeniser for text to token mapping
    :param model: the language model for token to audio
    :return: audio array, sampled at 16 kHz
    """
    tokens = processor(text=text, src_lang="eng", return_tensors="pt")
    audio = model.generate(**tokens, tgt_lang="eng")[0].cpu().numpy().squeeze()
    sender_connection.send(audio)
    return None


def transcribe_audio(sender_connection, audio, processor, model):
    input_tokens = processor(audios=[audio], return_tensors="pt", sampling_rate=16000)
    output_tokens = model.generate(**input_tokens, tgt_lang="eng", generate_speech=False)
    response_text = processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)
    sender_connection.send(response_text)
    return None


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
        self.hints = hints[:5]  # restrict to 5 hints per question
        self.hint_count = len(self.hints)


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
        self.startup_screen = Screen(self.display_size, colour=Colours.lightGrey.value)
        self.consult_screen = ConsultDisplay(self.main_panel.get_size())
        self.backend_screen = Screen(self.backend_panel.get_size(), self.fonts.normal, colour=Colours.lightGrey.value)

        self.startup_screen.load_image("logo.png", self.startup_screen.size/2, location=BlitLocation.centre,
                                       base=True)

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

        self.processor, self.model, self.t2s = None, None, None
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

        # multiprocessing helpers
        text_tokens = self.processor(text=self.questions[0].text, src_lang="eng", return_tensors="pt")
        audio = self.t2s.generate(**text_tokens, tgt_lang="eng")[0].cpu().numpy().squeeze()
        self.next_question_audio = audio
        self.prev_answer_audio = None
        self.prev_answer_text = None

        # Show initialisation screen

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

            if (time.monotonic() - start_time) > 0.1:
                self.consult_screen.avatar_display.time = (self.consult_screen.avatar_display.time + 0.5) % 24
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
        self.update_consult_screen(instruction="Press N to finish recording")
        if self.config.text:
            self.update_consult_screen(question=question)
            self.update_display()

        if self.config.speech:
            self.action = "speaking"
            self.update_info_screen()
            self.update_display()

            # audio = generate_question_speech(question.text, self.processor, self.t2s)
            if self.next_question_audio is None:
                t1 = time.monotonic()
                tokens = self.processor(text=question.text, src_lang="eng", return_tensors="pt")
                self.next_question_audio = self.t2s.generate(**tokens, tgt_lang=self.config.output_lang)[0].cpu().numpy().squeeze()
                print(f"Generated in {time.monotonic() - t1} seconds")

            # maybe use pygame sound
            write("tempsave_question.wav", 16000, self.next_question_audio)
            pg.mixer.music.load("tempsave_question.wav")
            pg.mixer.music.play()

            # Keep in idle loop while speaking
            self.avatar.state = 1

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

            os.remove("tempsave_question.wav")

    def record_answer(self, path, max_time=20, rate=16000, chunk=1024, run_backend=False):
        def check_next_question():
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_n:
                        return True

            return False

        backend_complete = False

        if run_backend:
            next_question = self.questions[(self.question_idx + 1) % len(self.questions)]
            if self.prev_answer_audio is None:
                backend_args = (sender, self.processor, self.t2s, self.model, next_question.text)
            else:
                backend_args = (sender, self.processor, self.t2s, self.model, next_question.text, self.prev_answer_audio)

            process = multiprocessing.Process(
                target=consult_backend,
                args=backend_args
            )
            process.daemon = True
            process.start()

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
        if run_backend:
            while not backend_complete:
                if receiver.poll():
                    question_audio, response_text = receiver.recv()
                    backend_complete = True
                    self.next_question_audio = question_audio
                    print("Question generated!!")
                    if response_text:
                        self.prev_answer_text = response_text
                        print("Response Transcribed!!")

        print(f"Backend run time {time.monotonic() - t1} seconds")

        _, data = read(path)
        self.prev_answer_audio = data
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
                        audio_data = self.record_answer(audio_file, run_backend=True)
                        # t1 = time.monotonic()
                        # response = self.transcribe_answer(audio_data, text_file)
                        # print(f"Transcribed in {time.monotonic() - t1} seconds")

                        self.action = "None"
                        self.update_info_screen()
                        self.update_consult_screen(instruction="Press Q to ask next question")
                        self.update_display()

                        self.question_idx = (self.question_idx + 1) % len(self.questions)

                elif event.type == pg.QUIT:
                    self.running = False


if __name__ == '__main__':
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
    warnings.simplefilter(action='ignore', category=FutureWarning)

    # os.chdir('/Users/benhoskings/Documents/Projects/hero-monitor')
    os.chdir("/Users/benhoskings/Documents/Pycharm/Hero_Monitor")

    pg.init()
    pg.event.pump()
    pyaud = pyaudio.PyAudio()
    receiver, sender = multiprocessing.Pipe(duplex=False)

    consultation = Consultation(pyaud, load_on_startup=True, info_width=0, enable_speech=True)
    consultation.loop()
