import threading
import time

from pinpong.board import PWM, Board, Pin, Servo
from unihiker import GUI


class MuseumGuide:
    def __init__(self):
        self.gui = GUI()
        self.stage = 0
        self.lock = threading.Lock()

        # Initialize hardware
        Board().begin()
        self.led = PWM(Pin(Pin.P23))
        self.servo = Servo(Pin(Pin.P21))

    def greet(self, gender: str):
        self.gui.clear()
        # Reset servo angle
        self.look()

        self.gui.draw_image(
            image=f"resource/{gender}.png",
            origin="center",
            x=120,
            y=100,
            w=100,
            h=100,
            onclick=self.next_stage,
        )

        title_color = "#9b3434" if gender == "female" else "#1666d2"
        self.gui.draw_text(
            text="博宝", origin="center", x=120, y=190, color=title_color, font_size=30
        )
        self.gui.draw_text(
            text="Your Private Museum Guide",
            origin="center",
            x=120,
            y=230,
            color="#444444",
            font_size=10,
        )

    def exhibition(self):
        self.gui.clear()
        self.gui.draw_image(
            image="resource/exhibition.png",
            origin="center",
            x=120,
            y=160,
            w=210,
            h=210,
            onclick=self.next_stage,
        )
        self.gui.draw_text(
            text="诗意中国",
            origin="center",
            x=120,
            y=130,
            color="#333333",
            font_size=16,
        )

    def painting(self):
        self.gui.clear()
        # 240x360
        self.gui.draw_image(
            image="resource/painting.png",
            origin="center",
            x=120,
            y=160,
            w=240,
            h=360,
            onclick=self.next_stage,
        )

    def look(self, value: int = 90):
        if self.stage == 3:
            interval = 1
            self.servo.write_angle(90)
            time.sleep(interval)
            self.servo.write_angle(135)
            time.sleep(interval)
            self.servo.write_angle(90)
            time.sleep(interval)
            self.servo.write_angle(45)
            time.sleep(interval)
            self.servo.write_angle(90)
            time.sleep(interval)
        else:
            self.servo.write_angle(value)

    def warning(self):
        self.gui.clear()
        self.gui.draw_image(
            image="resource/warning.png",
            origin="center",
            x=120,
            y=160,
            w=200,
            h=280,
            onclick=lambda: self.next_stage(forward=False),
        )

        # Start red light flashing thread
        threading.Thread(target=self.flash, args=(500, 0.2), daemon=True).start()

    def flash(self, value: int, interval: float):
        while self.stage == 4:
            self.led.duty(0)
            time.sleep(interval)
            self.led.duty(value)
            time.sleep(interval)
            self.led.duty(0)

        # Ensure red light is off when stage changes
        self.led.duty(0)

    def next_stage(self, forward: bool = True):
        with self.lock:
            step = 1 if forward else -1
            self.stage = (self.stage + step) % 5
            self.render()

    def render(self):
        if self.stage == 1:
            self.greet(gender="female")
        elif self.stage == 2:
            self.exhibition()
        elif self.stage == 3:
            self.look()
            self.painting()
        elif self.stage == 4:
            self.warning()
        else:
            self.greet(gender="male")

    def main(self):
        while True:
            self.render()
            time.sleep(600)  # Keep the program running


if __name__ == "__main__":
    guide = MuseumGuide()
    guide.main()
