from pybricks.tools import StopWatch

try:
    import runs.run01.m08_m06_m05 as _variant_m08_m06_m05
except ImportError:
    import m08_m06_m05 as _variant_m08_m06_m05

ACTIVE_VARIANT = "m08_m06_m05"
VARIANTS = {"m08_m06_m05": _variant_m08_m06_m05}


async def run_with_timing(label, coro_fn):
    timer = StopWatch()
    timer.reset()
    print(f"[RUN] {label} start")
    result = await coro_fn()
    elapsed_ms = timer.time()
    print(f"[RUN] {label} done ({elapsed_ms:.0f} ms)")
    return result


def load_variant():
    """ACTIVE_VARIANT で指定したモジュールを返す。"""
    return VARIANTS[ACTIVE_VARIANT]


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
