import json
import yaml
import speech_recognition as sr
from urllib.error import URLError
from device.python.services.client_mqtt import ClientMqtt
from pathlib import Path
from pydub import AudioSegment
from pydub.playback import play

KEYWORD = 'альфа'
# region Загрузка конфигурации
PATH_TO_CONFIG = str(Path(__file__).parent.joinpath("data/config.yaml"))
with open(PATH_TO_CONFIG, 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)
# endregion

# region Инициализация микрофона и онлайн модели распознавания текста из звука
recognizer = sr.Recognizer()
recognizer.energy_threshold = config['microphone']['energy']
recognizer.pause_threshold = config['microphone']['pause']
# endregion

# region Инициализация офлайн модели распознавания текста из звука
# PATH_TO_MODEL = str(Path(__file__).parent.joinpath("data/vosk-model-small-ru-0.22"))
# model = vosk.Model(PATH_TO_MODEL)
# modelVosk = None
# endregion

# region Инициализация звуковых дорожек
# PATH_TO_RECORD_OFFLINE = (str(Path(__file__).parent.joinpath("data/select_offline_mode_recognize.wav"))
#                           .replace('\\', '/'))
# sound_offline = AudioSegment.from_wav(PATH_TO_RECORD_OFFLINE)
DIRECTORY_TO_DATA = Path(__file__).parent.joinpath('data')
sound_hello = AudioSegment.from_wav(str(DIRECTORY_TO_DATA.joinpath('hello.wav')))
sound_broker_die = AudioSegment.from_wav(str(DIRECTORY_TO_DATA.joinpath('broker_die.wav')))
sound_internet_die = AudioSegment.from_wav(str(DIRECTORY_TO_DATA.joinpath('internet_die.wav')))
sound_microphone_not_found = AudioSegment.from_wav(str(DIRECTORY_TO_DATA.joinpath('microphone_not_found.wav')))
# endregion
try:
    clientMqtt = ClientMqtt(config['mqtt']['host'], config['mqtt']['port'], config['mqtt']['keepalive'],
                            config['mqtt']['username'], config['mqtt']['password'])  # Инициализация клиента mqtt
except OSError as e:
    play(sound_broker_die)
    exit(1)

microphone_list = sr.Microphone.list_microphone_names()
if config['microphone']['deviceIndex'] >= len(microphone_list) or config['microphone']['deviceIndex'] < 0:
    play(sound_microphone_not_found)
    raise ValueError(f"Ошибка: микрофон с индексом {config['microphone']['deviceIndex']} не найден.")

current_phrase_time_limit = config['microphone']['phrase']

play(sound_hello)

with sr.Microphone(device_index=config['microphone']['deviceIndex']) as source:
    recognizer.adjust_for_ambient_noise(source, duration=1)
    while True:
        print('Я вас слушаю: ')
        text = ''
        audio = recognizer.listen(source, phrase_time_limit=current_phrase_time_limit)
        try:
            text = recognizer.recognize_google(audio, language="ru-RU").lower().strip()
            # if current_phrase_time_limit == config['microphone']['phraseOffline']:
            #     current_phrase_time_limit = config['microphone']['phraseOnline']
            #     play(sound_online)
            #     continue
        except sr.UnknownValueError:
            text = ''
        except (sr.RequestError, URLError, TimeoutError):
            play(sound_internet_die)
            exit(1)
            # if current_phrase_time_limit == config['microphone']['phraseOnline']:
            #     current_phrase_time_limit = config['microphone']['phraseOffline']
            #     play(sound_offline)
            #     continue
            # if modelVosk is None:
            #     modelVosk = vosk.KaldiRecognizer(model, audio.sample_rate)
            # data = audio.get_raw_data()
            # if modelVosk.AcceptWaveform(data):
            #     result = json.loads(modelVosk.Result())
            #     text = result.get("text", "")
        if KEYWORD in text:
            clientMqtt.send_message(text, config['mqtt']['topicMicrophone'])
