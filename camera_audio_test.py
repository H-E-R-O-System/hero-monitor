import time

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
import wave
import pyaudio


picam2.start_recording(encoder, 'affective_record.h264')

picam2 = Picamera2()
video_config = picam2.create_video_configuration()
picam2.configure(video_config)

encoder = H264Encoder(10000000)

picam2.stop_recording()

# pyaud = pyaudio.PyAudio()

# device_info = pyaud.get_default_input_device_info()
# print(device_info)
# rate = device_info["defaultSampleRate"]
# chunk, max_time = 1024, 10
# path = "mic_test.wav"

# stream = pyaud.open(format=pyaudio.paInt16, channels=1, rate=int(rate), input=True, frames_per_buffer=chunk)


# frames = []
#
# iter_per_second = int((rate / chunk))
# for i in range(0, iter_per_second * max_time):
#     data = stream.read(chunk)
#     # data is a raw bytes object
#     frames.append(data)
#
# stream.stop_stream()
# stream.close()





# wf = wave.open(path, 'wb')
# wf.setnchannels(1)
# wf.setsampwidth(pyaud.get_sample_size(pyaudio.paInt16))
# wf.setframerate(rate)
# wf.writeframes(b''.join(frames))
# wf.close()