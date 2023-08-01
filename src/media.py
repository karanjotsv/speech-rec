import os
import numpy as np
from scipy.io import wavfile

from mediapipe.tasks import python

# import tensorflow as tf
# import tensorflow_hub as hub

from . import cfg


class Context:
    def __init__(
            self,
            model=os.path.abspath(cfg.MEDIAPIPE),
            # model=cfg.YAMNET,
            max_results=4
    ):
        self.model = model
        self.max_results = max_results

    
    def init_model(self):
        '''
        initialize model
        '''
        self.base = python.BaseOptions(model_asset_path=self.model)
        self.options = python.audio.AudioClassifierOptions(self.base, self.max_results)


    def get_context(self, f):
        '''
        get background context
        '''
        self.init_model()

        with python.audio.AudioClassifier.create_from_options(self.options) as clf:
            # read wav
            sample_rate, wav_data = wavfile.read(f)

            clip = python.components.containers.AudioData.create_from_array(
                wav_data.astype(float) / np.iinfo(np.int16).max, sample_rate)

            result = clf.classify(clip)

        return result
