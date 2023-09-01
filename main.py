import kivy
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from threading import Thread
import pyaudio
import wave
from kivy.core.window import Window

Window.size = (200, 200)


class AudioRecorder(MDApp):
    def update_message_label(self, dt):
        text = self.message_label.text
        updated_text = text[1:] + text[0]  # Move the first character to the end
        self.message_label.text = updated_text

    # text = self.message_label.text
        # updated_text = text[-1] + text[:-1]  # Move the last character to the beginning
        # self.message_label.text = updated_text

    def record_thread(self, event):
        self.record_button.text = "Recording..."
        self.record_button.disabled = True
        Thread(target=self.record_audio).start()

    def record_audio(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        RECORD_SECONDS = 10
        WAVE_OUTPUT_FILENAME = "output.wav"

        p = pyaudio.PyAudio()

        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(WAVE_OUTPUT_FILENAME, "wb")
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))
        wf.close()

        self.record_button.text = "Record"
        self.record_button.disabled = False

    def stop_recording(self, event):
        self.message_label.text = "Recording stopped"
        self.stop_button.disabled = True
        self.record_button.disabled = False

    def build(self):
        self.root = MDRelativeLayout(md_bg_color=(0.1, 0.1, 0.1, 1))
        self.record_button = Button(
            text="Record",
            font_size=30,
            size_hint=(0.3, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.7},
            background_color=(1, 0, 0),
        )
        self.record_button.bind(on_press=self.record_thread)
        self.root.add_widget(self.record_button)
        self.stop_button = Button(
            text="Stop",
            font_size=30,
            size_hint=(0.3, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            background_color=(1, 0, 0),
        )
        self.root.bind(on_press=self.stop_recording)
        self.root.add_widget(self.stop_button)

        self.message_label = Label(
            text="Press Record to start recording....... ",
            font_size=40,
            size_hint=(0.3, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.3},
        )
        self.root.add_widget(self.message_label)

        Clock.schedule_interval(self.update_message_label, 0.1)

        return self.root


if __name__ == "__main__":
    AudioRecorder().run()
