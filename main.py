import threading
import tkinter as tk

from src.service.audio_service import AudioService
from src.service.conversation_service import ConversationService


class GrowthCareBot:
    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.title("Growth Care Bot")
        self.master.geometry("240x360")

        # 绑定空格键
        self.master.bind("<space>", self.spacebar_pressed)

        self.conversation = ConversationService()
        self.audio = AudioService()
        self.thread = None

        # 绑定标签并支持换行
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill="both", expand=True)
        self.label = tk.Label(
            self.main_frame,
            text="Waiting",
            wraplength=200,
            justify="left",
            anchor="w",
        )
        self.label.pack(pady=(20, 10), padx=20, fill="x")

        # 控制按钮
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(side="bottom", fill="x")  # 按钮框架固定在底部
        self.button = tk.Button(
            self.button_frame,
            text="Start Listening",
            command=self.toggle_recording,
            width=18,
            height=1,
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

            # self.master.after(0, lambda: self.label.config(text="Transcribing ..."))
            # transcript = self.audio.speech_to_text()
            # print("transcript:", transcript.strip())

            # self.master.after(0, lambda: self.label.config(text="Encoding Audio ..."))

            self.master.after(0, lambda: self.label.config(text="Chat Completion ..."))
            encoded_input = self.audio.encode_audio()
            response = self.conversation.chat(encoded_input)

            # Generator
            for chunk_pcm in response:
                if chunk_pcm:
                    # print(len(chunk_pcm), self.conversation.transcript_)
                    self.master.after(
                        0, lambda: self.label.config(text=self.conversation.transcript_)
                    )
                    self.audio.play_chunk(chunk_pcm)

            # # self.master.after(0, lambda: self.label.config(text="Synthesizing ..."))
            # # self.audio.speech_synthesis(content)
            # # print("Speech Synthesizied")

            # self.master.after(0, lambda: self.label.config(text=result.transcript))
            # self.audio.play(result.data)
            print("Transcript:", self.conversation.transcript_)
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
