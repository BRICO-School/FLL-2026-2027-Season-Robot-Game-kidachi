from pybricks.tools import StopWatch, wait, multitask, run_task
import m10_m11 as _variant_m10_m11  # 同ディレクトリ内をフラット import
import setup

ACTIVE_VARIANT = "m10_m11"
VARIANTS = {"m10_m11": _variant_m10_m11}


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
    label = f"run03:{ACTIVE_VARIANT}"
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


def main(hub=None, robot=None, left_wheel=None, right_wheel=None, left_lift=None, right_lift=None):
    if hub is None:
        hub, robot, left_wheel, right_wheel, left_lift, right_lift = setup.initialize_robot()
    variant = load_variant()
    label = f"run03:{ACTIVE_VARIANT}"

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


if __name__ == "__main__":
    main()
