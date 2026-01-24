"""
司令塔エントリーポイント。
各 runXX ディレクトリに chdir して main.py をフラット import し、main() を実行する。
"""

import os
import sys

from pybricks.parameters import Button, Color, Port
from pybricks.pupdevices import ForceSensor
from pybricks.tools import wait

import setup

PROGRAMS = [
    {"dir": "run01", "display": 1},
    {"dir": "run02", "display": 2},
    {"dir": "run03", "display": 3},
    {"dir": "run04", "display": 4},
    {"dir": "run05", "display": 5},
    {"dir": "run06", "display": 6},
]


def load_and_run(run_dir, hub, robot, left_wheel, right_wheel, left_lift, right_lift):
    """run_dir/main.py をフラット import して main() を呼ぶ。"""
    cwd = os.getcwd()
    try:
        os.chdir(run_dir)
        if "main" in sys.modules:
            del sys.modules["main"]
        mod = __import__("main")
        if hasattr(mod, "main"):
            mod.main(hub, robot, left_wheel, right_wheel, left_lift, right_lift)
    finally:
        os.chdir(cwd)


def main():
    hub, robot, left_wheel, right_wheel, left_lift, right_lift = setup.initialize_robot()
    button = ForceSensor(Port.C)
    program_id = 0
    max_program = len(PROGRAMS) - 1

    while True:
        current = PROGRAMS[program_id]
        display_num = current.get("display", program_id)
        hub.display.char(str(display_num))

        pressed = hub.buttons.pressed()
        if Button.RIGHT in pressed:
            program_id = (program_id + 1) % (max_program + 1)
            hub.light.on(Color.GREEN)
            wait(150)
            hub.light.off()
        elif Button.LEFT in pressed:
            program_id = program_id - 1 if program_id > 0 else max_program
            hub.light.on(Color.BLUE)
            wait(150)
            hub.light.off()

        if button.force() >= 0.5:
            hub.light.on(Color.RED)
            load_and_run(current["dir"], hub, robot, left_wheel, right_wheel, left_lift, right_lift)
            hub.light.off()
            wait(200)

        wait(80)


if __name__ == "__main__":
    main()
