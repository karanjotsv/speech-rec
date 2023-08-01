import os
import csv
import numpy as np

import scipy
from scipy.io import wavfile

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf
import tensorflow_hub as hub

import warnings
warnings.filterwarnings('ignore')

from . import cfg


class Context:
    def __init__(
            self,
            model=cfg.YAMNET,
            max_results=4
    ):
        self.model = model
        self.max_results = max_results

        self.init_model()

        # get list of labels from class map
        self.labels = self.get_classes(self.clf.class_map_path().numpy())

    
    def init_model(self):
        '''
        initialize model
        '''
        # load model
        self.clf = hub.load(self.model)
    

    def check_rate(self, original_rate, waveform, desired_rate=cfg.SAMPLE_RATE):
        '''
        resample waveform if required
        '''
        if original_rate != desired_rate:
            desired_len = int(round(float(len(waveform)) / desired_rate))

            waveform = scipy.signal.resample(waveform, desired_len)
        
        return desired_rate, waveform
    

    def get_classes(self, class_map):
        '''
        get list of labels corresponding to score vector
        '''
        labels = []

        with tf.io.gfile.GFile(class_map) as f:
            reader = csv.DictReader(f)

            for row in reader:
                labels.append(row["display_name"])
        
        return labels


    def get_context(self, wav_data):
        '''
        get context of audio
        '''
        # read wav
        '''
        sr, wav_data = wavfile.read(f, 'rb')
        sr, wav_data = self.check_rate(sr, wav_data)
        '''
        waveform = wav_data / tf.int16.max
        # run model
        scores, embeddings, spectrogram = self.clf(waveform)

        # get top k classes
        result = np.array(self.labels)[np.argsort(scores.numpy().mean(axis=0))[ : : -1][ : self.max_results]]

        return result
