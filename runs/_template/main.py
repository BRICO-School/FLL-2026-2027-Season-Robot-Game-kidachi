"""
新しい run ディレクトリを作るときのテンプレート。
runXX/main.py をこのファイルからコピーして、ACTIVE_VARIANT とラベルを差し替えてください。
"""

from pybricks.tools import StopWatch, multitask, run_task, wait

# 同ディレクトリ内のバリアント（例: sample_variant.py）を指定
ACTIVE_VARIANT = "sample_variant"
try:
    import runs._template.sample_variant as _variant_sample
except ImportError:
    import sample_variant as _variant_sample

VARIANTS = {"sample_variant": _variant_sample}


async def run_with_timing(label, coro_fn):
    timer = StopWatch()
    timer.reset()
    print(f"[RUN] {label} start")
    result = await coro_fn()
    elapsed_ms = timer.time()
    print(f"[RUN] {label} done ({elapsed_ms:.0f} ms)")
    return result


def load_variant():
    """
    ACTIVE_VARIANT で指定したモジュールをロードして返す。
    """
    return VARIANTS[ACTIVE_VARIANT]


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
