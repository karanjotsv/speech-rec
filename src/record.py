import os
import io
from queue import Queue
from sys import platform
from tempfile import NamedTemporaryFile

from time import sleep
from datetime import datetime, timedelta

import sounddevice
import speech_recognition as sr
import torchaudio

import warnings
warnings.filterwarnings('ignore')

from . import context, transcribe, parse
from . import cfg


class Recorder:
    def __init__(
            self,
            audio_src=0,
            window=cfg.WINDOW,
            phrase_threshold=cfg.PHRASE_THRESHOLD 
    ):
        self.src = audio_src

        self.phrase_time = None  # timestamp of last retreived from queue
        self.last_sample = bytes()  # current raw sample
        self.data_queue = Queue()

        self.window = window  # duration
        self.phrase_threshold = phrase_threshold

        # self.temp = NamedTemporaryFile().name
        self.temp = os.path.join(os.path.abspath(cfg.BASE), 'tmp.mp3')

        self.phrase_complete = True

        self.transcriber = transcribe.Transcriber()
        self.parser = parse.Parser()
        self.classifier = context.Context()

    
    def check_source(self):
        '''
        validate audio source
        '''
        if not self.src:
            if "linux" in platform:
                mic = cfg.MIC

                if not mic or mic == "list":
                    print("available devices: ")
                    for index, name in enumerate(sr.Microphone.list_microphone_names()):
                        print(f"{name} found")
                    return
                else:
                    if mic in sr.Microphone.list_microphone_names():
                        self.src = sr.Microphone(sample_rate=cfg.SAMPLE_RATE, 
                                                 device_index=sr.Microphone.list_microphone_names().index(mic))
            else:
                self.src = sr.Microphone(sample_rate=cfg.SAMPLE_RATE)

    
    def record_callback(self, _, audio):
        '''
        threaded callback function to store audio data
        audio: AudioData containing the recorded bytes
        '''
        # get bytes and push into queue
        data = audio.get_raw_data()
        self.data_queue.put(data)
    

    def check_phrase(self):
        '''
        clear current working audio buffer
        '''
        self.now = datetime.utcnow()

        # check phrase complete threshold
        if self.phrase_time and self.now - self.phrase_time > timedelta(seconds=self.phrase_threshold):
            self.last_sample = bytes()
            self.phrase_complete = True
    

    def to_wav(self, save_temp=False):
        '''
        convert raw data to wav
        '''
        raw_data = sr.AudioData(self.last_sample, self.src.SAMPLE_RATE, self.src.SAMPLE_WIDTH)
        self.wav = io.BytesIO(raw_data.get_wav_data())
        
        # wav data to temporary file
        if save_temp:
            with open(self.temp, 'wb+') as f:
                f.write(self.wav.read())

        wav, rate = torchaudio.load(self.wav)
        if rate != 16000:
            wav = torchaudio.transforms.Resample(rate, cfg.SAMPLE_RATE)(wav)

        self.wav = wav.squeeze(0)

        
    def start(self):
        print("Hi!")
        while True:
            # check data queue
            if not self.data_queue.empty():
                self.phrase_complete = False

                self.check_phrase()
            
                # when new data received
                self.phrase_time = self.now

                # concat current data with latest
                while not self.data_queue.empty():
                    data = self.data_queue.get()
                    self.last_sample += data

                self.to_wav()

                # run whisper
                text = self.transcriber.to_text(self.wav)
                # run YAMNET
                context = self.classifier.get_context(self.wav)

                self.parser.save(text, list(context), self.phrase_complete)


    def __enter__(self):
        self.check_source()

        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = cfg.ENERGY_THRESHOLD

        # lowers energy threshold dramtically to a point where recording never stops
        self.recognizer.dynamic_energy_threshold = False
        '''
        self.recognizer.adjust_for_ambient_noise(self.src)
        '''
        # background thread to pass raw audio bytes
        self.recognizer.listen_in_background(self.src, self.record_callback, phrase_time_limit=self.window)
        
        return self
    

    def __exit__(self, exception_type, exception_value, traceback):
        return self
    