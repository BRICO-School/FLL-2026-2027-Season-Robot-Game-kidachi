import sys
from importlib import import_module
from pathlib import Path

if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from utils.control import run_with_timing
from utils.runtime import ensure_project_root

ensure_project_root(__file__)

# 現在有効なバージョン（同ディレクトリのファイル名から拡張子を除いたもの）
ACTIVE_VARIANT = "m08_m06_m05"


def load_variant():
    """ACTIVE_VARIANT で指定したモジュールをロードして返す。"""
    module_path = (
        f"{__package__}.{ACTIVE_VARIANT}" if __package__ else f"runs.run01.{ACTIVE_VARIANT}"
    )
    return import_module(module_path)


async def run(hub, robot, left_wheel, right_wheel, left_lift, right_lift):
    variant = load_variant()
    label = f"run01:{ACTIVE_VARIANT}"
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
    from pybricks.tools import multitask, run_task
    from setup import initialize_robot

    hub, robot, left_wheel, right_wheel, left_lift, right_lift = initialize_robot()
    variant = load_variant()
    label = f"run01:{ACTIVE_VARIANT}"

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

    # センサーロガーがあれば並行実行、なければ run だけ実行
    if hasattr(variant, "sensor_logger_task"):
        run_task(
            multitask(variant.sensor_logger_task(hub, robot, left_wheel, right_wheel), timed_run())
        )
    else:
        run_task(timed_run())
