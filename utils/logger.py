"""
ログ出力ユーティリティ。

目的:
- 既存の print() を活かしつつ、コンソールとファイルへ同時出力（tee）する
- ログはプロジェクトルート直下の logs/ に保存する
"""

try:
    import builtins
    from datetime import datetime
    from pathlib import Path
except ImportError:
    builtins = None
    datetime = None
    Path = None


class _NullTee:
    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, tb):
        return False


def logs_dir():
    """logs ディレクトリの Path を返し、なければ作成する。"""
    if Path is None:
        return None
    root = Path(__file__).resolve().parents[1]
    path = root / "logs"
    try:
        path.mkdir(exist_ok=True)
    except Exception:
        return None
    return path


def tee_stdout(run_name):
    """
    print をフックし、コンソールとファイルに同時出力する。

    Args:
        run_name: ログファイル名に付与する識別子（例: "run01"）
    """
    if builtins is None or datetime is None or Path is None:
        return _NullTee()

    log_root = logs_dir()
    if log_root is None:
        return _NullTee()

    log_path = log_root / f"{run_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
    try:
        log_file = log_path.open("a", encoding="utf-8")
    except Exception:
        return _NullTee()

    original_print = builtins.print

    class _Tee:
        def __enter__(self):
            def _print(*args, **kwargs):
                sep = kwargs.get("sep", " ")
                end = kwargs.get("end", "\n")
                message = sep.join(str(a) for a in args) + end
                try:
                    log_file.write(message)
                    log_file.flush()
                except Exception:
                    pass
                original_print(*args, **kwargs)

            builtins.print = _print
            return log_path

        def __exit__(self, exc_type, exc, tb):
            builtins.print = original_print
            try:
                log_file.close()
            except Exception:
                pass
            return False

    return _Tee()
