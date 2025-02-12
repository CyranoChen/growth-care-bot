import threading
import tkinter as tk
import wave

import numpy as np
import pygame
import sounddevice as sd

from src.domain.azure_setup import init_openai_service
from src.service.conversation_service import ConversationService


class GrowthCareBot:
    def __init__(self, master, client):
        self.conversation = ConversationService()

        self.master = master
        self.client = client
        self.master.title("Growth Care Bot")

        self.recording = False
        self.fs = 44100  # Sampling frequency

        self.label = tk.Label(master, text="Waiting")
        self.label.pack(pady=20)

        self.button = tk.Button(
            master, text="Start Listening", command=self.toggle_recording
        )
        self.button.pack(pady=10)

        self.lock = threading.Lock()
        self.thread = None

    def toggle_recording(self):
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.button.config(text="Stop Listening")
        self.label.config(text="Recording...")
        self.recording = True
        self.frames = []

        self.thread = threading.Thread(target=self.record)
        self.thread.start()

    def record(self):
        try:
            with sd.InputStream(samplerate=self.fs, channels=1, callback=self.callback):
                while self.recording:
                    sd.sleep(100)  # Wait in the loop while streaming audio
        except Exception as e:
            print(f"Error in recording: {e}")

    def callback(self, indata, frames, time, status):
        if status:
            print(status, flush=True)
        with self.lock:
            self.frames.append(indata.copy())

    def stop_recording(self):
        self.recording = False
        self.thread.join()

        filename = "input.wav"
        self.save_recording(filename)
        self.button.config(text="Start Listening")

        # Create a new thread for processing the audio and updating the GUI
        processing_thread = threading.Thread(
            target=self.process_audio, args=(filename,)
        )
        processing_thread.start()

    def save_recording(self, filename):
        with self.lock:
            data = np.concatenate(self.frames, axis=0)
            scaled = np.int16(data / np.max(np.abs(data)) * 32767)

        with wave.open(filename, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16 bits per sample
            wf.setframerate(self.fs)
            wf.writeframes(scaled.tobytes())

    def process_audio(self, input_filename):
        try:
            # 通过after方法在主线程更新标签
            self.master.after(0, lambda: self.label.config(text="Transcribing..."))
            transcript = self.speech_to_text(input_filename)
            print("transcript:", transcript)

            self.master.after(0, lambda: self.label.config(text="Chat Completion ..."))
            content = self.conversation.chat(transcript)
            print("chat completion:", content)

            self.master.after(
                0, lambda: self.label.config(text="Synthesizing speech...")
            )
            output_filename = "output.wav"
            self.speech_synthesis(output_filename, content)

            self.master.after(0, lambda: self.label.config(text="Playing..."))
            self.play_audio(output_filename)

            # self.master.after(0, lambda: self.play_audio(output_filename))
        except Exception as exc:
            print(f"Error processing audio: {exc}")
        finally:
            self.master.after(0, self.reset_interface)

    def reset_interface(self):
        """在主线程重置UI"""
        self.label.config(text="Waiting")
        self.button.config(text="Start Listening")
        print("-" * 100)

    def speech_to_text(self, filename):
        # Placeholder for Azure OpenAI Speech to Text
        with open(filename, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper", file=audio_file, language="zh", response_format="text"
            )
        return transcript

    def speech_synthesis(self, filename, text):
        # Placeholder for Azure OpenAI Speech Synthesis
        with self.client.audio.speech.with_streaming_response.create(
            model="tts", voice="alloy", input=text, response_format="wav"
        ) as response:
            response.stream_to_file(filename)
        print("语音合成，保存为文件:", filename)

    def play_audio(self, filename):
        print("正在播放音频:", filename)
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pass  # 等音频播放完，可以通过时间循环或其他方式优化

    def on_closing(self):
        if self.recording:
            self.recording = False
            self.thread.join()

        self.master.destroy()


if __name__ == "__main__":
    azure_openai_helper = init_openai_service()

    root = tk.Tk()
    voice_recorder = GrowthCareBot(root, azure_openai_helper)

    root.protocol("WM_DELETE_WINDOW", voice_recorder.on_closing)
    root.mainloop()
