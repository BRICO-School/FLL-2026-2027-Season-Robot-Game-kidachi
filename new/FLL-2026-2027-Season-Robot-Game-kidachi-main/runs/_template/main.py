"""
新しい run ディレクトリを作るときのテンプレート。
runXX/main.py をこのファイルからコピーして、ACTIVE_VARIANT とラベルを差し替えてください。
"""

import sys
from importlib import import_module
from pathlib import Path

if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pybricks.tools import multitask, run_task, wait
from utils.control import run_with_timing
from utils.runtime import ensure_project_root

ensure_project_root(__file__)

# 同ディレクトリ内のバリアント（例: sample_variant.py）を指定
ACTIVE_VARIANT = "sample_variant"


def load_variant():
    """
    ACTIVE_VARIANT で指定したモジュールをロードして返す。
    """
    module_path = (
        f"{__package__}.{ACTIVE_VARIANT}" if __package__ else f"runs._template.{ACTIVE_VARIANT}"
    )
    return import_module(module_path)


async def run(hub, robot, left_wheel, right_wheel, left_lift, right_lift):
    variant = load_variant()
    label = f"runXX:{ACTIVE_VARIANT}"
    return await run_with_timing(
        label,
        lambda: variant.run(
            hub,
            robot,
            left_wheel,
            right_wheel,
            left_lift,
            right_lift,
        ),
    )


if __name__ == "__main__":
    from setup import initialize_robot

    hub, robot, left_wheel, right_wheel, left_lift, right_lift = initialize_robot()
    variant = load_variant()
    label = f"runXX:{ACTIVE_VARIANT}"

    async def timed_run():
        await run_with_timing(
            label,
            lambda: variant.run(
                hub,
                robot,
                left_wheel,
                right_wheel,
                left_lift,
                right_lift,
            ),
        )

    if hasattr(variant, "sensor_logger_task"):
        if hasattr(variant, "stop_logging"):

            async def wrapped_run():
                await timed_run()
                variant.stop_logging = True
                await wait(500)

            run_task(
                multitask(
                    variant.sensor_logger_task(hub, robot, left_wheel, right_wheel),
                    wrapped_run(),
                )
            )
        else:
            run_task(
                multitask(
                    variant.sensor_logger_task(hub, robot, left_wheel, right_wheel),
                    timed_run(),
                )
            )
    else:
        run_task(timed_run())
