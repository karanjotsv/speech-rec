from . import cfg
import whisper

import warnings
warnings.filterwarnings('ignore')


class Transcriber:
    def __init__(
            self,
            model=cfg.WHISPER, 
            lang=cfg.LANGUAGE,
            device="cpu"
    ):
        self.lang = lang
        self.device = device

        self.model = model
        self.audio_model = whisper.load_model(model).to(self.device)

    
    def to_text(self, wav):
        '''
        transcribe wav file
        '''
        fp16 = True
        # read wav and pad
        '''
        wav = whisper.load_audio(f)
        '''
        audio = whisper.pad_or_trim(wav)
        # make log-Mel
        mel = whisper.log_mel_spectrogram(audio).to(self.device)

        # detect language
        '''
        _, probs = self.model.detect_language(mel)
        print(f"detected language: {max(probs, key=probs.get)}")
        '''
        # decode
        if self.device == "cpu": fp16 = False
        options = {
            "fp16": fp16,
            "language": self.lang
            }
        self.options = whisper.DecodingOptions(**options)

        result = whisper.decode(self.audio_model, mel, self.options)

        # high level
        '''
        result, _ = self.audio_model.transcribe(wav)
        print(result)
        text = result["text"].strip()
        '''
        return result.text
