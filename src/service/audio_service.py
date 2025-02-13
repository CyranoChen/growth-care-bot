# pylint: disable=no-member
import os
import threading
import wave
from pathlib import Path

import numpy as np
import pygame
import sounddevice as sd
from openai import AzureOpenAI

from src.domain.azure_setup import init_openai_service

ROOT_DIR = Path(__file__).parents[2]


class AudioService:
    def __init__(self):
        self.client: AzureOpenAI = init_openai_service()
        self.recording: bool = False
        self.lock = threading.Lock()
        self.param_recording: dict = {
            "blocksize": 1024,
            "samplerate": 44100,
            "samplewidth": 2,
            "channels": 1,
        }
        self.model_stt: str = "whisper"
        self.param_stt: dict = {"language": "zh", "response_format": "text"}
        self.model_tts: str = "tts"
        self.param_tts: dict = {"voice": "nova", "response_format": "wav"}
        self.input_audio_file: str = os.path.join(ROOT_DIR, "artifacts/input.wav")
        self.output_audio_file: str = os.path.join(ROOT_DIR, "artifacts/output.wav")

        self.recording_frames_ = []

    def record(self) -> "AudioService":
        try:
            with sd.InputStream(
                samplerate=self.param_recording.get("samplerate"),
                channels=self.param_recording.get("channels"),
                callback=self.callback,
            ):
                while self.recording:
                    sd.sleep(100)  # Wait in the loop while streaming audio
        # pylint: disable=broad-exception-caught
        except Exception as exc:
            print(f"Error in recording: {exc}")

        return self

    # pylint: disable=unused-argument
    def callback(self, indata: np.ndarray, frames: int, time, status) -> "AudioService":
        if status:
            print("Recording callback:", status, flush=True)
        with self.lock:
            self.recording_frames_.append(indata.copy())

        return self

    def save(self) -> "AudioService":
        if not self.recording_frames_:
            print("No recording frames to save")
            return self

        with self.lock:
            data = np.concatenate(self.recording_frames_, axis=0)
            # 16 bits per sample
            scaled = np.int16(data / np.max(np.abs(data)) * (2**15 - 1))

        with wave.open(self.input_audio_file, "wb") as audio_file:
            audio_file.setnchannels(self.param_recording.get("channels"))
            audio_file.setsampwidth(self.param_recording.get("samplewidth"))
            audio_file.setframerate(self.param_recording.get("samplerate"))
            audio_file.writeframes(scaled.tobytes())

            # Reset the recording frames
            self.recording_frames_ = []

        return self

    def speech_to_text(self) -> str:
        with open(self.input_audio_file, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model=self.model_stt, file=audio_file, **self.param_stt
            )

        return transcript

    def speech_synthesis(self, text) -> "AudioService":
        with self.client.audio.speech.with_streaming_response.create(
            model=self.model_tts, input=text, **self.param_tts
        ) as response:
            response.stream_to_file(self.output_audio_file)

        return self

    def play(self) -> "AudioService":
        pygame.mixer.init()
        pygame.mixer.music.load(self.output_audio_file)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pass  # 等音频播放完，可以通过时间循环或其他方式优化
