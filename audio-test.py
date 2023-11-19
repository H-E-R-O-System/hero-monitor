import pyaudio

p = pyaudio.PyAudio()

print(p.get_device_count())
print(p.get_default_input_device_info())