import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import simpleaudio as sa

import sounddevice as sd
import openai

from src.application.azure_setup import init_openai_service


def list_audio_devices():
    print("可用音频设备列表：")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        print(
            f"{i}: {device['name']} (输入通道: {device['max_input_channels']}, 输出通道: {device['max_output_channels']})"
        )


def record_audio(duration, filename, samplerate=44100, channels=1, device=2):
    """
    录制音频并保存为 WAV 文件
    :param duration: 录音时长（秒）
    :param filename: 保存的文件名
    :param samplerate: 采样率（默认44100Hz）
    """
    print("开始录音...")
    audio_data = sd.rec(
        int(duration * samplerate),
        samplerate=samplerate,
        channels=channels,
        dtype="int16",
        device=device,
    )
    sd.wait()  # 等待录音结束

    print("录音结束，保存为文件:", filename)
    wav.write(filename, samplerate, audio_data)

    return filename


def play_audio(filename):
    """
    播放指定的 WAV 文件
    :param filename: 要播放的文件名
    """
    print("正在播放音频:", filename)
    wave_obj = sa.WaveObject.from_wave_file(filename)
    play_obj = wave_obj.play()
    play_obj.wait_done()  # 等待播放完成
    print("播放结束")


# azure openai speech to text
def speech_to_text(client: openai.AzureOpenAI, filename: str):
    with open(filename, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper", file=audio_file, language="zh", response_format="text"
        )

    return transcript


def speech_synthesis(client: openai.AzureOpenAI, filename: str, text: str):
    with client.audio.speech.with_streaming_response.create(
        model="tts", voice="alloy", input=text, response_format="wav"
    ) as response:
        response.stream_to_file(filename)

    print("语音合成，保存为文件:", filename)
    return filename


def chat_completion(client: openai.AzureOpenAI, content):
    try:
        response = client.chat.completions.create(
            model="gpt-4o", messages=[{"role": "user", "content": content}]
        )

        # 提取response中的content并返回
        return response.choices[0].message.content

    except Exception as exc:
        print("Error in chat_completion:", exc)
        return "Error in gpt.chat_completion"


if __name__ == "__main__":
    azure_openai_helper = init_openai_service()
    INPUT_FILENAME = "input.wav"
    OUTPUT_FILENAME = "output.wav"
    DURATION = 5  # 录音时长（秒）

    # 可用音频设备列表
    list_audio_devices()
    # 2: MacBook Pro Microphone (输入通道: 1, 输出通道: 0)
    # 3: MacBook Pro Speakers (输入通道: 0, 输出通道: 2)

    # 录音并保存
    # input_filename = record_audio(DURATION, INPUT_FILENAME, channels=1, device=3)

    # script = speech_to_text(azure_openai_helper, input_filename)
    # print("transcript:", script)

    # response_text = chat_completion(azure_openai_helper, script)
    # print("chat completion:", response_text)

    response_text = "Hello! I'm an AI language model created by OpenAI. I'm here to assist you with information and answer questions to the best of my ability. How can I help you today?"
    output_filename = speech_synthesis(
        azure_openai_helper, OUTPUT_FILENAME, response_text
    )
    print("speech synthesis:", output_filename)

    # 播放录制的音频
    play_audio(output_filename)
