import sys
import time
from datetime import datetime

from unihiker import GUI, Audio

data = {
    "title": "GrowthCareBot GUI",
    "subtitle": "Python version: " + sys.version.split(" ", maxsplit=1)[0],
    "content": "This is a Python GUI example.",
}


def play_audio(audio: Audio, audio_file: str):
    # global flag
    audio.play(audio_file)
    # u_gui.stop_thread(thread1)
    # flag = 0


# pylint: disable=redefined-outer-name
def display(gui: GUI, data: dict):
    gui.draw_text(
        text=data.get("title", "<TITLE>"),
        origin="center",
        x=120,
        y=30,
        font_size=16,
        color="#0066CC",
    )

    gui.draw_text(
        text=data.get("subtitle", "<SUBTITLE>"),
        origin="center",
        x=120,
        y=50,
        font_size=12,
        color="#0066CC",
    )

    gui.draw_text(
        text=datetime.now().strftime(r"%Y-%m-%d %H:%M:%S"),
        origin="center",
        x=120,
        y=70,
        font_size=10,
        color="#FF6600",
    )

    gui.draw_text(
        text=data.get("content", "<CONTENT>"),
        origin="center",
        x=120,
        y=100,
        font_size=10,
        color="#FF6600",
    )

    gui.add_button(
        text="Record",
        origin="center",
        x=120,
        y=240,
        w=100,
        onclick=on_record_click,
    )

    gui.add_button(
        text="Play",
        origin="center",
        x=120,
        y=280,
        w=100,
        onclick=on_play_click,
    )


def on_record_click():
    data["content"] = "Recording ..."
    u_audio = Audio()
    u_audio.record("test.wav", duration=10)


def on_play_click():
    data["content"] = "Playing ..."
    u_audio = Audio()
    u_audio.start_play("test.wav")


def main():
    u_gui = GUI()

    while True:
        u_gui.clear()
        display(u_gui, data)
        u_gui.update()
        time.sleep(1)


if __name__ == "__main__":
    main()
