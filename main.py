import threading
import tkinter as tk

from src.service.audio_service import AudioService
from src.service.conversation_service import ConversationService


class GrowthCareBot:
    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.title("Growth Care Bot")
        self.master.bind("<space>", self.spacebar_pressed)

        self.conversation = ConversationService()
        self.audio = AudioService()
        self.thread = None

        self.label = tk.Label(master, text="Waiting")
        self.label.pack(pady=20)

        self.button = tk.Button(
            master, text="Start Listening", command=self.toggle_recording
        )
        self.button.pack(pady=10)

    def on_closing(self):
        if self.audio and self.audio.recording:
            self.audio.recording = False
            self.thread.join()

        self.master.destroy()

    def reset_interface(self):
        if self.audio and self.audio.recording:
            self.audio.recording = False

        self.label.config(text="Waiting")
        self.button.config(text="Start Listening")
        print("-" * 100)

    def toggle_recording(self):
        if self.audio and self.audio.recording:
            self.stop_recording()
        else:
            self.start_recording()

    # pylint: disable=unused-argument
    def spacebar_pressed(self, event):
        # Simulate button click when spacebar is pressed
        self.button.invoke()

    def start_recording(self):
        self.button.config(text="Stop Listening")
        self.label.config(text="Recording...")
        self.audio.recording = True
        print("Start recording")

        self.thread = threading.Thread(target=self.audio.record)
        self.thread.start()

    def stop_recording(self):
        self.audio.recording = False
        self.thread.join()
        print("Stop recording")

        self.button.config(text="Start Listening")
        self.audio.save()
        print("Recording saved")

        # Create a new thread for processing the audio and updating the GUI
        processing_thread = threading.Thread(target=self.run)
        processing_thread.start()

    def run(self) -> "GrowthCareBot":
        # pylint: disable=too-many-try-statements
        try:
            # 通过after方法在主线程更新标签
            self.master.after(0, lambda: self.label.config(text="Transcribing ..."))
            transcript = self.audio.speech_to_text()
            print("transcript:", transcript.strip())

            self.master.after(0, lambda: self.label.config(text="Chat Completion ..."))
            content = self.conversation.chat(transcript.strip())
            print("chat completion:", content)

            self.master.after(0, lambda: self.label.config(text="Synthesizing ..."))
            self.audio.speech_synthesis(content)
            print("Speech Synthesizied")

            self.master.after(0, lambda: self.label.config(text="Playing..."))
            self.audio.play()
            print("Audio Played")
        # pylint: disable=broad-exception-caught
        except Exception as exc:
            print("Error processing audio:", exc)
        finally:
            self.master.after(0, self.reset_interface)

        return self


if __name__ == "__main__":
    root = tk.Tk()
    app = GrowthCareBot(root)

    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
