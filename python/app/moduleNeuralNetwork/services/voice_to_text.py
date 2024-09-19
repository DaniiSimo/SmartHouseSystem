import speech_recognition as sr


class VoiceControl:
    """
       Класс голосового управления, который активируется по ключевой фразе
       и распознает команды пользователя.

       Args:
           activation_phrase (str): Ключевая фраза для активации распознавания команды.
           is_active (bool): Состояние активации распознавания команды (True - активирован, False - неактивен).
           recognizer (sr.Recognizer): Объект для распознавания речи.
           microphone (sr.Microphone): Объект микрофона для записи аудио.
   """

    def __init__(self, activation_phrase):
        """
            Инициализая экземпляра класса

            Args:
                activation_phrase (str): Ключевая фраза для активации.
        """
        self.activation_phrase = activation_phrase.lower()
        self.is_active = False
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

    def callback(self, audio):
        """
           Метод обратного вызова, который вызывается при захвате аудио из микрофона.
           Пытается распознать речь и определить активационную фразу или команду.

           Args:
                audio (sr.AudioData): Аудио данные, которые нужно распознать.

           Returns:
                phrase (str): Текст распознанной команды.
        """
        try:
            phrase = self.recognizer.recognize_google(audio, language="ru-RU").lower()

            if not self.is_active and self.activation_phrase in phrase:
                self.is_active = True
            elif self.is_active:
                print(f"Распознана команда: {phrase}")
                self.is_active = False
                return phrase

        except sr.UnknownValueError:
            print("Не удалось распознать фразу.")
        except sr.RequestError as e:
            print(f"Ошибка запроса к сервису Google Speech Recognition: {e}")

    def start_listening(self):
        """
            Запускает фоновое прослушивание микрофона для активации голосового ассистента
            и распознавания команд. Функция работает в фоне, пока не будет вызвано завершение программы.
        """
        stop_listening = self.recognizer.listen_in_background(self.microphone, self.callback)

        try:
            while True:
                print("Выполнение других процессов...")
                time.sleep(5)
        except KeyboardInterrupt:
            stop_listening(wait_for_stop=False)
            print("Программа завершена.")

    def recognize_file(self, path):
        """
        Распознает голосовое сообщение из файла

        Args:
            path (str): файл, из которого надо распознать текст

        Returns:
            text: текстовое представление голосового сообщения
        """

        r = sr.Recognizer()
        with sr.AudioFile(path) as f:
            audio = r.record(f)
        try:
            text = r.recognize_google(audio, language='ru-RU')
            return text
        except sr.UnknownValueError:
            return "Не удалось распознать текс"
        except sr.RequestError as e:
            return f"Ошибка обращения к сервису; {e}"
