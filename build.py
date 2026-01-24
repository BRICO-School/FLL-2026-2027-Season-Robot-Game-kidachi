"""
PC側で実行するビルドスクリプト。
run01〜run06 を 1 ファイル (hub_main.py) に結合し、Hub 側のメニューで実行を切り替える。
Hub 側では import なしで動作するコードを生成する。

使い方:
    python build.py
生成物:
    hub_main.py （カレントディレクトリ直下）
"""

import argparse
import ast
import re
from pathlib import Path
from typing import Iterable, List, Sequence


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def strip_main_guard(text: str) -> str:
    """__main__ ブロックを除去する。"""
    lines = text.splitlines()
    out: List[str] = []
    skipping = False
    guard_indent = 0

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('if __name__ == "__main__"') or stripped.startswith("if __name__ == '__main__'"):
            skipping = True
            guard_indent = len(line) - len(line.lstrip())
            continue

        if skipping:
            if not line.strip():
                continue
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= guard_indent:
                skipping = False
            else:
                continue

        if not skipping:
            out.append(line)

    return "\n".join(out)


def drop_setup_imports(text: str) -> str:
    """mission / main から setup import を削除する。"""
    cleaned = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("import setup") or stripped.startswith("from setup import"):
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


def collect_exports(source: str) -> List[str]:
    """mission ファイルで公開されているシンボル名を抽出する。"""
    names = set()
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name):
                names.add(node.target.id)
    return sorted(name for name in names if not name.startswith("_"))


def collect_global_names(source: str) -> List[str]:
    """global 文で参照されているシンボル名を抽出する。"""
    names = set()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Global):
            names.update(node.names)
    return sorted(names)


def rewrite_mission(path: Path) -> tuple[str, List[str], List[str]]:
    """mission ファイルを Hub 用に整形し、公開シンボル一覧を返す。"""
    text = load_text(path)
    text = drop_setup_imports(strip_main_guard(text))
    exports = collect_exports(text)
    global_names = collect_global_names(text)
    return text, exports, global_names


def mission_binding(mission_name: str, exports: Iterable[str], global_names: Iterable[str]) -> str:
    lines = [
        "# ---- mission binding ----",
        "class _MissionModule:",
        "    pass",
        f"{mission_name} = _MissionModule()",
    ]
    for name in exports:
        lines.extend(
            [
                "try:",
                f"    {mission_name}.{name} = {name}",
                "except NameError:",
                "    pass",
            ]
        )
    return "\n".join(lines)


def rewrite_main(main_text: str, mission_names: List[str]) -> str:
    """main.py の import をファイル内参照に書き換える。"""
    main_text = drop_setup_imports(strip_main_guard(main_text))
    lines: List[str] = []
    for line in main_text.splitlines():
        stripped = line.strip()
        handled = False
        for mission in mission_names:
            pattern_import = rf"^(?P<indent>\s*)import\s+(?P<prefix>[\w.]*\.)?{mission}\s+as\s+(?P<alias>[\w_]+)"
            pattern_from = rf"^(?P<indent>\s*)from\s+[\w.]*\s+import\s+{mission}\s+as\s+(?P<alias>[\w_]+)"

            for pattern in (pattern_import, pattern_from):
                match = re.match(pattern, line)
                if match:
                    indent = match.group("indent")
                    alias = match.group("alias")
                    lines.append(f"{indent}{alias} = {mission}")
                    handled = True
                    break
            if handled:
                break

        if not handled:
            lines.append(line)

    rewritten = "\n".join(lines)
    rewritten = rewritten.replace("setup.", "")
    return rewritten


def normalize_run_arg(run_arg: str) -> str:
    """
    Accepts "run01", "01", or "1" and returns zero-padded run name (e.g., "run01").
    Other strings are returned unchanged.
    """
    text = run_arg.strip()
    match = re.fullmatch(r"run(\d+)", text, re.IGNORECASE)
    if match:
        num = match.group(1)
    else:
        match = re.fullmatch(r"(\d+)", text)
        if not match:
            return text
        num = match.group(1)
    return f"run{int(num):02d}"


def indent_text(text: str, spaces: int) -> str:
    prefix = " " * spaces
    return "\n".join(prefix + line if line else "" for line in text.splitlines())


def build_single_run_block(run_dir: Path) -> str:
    """runXX ディレクトリを 1 つのファクトリ関数にまとめたコードを返す。"""
    mission_files = [
        path for path in sorted(run_dir.glob("m*.py")) if path.name != "main.py" and re.match(r"m\d", path.stem)
    ]
    if not mission_files:
        raise FileNotFoundError(f"No mission file (m*.py) found in {run_dir}")

    setup_path = run_dir / "setup.py"
    main_path = run_dir / "main.py"
    if not main_path.exists():
        raise FileNotFoundError(f"main.py not found in {run_dir}")

    mission_names: List[str] = []
    parts: List[str] = [f"def _make_{run_dir.name}():", f"    # Auto-generated from {run_dir.name}"]

    for mission_path in mission_files:
        mission_name = mission_path.stem
        mission_names.append(mission_name)
        mission_text, exports, global_names = rewrite_mission(mission_path)
        parts.append(f"    # ---- mission: {mission_name} ----")
        if global_names:
            parts.append(f"    global {', '.join(global_names)}")
        parts.append(indent_text(mission_text, 4))
        parts.append(indent_text(mission_binding(mission_name, exports, global_names), 4))

    if setup_path.exists():
        parts.append("    # ---- setup ----")
        parts.append(indent_text(load_text(setup_path), 4))

    parts.append("    # ---- main ----")
    main_text = load_text(main_path)
    parts.append(indent_text(rewrite_main(main_text, mission_names), 4))
    parts.append("    # ---- run entry ----")
    parts.append("    async def _run_entry(ctx):")
    parts.append("        variant = load_variant()")
    parts.append("        has_stop_logging = \"stop_logging\" in globals()")
    parts.append("        async def timed_run():")
    parts.append(
        "            await run(ctx.hub, ctx.robot, ctx.left_wheel, ctx.right_wheel, ctx.left_lift, ctx.right_lift)"
    )
    parts.append("        if hasattr(variant, \"sensor_logger_task\"):")
    parts.append("            if has_stop_logging:")
    parts.append("                async def wrapped_run():")
    parts.append("                    await timed_run()")
    parts.append("                    globals()[\"stop_logging\"] = True")
    parts.append("                    await wait(500)")
    parts.append(
        "                await multitask(variant.sensor_logger_task(ctx.hub, ctx.robot, ctx.left_wheel, ctx.right_wheel), wrapped_run())"
    )
    parts.append("            else:")
    parts.append(
        "                await multitask(variant.sensor_logger_task(ctx.hub, ctx.robot, ctx.left_wheel, ctx.right_wheel), timed_run())"
    )
    parts.append("        else:")
    parts.append("            await timed_run()")
    parts.append("    return RunBundle(initialize_robot, _run_entry)")
    return "\n".join(parts)


def build_multi(run_dirs: Sequence[Path], output: Path) -> None:
    """複数 run を 1 ファイルにまとめ、Hub のメニューで切り替える hub_main.py を生成する。"""
    if not run_dirs:
        raise FileNotFoundError("No run directories found.")

    run_dirs = sorted(run_dirs, key=lambda p: p.name)
    header = [
        "# Auto-generated menu hub_main.py. Do not edit this file on Hub.",
        "# Select run on Hub; no PC-side RUN selection required.",
        "from pybricks.hubs import PrimeHub",
        "from pybricks.parameters import Button, Port",
        "from pybricks.pupdevices import ForceSensor",
        "from pybricks.tools import multitask, run_task, wait",
        "",
        "_HUB = None",
        "_TOUCH = None",
        "_LAST_CONTEXT = None",
        "STORAGE_OFFSET = 0",
        "STORAGE_LEN = 1",
        "RUN_MIN = 1",
    ]

    body: List[str] = []
    factory_entries: List[str] = []
    for idx, run_dir in enumerate(run_dirs, start=1):
        run_name = run_dir.name
        factory_entries.append(f"    \"{idx}\": _make_{run_name}")
        body.append("")
        body.append(build_single_run_block(run_dir))

    max_run = len(run_dirs)
    menu_line = f"RUN_MAX = {max_run}"
    body.append("")
    body.append(menu_line)
    body.append("")
    body.append("RUNNERS = {\n" + ",\n".join(factory_entries) + "\n}")
    body.append(
        """
class StopRequested(Exception):
    pass


class RunContext:
    def __init__(self, hub, robot, left_wheel, right_wheel, left_lift, right_lift):
        self.hub = hub
        self.robot = robot
        self.left_wheel = left_wheel
        self.right_wheel = right_wheel
        self.left_lift = left_lift
        self.right_lift = right_lift


class RunBundle:
    def __init__(self, setup_fn, run_fn):
        self.setup = setup_fn
        self.run = run_fn


def _get_hub():
    global _HUB
    if _HUB is None:
        _HUB = PrimeHub()
    return _HUB


def _get_touch():
    global _TOUCH
    if _TOUCH is None:
        _TOUCH = _detect_touch_sensor()
    return _TOUCH


def _set_stop_button(buttons):
    hub = _get_hub()
    try:
        hub.system.set_stop_button(buttons)
    except Exception:
        pass


def _detect_touch_sensor():
    for port in (Port.A, Port.B, Port.C, Port.D, Port.E, Port.F):
        try:
            return ForceSensor(port)
        except Exception:
            pass
    return None


def _touch_pressed():
    sensor = _get_touch()
    if sensor is None:
        return False
    try:
        return sensor.pressed()
    except Exception:
        try:
            return sensor.touched()
        except Exception:
            return False


def _wait_touch_release():
    sensor = _get_touch()
    if sensor is None:
        return
    while _touch_pressed():
        wait(20)


def _read_last_selection():
    hub = _get_hub()
    try:
        data = hub.system.storage(STORAGE_OFFSET, read=STORAGE_LEN)
    except Exception:
        return None
    if not data:
        return None
    value = data[0]
    if value == 0:
        return None
    if RUN_MIN <= value <= RUN_MAX:
        return value
    return None


def _write_last_selection(value):
    if not (RUN_MIN <= value <= RUN_MAX):
        return
    hub = _get_hub()
    try:
        hub.system.storage(STORAGE_OFFSET, write=bytes([int(value)]))
    except Exception:
        pass


def _wait_for_release(button):
    hub = _get_hub()
    while True:
        try:
            if button not in hub.buttons.pressed():
                return
        except Exception:
            pass
        wait(20)


def _stop_all_motors():
    ctx = _LAST_CONTEXT
    if not ctx:
        return
    try:
        ctx[1].stop()
    except Exception:
        pass
    for motor in ctx[2:]:
        try:
            motor.stop()
        except Exception:
            pass


async def _monitor_stop():
    hub = _get_hub()
    while True:
        try:
            pressed = hub.buttons.pressed()
        except Exception:
            pressed = []
        if Button.CENTER in pressed:
            _stop_all_motors()
            raise StopRequested("center stop")
        await wait(20)


def _run_selected(selected):
    factory = RUNNERS.get(str(selected))
    if factory is None:
        return
    try:
        bundle = factory()
        ctx = RunContext(*bundle.setup())
        global _LAST_CONTEXT
        _LAST_CONTEXT = ctx
        run_task(multitask(_monitor_stop(), bundle.run(ctx)))
    except StopRequested:
        return
    except BaseException as exc:
        print("Run failed:", exc)
        _stop_all_motors()


def select_loop():
    _set_stop_button((Button.CENTER, Button.BLUETOOTH))
    selected = _read_last_selection() or RUN_MIN
    while True:
        hub = _get_hub()
        try:
            hub.display.text(str(int(selected)))
        except Exception:
            try:
                hub.display.number(int(selected))
            except Exception:
                pass
        if _touch_pressed():
            _wait_touch_release()
            _write_last_selection(selected)
            _run_selected(selected)
            _wait_touch_release()
        try:
            pressed = hub.buttons.pressed()
        except Exception:
            pressed = []
        if Button.LEFT in pressed:
            _wait_for_release(Button.LEFT)
            selected -= 1
            if selected < RUN_MIN:
                selected = RUN_MAX
            _write_last_selection(selected)
        elif Button.RIGHT in pressed:
            _wait_for_release(Button.RIGHT)
            selected += 1
            if selected > RUN_MAX:
                selected = RUN_MIN
            _write_last_selection(selected)
        wait(20)


def main():
    return select_loop()


if __name__ == "__main__":
    main()
""".strip()
    )

    output.write_text("\n".join(header + body) + "\n", encoding="utf-8")
    print(f"Generated {output} with runs: {[d.name for d in run_dirs]}")


def build(run_dir: Path, output: Path) -> None:
    mission_files = [
        path for path in sorted(run_dir.glob("m*.py")) if path.name != "main.py" and re.match(r"m\d", path.stem)
    ]
    if not mission_files:
        raise FileNotFoundError(f"No mission file (m*.py) found in {run_dir}")

    setup_path = run_dir / "setup.py"
    main_path = run_dir / "main.py"
    if not main_path.exists():
        raise FileNotFoundError(f"main.py not found in {run_dir}")

    mission_names: List[str] = []
    parts: List[str] = [
        f"# Auto-generated from {run_dir.name}. Do not edit this file on Hub.",
        f"# Missions: {', '.join(path.stem for path in mission_files)}",
    ]

    for mission_path in mission_files:
        mission_name = mission_path.stem
        mission_names.append(mission_name)
        mission_text, exports, global_names = rewrite_mission(mission_path)
        parts.append(f"# ---- mission: {mission_name} ----")
        if global_names:
            parts.append(f"global {', '.join(global_names)}")
        parts.append(mission_text)
        parts.append(mission_binding(mission_name, exports, global_names))

    if setup_path.exists():
        parts.append("# ---- setup ----")
        parts.append(load_text(setup_path))

    parts.append("# ---- main ----")
    main_text = load_text(main_path)
    parts.append(rewrite_main(main_text, mission_names))

    output.write_text("\n\n".join(parts) + "\n", encoding="utf-8")
    print(f"Generated {output} from {run_dir.name}")


def main():
    parser = argparse.ArgumentParser(description="Build hub_main.py (menu-based multi-run)")
    parser.add_argument(
        "-o",
        "--output",
        default="hub_main.py",
        help="output filename (default: hub_main.py)",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    run_dirs = [p for p in root.glob("run*") if p.is_dir() and re.match(r"run\d+", p.name)]
    build_multi(run_dirs, root / args.output)


if __name__ == "__main__":
    main()
