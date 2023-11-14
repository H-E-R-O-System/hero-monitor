import sys

from transformers import AutoProcessor, SeamlessM4TModel, SeamlessM4TForTextToSpeech
from scipy.io.wavfile import write, read
from Screen import Screen, BlitLocation
import numpy as np
import pygame as pg
import pyaudio
import wave


def ask_question(question):
    print(question)
    tokens = processor(text=question, src_lang="eng", return_tensors="pt")
    audio = t2s.generate(**tokens, tgt_lang="eng")[0].cpu().numpy().squeeze()
    write("tempsave.wav", 16000, audio)
    pg.mixer.music.load("tempsave.wav")
    pg.mixer.music.play()


def transcribe_answer(response):
    input_tokens = processor(audios=[response], return_tensors="pt", sampling_rate=16000)
    output_tokens = model.generate(**input_tokens, tgt_lang="eng", generate_speech=False)
    response_text = processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)
    with open('test.txt', 'w') as f:
        f.write(response_text)

    return response_text


def check_next_question():
    for event in pg.event.get():
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_n:
                return True

    return False


def record_answer(path, max_time=10, rate=16000, chunk=1024):
    try:
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=rate,
            input=True, frames_per_buffer=chunk)
    except OSError:
        pg.quit()
        raise SystemError("No Microphone detected!")

    frames = []
    print("* recording")
    for i in range(0, int((rate / chunk) * max_time)):
        data = stream.read(chunk)
        # data is a raw bytes object
        frames.append(data)
        if check_next_question():
            break

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

    print("* done recording")


def update_screen(base, screen, text):
    screen.refresh()
    # add text to middle
    middle = pg.Vector2(screen.surface.get_size()) / 2
    screen.addText(text, middle, location=BlitLocation.centre)
    base.blit(screen.surface, (0, 0))
    pg.display.update()


p = pyaudio.PyAudio()

# Get the number of audio I/O devices
if p.get_device_count() == 0:
    raise SystemError("No Microphone detected!")
else:
    print("Microphone check passed")

pg.init()

base_screen = pg.display.set_mode((1024, 600))
base_screen.fill(pg.Color(255, 255, 255))
font = pg.font.Font("Fonts/calibri-regular.ttf", size=50)
screen = Screen(base_screen.get_size(), font, colour=pg.Color(255, 255, 255))

update_screen(base_screen, screen, "Hello!")
pg.event.pump()

processor = AutoProcessor.from_pretrained("facebook/hf-seamless-m4t-medium")
model = SeamlessM4TModel.from_pretrained("facebook/hf-seamless-m4t-medium")
t2s = SeamlessM4TForTextToSpeech.from_pretrained("facebook/hf-seamless-m4t-medium")

questions = ["how are you feeling today?",
             "How were your tremors over the past few days?",
             "how has is your mood?"]

running = True
question_idx = 0

update_screen(base_screen, screen, "System ready!")

while running:
    # Process events in queue
    for event in pg.event.get():
        # Key down events
        if event.type == pg.KEYDOWN:
            # start the consultation
            if event.key == pg.K_s:
                update_screen(base_screen, screen, "Starting interview!")

                # ask the question on screen and audio
                update_screen(base_screen, screen, questions[0])
                ask_question(questions[0])

                record_answer("Response Data/answer_0.wav")
                print("Starting transcription")
                sample_rate, data = read("Response Data/answer_0.wav")
                transcribe_answer(data)
                print("transcription done!")

                question_idx = 1
                # next question
            elif event.key == pg.K_n:
                print("next question")
                # ask the question on screen and audio
                update_screen(base_screen, screen, questions[question_idx])

                ask_question(questions[question_idx])
                record_answer(f"answer_{question_idx}.wav")
                question_idx = (question_idx + 1) % 3

            elif event.key == pg.K_q:
                pg.quit()

        elif event.type == pg.QUIT:
            pg.quit()
            sys.exit()
