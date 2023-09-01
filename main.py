import kivy
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from threading import Thread, Lock
import pyaudio
import wave
from kivy.core.window import Window

Window.size = (300, 200)


class AudioRecorder(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lock = Lock()
        self.recording_active = False
        self.recording_thread = None
        self.frames = []

    def update_message_label(self, dt):
        text = self.message_label.text
        updated_text = text[1:] + text[0]
        self.message_label.text = updated_text

    def record_thread(self, event):
        with self.lock:
            self.record_button.text = "Recording..."
            self.record_button.disabled = True
            self.stop_button.disabled = False
            self.recording_active = True
        self.frames = []
        self.recording_thread = Thread(target=self.record_audio)
        self.recording_thread.start()

    def record_audio(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100

        p = pyaudio.PyAudio()
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        while self.recording_active:
            Clock.schedule_once(lambda dt: setattr(self.message_label, 'text', "Recording..."))
            data = stream.read(CHUNK)
            self.frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def save_audio_to_disk(self):
        print("Saving to disk...")
        WAVE_OUTPUT_FILENAME = "output.wav"
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100

        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        print("Saved to disk.")
        Clock.schedule_once(lambda dt: self.update_gui_after_stop())

    def update_gui_after_stop(self):
        self.record_button.text = "Record"
        self.record_button.disabled = False
        self.message_label.text = "Press Record to start recording....... "
        self.stop_button.disabled = True

    def stop_recording(self, event):
        with self.lock:
            self.recording_active = False

        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join()

        self.save_audio_to_disk()

    def build(self):
        self.root = MDRelativeLayout(md_bg_color=(0.1, 0.1, 0.1, 1))
        self.record_button = Button(
            text="Record",
            font_size=20,
            size_hint=(0.4, 0.2),
            pos_hint={"center_x": 0.5, "center_y": 0.7},
            background_color=(1, 0, 0),
        )
        self.record_button.bind(on_press=self.record_thread)
        self.root.add_widget(self.record_button)

        self.stop_button = Button(
            text="Stop",
            font_size=20,
            size_hint=(0.4, 0.2),
            pos_hint={"center_x": 0.5, "center_y": 0.4},
            background_color=(1, 0, 0),
            disabled=True,
        )
        self.stop_button.bind(on_press=self.stop_recording)
        self.root.add_widget(self.stop_button)

        self.message_label = Label(
            text="Press Record to start recording....... ",
            font_size=20,
            size_hint=(0.8, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.2},
        )
        self.root.add_widget(self.message_label)

        Clock.schedule_interval(self.update_message_label, 0.3)

        return self.root


if __name__ == "__main__":
    AudioRecorder().run()
