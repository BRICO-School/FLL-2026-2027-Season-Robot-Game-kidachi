from pybricks.tools import StopWatch, multitask, run_task
import m09_m07 as _variant_m09_m07  # 同ディレクトリ内をフラット import
import setup

ACTIVE_VARIANT = "m09_m07"
VARIANTS = {"m09_m07": _variant_m09_m07}


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
    label = f"run02:{ACTIVE_VARIANT}"
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
    label = f"run02:{ACTIVE_VARIANT}"

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
        run_task(multitask(variant.sensor_logger_task(hub, robot, left_wheel, right_wheel), timed_run()))
    else:
        run_task(timed_run())


if __name__ == "__main__":
    main()
