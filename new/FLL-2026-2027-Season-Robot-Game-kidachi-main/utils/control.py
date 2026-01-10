"""
ロボット制御系の共通ユーティリティ。
タイムアウトや計測など、制御まわりの共通処理を提供します。
"""

from typing import Awaitable, Callable, TypeVar

from pybricks.tools import StopWatch, wait

T = TypeVar("T")


async def run_with_timeout(
    start_fn: Callable[[], None],
    done_fn: Callable[[], bool],
    stop_fn: Callable[[], None],
    timeout_ms: int,
    poll_ms: int = 10,
) -> bool:
    """
    非同期ループで完了を監視し、タイムアウトで停止する共通関数。

    Args:
        start_fn: 非同期実行を開始する関数（wait=False で開始するなど）。
        done_fn: 完了を True/False で返す関数。
        stop_fn: タイムアウト時に呼ぶ停止関数。
        timeout_ms: タイムアウト（ミリ秒）。
        poll_ms: ポーリング間隔（ミリ秒）。

    Returns:
        bool: 正常完了で True、タイムアウトで False。
    """
    start_fn()
    timer = StopWatch()
    timer.reset()

    while timer.time() < timeout_ms:
        if done_fn():
            return True
        await wait(poll_ms)

    stop_fn()
    return False


async def run_with_timing(label: str, coro_fn: Callable[[], Awaitable[T]]) -> T:
    """
    実行時間を計測しつつ非同期処理を実行する共通関数。

    Args:
        label: ログに出す識別子（例: run01:m08_m06_m05）
        coro_fn: 実行する非同期関数を返すコールバック

    Returns:
        非同期関数の戻り値
    """
    timer = StopWatch()
    timer.reset()
    print(f"[RUN] {label} start")
    result = await coro_fn()
    elapsed_ms = timer.time()
    print(f"[RUN] {label} done ({elapsed_ms:.0f} ms)")
    return result


def apply_curve_settings(
    set_settings_fn: Callable[[int, int], None],
    speed: int | None,
    acceleration: int | None,
) -> None:
    """
    カーブ用の速度・加速度設定を適用するユーティリティ。

    Args:
        set_settings_fn: settings(straight_speed=..., straight_acceleration=...) を受け取る関数
        speed: 速度（None の場合は適用しない）
        acceleration: 加速度（None の場合は適用しない）
    """
    params: dict[str, int] = {}
    if speed is not None:
        params["straight_speed"] = speed
    if acceleration is not None:
        params["straight_acceleration"] = acceleration
    if params:
        set_settings_fn(**params)
