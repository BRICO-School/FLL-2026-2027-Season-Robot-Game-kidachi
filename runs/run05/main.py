from pybricks.tools import StopWatch
try:
    import runs.run05.m01_m02_kanna as _variant_m01_m02_kanna
except ImportError:
    import m01_m02_kanna as _variant_m01_m02_kanna

ACTIVE_VARIANT = "m01_m02_kanna"
VARIANTS = {"m01_m02_kanna": _variant_m01_m02_kanna}


async def run_with_timing(label, coro_fn):
    timer = StopWatch()
    timer.reset()
    print(f"[RUN] {label} start")
    result = await coro_fn()
    elapsed_ms = timer.time()
    print(f"[RUN] {label} done ({elapsed_ms:.0f} ms)")
    return result


def load_variant():
    return VARIANTS[ACTIVE_VARIANT]


async def run(hub, robot, left_wheel, right_wheel, left_lift, right_lift):
    variant = load_variant()
    label = f"run05:{ACTIVE_VARIANT}"
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
    from pybricks.tools import multitask, run_task, wait
    from setup import initialize_robot

    hub, robot, left_wheel, right_wheel, left_lift, right_lift = initialize_robot()
    variant = load_variant()
    label = f"run05:{ACTIVE_VARIANT}"

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
