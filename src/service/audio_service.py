# pylint: disable=no-member
import base64
import os
import threading
import wave
from pathlib import Path
from typing import Optional

import numpy as np
import pygame
import sounddevice as sd
from openai import AzureOpenAI
from pyaudio import PyAudio, paInt16

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
            print("Error in recording:", exc)

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

    def encode_audio(self) -> str:
        with open(self.input_audio_file, "rb") as audio_file:
            data = audio_file.read()

        return base64.b64encode(data).decode("utf-8")

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

    def play(self, encoded_str: Optional[str] = None) -> "AudioService":
        if encoded_str:
            with open(self.output_audio_file, "wb") as audio_file:
                audio_file.write(base64.b64decode(encoded_str))

        pygame.mixer.init(frequency=16000, channels=1)
        pygame.mixer.music.load(self.output_audio_file)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)

    def play_chunk(self, encoded_str: str) -> "AudioService":
        decoded_audio = base64.b64decode(encoded_str)

        stream = PyAudio().open(
            format=paInt16,  # Assuming 16-bit PCM
            channels=1,  # Assuming mono audio
            rate=24000,  # Assuming a sample rate of 24000 Hz
            output=True,
        )

        stream.write(decoded_audio)
