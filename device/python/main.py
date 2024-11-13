import json
import yaml
import speech_recognition as sr
import vosk
from urllib.error import URLError
from device.python.services.client_mqtt import ClientMqtt
from pathlib import Path
from pydub import AudioSegment
from pydub.playback import play


KEYWORD = 'альфред'
# region Загрузка конфигурации
PATH_TO_CONFIG = str(Path(__file__).parent.joinpath("data/config.yaml"))
with open(PATH_TO_CONFIG) as file:
    config = yaml.safe_load(file)
# endregion

# region Инициализация микрофона и онлайн модели распознавания текста из звука
recognizer = sr.Recognizer()
recognizer.energy_threshold = config['microphone']['energy']
recognizer.pause_threshold = config['microphone']['pause']
# endregion

# region Инициализация офлайн модели распознавания текста из звука
PATH_TO_MODEL = str(Path(__file__).parent.joinpath("data/vosk-model-small-ru-0.22"))
model = vosk.Model(PATH_TO_MODEL)
modelVosk = vosk.KaldiRecognizer(model, config['microphone']['rate'])
# endregion

# region Инициализация звуковых дорожек при переходе из онлайн режима в оффлайн и наоборот
PATH_TO_RECORD_OFFLINE = (str(Path(__file__).parent.joinpath("data/select_offline_mode_recognize.wav"))
                          .replace('\\', '/'))
PATH_TO_RECORD_ONLINE = str(Path(__file__).parent.joinpath("data/select_online_mode_recognize.wav")).replace('\\', '/')
sound_offline = AudioSegment.from_wav(PATH_TO_RECORD_OFFLINE)
sound_online = AudioSegment.from_wav(PATH_TO_RECORD_ONLINE)
# endregion

clientMqtt = ClientMqtt(config['mqtt']['host'], config['mqtt']['port'], config['mqtt']['keepalive'])  # Инициализация клиента mqtt

current_phrase_time_limit = config['microphone']['phraseOnline']

print("Начало записи: ")

with sr.Microphone(sample_rate=config['microphone']['rate']) as source:
    recognizer.adjust_for_ambient_noise(source, duration=1)
    while True:
        print('Я вас слушаю: ')
        text = ''
        audio = recognizer.listen(source, phrase_time_limit=current_phrase_time_limit)
        try:
            text = recognizer.recognize_google(audio, language="ru-RU").lower().strip()
            if current_phrase_time_limit == config['microphone']['phraseOffline']:
                current_phrase_time_limit = config['microphone']['phraseOnline']
                play(sound_online)
                continue
        except sr.UnknownValueError:
            text = ''
        except (sr.RequestError, URLError, TimeoutError):
            if current_phrase_time_limit == config['microphone']['phraseOnline']:
                current_phrase_time_limit = config['microphone']['phraseOffline']
                play(sound_offline)
                continue
            data = audio.get_raw_data()
            if modelVosk.AcceptWaveform(data):
                result = json.loads(modelVosk.Result())
                text = result.get("text", "")

        if KEYWORD in text:
            clientMqtt.send_message(text, config['mqtt']['topic'])
