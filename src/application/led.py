import time

from pinpong.board import PWM, Board, Pin

# 初始化开发板
board = Board()
board.begin()

# 初始化 PWM 引脚
led = PWM(Pin(Pin.P23))

# 主程序
try:
    while True:
        # 红色模式
        led.duty(0)
        time.sleep(2)

        # 绿色模式
        led.duty(100)
        time.sleep(2)

        # 蓝色模式
        led.duty(500)
        time.sleep(2)

except KeyboardInterrupt:
    # 程序中断时关闭灯
    led.duty(0)
