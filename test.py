import sys
import time

import openai
from unihiker import GUI, Audio


def main():
    gui = GUI()
    counter = 0

    while True:
        # 动态更新文字
        gui.clear()  # 清除之前的内容
        gui.draw_text(
            text=f"Counter: {counter}",
            origin="center",
            x=120,
            y=160,
            font_size=10,
            color="#0066CC",
        )
        gui.update()

        counter += 1
        time.sleep(1)  # 每秒更新一次


if __name__ == "__main__":
    main()
