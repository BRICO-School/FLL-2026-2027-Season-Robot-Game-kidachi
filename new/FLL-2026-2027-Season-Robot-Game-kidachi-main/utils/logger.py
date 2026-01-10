"""
ログ出力ユーティリティ。

目的:
- 既存の print() を活かしつつ、コンソールとファイルへ同時出力（tee）する
- ログはプロジェクトルート直下の logs/ に保存する
"""

from __future__ import annotations

import builtins
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator


def logs_dir() -> Path:
    """logs ディレクトリの Path を返し、なければ作成する。"""
    root = Path(__file__).resolve().parents[1]
    path = root / "logs"
    path.mkdir(exist_ok=True)
    return path


@contextmanager
def tee_stdout(run_name: str) -> Iterator[Path]:
    """
    print をフックし、コンソールとファイルに同時出力するコンテキストマネージャ。

    Args:
        run_name: ログファイル名に付与する識別子（例: "run01"）

    Yields:
        Path: 書き込み先のログファイルパス
    """
    log_path = logs_dir() / f"{run_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
    log_file = log_path.open("a", encoding="utf-8")
    original_print = builtins.print

    def _print(*args, **kwargs):
        sep = kwargs.get("sep", " ")
        end = kwargs.get("end", "\n")
        message = sep.join(str(a) for a in args) + end
        log_file.write(message)
        log_file.flush()
        original_print(*args, **kwargs)

    builtins.print = _print
    try:
        yield log_path
    finally:
        builtins.print = original_print
        log_file.close()
