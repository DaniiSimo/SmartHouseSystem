import speech_recognition as sr


class VoiceControl:
    def __init__(self, stop_keyword: str = "стоп"):
        self.recognizer = sr.Recognizer()
        self.stop_keyword = stop_keyword

    def start_listening(self):
        """
        Слушает голосовое сообщение пользователя и возвращает его в текстовом виде

        Returns:
            text: расшифровка голосового сообщения
        """
        while True:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                print("Я вас слушаю:")
                audio = self.recognizer.listen(source)
            try:
                text = self.recognizer.recognize_google(audio, language="ru-RU")
                print("Распознано:", text)

                if self.stop_keyword in text.lower():
                    print("Программа завершена.")
                    break
                return text

            except sr.UnknownValueError as e:
                print(f"Неизвестная ошибка: {e}")
                break
            except sr.RequestError as e:
                print(f"Ошибка сервиса распознавания: {e}")
            except sr.WaitTimeoutError as e:
                print(f"Программа перешла в спящий режим {e}")
                break

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
