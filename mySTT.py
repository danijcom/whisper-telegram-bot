import os
import time

import openai
import soundfile as sf

from loguru import logger

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google_key.json'


class MySTT:
    def __init__(self, openai_key):
        self.whisper_types = ['flac', 'mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'ogg', 'wav', 'webm']
        self.max_cache = 10
        self.cached = {}
        openai.api_key = openai_key

    def stt_whisper(self, voice_path):
        self._clean_up()
        if voice_path in self.cached:
            if self.cached[voice_path].get('whisper'):
                return self.cached[voice_path]['whisper']['transcript']
            else:
                self.cached[voice_path]['whisper'] = {}
        else:
            self.cached[voice_path] = {'whisper': {}}

        if voice_path[voice_path.rfind('.') + 1:] not in self.whisper_types:
            supported_format = voice_path.replace(voice_path[voice_path.rfind('.'):], '.wav')
            data, samplerate = sf.read(voice_path)
            sf.write(supported_format, data, samplerate)
        else:
            supported_format = voice_path

        with open(supported_format, 'rb') as voice:
            time_start = time.time()
            transcript = openai.Audio.transcribe("whisper-1", voice)
            time_end = time.time()

        self.cached[voice_path]['whisper'] = {
            'transcript': transcript['text']
        }

        logger.info("[Whisper STT] Transcript: {}".format(transcript['text']))
        logger.info("[Whisper STT] Done in: {} seconds".format(time_end - time_start))
        os.remove(supported_format)
        return transcript['text']

    def _clean_up(self):
        if len(self.cached) > self.max_cache:
            self.cached.pop(0)