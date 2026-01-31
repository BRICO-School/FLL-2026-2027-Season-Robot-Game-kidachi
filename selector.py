"""
PC 専用のビルド＆送信ツール。Hub には送らない。
run01〜run06 を 1 つの hub_main.py に結合し、pybricksdev で送信する。
デフォルトは送信のみ（Hub 側で手動開始）。

使い方:
    python selector.py
    # 生成された hub_main.py を送信（開始はしない）
    pybricksdev run ble --no-start hub_main.py --name "Pybricks Hub"
"""

import argparse
import re
import shutil
import subprocess
from pathlib import Path

import build


def ensure_pybricksdev_available() -> None:
    if shutil.which("pybricksdev") is None:
        raise SystemExit("pybricksdev が見つかりません。pipx/pip でインストールしてください。")


def supports_no_start() -> bool:
    try:
        result = subprocess.run(
            ["pybricksdev", "run", "ble", "--help"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return False
    help_text = (result.stdout or "") + (result.stderr or "")
    return "--no-start" in help_text


def main():
    parser = argparse.ArgumentParser(description="PC-only: build hub_main.py and send via pybricksdev")
    parser.add_argument(
        "--run-id",
        type=int,
        default=None,
        help="(deprecated) ignored. RUN selection happens on Hub menu now.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="hub_main.py",
        help="output filename (default: hub_main.py)",
    )
    parser.add_argument(
        "--hub",
        default="Pybricks Hub",
        help='target hub name for pybricksdev (default: "Pybricks Hub")',
    )
    parser.add_argument(
        "--start-now",
        action="store_true",
        help="start the program immediately after sending (default: no start)",
    )
    parser.add_argument(
        "--single",
        help="build and run a single run directory or mission file (e.g., run06 or run06/m13_m03.py)",
    )
    parser.add_argument(
        "--build-only",
        action="store_true",
        help="generate hub_main.py without sending to Hub",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    output_path = root / args.output
    if args.run_id is not None:
        print("Warning: --run-id is deprecated and ignored. Select RUN on Hub menu.")

    if args.single:
        single_path = Path(args.single)
        if not single_path.is_absolute():
            single_path = root / single_path
        if single_path.is_file():
            candidate = single_path.parent
            mission_override = single_path.stem if re.match(r"[mM]\d", single_path.stem) else None
        else:
            candidate = single_path
            mission_override = None
        run_dir = None
        current = candidate
        while True:
            if current.name.startswith("run") and re.match(r"run\d+", current.name):
                run_dir = current
                break
            if current == current.parent:
                break
            current = current.parent
        if run_dir is None or not run_dir.is_dir():
            raise FileNotFoundError(
                f"Run directory not found from: {single_path}. "
                "Open a file inside runXX or pass runXX."
            )
        build.build(run_dir, output_path, mission_override=mission_override)
    else:
        run_dirs = [p for p in root.glob("run*") if p.is_dir() and re.match(r"run\d+", p.name)]
        if not run_dirs:
            raise FileNotFoundError("No run directories found (expected run01, run02, ...).")
        build.build_multi(run_dirs, output_path)

    if args.build_only:
        print("Build completed. Skip sending because --build-only is set.")
        return

    ensure_pybricksdev_available()
    cmd = ["pybricksdev", "run", "ble"]
    if not args.start_now:
        if supports_no_start():
            cmd.append("--no-start")
        else:
            print("Warning: pybricksdev が --no-start をサポートしていません。即時開始になります。")
    cmd.extend([str(output_path), "--name", args.hub])
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=str(root))


if __name__ == "__main__":
    main()
