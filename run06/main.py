from pybricks.tools import StopWatch, multitask, run_task, wait
import M03_M04 as _variant_M03_M04  # 同ディレクトリ内をフラット import
import M03_M04_ayumu_01_30 as _variant_M03_M04_ayumu_01_30  # 同ディレクトリ内をフラット import
import m13_m03 as _variant_m13_m03  # 同ディレクトリ内をフラット import
import setup

CURRENT_MISSION = None
ACTIVE_VARIANT = "M03_M04_ayumu_01_30"
VARIANTS = {
    "M03_M04_ayumu_01_30": _variant_M03_M04_ayumu_01_30,
    "M03_M04": _variant_M03_M04,
    "m13_m03": _variant_m13_m03,
}


async def run_with_timing(label, coro_fn):
    timer = StopWatch()
    timer.reset()
    print(f"[RUN] {label} start")
    result = await coro_fn()
    elapsed_ms = timer.time()
    print(f"[RUN] {label} done ({elapsed_ms:.0f} ms)")
    return result


def get_active_variant_name():
    if isinstance(CURRENT_MISSION, str) and CURRENT_MISSION in VARIANTS:
        return CURRENT_MISSION
    for name, variant in VARIANTS.items():
        if getattr(variant, "IS_CURRENT", False):
            return name
    return ACTIVE_VARIANT


def load_variant():
    name = get_active_variant_name()
    return name, VARIANTS[name]


async def run(hub, robot, left_wheel, right_wheel, left_lift, right_lift):
    variant_name, variant = load_variant()
    label = f"run06:{variant_name}"
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
    variant_name, variant = load_variant()
    label = f"run06:{variant_name}"

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
